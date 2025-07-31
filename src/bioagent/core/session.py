"""
Session management for biomedical research sessions.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from uuid import uuid4

from .models import AgentMessage, ResearchContext, SessionState

if TYPE_CHECKING:
    from .agent import BiomedicalAgent

logger = logging.getLogger(__name__)


class AgentSession:
    """Manages a biomedical research session with conversation history and context."""
    
    def __init__(self, 
                 session_id: str, 
                 agent: 'BiomedicalAgent',
                 context: Optional[ResearchContext] = None):
        self.session_id = session_id
        self.agent = agent
        self.context = context
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.messages: List[AgentMessage] = []
        self.metadata: Dict[str, Any] = {}
        
        logger.info(f"Started new biomedical research session: {session_id}")
    
    def add_message(self, message: AgentMessage) -> None:
        """Add a message to the session history."""
        self.messages.append(message)
        self.last_active = datetime.now()
        
        # Log message for debugging
        logger.debug(f"Added message to session {self.session_id}: {message.role} - {message.content[:100]}...")
    
    def get_recent_messages(self, count: int = 10) -> List[AgentMessage]:
        """Get the most recent messages from the session."""
        return self.messages[-count:] if len(self.messages) > count else self.messages
    
    def get_messages_by_role(self, role: str) -> List[AgentMessage]:
        """Get all messages from a specific role (user, assistant, system, tool)."""
        return [msg for msg in self.messages if msg.role == role]
    
    def update_context(self, context: ResearchContext) -> None:
        """Update the research context for this session."""
        self.context = context
        self.last_active = datetime.now()
        
        logger.info(f"Updated context for session {self.session_id}: {context.domain}")
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the session."""
        self.metadata[key] = value
        self.last_active = datetime.now()
    
    def get_conversation_summary(self) -> str:
        """Generate a summary of the conversation."""
        if not self.messages:
            return "No conversation yet."
        
        user_messages = len(self.get_messages_by_role("user"))
        assistant_messages = len(self.get_messages_by_role("assistant"))
        tool_calls = sum(len(msg.tool_calls) for msg in self.messages)
        
        summary = f"Session {self.session_id}:\n"
        summary += f"- Duration: {self.last_active - self.created_at}\n"
        summary += f"- User messages: {user_messages}\n"
        summary += f"- Assistant messages: {assistant_messages}\n"
        summary += f"- Tool calls: {tool_calls}\n"
        
        if self.context:
            summary += f"- Research domain: {self.context.domain or 'General'}\n"
            if self.context.research_question:
                summary += f"- Research question: {self.context.research_question}\n"
        
        return summary
    
    def get_session_state(self) -> SessionState:
        """Get the current session state as a Pydantic model."""
        active_tools = []
        for message in self.messages:
            for tool_call in message.tool_calls:
                if tool_call.tool_name not in active_tools:
                    active_tools.append(tool_call.tool_name)
        
        return SessionState(
            session_id=self.session_id,
            created_at=self.created_at,
            last_active=self.last_active,
            messages=self.messages,
            context=self.context,
            active_tools=active_tools,
            metadata=self.metadata
        )
    
    def export_conversation(self, format: str = "json") -> str:
        """Export the conversation in the specified format."""
        if format.lower() == "json":
            return self._export_json()
        elif format.lower() == "markdown":
            return self._export_markdown()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self) -> str:
        """Export conversation as JSON."""
        session_state = self.get_session_state()
        return session_state.model_dump_json(indent=2)
    
    def _export_markdown(self) -> str:
        """Export conversation as Markdown."""
        lines = [
            f"# Biomedical Research Session: {self.session_id}",
            f"**Created:** {self.created_at.isoformat()}",
            f"**Last Active:** {self.last_active.isoformat()}",
            ""
        ]
        
        if self.context:
            lines.extend([
                "## Research Context",
                f"**Domain:** {self.context.domain or 'General'}",
                f"**Organism:** {self.context.organism or 'N/A'}",
                f"**Research Question:** {self.context.research_question or 'N/A'}",
                ""
            ])
        
        lines.append("## Conversation")
        lines.append("")
        
        for message in self.messages:
            role_title = message.role.title()
            timestamp = message.timestamp.strftime("%H:%M:%S")
            
            lines.append(f"### {role_title} ({timestamp})")
            lines.append("")
            lines.append(message.content)
            lines.append("")
            
            # Add tool call information
            if message.tool_calls:
                lines.append("**Tool Calls:**")
                for tool_call in message.tool_calls:
                    lines.append(f"- {tool_call.tool_name}: {tool_call.parameters}")
                lines.append("")
            
            # Add tool results
            if message.tool_results:
                lines.append("**Tool Results:**")
                for result in message.tool_results:
                    status = "✅ Success" if result.success else "❌ Failed"
                    lines.append(f"- {status}: {result.result or result.error}")
                lines.append("")
        
        return "\n".join(lines)
    
    async def analyze_research_progress(self) -> Dict[str, Any]:
        """Analyze the research progress in this session."""
        analysis = {
            "session_id": self.session_id,
            "duration_minutes": (self.last_active - self.created_at).total_seconds() / 60,
            "message_count": len(self.messages),
            "tool_usage": {},
            "research_themes": [],
            "next_steps": []
        }
        
        # Analyze tool usage
        for message in self.messages:
            for tool_call in message.tool_calls:
                tool_name = tool_call.tool_name
                if tool_name not in analysis["tool_usage"]:
                    analysis["tool_usage"][tool_name] = 0
                analysis["tool_usage"][tool_name] += 1
        
        # Extract research themes from context and messages
        if self.context:
            if self.context.domain:
                analysis["research_themes"].append(self.context.domain)
            analysis["research_themes"].extend(self.context.keywords)
        
        # Simple keyword extraction from user messages
        user_messages = self.get_messages_by_role("user")
        research_keywords = ["gene", "protein", "drug", "disease", "analysis", "sequence", "structure"]
        
        for message in user_messages:
            content_lower = message.content.lower()
            for keyword in research_keywords:
                if keyword in content_lower and keyword not in analysis["research_themes"]:
                    analysis["research_themes"].append(keyword)
        
        # Suggest next steps based on current progress
        if analysis["tool_usage"]:
            analysis["next_steps"].append("Continue analysis with additional tools")
        
        if self.context and self.context.research_question:
            analysis["next_steps"].append("Refine research question based on findings")
        
        return analysis
    
    def clear_history(self, keep_last: int = 0) -> None:
        """Clear conversation history, optionally keeping the last N messages."""
        if keep_last > 0:
            self.messages = self.messages[-keep_last:]
        else:
            self.messages = []
        
        self.last_active = datetime.now()
        logger.info(f"Cleared history for session {self.session_id}, kept last {keep_last} messages")
    
    def __str__(self) -> str:
        return f"AgentSession({self.session_id}, {len(self.messages)} messages)"
    
    def __repr__(self) -> str:
        return f"AgentSession(session_id='{self.session_id}', created_at='{self.created_at}', message_count={len(self.messages)})"
