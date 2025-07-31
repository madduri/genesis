"""
Core data models for the biomedical agent framework.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class MCPServerStatus(str, Enum):
    """Status of an MCP server connection."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class ToolParameter(BaseModel):
    """Schema for a tool parameter."""
    name: str
    type: str
    description: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None


class Tool(BaseModel):
    """Schema for an MCP tool."""
    name: str
    description: str
    parameters: List[ToolParameter] = Field(default_factory=list)
    server_id: str
    schema: Optional[Dict[str, Any]] = None


class ToolCall(BaseModel):
    """Schema for a tool call request."""
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    call_id: Optional[str] = None


class ToolResult(BaseModel):
    """Schema for a tool call result."""
    call_id: Optional[str] = None
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class MCPServer(BaseModel):
    """Schema for an MCP server configuration."""
    id: str
    name: str
    description: Optional[str] = None
    endpoint: str
    status: MCPServerStatus = MCPServerStatus.DISCONNECTED
    tools: List[Tool] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentMessage(BaseModel):
    """Schema for agent messages."""
    id: str
    timestamp: datetime
    role: str  # "user", "assistant", "system", "tool"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tool_calls: List[ToolCall] = Field(default_factory=list)
    tool_results: List[ToolResult] = Field(default_factory=list)


class ResearchContext(BaseModel):
    """Schema for biomedical research context."""
    domain: Optional[str] = None  # e.g., "genomics", "drug_discovery", "proteomics"
    organism: Optional[str] = None
    dataset: Optional[str] = None
    research_question: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentConfiguration(BaseModel):
    """Configuration for the biomedical agent."""
    model_provider: str = "ollama"  # "ollama", "openai", "anthropic"
    model_name: str = "llama3.1"
    temperature: float = 0.7
    max_tokens: int = 2000
    context_window: int = 4000
    research_context: Optional[ResearchContext] = None
    enabled_servers: List[str] = Field(default_factory=list)
    system_prompt: Optional[str] = None


class SessionState(BaseModel):
    """State of an agent session."""
    session_id: str
    created_at: datetime
    last_active: datetime
    messages: List[AgentMessage] = Field(default_factory=list)
    context: Optional[ResearchContext] = None
    active_tools: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
