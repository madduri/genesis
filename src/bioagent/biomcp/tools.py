"""
BioMCP Tools wrapper to expose biomcp-python tools to the agent.
"""

import inspect
import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional

from biomcp import individual_tools
from ..core.models import Tool, ToolParameter
from .gget_tools import gget_tools

logger = logging.getLogger(__name__)


class BioMCPTools:
    """Wrapper for discovering and exposing BioMCP tools."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._tool_functions: Dict[str, Callable[..., Coroutine[Any, Any, Any]]] = {}
        self._discover_tools()

    def _discover_tools(self):
        """Discover all available tools from biomcp.individual_tools."""
        for name, func in inspect.getmembers(individual_tools, inspect.iscoroutinefunction):
            if not name.startswith('_'):
                try:
                    tool = self._create_tool_from_function(name, func)
                    self._tools[name] = tool
                    self._tool_functions[name] = func
                    logger.info(f"Discovered BioMCP tool: {name}")
                except Exception as e:
                    logger.warning(f"Could not create tool for {name}: {e}")
    
    def _create_tool_from_function(self, name: str, func: Callable[..., Any]) -> Tool:
        """Create a Tool object from an async function."""
        sig = inspect.signature(func)
        doc = inspect.getdoc(func) or f"BioMCP tool: {name}"
        
        parameters = []
        for param_name, param in sig.parameters.items():
            # Map python types to JSON schema types
            param_type = "string"
            if param.annotation == int:
                param_type = "integer"
            elif param.annotation == bool:
                param_type = "boolean"
            elif param.annotation == list:
                param_type = "array"
                
            parameters.append(ToolParameter(
                name=param_name,
                type=param_type,
                description=None,  # Not easily available from signature
                required=param.default == inspect.Parameter.empty,
                default=param.default if param.default != inspect.Parameter.empty else None
            ))
        
        return Tool(
            name=name,
            description=doc.split('\n')[0],
            server_id="biomcp_direct",
            parameters=parameters
        )
    
    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Call a discovered BioMCP or gget tool."""
        # Check if it's a gget tool first
        if tool_name.startswith('gget_'):
            return await gget_tools.call_tool(tool_name, params)
        
        # Otherwise, use BioMCP tools
        if tool_name not in self._tool_functions:
            raise NotImplementedError(f"Tool {tool_name} not found in BioMCP tools")
        
        func = self._tool_functions[tool_name]
        return await func(**params)

    def get_available_tools(self) -> List[Tool]:
        """Get all discovered BioMCP and gget tools."""
        all_tools = list(self._tools.values())
        all_tools.extend(gget_tools.get_available_tools())
        return all_tools
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a specific tool by name."""
        # Check gget tools first
        if tool_name.startswith('gget_'):
            return gget_tools.get_tool(tool_name)
        
        # Otherwise check BioMCP tools
        return self._tools.get(tool_name)


# Singleton instance of BioMCPTools
biomcp_tools = BioMCPTools()
