"""
Main biomedical agent that orchestrates MCP tools and LLM interactions.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import httpx
from pydantic import ValidationError

from .models import (
    AgentConfiguration, AgentMessage, ResearchContext, 
    ToolCall, ToolResult, MCPServer
)
from .session import AgentSession
from ..mcp.registry import MCPRegistry
from ..biomcp.tools import biomcp_tools

logger = logging.getLogger(__name__)


class BiomedicalAgent:
    """
    Main biomedical research agent that integrates MCP tools with LLM capabilities.
    """
    
    def __init__(self, config: AgentConfiguration):
        self.config = config
        self.mcp_registry = MCPRegistry()
        self.session: Optional[AgentSession] = None
        self._llm_client: Optional[httpx.AsyncClient] = None
        
        # Default biomedical system prompt
        self.system_prompt = config.system_prompt or self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for biomedical research."""
        return """You are a specialized biomedical research assistant with access to various computational tools and databases. Your role is to help researchers with:

1. Literature analysis and systematic reviews
2. Genomics and proteomics data analysis  
3. Drug discovery and molecular modeling
4. Clinical data interpretation
5. Bioinformatics workflows
6. Data visualization and statistical analysis

You have access to multiple MCP (Model Context Protocol) tools that can:
- Query biomedical databases (PubMed, UniProt, ChEMBL, etc.)
- Perform sequence analysis and alignments
- Run statistical analyses
- Generate visualizations
- Access specialized bioinformatics software

Always:
- Provide clear, scientifically accurate information
- Cite sources when making factual claims
- Explain complex concepts in an accessible way
- Suggest appropriate tools for specific research tasks
- Consider ethical implications of research

When using tools:
- Choose the most appropriate tool for each task
- Provide clear parameters
- Interpret results in biological context
- Suggest follow-up analyses when relevant"""
    
    async def initialize(self) -> None:
        """Initialize the agent and its dependencies."""
        # Initialize LLM client based on provider
        if self.config.model_provider == "ollama":
            await self._initialize_ollama()
        elif self.config.model_provider in ["openai", "anthropic"]:
            await self._initialize_api_client()
        
        # Register enabled MCP servers
        for server_id in self.config.enabled_servers:
            # This would typically load from configuration
            logger.info(f"Would register MCP server: {server_id}")
    
    async def _initialize_ollama(self) -> None:
        """Initialize Ollama client."""
        self._llm_client = httpx.AsyncClient(
            base_url="http://localhost:11434",
            timeout=httpx.Timeout(180.0)  # 180 second timeout
        )
        
        # Test connection
        try:
            response = await self._llm_client.get("/api/tags")
            if response.status_code != 200:
                raise ConnectionError("Failed to connect to Ollama")
            logger.info("Connected to Ollama")
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            raise
    
    async def _initialize_api_client(self) -> None:
        """Initialize API client for OpenAI/Anthropic."""
        # This would be implemented based on the specific provider
        logger.info(f"Initializing {self.config.model_provider} client")
        self._llm_client = httpx.AsyncClient()
    
    def register_mcp_server(self, server: MCPServer) -> None:
        """Register an MCP server with the agent."""
        self.mcp_registry.register_server(server)
    
    async def connect_mcp_servers(self, server_ids: Optional[List[str]] = None) -> Dict[str, bool]:
        """Connect to MCP servers."""
        return await self.mcp_registry.connect_all(server_ids)
    
    async def start_session(self, 
                          session_id: Optional[str] = None,
                          context: Optional[ResearchContext] = None) -> AgentSession:
        """Start a new research session."""
        if session_id is None:
            session_id = str(uuid4())
        
        self.session = AgentSession(
            session_id=session_id,
            agent=self,
            context=context or self.config.research_context
        )
        
        return self.session
    
    async def process_message(self, message: str, session_id: Optional[str] = None) -> AgentMessage:
        """Process a user message and return the agent's response."""
        if self.session is None or (session_id and self.session.session_id != session_id):
            await self.start_session(session_id)
        
        # Create user message
        user_message = AgentMessage(
            id=str(uuid4()),
            timestamp=datetime.now(),
            role="user",
            content=message
        )
        
        # Add to session
        self.session.add_message(user_message)
        
        # Generate response
        response = await self._generate_response(message)
        
        # Add response to session
        self.session.add_message(response)
        
        return response
    
    async def _generate_response(self, user_input: str) -> AgentMessage:
        """Generate a response using the LLM and available tools."""
        try:
            # Prepare conversation context
            context = self._prepare_context()
            
            # Check if tools should be used
            tool_calls = await self._identify_tool_calls(user_input, context)
            
            if tool_calls:
                # Execute tool calls
                tool_results = await self._execute_tool_calls(tool_calls)
                
                # Generate response with tool results
                response_content = await self._generate_with_tools(
                    user_input, context, tool_calls, tool_results
                )
                
                return AgentMessage(
                    id=str(uuid4()),
                    timestamp=datetime.now(),
                    role="assistant",
                    content=response_content,
                    tool_calls=tool_calls,
                    tool_results=tool_results
                )
            else:
                # Generate simple response
                response_content = await self._generate_simple_response(user_input, context)
                
                return AgentMessage(
                    id=str(uuid4()),
                    timestamp=datetime.now(),
                    role="assistant", 
                    content=response_content
                )
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return AgentMessage(
                id=str(uuid4()),
                timestamp=datetime.now(),
                role="assistant",
                content=f"I encountered an error while processing your request: {str(e)}"
            )
    
    def _prepare_context(self) -> str:
        """Prepare conversation context for the LLM."""
        context_parts = [self.system_prompt]
        
        if self.session and self.session.context:
            context_parts.append(f"Research Context: {self.session.context.model_dump_json()}")
        
        # Add available tools
        available_tools = self.mcp_registry.get_available_tools()
        if available_tools:
            tools_info = "Available tools:\n"
            for tool in available_tools[:10]:  # Limit to prevent context overflow
                tools_info += f"- {tool.name}: {tool.description}\n"
            context_parts.append(tools_info)
        
        # Add recent conversation history
        if self.session:
            recent_messages = self.session.get_recent_messages(5)
            if recent_messages:
                history = "Recent conversation:\n"
                for msg in recent_messages[:-1]:  # Exclude current message
                    history += f"{msg.role}: {msg.content[:200]}...\n"
                context_parts.append(history)
        
        return "\n\n".join(context_parts)
    
    async def _identify_tool_calls(self, user_input: str, context: str) -> List[ToolCall]:
        """Identify if and which tools should be called based on user input."""
        # This is a simplified implementation
        # A more sophisticated version would use the LLM to decide on tool usage
        
        tool_calls = []
        available_tools = self.mcp_registry.get_available_tools()
        
        # Simple keyword-based tool identification
        user_input_lower = user_input.lower()
        
        for tool in available_tools:
            # Check if tool name or keywords appear in user input
            if (tool.name.lower() in user_input_lower or 
                any(keyword in user_input_lower for keyword in 
                    tool.description.lower().split() if len(keyword) > 4)):
                
                # For demo purposes, create a simple tool call
                # In practice, this would be much more sophisticated
                tool_call = ToolCall(
                    tool_name=tool.name,
                    parameters={},  # Would be extracted from user input
                    call_id=str(uuid4())
                )
                tool_calls.append(tool_call)
                break  # Only use one tool for now
        
        return tool_calls
    
    async def _execute_tool_calls(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        """Execute the identified tool calls."""
        results = []
        
        for tool_call in tool_calls:
            try:
                # Check if it's a BioMCP direct tool first
                biomcp_tool = biomcp_tools.get_tool(tool_call.tool_name)
                if biomcp_tool:
                    # Execute BioMCP tool directly
                    result_data = await biomcp_tools.call_tool(tool_call.tool_name, tool_call.parameters)
                    result = ToolResult(
                        call_id=tool_call.call_id,
                        success=True,
                        result=result_data
                    )
                else:
                    # Try MCP registry
                    result = await self.mcp_registry.call_tool(
                        tool_call.tool_name,
                        tool_call.parameters,
                        tool_call.call_id
                    )
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing tool {tool_call.tool_name}: {e}")
                results.append(ToolResult(
                    call_id=tool_call.call_id,
                    success=False,
                    error=str(e)
                ))
        
        return results
    
    async def _generate_with_tools(self, 
                                 user_input: str, 
                                 context: str,
                                 tool_calls: List[ToolCall], 
                                 tool_results: List[ToolResult]) -> str:
        """Generate response incorporating tool results."""
        # Prepare prompt with tool results
        prompt_parts = [
            context,
            f"User: {user_input}",
            "\nTool results:"
        ]
        
        for i, (call, result) in enumerate(zip(tool_calls, tool_results)):
            if result.success:
                prompt_parts.append(f"Tool {call.tool_name}: {result.result}")
            else:
                prompt_parts.append(f"Tool {call.tool_name} failed: {result.error}")
        
        prompt_parts.append("\nPlease provide a comprehensive response based on the tool results and your knowledge:")
        
        prompt = "\n".join(prompt_parts)
        
        return await self._call_llm(prompt)
    
    async def _generate_simple_response(self, user_input: str, context: str) -> str:
        """Generate a simple response without tools."""
        prompt = f"{context}\n\nUser: {user_input}\n\nAssistant:"
        return await self._call_llm(prompt)
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM with the given prompt."""
        if self.config.model_provider == "ollama":
            return await self._call_ollama(prompt)
        else:
            # Implement other providers
            return "LLM integration not implemented for this provider yet."
    
    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API."""
        try:
            logger.debug(f"Calling Ollama with model: {self.config.model_name}")
            response = await self._llm_client.post("/api/generate", json={
                "model": self.config.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            })
            
            if response.status_code != 200:
                error_text = response.text if hasattr(response, 'text') else "Unknown error"
                raise Exception(f"Ollama API error {response.status_code}: {error_text}")
            
            result = response.json()
            return result.get("response", "No response generated")
            
        except httpx.TimeoutException as e:
            logger.error(f"Ollama request timed out: {e}")
            return f"Request timed out - try reducing prompt length or increasing timeout"
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return f"Connection error - ensure Ollama is running on localhost:11434"
        except Exception as e:
            logger.error(f"Error calling Ollama: {type(e).__name__}: {e}")
            return f"Error generating response: {str(e)}"
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get information about available tools."""
        # Get tools from MCP registry
        mcp_tools = self.mcp_registry.get_available_tools()
        
        # Get tools from BioMCP direct integration
        biomcp_direct_tools = biomcp_tools.get_available_tools()
        
        # Combine all tools
        all_tools = mcp_tools + biomcp_direct_tools
        
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "server": tool.server_id,
                "parameters": [p.model_dump() for p in tool.parameters]
            }
            for tool in all_tools
        ]
    
    async def get_server_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers."""
        return self.mcp_registry.get_server_status_summary()
    
    async def shutdown(self) -> None:
        """Shutdown the agent and cleanup resources."""
        await self.mcp_registry.disconnect_all()
        
        if self._llm_client:
            await self._llm_client.aclose()
        
        logger.info("Biomedical agent shutdown complete")
