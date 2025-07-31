"""
Registry for managing multiple MCP server connections.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set

from ..core.models import MCPServer, MCPServerStatus, Tool, ToolCall, ToolResult
from .client import MCPClient

logger = logging.getLogger(__name__)


class MCPRegistry:
    """Registry for managing multiple MCP server connections."""
    
    def __init__(self):
        self._servers: Dict[str, MCPServer] = {}
        self._clients: Dict[str, MCPClient] = {}
        self._tools_cache: Dict[str, Tool] = {}  # tool_name -> Tool
    
    def register_server(self, server: MCPServer) -> None:
        """Register a new MCP server."""
        self._servers[server.id] = server
        self._clients[server.id] = MCPClient(server)
        logger.info(f"Registered MCP server: {server.name} ({server.id})")
    
    def unregister_server(self, server_id: str) -> None:
        """Unregister an MCP server."""
        if server_id in self._servers:
            # Disconnect if connected
            asyncio.create_task(self.disconnect_server(server_id))
            
            # Remove from caches
            server = self._servers[server_id]
            for tool in server.tools:
                if tool.name in self._tools_cache:
                    del self._tools_cache[tool.name]
            
            del self._servers[server_id]
            del self._clients[server_id]
            
            logger.info(f"Unregistered MCP server: {server_id}")
    
    async def connect_server(self, server_id: str) -> bool:
        """Connect to a specific MCP server."""
        if server_id not in self._clients:
            logger.error(f"Server {server_id} not registered")
            return False
        
        client = self._clients[server_id]
        success = await client.connect()
        
        if success:
            # Update tools cache
            for tool in client.get_available_tools():
                self._tools_cache[tool.name] = tool
        
        return success
    
    async def disconnect_server(self, server_id: str) -> None:
        """Disconnect from a specific MCP server."""
        if server_id in self._clients:
            client = self._clients[server_id]
            await client.disconnect()
            
            # Remove tools from cache
            server = self._servers[server_id]
            for tool in server.tools:
                if tool.name in self._tools_cache:
                    del self._tools_cache[tool.name]
    
    async def connect_all(self, server_ids: Optional[List[str]] = None) -> Dict[str, bool]:
        """Connect to all registered servers or specified servers."""
        if server_ids is None:
            server_ids = list(self._servers.keys())
        
        results = {}
        tasks = []
        
        for server_id in server_ids:
            if server_id in self._servers:
                task = asyncio.create_task(self.connect_server(server_id))
                tasks.append((server_id, task))
        
        for server_id, task in tasks:
            try:
                results[server_id] = await task
            except Exception as e:
                logger.error(f"Failed to connect to server {server_id}: {e}")
                results[server_id] = False
        
        return results
    
    async def disconnect_all(self) -> None:
        """Disconnect from all servers."""
        tasks = []
        
        for server_id in self._servers:
            task = asyncio.create_task(self.disconnect_server(server_id))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, any], call_id: Optional[str] = None) -> ToolResult:
        """Call a tool by name across all connected servers."""
        if tool_name not in self._tools_cache:
            return ToolResult(
                call_id=call_id,
                success=False,
                error=f"Tool '{tool_name}' not found in any connected server"
            )
        
        tool = self._tools_cache[tool_name]
        server_id = tool.server_id
        
        if server_id not in self._clients:
            return ToolResult(
                call_id=call_id,
                success=False,
                error=f"Server '{server_id}' not available"
            )
        
        client = self._clients[server_id]
        
        if self._servers[server_id].status != MCPServerStatus.CONNECTED:
            return ToolResult(
                call_id=call_id,
                success=False,
                error=f"Server '{server_id}' not connected"
            )
        
        tool_call = ToolCall(
            tool_name=tool_name,
            parameters=parameters,
            call_id=call_id
        )
        
        return await client.call_tool(tool_call)
    
    def get_servers(self, status: Optional[MCPServerStatus] = None) -> List[MCPServer]:
        """Get servers, optionally filtered by status."""
        servers = list(self._servers.values())
        
        if status is not None:
            servers = [s for s in servers if s.status == status]
        
        return servers
    
    def get_server(self, server_id: str) -> Optional[MCPServer]:
        """Get a specific server by ID."""
        return self._servers.get(server_id)
    
    def get_connected_servers(self) -> List[MCPServer]:
        """Get all connected servers."""
        return self.get_servers(MCPServerStatus.CONNECTED)
    
    def get_available_tools(self, server_id: Optional[str] = None) -> List[Tool]:
        """Get available tools, optionally from a specific server."""
        if server_id is not None:
            if server_id in self._servers:
                return self._servers[server_id].tools
            return []
        
        return list(self._tools_cache.values())
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a specific tool by name."""
        return self._tools_cache.get(tool_name)
    
    def get_tools_by_server(self, server_id: str) -> List[Tool]:
        """Get tools from a specific server."""
        if server_id in self._servers:
            return self._servers[server_id].tools
        return []
    
    def search_tools(self, query: str, server_ids: Optional[List[str]] = None) -> List[Tool]:
        """Search for tools by name or description."""
        tools = self.get_available_tools()
        
        if server_ids is not None:
            tools = [t for t in tools if t.server_id in server_ids]
        
        query = query.lower()
        matching_tools = []
        
        for tool in tools:
            if (query in tool.name.lower() or 
                query in tool.description.lower()):
                matching_tools.append(tool)
        
        return matching_tools
    
    def get_server_status_summary(self) -> Dict[str, Dict[str, any]]:
        """Get a summary of all server statuses."""
        summary = {}
        
        for server_id, server in self._servers.items():
            summary[server_id] = {
                "name": server.name,
                "status": server.status.value,
                "endpoint": server.endpoint,
                "tool_count": len(server.tools),
                "description": server.description
            }
        
        return summary
    
    async def health_check(self) -> Dict[str, bool]:
        """Perform health check on all servers."""
        results = {}
        
        for server_id, client in self._clients.items():
            try:
                server = self._servers[server_id]
                if server.status == MCPServerStatus.CONNECTED:
                    # Could implement a proper health check method in MCPClient
                    results[server_id] = True
                else:
                    results[server_id] = False
            except Exception as e:
                logger.error(f"Health check failed for {server_id}: {e}")
                results[server_id] = False
        
        return results
