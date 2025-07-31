"""
MCP (Model Context Protocol) client for connecting to MCP servers.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import aiohttp
import websockets
from pydantic import ValidationError

from ..core.models import MCPServer, MCPServerStatus, Tool, ToolCall, ToolResult, ToolParameter

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for connecting to and communicating with MCP servers."""
    
    def __init__(self, server: MCPServer):
        self.server = server
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._tools_cache: Dict[str, Tool] = {}
        
    async def connect(self) -> bool:
        """Connect to the MCP server."""
        try:
            self.server.status = MCPServerStatus.CONNECTING
            
            if self.server.endpoint.startswith("ws://") or self.server.endpoint.startswith("wss://"):
                await self._connect_websocket()
            else:
                await self._connect_http()
                
            # Fetch available tools
            await self._fetch_tools()
            
            self.server.status = MCPServerStatus.CONNECTED
            logger.info(f"Connected to MCP server: {self.server.name}")
            return True
            
        except Exception as e:
            self.server.status = MCPServerStatus.ERROR
            logger.error(f"Failed to connect to MCP server {self.server.name}: {e}")
            return False
    
    async def _connect_http(self) -> None:
        """Connect via HTTP."""
        self.session = aiohttp.ClientSession()
        # Test connection with a ping/health check
        async with self.session.get(f"{self.server.endpoint}/health") as response:
            if response.status != 200:
                raise ConnectionError(f"Server health check failed: {response.status}")
    
    async def _connect_websocket(self) -> None:
        """Connect via WebSocket."""
        self.websocket = await websockets.connect(self.server.endpoint)
        
        # Send initialization message
        init_message = {
            "jsonrpc": "2.0",
            "id": str(uuid4()),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True}
                },
                "clientInfo": {
                    "name": "biomedical-agent-framework",
                    "version": "0.1.0"
                }
            }
        }
        
        await self.websocket.send(json.dumps(init_message))
        response = await self.websocket.recv()
        # TODO: Parse and validate initialization response
    
    async def _fetch_tools(self) -> None:
        """Fetch available tools from the server."""
        try:
            if self.websocket:
                await self._fetch_tools_websocket()
            else:
                await self._fetch_tools_http()
        except Exception as e:
            logger.error(f"Failed to fetch tools from {self.server.name}: {e}")
    
    async def _fetch_tools_websocket(self) -> None:
        """Fetch tools via WebSocket."""
        if not self.websocket:
            return
            
        message = {
            "jsonrpc": "2.0",
            "id": str(uuid4()),
            "method": "tools/list"
        }
        
        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()
        data = json.loads(response)
        
        if "result" in data and "tools" in data["result"]:
            await self._parse_tools(data["result"]["tools"])
    
    async def _fetch_tools_http(self) -> None:
        """Fetch tools via HTTP."""
        if not self.session:
            return
            
        async with self.session.post(
            f"{self.server.endpoint}/tools/list",
            json={"jsonrpc": "2.0", "id": str(uuid4()), "method": "tools/list"}
        ) as response:
            data = await response.json()
            
            if "result" in data and "tools" in data["result"]:
                await self._parse_tools(data["result"]["tools"])
    
    async def _parse_tools(self, tools_data: List[Dict[str, Any]]) -> None:
        """Parse tools data and update server tools."""
        tools = []
        
        for tool_data in tools_data:
            try:
                # Parse parameters from JSON Schema
                parameters = []
                if "inputSchema" in tool_data:
                    schema = tool_data["inputSchema"]
                    if "properties" in schema:
                        for param_name, param_info in schema["properties"].items():
                            parameter = ToolParameter(
                                name=param_name,
                                type=param_info.get("type", "string"),
                                description=param_info.get("description"),
                                required=param_name in schema.get("required", [])
                            )
                            parameters.append(parameter)
                
                tool = Tool(
                    name=tool_data["name"],
                    description=tool_data.get("description", ""),
                    parameters=parameters,
                    server_id=self.server.id,
                    schema=tool_data.get("inputSchema")
                )
                
                tools.append(tool)
                self._tools_cache[tool.name] = tool
                
            except ValidationError as e:
                logger.warning(f"Failed to parse tool {tool_data.get('name', 'unknown')}: {e}")
        
        self.server.tools = tools
        logger.info(f"Loaded {len(tools)} tools from {self.server.name}")
    
    async def call_tool(self, tool_call: ToolCall) -> ToolResult:
        """Call a tool on the MCP server."""
        start_time = time.time()
        
        try:
            if tool_call.tool_name not in self._tools_cache:
                return ToolResult(
                    call_id=tool_call.call_id,
                    success=False,
                    error=f"Tool '{tool_call.tool_name}' not found"
                )
            
            if self.websocket:
                result = await self._call_tool_websocket(tool_call)
            else:
                result = await self._call_tool_http(tool_call)
            
            execution_time = time.time() - start_time
            
            return ToolResult(
                call_id=tool_call.call_id,
                success=True,
                result=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Tool call failed for {tool_call.tool_name}: {e}")
            
            return ToolResult(
                call_id=tool_call.call_id,
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    async def _call_tool_websocket(self, tool_call: ToolCall) -> Any:
        """Call tool via WebSocket."""
        if not self.websocket:
            raise ConnectionError("WebSocket not connected")
        
        message = {
            "jsonrpc": "2.0",
            "id": tool_call.call_id or str(uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_call.tool_name,
                "arguments": tool_call.parameters
            }
        }
        
        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()
        data = json.loads(response)
        
        if "error" in data:
            raise Exception(f"Tool call error: {data['error']}")
        
        return data.get("result")
    
    async def _call_tool_http(self, tool_call: ToolCall) -> Any:
        """Call tool via HTTP."""
        if not self.session:
            raise ConnectionError("HTTP session not initialized")
        
        message = {
            "jsonrpc": "2.0",
            "id": tool_call.call_id or str(uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_call.tool_name,
                "arguments": tool_call.parameters
            }
        }
        
        async with self.session.post(
            f"{self.server.endpoint}/tools/call",
            json=message
        ) as response:
            data = await response.json()
            
            if "error" in data:
                raise Exception(f"Tool call error: {data['error']}")
            
            return data.get("result")
    
    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        try:
            if self.websocket:
                await self.websocket.close()
                self.websocket = None
            
            if self.session:
                await self.session.close()
                self.session = None
            
            self.server.status = MCPServerStatus.DISCONNECTED
            logger.info(f"Disconnected from MCP server: {self.server.name}")
            
        except Exception as e:
            logger.error(f"Error disconnecting from {self.server.name}: {e}")
    
    def get_available_tools(self) -> List[Tool]:
        """Get list of available tools."""
        return list(self._tools_cache.values())
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a specific tool by name."""
        return self._tools_cache.get(tool_name)
