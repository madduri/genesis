#!/usr/bin/env python3
"""
Basic usage example for the Biomedical Agent Framework.

This example demonstrates how to:
1. Create and configure a biomedical agent
2. Register MCP servers 
3. Start a research session
4. Process research queries
"""

import asyncio
import logging
from bioagent import BiomedicalAgent
from bioagent.core.models import AgentConfiguration, MCPServer, ResearchContext

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main example function."""
    
    # Create agent configuration
    config = AgentConfiguration(
        model_provider="ollama",
        model_name="llama3.1", 
        temperature=0.7,
        max_tokens=2000,
        research_context=ResearchContext(
            domain="genomics",
            organism="human",
            research_question="What are the genetic factors in Alzheimer's disease?",
            keywords=["alzheimer", "genetics", "GWAS", "neurodegeneration"]
        )
    )
    
    # Create the biomedical agent
    agent = BiomedicalAgent(config)
    
    try:
        # Initialize the agent
        print("🧬 Initializing Biomedical Agent...")
        await agent.initialize()
        
        # Register example MCP servers
        # Note: These are example servers - replace with actual biomcp or other MCP servers
        example_servers = [
            MCPServer(
                id="biomcp-pubmed",
                name="BioMCP PubMed Server",
                description="Access to PubMed literature database",
                endpoint="http://localhost:8001"
            ),
            MCPServer(
                id="biomcp-uniprot", 
                name="BioMCP UniProt Server",
                description="Protein sequence and annotation database",
                endpoint="http://localhost:8002"
            )
        ]
        
        for server in example_servers:
            agent.register_mcp_server(server)
            print(f"📡 Registered server: {server.name}")
        
        # Connect to servers (this would fail with example servers)
        print("🔌 Connecting to MCP servers...")
        # connection_results = await agent.connect_mcp_servers()
        # for server_id, success in connection_results.items():
        #     status = "✅" if success else "❌"
        #     print(f"  {status} {server_id}")
        
        # Start a research session
        print("🔬 Starting research session...")
        session = await agent.start_session()
        
        # Example research queries
        research_queries = [
            "What are the latest findings about APOE4 and Alzheimer's disease?",
            "Can you search for recent papers on tau protein aggregation?",
            "What genetic variants are associated with early-onset Alzheimer's?",
            "Summarize the role of amyloid beta in neurodegeneration"
        ]
        
        for i, query in enumerate(research_queries, 1):
            print(f"\n📝 Query {i}: {query}")
            print("🤔 Processing...")
            
            try:
                response = await agent.process_message(query)
                
                print("🤖 Response:")
                print("-" * 60)
                print(response.content)
                print("-" * 60)
                
                if response.tool_calls:
                    print(f"🔧 Used {len(response.tool_calls)} tools:")
                    for tool_call in response.tool_calls:
                        print(f"  • {tool_call.tool_name}")
                
            except Exception as e:
                print(f"❌ Error processing query: {e}")
        
        # Show session summary
        print("\n📊 Session Summary:")
        print(session.get_conversation_summary())
        
        # Export conversation
        print("\n💾 Exporting conversation...")
        try:
            conversation_json = session.export_conversation("json")
            with open("example_conversation.json", "w") as f:
                f.write(conversation_json)
            print("✅ Exported to example_conversation.json")
            
            conversation_md = session.export_conversation("markdown")
            with open("example_conversation.md", "w") as f:
                f.write(conversation_md)
            print("✅ Exported to example_conversation.md")
            
        except Exception as e:
            print(f"❌ Export error: {e}")
        
        # Analyze research progress
        print("\n📈 Research Progress Analysis:")
        analysis = await session.analyze_research_progress()
        
        print(f"  Duration: {analysis['duration_minutes']:.1f} minutes")
        print(f"  Messages: {analysis['message_count']}")
        print(f"  Tool usage: {analysis['tool_usage']}")
        print(f"  Research themes: {analysis['research_themes']}")
        print(f"  Next steps: {analysis['next_steps']}")
        
    except Exception as e:
        logger.exception(f"Error in example: {e}")
        
    finally:
        # Cleanup
        print("\n🧹 Shutting down agent...")
        await agent.shutdown()
        print("✅ Done!")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
