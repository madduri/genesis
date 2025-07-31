"""
Command-line interface for the biomedical agent framework.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .core.agent import BiomedicalAgent
from .core.models import AgentConfiguration, MCPServer, ResearchContext
from .ui.interactive import InteractiveSession

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config: Optional[str], verbose: bool):
    """Biomedical Agent Framework - Interactive research assistant with MCP tools"""
    
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    if config:
        config_path = Path(config)
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            ctx.obj = config_data
        else:
            console.print(f"[red]Configuration file not found: {config}[/red]")
            sys.exit(1)
    else:
        ctx.obj = {}


@cli.command()
@click.option('--model', default='llama3.1', help='LLM model to use')
@click.option('--provider', default='ollama', help='LLM provider (ollama, openai, anthropic)')
@click.option('--temperature', default=0.7, help='LLM temperature')
@click.pass_context
def interactive(ctx, model: str, provider: str, temperature: float):
    """Start an interactive research session"""
    
    config_data = ctx.obj
    
    # Create agent configuration
    agent_config = AgentConfiguration(
        model_provider=provider,
        model_name=model,
        temperature=temperature,
        enabled_servers=config_data.get('enabled_servers', [])
    )
    
    # Start interactive session
    asyncio.run(_run_interactive_session(agent_config, config_data))


async def _run_interactive_session(agent_config: AgentConfiguration, config_data: dict):
    """Run the interactive session"""
    
    console.print(Panel.fit(
        "[bold blue]Biomedical Agent Framework[/bold blue]\n"
        "Interactive research assistant with MCP tools",
        border_style="blue"
    ))
    
    # Initialize agent
    agent = BiomedicalAgent(agent_config)
    
    try:
        await agent.initialize()
        
        # Register MCP servers from config
        if agent_config.enabled_servers:
            for server_id in agent_config.enabled_servers:
                if server_id in config_data.get('mcp_servers', {}):
                    server_config = config_data['mcp_servers'][server_id]
                    server = MCPServer(
                        id=server_id,
                        name=server_config['name'],
                        description=server_config.get('description', ''),
                        endpoint=server_config['endpoint']
                    )
                    agent.register_mcp_server(server)
            
            # Connect to servers
            console.print("[yellow]Connecting to MCP servers...[/yellow]")
            connection_results = await agent.connect_mcp_servers()
            
            for server_id, success in connection_results.items():
                status = "[green]✓[/green]" if success else "[red]✗[/red]"
                console.print(f"  {status} {server_id}")
        
        # Start interactive session
        interactive_session = InteractiveSession(agent)
        await interactive_session.run()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Session interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Error in interactive session")
    finally:
        await agent.shutdown()


@cli.command()
@click.option('--format', default='table', help='Output format (table, json)')
@click.pass_context
def list_servers(ctx, format: str):
    """List configured MCP servers"""
    
    config_data = ctx.obj
    servers = config_data.get('mcp_servers', {})
    
    if not servers:
        console.print("[yellow]No MCP servers configured[/yellow]")
        return
    
    if format == 'json':
        import json
        console.print(json.dumps(servers, indent=2))
        return
    
    # Table format
    table = Table(title="Configured MCP Servers")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Endpoint", style="green")
    table.add_column("Description")
    
    for server_id, server_config in servers.items():
        table.add_row(
            server_id,
            server_config.get('name', ''),
            server_config.get('endpoint', ''),
            server_config.get('description', '')
        )
    
    console.print(table)


@cli.command()
@click.argument('server_id')
@click.pass_context
def test_server(ctx, server_id: str):
    """Test connection to a specific MCP server"""
    
    config_data = ctx.obj
    servers = config_data.get('mcp_servers', {})
    
    if server_id not in servers:
        console.print(f"[red]Server '{server_id}' not found in configuration[/red]")
        return
    
    asyncio.run(_test_server_connection(server_id, servers[server_id]))


async def _test_server_connection(server_id: str, server_config: dict):
    """Test connection to a server"""
    
    console.print(f"[yellow]Testing connection to {server_id}...[/yellow]")
    
    server = MCPServer(
        id=server_id,
        name=server_config['name'],
        endpoint=server_config['endpoint'],
        description=server_config.get('description', '')
    )
    
    from .mcp.client import MCPClient
    
    client = MCPClient(server)
    
    try:
        success = await client.connect()
        
        if success:
            console.print(f"[green]✓ Connected to {server_id}[/green]")
            
            tools = client.get_available_tools()
            if tools:
                console.print(f"[blue]Available tools ({len(tools)}):[/blue]")
                for tool in tools:
                    console.print(f"  • {tool.name}: {tool.description}")
            else:
                console.print("[yellow]No tools available[/yellow]")
                
        else:
            console.print(f"[red]✗ Failed to connect to {server_id}[/red]")
        
        await client.disconnect()
        
    except Exception as e:
        console.print(f"[red]Error testing {server_id}: {e}[/red]")


@cli.command()
@click.option('--output', '-o', help='Output configuration file path')
def init_config(output: Optional[str]):
    """Initialize a new configuration file"""
    
    config_template = {
        'agent': {
            'model_provider': 'ollama',
            'model_name': 'llama3.1',
            'temperature': 0.7,
            'max_tokens': 2000,
            'system_prompt': None
        },
        'enabled_servers': ['biomcp-example'],
        'mcp_servers': {
            'biomcp-example': {
                'name': 'BioMCP Example Server',
                'endpoint': 'http://localhost:8000',
                'description': 'Example BioMCP server for biomedical research'
            },
            'ollama-tools': {
                'name': 'Ollama Tools',
                'endpoint': 'ws://localhost:8001',
                'description': 'Ollama-based tools server'
            }
        },
        'research_context': {
            'domain': 'genomics',
            'organism': 'human',
            'keywords': ['gene expression', 'GWAS', 'variant analysis']
        }
    }
    
    output_path = Path(output) if output else Path('agent_config.yaml')
    
    with open(output_path, 'w') as f:
        yaml.dump(config_template, f, default_flow_style=False, indent=2)
    
    console.print(f"[green]Configuration template created: {output_path}[/green]")
    console.print("[blue]Edit the configuration file to match your setup[/blue]")


@cli.command()
@click.argument('message')
@click.option('--session-id', help='Session ID to use')
@click.option('--context-domain', help='Research domain context')
@click.pass_context
def query(ctx, message: str, session_id: Optional[str], context_domain: Optional[str]):
    """Send a single query to the agent"""
    
    config_data = ctx.obj
    
    agent_config = AgentConfiguration(
        enabled_servers=config_data.get('enabled_servers', [])
    )
    
    if context_domain:
        agent_config.research_context = ResearchContext(domain=context_domain)
    
    asyncio.run(_run_single_query(agent_config, config_data, message, session_id))


async def _run_single_query(agent_config: AgentConfiguration, 
                           config_data: dict, 
                           message: str, 
                           session_id: Optional[str]):
    """Run a single query"""
    
    agent = BiomedicalAgent(agent_config)
    
    try:
        await agent.initialize()
        
        # Register and connect to servers (simplified)
        if agent_config.enabled_servers:
            # Similar to interactive mode but simplified
            pass
        
        # Process message
        response = await agent.process_message(message, session_id)
        
        # Display response
        console.print(Panel(
            Markdown(response.content),
            title="Agent Response",
            border_style="green"
        ))
        
        if response.tool_calls:
            console.print("[blue]Tools used:[/blue]")
            for tool_call in response.tool_calls:
                console.print(f"  • {tool_call.tool_name}")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.exception("Error in query")
    finally:
        await agent.shutdown()


def main():
    """Main entry point"""
    cli()


if __name__ == '__main__':
    main()
