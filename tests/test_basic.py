"""
Basic tests for the biomedical agent framework.
"""

import pytest
import asyncio
from datetime import datetime

from bioagent.core.models import (
    AgentConfiguration, AgentMessage, ResearchContext,
    MCPServer, Tool, ToolParameter, ToolCall, ToolResult
)
from bioagent.core.agent import BiomedicalAgent
from bioagent.core.session import AgentSession
from bioagent.mcp.registry import MCPRegistry


def test_agent_configuration():
    """Test agent configuration creation."""
    config = AgentConfiguration(
        model_provider="ollama",
        model_name="llama3.1",
        temperature=0.5
    )
    
    assert config.model_provider == "ollama"
    assert config.model_name == "llama3.1"
    assert config.temperature == 0.5
    assert config.max_tokens == 2000  # default


def test_research_context():
    """Test research context creation."""
    context = ResearchContext(
        domain="genomics",
        organism="human",
        research_question="What are the genetic factors in cancer?",
        keywords=["cancer", "genetics", "mutations"]
    )
    
    assert context.domain == "genomics"
    assert context.organism == "human"
    assert len(context.keywords) == 3


def test_mcp_server():
    """Test MCP server model."""
    server = MCPServer(
        id="test-server",
        name="Test Server",
        description="A test server",
        endpoint="http://localhost:8000"
    )
    
    assert server.id == "test-server"
    assert server.name == "Test Server"
    assert server.endpoint == "http://localhost:8000"


def test_tool_parameter():
    """Test tool parameter model."""
    param = ToolParameter(
        name="query",
        type="string",
        description="Search query",
        required=True
    )
    
    assert param.name == "query"
    assert param.type == "string"
    assert param.required is True


def test_tool():
    """Test tool model."""
    param = ToolParameter(
        name="query",
        type="string",
        description="Search query",
        required=True
    )
    
    tool = Tool(
        name="pubmed_search",
        description="Search PubMed database",
        parameters=[param],
        server_id="biomcp-pubmed"
    )
    
    assert tool.name == "pubmed_search"
    assert len(tool.parameters) == 1
    assert tool.parameters[0].name == "query"


def test_agent_message():
    """Test agent message model."""
    message = AgentMessage(
        id="msg-123",
        timestamp=datetime.now(),
        role="user",
        content="What are the genetic factors in Alzheimer's disease?"
    )
    
    assert message.id == "msg-123"
    assert message.role == "user"
    assert "Alzheimer's" in message.content


def test_tool_call():
    """Test tool call model."""
    tool_call = ToolCall(
        tool_name="pubmed_search",
        parameters={"query": "Alzheimer's disease genetics"},
        call_id="call-123"
    )
    
    assert tool_call.tool_name == "pubmed_search"
    assert tool_call.parameters["query"] == "Alzheimer's disease genetics"


def test_tool_result():
    """Test tool result model."""
    result = ToolResult(
        call_id="call-123",
        success=True,
        result={"papers": ["paper1", "paper2"]},
        execution_time=1.5
    )
    
    assert result.call_id == "call-123"
    assert result.success is True
    assert result.execution_time == 1.5


def test_mcp_registry():
    """Test MCP registry functionality."""
    registry = MCPRegistry()
    
    server = MCPServer(
        id="test-server",
        name="Test Server",
        endpoint="http://localhost:8000"
    )
    
    # Register server
    registry.register_server(server)
    
    # Check registration
    servers = registry.get_servers()
    assert len(servers) == 1
    assert servers[0].id == "test-server"
    
    # Get specific server
    retrieved_server = registry.get_server("test-server")
    assert retrieved_server is not None
    assert retrieved_server.name == "Test Server"


def test_agent_session():
    """Test agent session functionality."""
    from unittest.mock import Mock
    
    # Mock agent
    mock_agent = Mock()
    
    session = AgentSession(
        session_id="session-123",
        agent=mock_agent,
        context=ResearchContext(domain="genomics")
    )
    
    assert session.session_id == "session-123"
    assert session.context.domain == "genomics"
    
    # Add a message
    message = AgentMessage(
        id="msg-1",
        timestamp=datetime.now(),
        role="user",
        content="Test message"
    )
    
    session.add_message(message)
    assert len(session.messages) == 1
    
    # Test conversation summary
    summary = session.get_conversation_summary()
    assert "session-123" in summary
    assert "User messages: 1" in summary


@pytest.mark.asyncio
async def test_biomedical_agent_creation():
    """Test biomedical agent creation."""
    config = AgentConfiguration(
        model_provider="ollama",
        model_name="llama3.1"
    )
    
    agent = BiomedicalAgent(config)
    assert agent.config.model_provider == "ollama"
    assert agent.mcp_registry is not None
    
    # Test server registration
    server = MCPServer(
        id="test-server",
        name="Test Server",
        endpoint="http://localhost:8000"
    )
    
    agent.register_mcp_server(server)
    servers = agent.mcp_registry.get_servers()
    assert len(servers) == 1


if __name__ == "__main__":
    pytest.main([__file__])
