"""
Interactive UI session manager using Rich console.
"""

import asyncio
import logging
from typing import List, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from ..core.agent import BiomedicalAgent
from ..core.models import ResearchContext

console = Console()
logger = logging.getLogger(__name__)


class InteractiveSession:
    """Interactive session manager for the biomedical agent."""
    
    def __init__(self, agent: BiomedicalAgent):
        self.agent = agent
        self.session = None
        self.running = False
    
    async def run(self) -> None:
        """Run the interactive session."""
        self.running = True
        
        # Welcome message
        self._show_welcome()
        
        # Show available tools
        await self._show_available_tools()
        
        # Start main loop
        while self.running:
            try:
                # Get user input
                user_input = await self._get_user_input()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.startswith('/'):
                    await self._handle_command(user_input)
                    continue
                
                # Process regular message
                await self._process_message(user_input)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use /quit to exit gracefully[/yellow]")
            except EOFError:
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                logger.exception("Error in interactive session")
        
        console.print("[blue]Goodbye![/blue]")
    
    def _show_welcome(self) -> None:
        """Show welcome message and instructions."""
        welcome_text = """
# Welcome to the Biomedical Agent Framework! 🧬

I'm your research assistant specialized in biomedical research. I can help you with:

- **Literature searches** and systematic reviews
- **Genomics and proteomics** data analysis  
- **Drug discovery** and molecular modeling
- **Clinical data** interpretation
- **Bioinformatics workflows**
- **Data visualization** and statistical analysis

## Available Commands:
- `/help` - Show this help message
- `/tools` - List available tools
- `/servers` - Show server status
- `/context` - Set research context
- `/export` - Export conversation
- `/clear` - Clear conversation history
- `/quit` - Exit the session

Just type your research question or request, and I'll help you find the answers!
        """
        
        console.print(Panel(
            Markdown(welcome_text),
            title="Biomedical Agent Framework",
            border_style="blue"
        ))
    
    async def _show_available_tools(self) -> None:
        """Show available tools from connected servers."""
        try:
            tools = await self.agent.get_available_tools()
            
            if not tools:
                console.print("[yellow]No tools currently available. Check your MCP server connections.[/yellow]")
                return
            
            table = Table(title="Available Research Tools")
            table.add_column("Tool", style="cyan", no_wrap=True)
            table.add_column("Server", style="magenta")
            table.add_column("Description", style="white")
            
            for tool in tools[:10]:  # Limit display
                table.add_row(
                    tool['name'],
                    tool['server'],
                    tool['description'][:80] + "..." if len(tool['description']) > 80 else tool['description']
                )
            
            if len(tools) > 10:
                table.add_row("...", "...", f"and {len(tools) - 10} more tools")
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error loading tools: {e}[/red]")
    
    async def _get_user_input(self) -> str:
        """Get user input with proper async handling."""
        return await asyncio.to_thread(
            Prompt.ask,
            "[bold green]Research Question[/bold green]",
            console=console
        )
    
    async def _process_message(self, message: str) -> None:
        """Process a user message and display the response."""
        # Show thinking indicator
        with console.status("[bold green]Thinking..."):
            try:
                # Start session if needed
                if self.session is None:
                    self.session = await self.agent.start_session()
                
                # Process message
                response = await self.agent.process_message(message)
                
                # Display response
                self._display_response(response)
                
            except Exception as e:
                console.print(f"[red]Error processing message: {e}[/red]")
                logger.exception("Error processing message")
    
    def _display_response(self, response) -> None:
        """Display the agent's response with formatting."""
        # Main response
        console.print(Panel(
            Markdown(response.content),
            title="🤖 Agent Response",
            border_style="green"
        ))
        
        # Tool information if tools were used
        if response.tool_calls:
            console.print("\n[blue]🔧 Tools Used:[/blue]")
            
            for i, (tool_call, result) in enumerate(zip(response.tool_calls, response.tool_results)):
                status = "✅" if result.success else "❌"
                execution_time = f" ({result.execution_time:.2f}s)" if result.execution_time else ""
                
                console.print(f"  {status} {tool_call.tool_name}{execution_time}")
                
                if not result.success and result.error:
                    console.print(f"    [red]Error: {result.error}[/red]")
    
    async def _handle_command(self, command: str) -> None:
        """Handle special commands."""
        cmd_parts = command[1:].split()
        cmd = cmd_parts[0].lower()
        
        if cmd == 'help':
            self._show_welcome()
        
        elif cmd == 'tools':
            await self._show_available_tools()
        
        elif cmd == 'servers':
            await self._show_server_status()
        
        elif cmd == 'context':
            await self._set_research_context()
        
        elif cmd == 'export':
            await self._export_conversation(cmd_parts[1] if len(cmd_parts) > 1 else 'json')
        
        elif cmd == 'clear':
            await self._clear_history()
        
        elif cmd == 'quit' or cmd == 'exit':
            self.running = False
        
        else:
            console.print(f"[red]Unknown command: {command}[/red]")
            console.print("[yellow]Type /help for available commands[/yellow]")
    
    async def _show_server_status(self) -> None:
        """Show status of all MCP servers."""
        try:
            status = await self.agent.get_server_status()
            
            if not status:
                console.print("[yellow]No servers configured[/yellow]")
                return
            
            table = Table(title="MCP Server Status")
            table.add_column("Server", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Tools", style="green")
            table.add_column("Endpoint", style="white")
            
            for server_id, info in status.items():
                status_color = {
                    'connected': '[green]Connected[/green]',
                    'disconnected': '[red]Disconnected[/red]',
                    'connecting': '[yellow]Connecting[/yellow]',
                    'error': '[red]Error[/red]'
                }.get(info['status'], info['status'])
                
                table.add_row(
                    info['name'],
                    status_color,
                    str(info['tool_count']),
                    info['endpoint']
                )
            
            console.print(table)
            
        except Exception as e:
            console.print(f"[red]Error getting server status: {e}[/red]")
    
    async def _set_research_context(self) -> None:
        """Set research context for the session."""
        console.print("[blue]Setting Research Context[/blue]")
        
        domain = await asyncio.to_thread(
            Prompt.ask,
            "Research domain (e.g., genomics, proteomics, drug_discovery)",
            default="",
            console=console
        )
        
        organism = await asyncio.to_thread(
            Prompt.ask,
            "Target organism (e.g., human, mouse, yeast)",
            default="",
            console=console
        )
        
        research_question = await asyncio.to_thread(
            Prompt.ask,
            "Research question",
            default="",
            console=console
        )
        
        keywords = await asyncio.to_thread(
            Prompt.ask,
            "Keywords (comma-separated)",
            default="",
            console=console
        )
        
        context = ResearchContext(
            domain=domain if domain else None,
            organism=organism if organism else None,
            research_question=research_question if research_question else None,
            keywords=[k.strip() for k in keywords.split(',')] if keywords else []
        )
        
        if self.session:
            self.session.update_context(context)
            console.print("[green]Research context updated[/green]")
        else:
            # Store for when session is created
            self.agent.config.research_context = context
            console.print("[green]Research context will be applied to the next session[/green]")
    
    async def _export_conversation(self, format: str = 'json') -> None:
        """Export the current conversation."""
        if not self.session:
            console.print("[yellow]No active session to export[/yellow]")
            return
        
        try:
            if format.lower() == 'markdown':
                content = self.session.export_conversation('markdown')
                filename = f"conversation_{self.session.session_id}.md"
            else:
                content = self.session.export_conversation('json')
                filename = f"conversation_{self.session.session_id}.json"
            
            with open(filename, 'w') as f:
                f.write(content)
            
            console.print(f"[green]Conversation exported to {filename}[/green]")
            
        except Exception as e:
            console.print(f"[red]Error exporting conversation: {e}[/red]")
    
    async def _clear_history(self) -> None:
        """Clear conversation history."""
        if not self.session:
            console.print("[yellow]No active session[/yellow]")
            return
        
        confirm = await asyncio.to_thread(
            Prompt.ask,
            "Clear conversation history? (y/N)",
            default="n",
            console=console
        )
        
        if confirm.lower() == 'y':
            self.session.clear_history()
            console.print("[green]Conversation history cleared[/green]")
        else:
            console.print("Operation cancelled")
    
    def stop(self) -> None:
        """Stop the interactive session."""
        self.running = False
