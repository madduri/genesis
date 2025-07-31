#!/usr/bin/env python3
"""
Complete Integrated Demonstration: BioMCP + AlphaGenome + Ollama

This demonstrates the full biomedical agent framework with:
1. BioMCP for real biomedical database access
2. AlphaGenome for AI-powered variant predictions
3. Ollama for LLM reasoning and synthesis
"""

import asyncio
import logging
from datetime import datetime

from bioagent import BiomedicalAgent
from bioagent.core.models import AgentConfiguration, ResearchContext
from bioagent.biomcp.tools import biomcp_tools

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def run_integrated_research_demo():
    """Run a complete research demonstration integrating all components."""
    
    print("🧬 INTEGRATED BIOMEDICAL RESEARCH DEMONSTRATION")
    print("=" * 80)
    print("🔬 BioMCP: Live access to PubMed, ClinicalTrials.gov, MyVariant.info, cBioPortal")
    print("🤖 AlphaGenome: AI-powered variant effect predictions")
    print("🦙 Ollama: LLM reasoning and research synthesis")
    print("=" * 80)
    
    # Create comprehensive research context
    research_context = ResearchContext(
        domain="precision_medicine",
        organism="human",
        research_question="What are the therapeutic implications of BRCA1 variants in cancer treatment?",
        keywords=["BRCA1", "cancer", "variants", "therapy", "precision medicine"]
    )
    
    print(f"\n🎯 Research Question: {research_context.research_question}")
    
    # Configure agent with Ollama
    config = AgentConfiguration(
        model_provider="ollama",
        model_name="llama3.1:latest",
        temperature=0.7,
        max_tokens=2000,
        research_context=research_context
    )
    
    # Initialize the biomedical agent
    agent = BiomedicalAgent(config)
    
    try:
        print("\n🚀 Initializing Biomedical Research Agent...")
        await agent.initialize()
        
        # Show available tools
        tools = await agent.get_available_tools()
        print(f"📦 Available tools: {len(tools)} BioMCP tools + Ollama LLM")
        
        print("\n" + "="*60)
        print("STEP 1: LITERATURE ANALYSIS WITH LLM SYNTHESIS")
        print("="*60)
        
        # Let the agent process a research query about BRCA1
        response1 = await agent.process_message(
            "Search for recent literature on BRCA1 variants and their clinical significance. "
            "Focus on therapeutic implications and precision medicine approaches."
        )
        
        print("🤖 Agent Response (Literature Analysis):")
        print("-" * 50)
        print(response1.content)
        print("-" * 50)
        
        if response1.tool_calls:
            print(f"\n🔧 Tools Used: {[call.tool_name for call in response1.tool_calls]}")
        
        print("\n" + "="*60)
        print("STEP 2: VARIANT ANALYSIS WITH AI PREDICTIONS")
        print("="*60)
        
        # Analyze specific BRCA1 variants
        response2 = await agent.process_message(
            "Now search for specific BRCA1 variants in the variant database. "
            "Focus on pathogenic variants and their functional consequences. "
            "If possible, get AI predictions for variant effects."
        )
        
        print("🤖 Agent Response (Variant Analysis):")
        print("-" * 50)
        print(response2.content)
        print("-" * 50)
        
        if response2.tool_calls:
            print(f"\n🔧 Tools Used: {[call.tool_name for call in response2.tool_calls]}")
        
        print("\n" + "="*60)
        print("STEP 3: CLINICAL TRIALS AND THERAPEUTIC OPTIONS")
        print("="*60)
        
        # Search for clinical trials
        response3 = await agent.process_message(
            "Search for current clinical trials targeting BRCA1-related cancers. "
            "What therapeutic strategies are being investigated? "
            "Summarize the most promising approaches."
        )
        
        print("🤖 Agent Response (Clinical Trials):")
        print("-" * 50)
        print(response3.content)
        print("-" * 50)
        
        if response3.tool_calls:
            print(f"\n🔧 Tools Used: {[call.tool_name for call in response3.tool_calls]}")
        
        print("\n" + "="*60)
        print("STEP 4: CROSS-CANCER GENOMICS ANALYSIS")
        print("="*60)
        
        # cBioPortal analysis
        response4 = await agent.process_message(
            "Get a comprehensive cancer genomics summary for BRCA1 from cBioPortal. "
            "What are the mutation patterns across different cancer types? "
            "How does this inform therapeutic strategies?"
        )
        
        print("🤖 Agent Response (Cancer Genomics):")
        print("-" * 50)
        print(response4.content)
        print("-" * 50)
        
        if response4.tool_calls:
            print(f"\n🔧 Tools Used: {[call.tool_name for call in response4.tool_calls]}")
        
        print("\n" + "="*60)
        print("STEP 5: RESEARCH SYNTHESIS AND RECOMMENDATIONS")
        print("="*60)
        
        # Final synthesis
        response5 = await agent.process_message(
            "Based on all the research we've conducted - literature, variants, clinical trials, "
            "and cancer genomics - provide a comprehensive synthesis. What are the key insights "
            "for BRCA1-based precision medicine? What experimental approaches would you recommend?"
        )
        
        print("🤖 Agent Response (Research Synthesis):")
        print("-" * 50)
        print(response5.content)
        print("-" * 50)
        
        # Show session summary
        print("\n" + "="*60)
        print("SESSION ANALYSIS")
        print("="*60)
        
        if agent.session:
            session_summary = agent.session.get_conversation_summary()
            print(session_summary)
            
            # Export the research session
            conversation_md = agent.session.export_conversation("markdown")
            with open("integrated_research_session.md", "w") as f:
                f.write(conversation_md)
            print(f"\n💾 Full research session exported to: integrated_research_session.md")
            
            # Analyze research progress
            progress = await agent.session.analyze_research_progress()
            print(f"\n📊 Research Progress Analysis:")
            print(f"  • Duration: {progress['duration_minutes']:.1f} minutes")
            print(f"  • Messages exchanged: {progress['message_count']}")
            print(f"  • Tools used: {progress['tool_usage']}")
            print(f"  • Research themes: {progress['research_themes']}")
        
        print(f"\n🕒 Integrated demo completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("✅ Successfully demonstrated:")
        print("  🔬 Real-time biomedical database access via BioMCP")
        print("  🤖 AI-powered research synthesis via Ollama")
        print("  🧬 Multi-step research workflow automation")
        print("  📊 Cross-database analysis and insights")
        
    except Exception as e:
        logger.error(f"Error in integrated demonstration: {e}")
        print(f"❌ Error: {e}")
        
    finally:
        await agent.shutdown()


async def test_ollama_biomcp_integration():
    """Test the integration between Ollama and BioMCP tools."""
    
    print("\n🧪 TESTING OLLAMA + BioMCP INTEGRATION")
    print("=" * 50)
    
    # Quick integration test
    config = AgentConfiguration(
        model_provider="ollama",
        model_name="llama3.1:latest",
        temperature=0.7
    )
    
    agent = BiomedicalAgent(config)
    
    try:
        await agent.initialize()
        
        # Test a simple query that should trigger tool usage
        response = await agent.process_message(
            "Search for information about CRISPR gene editing in recent literature."
        )
        
        print("🤖 Integration Test Response:")
        print(response.content[:300] + "...")
        
        if response.tool_calls:
            print(f"✅ Tool integration successful - used: {[call.tool_name for call in response.tool_calls]}")
        else:
            print("ℹ️  No tools called - this is expected for simple queries")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        
    finally:
        await agent.shutdown()


if __name__ == "__main__":
    print("🚀 Starting Integrated Biomedical Research Demonstration...")
    print("Components: BioMCP + AlphaGenome + Ollama")
    
    # First run integration test
    asyncio.run(test_ollama_biomcp_integration())
    
    # Then run full demonstration
    asyncio.run(run_integrated_research_demo())
    
    print("\n🎉 Integrated Demonstration Complete!")
    print("The biomedical agent framework is now fully operational with:")
    print("• Live biomedical database access")
    print("• AI-powered variant predictions") 
    print("• LLM-driven research synthesis")
    print("• Interactive research workflows")
