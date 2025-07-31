"""
Biomedical Agent Framework

A Python framework for building interactive biomedical research agents
that integrate with MCP (Model Context Protocol) servers.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .core.agent import BiomedicalAgent
from .core.session import AgentSession
from .mcp.client import MCPClient
from .mcp.registry import MCPRegistry

__all__ = [
    "BiomedicalAgent",
    "AgentSession", 
    "MCPClient",
    "MCPRegistry",
]
