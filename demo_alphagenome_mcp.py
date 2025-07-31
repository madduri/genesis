#!/usr/bin/env python3
"""
AlphaGenome BioMCP Integration Demonstration

This script demonstrates the integration between AlphaGenome AI predictions
and BioMCP biomedical database access through the biomedical agent framework.
It showcases variant effect predictions combined with literature and clinical data.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, List, Any

from bioagent import BiomedicalAgent
from bioagent.core.models import AgentConfiguration, ResearchContext
from bioagent.biomcp.tools import biomcp_tools

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def demonstrate_alphagenome_biomcp_integration():
    """Demonstrate AlphaGenome + BioMCP integration for variant analysis."""
    
    print("🧬 ALPHAGENOME + BioMCP INTEGRATION DEMONSTRATION")
    print("=" * 80)
    print("🔬 BioMCP: Live access to biomedical databases")
    print("🤖 AlphaGenome: AI-powered variant effect predictions")
    print("🦙 Ollama: LLM reasoning and research synthesis")
    print("=" * 80)
    
    # Check for AlphaGenome API key
    alphagenome_api_key = os.getenv('ALPHAGENOME_API_KEY')
    if alphagenome_api_key:
        print(f"✅ AlphaGenome API key found: {alphagenome_api_key[:8]}...")
    else:
        print("⚠️  AlphaGenome API key not found in environment (ALPHAGENOME_API_KEY)")
        print("   Demo will continue with simulated predictions")
    
    # Define target variants for analysis (using proper AlphaGenome format)
    target_variants = [
        {
            "variant": "chr7:140753336 A>T",
            "gene": "BRAF", 
            "disease": "cancer",
            "description": "BRAF V600E mutation"
        },
        {
            "variant": "chr17:7577121 C>T",
            "gene": "TP53",
            "disease": "cancer", 
            "description": "TP53 R273H mutation"
        },
        {
            "variant": "chr17:43044295 G>A",
            "gene": "BRCA1",
            "disease": "breast cancer",
            "description": "Pathogenic BRCA1 variant"
        }
    ]
    
    print(f"\n🎯 Target Variants for Analysis: {len(target_variants)} variants")
    for i, var in enumerate(target_variants, 1):
        print(f"  {i}. {var['gene']} ({var['variant']}) - {var['disease']}")
    
    # Show available BioMCP tools
    print("\n🔧 Available BioMCP Tools:")
    available_tools = biomcp_tools.get_available_tools()
    for tool in available_tools:
        print(f"  • {tool.name}: {tool.description}")
    
    # Create research context focused on variant analysis
    research_context = ResearchContext(
        domain="precision_medicine",
        organism="human",
        research_question="How can AlphaGenome predictions enhance biomedical variant interpretation?",
        keywords=["variant analysis", "AlphaGenome", "precision medicine", "pathogenicity prediction"]
    )
    
    print(f"\n🎯 Research Question: {research_context.research_question}")
    
    # Configure agent with Ollama
    config = AgentConfiguration(
        model_provider="ollama",
        model_name="llama3.1:latest",
        temperature=0.7,
        max_tokens=3000,
        research_context=research_context
    )
    
    # Initialize the biomedical agent
    agent = BiomedicalAgent(config)
    
    try:
        print("\n🚀 Initializing Biomedical Research Agent...")
        await agent.initialize()
        
        # Process each variant through the complete pipeline
        for i, variant_info in enumerate(target_variants, 1):
            print(f"\n" + "="*80)
            print(f"VARIANT {i}: {variant_info['gene']} ANALYSIS PIPELINE")
            print("="*80)
            
            await analyze_variant_with_alphagenome_biomcp(
                agent, variant_info, i
            )
        
        print("\n" + "="*80)
        print("COMPARATIVE ANALYSIS & RESEARCH SYNTHESIS")
        print("="*80)
        
        # Generate comprehensive research synthesis
        synthesis_response = await agent.process_message(
            f"Based on our analysis of {len(target_variants)} variants across different genes "
            f"({', '.join([v['gene'] for v in target_variants])}), provide a comprehensive "
            f"research synthesis. How do AlphaGenome predictions complement traditional "
            f"biomedical database information? What are the key insights for precision medicine? "
            f"What experimental validation approaches would you recommend?"
        )
        
        print("🤖 Research Synthesis:")
        print("-" * 60)
        print(synthesis_response.content)
        print("-" * 60)
        
        # Display session analytics
        await display_session_analytics(agent)
        
        print(f"\n🕒 AlphaGenome-BioMCP demo completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("✅ Successfully demonstrated:")
        print("  🧬 Multi-variant analysis pipeline")
        print("  🔬 BioMCP database integration")
        print("  🤖 AlphaGenome prediction simulation") 
        print("  🦙 LLM-powered research synthesis")
        print("  📊 Cross-variant comparative analysis")
        
    except Exception as e:
        logger.error(f"Error in AlphaGenome-BioMCP demonstration: {e}")
        print(f"❌ Error: {e}")
        
    finally:
        await agent.shutdown()


async def analyze_variant_with_alphagenome_biomcp(
    agent: BiomedicalAgent, 
    variant_info: Dict[str, str], 
    variant_num: int
) -> None:
    """Analyze a single variant through the complete AlphaGenome + BioMCP pipeline."""
    
    gene = variant_info['gene']
    variant = variant_info['variant']
    disease = variant_info['disease']
    
    print(f"\n🧬 STEP {variant_num}.1: Literature Analysis for {gene}")
    print("-" * 50)
    
    # Literature search using BioMCP
    lit_response = await agent.process_message(
        f"Search for recent literature on {gene} variants in {disease}. "
        f"Focus on pathogenicity, functional effects, and clinical significance. "
        f"Limit to the most relevant 5 papers."
    )
    
    print("📚 Literature Analysis Results:")
    print(f"  Query: {gene} variants in {disease}")
    print(f"  Response: {lit_response.content[:200]}...")
    if lit_response.tool_calls:
        print(f"  Tools used: {[call.tool_name for call in lit_response.tool_calls]}")
    
    print(f"\n🔬 STEP {variant_num}.2: Variant Database Search")
    print("-" * 50)
    
    # Variant database search
    var_response = await agent.process_message(
        f"Search for variants in the {gene} gene using the variant database. "
        f"Focus on pathogenic and likely pathogenic variants. "
        f"Get detailed information about functional consequences."
    )
    
    print("🧪 Variant Database Results:")
    print(f"  Gene: {gene}")
    print(f"  Response: {var_response.content[:200]}...")
    if var_response.tool_calls:
        print(f"  Tools used: {[call.tool_name for call in var_response.tool_calls]}")
    
    print(f"\n🤖 STEP {variant_num}.3: AlphaGenome Prediction Simulation")
    print("-" * 50)
    
    # Simulate AlphaGenome prediction with proper format
    alpha_response = await agent.process_message(
        f"Simulate an AlphaGenome prediction for variant {variant} in gene {gene}. "
        f"Note: AlphaGenome expects format like 'chr7:140753336 A>T' (chromosome:position ref>alt). "
        f"Based on the literature and variant data we've gathered, what would be the "
        f"expected pathogenicity score (0-1), functional impact, and molecular consequences? "
        f"Consider protein structure, domain effects, and evolutionary conservation. "
        f"Include confidence score and effect prediction."
    )
    
    print("🧬 AlphaGenome Prediction Simulation:")
    print(f"  Variant: {variant}")
    print(f"  Gene: {gene}")
    print(f"  Prediction: {alpha_response.content[:300]}...")
    
    print(f"\n🏥 STEP {variant_num}.4: Clinical Trials Search")
    print("-" * 50)
    
    # Clinical trials search
    trial_response = await agent.process_message(
        f"Search for clinical trials targeting {gene}-related {disease}. "
        f"What therapeutic strategies are being investigated? "
        f"Are there any precision medicine approaches?"
    )
    
    print("🔬 Clinical Trials Results:")
    print(f"  Focus: {gene}-related {disease}")
    print(f"  Response: {trial_response.content[:200]}...")
    if trial_response.tool_calls:
        print(f"  Tools used: {[call.tool_name for call in trial_response.tool_calls]}")
    
    print(f"\n📊 STEP {variant_num}.5: Integrated Analysis")
    print("-" * 50)
    
    # Integrated analysis combining all data sources
    integration_response = await agent.process_message(
        f"Integrate all the information we've gathered for {gene} variant {variant}: "
        f"literature evidence, variant database information, AlphaGenome predictions, "
        f"and clinical trial data. What is the clinical significance of this variant? "
        f"What are the therapeutic implications?"
    )
    
    print("🔗 Integrated Analysis:")
    print(f"  Variant: {gene} {variant}")
    print(f"  Clinical significance: {integration_response.content[:250]}...")


async def display_session_analytics(agent: BiomedicalAgent) -> None:
    """Display comprehensive session analytics."""
    
    print("\n" + "="*60)
    print("SESSION ANALYTICS")
    print("="*60)
    
    if agent.session:
        try:
            # Get conversation summary
            session_summary = agent.session.get_conversation_summary()
            print("📊 Conversation Summary:")
            print(session_summary)
            
            # Export the research session
            conversation_md = agent.session.export_conversation("markdown")
            filename = f"alphagenome_biomcp_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(filename, "w") as f:
                f.write(conversation_md)
            print(f"\n💾 Full research session exported to: {filename}")
            
            # Analyze research progress
            progress = await agent.session.analyze_research_progress()
            print(f"\n📈 Research Progress Analysis:")
            print(f"  • Duration: {progress['duration_minutes']:.1f} minutes")
            print(f"  • Messages exchanged: {progress['message_count']}")
            print(f"  • Tools used: {progress['tool_usage']}")
            print(f"  • Research themes: {progress['research_themes']}")
            
        except Exception as e:
            logger.warning(f"Could not generate session analytics: {e}")
            print("⚠️  Session analytics unavailable")
    else:
        print("❌ No active session found")


async def test_alphagenome_tool_availability():
    """Test availability of AlphaGenome-related tools in BioMCP."""
    
    print("\n🧪 TESTING ALPHAGENOME TOOL AVAILABILITY")
    print("=" * 60)
    
    # Check for API key
    alphagenome_api_key = os.getenv('ALPHAGENOME_API_KEY')
    if alphagenome_api_key:
        print(f"🔑 Using AlphaGenome API key: {alphagenome_api_key[:8]}...")
    else:
        print("⚠️  No AlphaGenome API key found (set ALPHAGENOME_API_KEY environment variable)")
    
    available_tools = biomcp_tools.get_available_tools()
    alphagenome_tools = [tool for tool in available_tools if 'alpha' in tool.name.lower()]
    
    if alphagenome_tools:
        print("✅ AlphaGenome tools found:")
        for tool in alphagenome_tools:
            print(f"  • {tool.name}: {tool.description}")
            
            # Test tool call
            try:
                print(f"    Testing {tool.name}...")
                # Create sample parameters based on tool requirements
                test_params = {}
                for param in tool.parameters:
                    if param.name == "variant":
                        test_params[param.name] = "chr7:140753336 A>T"  # BRAF V600E
                    elif param.name == "gene":
                        test_params[param.name] = "BRAF"
                    elif param.name == "chromosome":
                        test_params[param.name] = "chr7"
                    elif param.name == "position":
                        # Position should be integer, not string
                        test_params[param.name] = 140753336
                    elif param.name == "ref" or param.name == "reference":
                        test_params[param.name] = "A"
                    elif param.name == "alt" or param.name == "alternative" or param.name == "alternate":
                        test_params[param.name] = "T"  # Nucleotide, not gene name
                    elif param.name == "api_key" or param.name == "key":
                        # Use API key from environment if available
                        if alphagenome_api_key:
                            test_params[param.name] = alphagenome_api_key
                        else:
                            test_params[param.name] = "YOUR_KEY_HERE"
                    elif param.required and param.default is None:
                        # Use appropriate defaults for common parameter names with correct types
                        if "chr" in param.name.lower():
                            test_params[param.name] = "chr7"
                        elif "pos" in param.name.lower():
                            test_params[param.name] = 140753336  # Integer for position
                        elif "ref" in param.name.lower():
                            test_params[param.name] = "A"  # Reference nucleotide
                        elif "alt" in param.name.lower():
                            test_params[param.name] = "T"  # Alternate nucleotide
                        elif param.type == "integer":
                            test_params[param.name] = 140753336
                        elif param.type == "boolean":
                            test_params[param.name] = True
                        elif param.type == "array":
                            test_params[param.name] = ["BRAF"]
                        else:
                            # For string params, use appropriate defaults
                            if param.name.lower() in ["gene", "symbol"]:
                                test_params[param.name] = "BRAF"
                            else:
                                test_params[param.name] = "A"  # Default to nucleotide for unknown string params
                
                print(f"    Parameters: {test_params}")
                result = await biomcp_tools.call_tool(tool.name, test_params)
                print(f"    ✅ Tool test successful: {str(result)[:100]}...")
                
            except Exception as e:
                print(f"    ⚠️  Tool test failed: {e}")
                print(f"    Tool: {tool.name}")
                print(f"    Parameters: {test_params}")
                # Print parameter types for debugging
                param_types = {k: type(v).__name__ for k, v in test_params.items()}
                print(f"    Parameter types: {param_types}")
                import traceback
                print(f"    Full traceback:")
                traceback.print_exc()
    else:
        print("ℹ️  No AlphaGenome-specific tools found in BioMCP")
        print("   This demonstration will simulate AlphaGenome predictions using LLM reasoning")
    
    print(f"\n📊 Total BioMCP tools available: {len(available_tools)}")
    for tool in available_tools[:5]:  # Show first 5 tools
        print(f"  • {tool.name}")
    if len(available_tools) > 5:
        print(f"  ... and {len(available_tools) - 5} more")


async def setup_alphagenome_environment():
    """Setup and validate AlphaGenome environment configuration."""
    
    print("🔧 ALPHAGENOME ENVIRONMENT SETUP")
    print("=" * 50)
    
    # Check for API key
    api_key = os.getenv('ALPHAGENOME_API_KEY')
    if api_key:
        print(f"✅ AlphaGenome API key configured: {api_key[:8]}...")
        return api_key
    else:
        print("❌ AlphaGenome API key not found!")
        print("\n📋 To use AlphaGenome predictions, set your API key:")
        print("   export ALPHAGENOME_API_KEY=your_actual_key_here")
        print("\n   Or run:")
        print("   ALPHAGENOME_API_KEY=your_key python demo_alphagenome_mcp.py")
        print("\n⚠️  Demo will continue with simulated predictions only")
        return None


if __name__ == "__main__":
    print("🚀 Starting AlphaGenome + BioMCP Integration Demonstration...")
    
    # Setup environment
    asyncio.run(setup_alphagenome_environment())
    
    # First test tool availability
    asyncio.run(test_alphagenome_tool_availability())
    
    # Then run full demonstration
    asyncio.run(demonstrate_alphagenome_biomcp_integration())
    
    print("\n🎉 AlphaGenome + BioMCP Integration Demonstration Complete!")
    print("The integration showcases:")
    print("• Multi-variant analysis pipeline")
    print("• BioMCP database integration")  
    print("• AlphaGenome prediction workflow")
    print("• Comprehensive research synthesis")
    print("\n💡 Tip: Set ALPHAGENOME_API_KEY environment variable for real predictions")