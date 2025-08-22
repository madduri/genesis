# GENESIS

A Python agentic framework for advancing biomedical research using tools like Ollama, BioMCP, and other MCP (Model Context Protocol) servers. This framework facilitates the creation of interactive systems that utilize multiple MCP tools from various sources to assist researchers in their biomedical investigations.

## Features ✨

- **🔌 Multi-MCP Integration**: Connect to multiple MCP servers simultaneously
- **🤖 LLM Support**: Integration with Ollama, OpenAI, and Anthropic models
- **📊 Research Context**: Specialized data models for biomedical research contexts
- **⚡ Async Operations**: High-performance asynchronous tool calls and interactions
- **💬 Interactive Sessions**: Rich CLI interface with conversation management
- **📁 Export Capabilities**: Export conversations in JSON and Markdown formats
- **🔧 Tool Discovery**: Automatic discovery and registration of available tools
- **📈 Progress Analysis**: Track and analyze research progress over time

## Quick Start 🚀

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/biomedical-agent-framework
cd biomedical-agent-framework

# Install with all dependencies
pip install -e .[dev,ollama,biomcp]

# Or install basic version
pip install -e .
```

### Configuration

1. **Initialize configuration:**
   ```bash
   bioagent init-config --output my_config.yaml
   ```

2. **Edit the configuration file** to match your setup:
   ```yaml
   agent:
     model_provider: "ollama"
     model_name: "llama3.1"
   
   enabled_servers:
     - "biomcp-pubmed"
   
   mcp_servers:
     biomcp-pubmed:
       name: "BioMCP PubMed Server"
       endpoint: "http://localhost:8001"
   ```

### Running the Agent

**Interactive Mode:**
```bash
bioagent interactive --config my_config.yaml
```

**Single Query:**
```bash
bioagent query "What are the genetic factors in Alzheimer's disease?" --config my_config.yaml
```

**Test Server Connection:**
```bash
bioagent test-server biomcp-pubmed --config my_config.yaml
```

## Programmatic Usage 💻

### Basic Example

```python
import asyncio
from bioagent import BiomedicalAgent
from bioagent.core.models import AgentConfiguration, MCPServer, ResearchContext

async def main():
    # Configure the agent
    config = AgentConfiguration(
        model_provider="ollama",
        model_name="llama3.1",
        research_context=ResearchContext(
            domain="genomics",
            organism="human",
            research_question="What are the genetic factors in Alzheimer's disease?"
        )
    )
    
    # Create and initialize agent
    agent = BiomedicalAgent(config)
    await agent.initialize()
    
    # Register MCP servers
    server = MCPServer(
        id="biomcp-pubmed",
        name="BioMCP PubMed Server",
        endpoint="http://localhost:8001",
        description="Access to PubMed literature database"
    )
    agent.register_mcp_server(server)
    
    # Connect to servers
    await agent.connect_mcp_servers()
    
    # Start research session
    session = await agent.start_session()
    
    # Process queries
    response = await agent.process_message(
        "What are the latest findings about APOE4 and Alzheimer's disease?"
    )
    
    print("🤖 Response:", response.content)
    
    if response.tool_calls:
        print("🔧 Tools used:", [call.tool_name for call in response.tool_calls])
    
    # Export conversation
    conversation = session.export_conversation("markdown")
    with open("research_session.md", "w") as f:
        f.write(conversation)
    
    await agent.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Features

```python
# Set research context dynamically
context = ResearchContext(
    domain="drug_discovery",
    organism="human", 
    research_question="What are potential drug targets for COVID-19?",
    keywords=["covid-19", "drug targets", "antivirals"]
)
session.update_context(context)

# Analyze research progress
analysis = await session.analyze_research_progress()
print(f"Duration: {analysis['duration_minutes']:.1f} minutes")
print(f"Tools used: {analysis['tool_usage']}")
print(f"Research themes: {analysis['research_themes']}")

# Search for specific tools
tools = agent.mcp_registry.search_tools("pubmed")
for tool in tools:
    print(f"- {tool.name}: {tool.description}")
```

## Supported Research Domains 🔬

- **Genomics**: Gene expression analysis, GWAS, variant analysis
- **Proteomics**: Protein structure, function, and interactions
- **Drug Discovery**: Compound screening, target identification, ADMET
- **Clinical Research**: Patient data analysis, biomarker discovery
- **Systems Biology**: Pathway analysis, network modeling
- **Bioinformatics**: Sequence analysis, phylogenetics, comparative genomics

## MCP Server Integration 🔌

The framework is designed to work with various MCP servers:

- **BioMCP Servers**: Specialized biomedical databases and tools
- **Ollama Tools**: Local computational tools and models
- **Custom Servers**: Build your own MCP servers for specific needs

### Supported Databases & Tools

- PubMed (literature search)
- UniProt (protein data)
- ChEMBL (chemical/bioactivity data)
- Ensembl (genomic annotations)
- And many more through MCP servers...

## CLI Commands 📋

```bash
# Get help
bioagent --help

# Initialize configuration
bioagent init-config

# Start interactive session
bioagent interactive --config config.yaml

# Send single query
bioagent query "your question" --config config.yaml

# List configured servers
bioagent list-servers --config config.yaml

# Test server connection
bioagent test-server server-id --config config.yaml
```

## Development 🛠️

### Setup Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/yourusername/biomedical-agent-framework
cd biomedical-agent-framework
pip install -e .[dev]

# Run tests
pytest tests/

# Run linting
black src/
isort src/
flake8 src/
```

### Project Structure

```
biomedical-agent-framework/
├── src/bioagent/
│   ├── core/           # Core agent logic
│   ├── mcp/            # MCP client and registry
│   ├── ui/             # User interface components
│   └── cli.py          # Command-line interface
├── examples/           # Usage examples
├── tests/              # Test suite
├── config/             # Configuration files
└── docs/               # Documentation
```

## Contributing 🤝

We welcome contributions! Please see our contributing guidelines and feel free to:

- Report bugs and request features
- Submit pull requests
- Improve documentation
- Add new MCP server integrations

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation 📚

If you use this framework in your research, please cite:

```bibtex
@software{GENESIS,
  title={GENESIS: An agentic framework for advancing biomedical research with MCP Integration},
  author={Madduri et al.},
  year={2025},
  url={https://github.com/madduri/genesis}
}
```
