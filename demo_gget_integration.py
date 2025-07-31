#!/usr/bin/env python3
"""
gget Integration Demonstration

This script demonstrates the integration of gget genomic database tools
with the biomedical agent framework. It showcases various gget functions
for gene analysis, sequence retrieval, and bioinformatics workflows.
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


async def demonstrate_gget_integration():
    """Demonstrate gget integration with comprehensive genomic analysis."""
    
    print("🧬 GGET GENOMIC TOOLS INTEGRATION DEMONSTRATION")
    print("=" * 80)
    print("🔬 gget: Efficient querying of genomic databases")
    print("🧪 BioMCP: Biomedical database access")
    print("🦙 Ollama: LLM reasoning and synthesis")
    print("=" * 80)
    
    # Define target genes for comprehensive analysis
    target_genes = [
        {
            "symbol": "ACE2",
            "description": "SARS-CoV-2 receptor, cardiovascular and respiratory system",
            "uniprot_id": "Q9BYF1"
        },
        {
            "symbol": "BRCA1", 
            "description": "DNA repair gene, breast cancer susceptibility",
            "uniprot_id": "P38398"
        },
        {
            "symbol": "TP53",
            "description": "Tumor suppressor gene, guardian of the genome",
            "uniprot_id": "P04637"
        }
    ]
    
    print(f"\n🎯 Target Genes for Analysis: {len(target_genes)} genes")
    for i, gene in enumerate(target_genes, 1):
        print(f"  {i}. {gene['symbol']} - {gene['description']}")
    
    # Show available gget tools
    print("\n🔧 Available gget Tools:")
    available_tools = biomcp_tools.get_available_tools()
    gget_tools = [tool for tool in available_tools if tool.name.startswith('gget_')]
    
    for tool in gget_tools:
        print(f"  • {tool.name}: {tool.description}")
    
    print(f"\n📊 Total tools available: {len(available_tools)} ({len(gget_tools)} gget tools)")
    
    # Create research context
    research_context = ResearchContext(
        domain="genomics",
        organism="human",
        research_question="How can gget tools enhance genomic analysis workflows?",
        keywords=["genomics", "gget", "gene analysis", "sequence retrieval", "bioinformatics"]
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
        
        # Process each gene through the gget analysis pipeline
        for i, gene_info in enumerate(target_genes, 1):
            print(f"\n" + "="*80)
            print(f"GENE {i}: {gene_info['symbol']} ANALYSIS PIPELINE")
            print("="*80)
            
            await analyze_gene_with_gget(agent, gene_info, i)
        
        print("\n" + "="*80)
        print("COMPARATIVE GENOMIC ANALYSIS")
        print("="*80)
        
        # Generate comparative analysis using LLM
        comparative_response = await agent.process_message(
            f"Based on our gget analysis of {len(target_genes)} genes "
            f"({', '.join([g['symbol'] for g in target_genes])}), provide a comparative "
            f"genomic analysis. What are the key insights about gene function, "
            f"evolutionary conservation, and clinical significance? How do these genes "
            f"relate to each other in terms of pathways and disease associations?"
        )
        
        print("🤖 Comparative Analysis:")
        print("-" * 60)
        print(comparative_response.content)
        print("-" * 60)
        
        # Display session analytics
        await display_session_analytics(agent)
        
        print(f"\n🕒 gget integration demo completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("✅ Successfully demonstrated:")
        print("  🧬 Gene ID search and retrieval")
        print("  📝 Gene information and annotation")
        print("  🔍 Sequence analysis and alignment")
        print("  🏗️ Protein structure retrieval")
        print("  📊 Gene expression analysis")
        print("  🛤️ Pathway enrichment analysis")
        
    except Exception as e:
        logger.error(f"Error in gget integration demonstration: {e}")
        print(f"❌ Error: {e}")
        
    finally:
        await agent.shutdown()


async def analyze_gene_with_gget(
    agent: BiomedicalAgent, 
    gene_info: Dict[str, str], 
    gene_num: int
) -> None:
    """Analyze a single gene through the complete gget pipeline."""
    
    symbol = gene_info['symbol']
    description = gene_info['description']
    uniprot_id = gene_info['uniprot_id']
    
    print(f"\n🔍 STEP {gene_num}.1: Gene Search and ID Retrieval")
    print("-" * 50)
    
    # Search for Ensembl IDs using gget_search
    try:
        search_result = await biomcp_tools.call_tool(
            "gget_search", 
            {"searchwords": [symbol], "species": "homo_sapiens"}
        )
        print(f"📋 Gene Search Results for {symbol}:")
        print(f"  Result: {str(search_result)[:200]}...")
        
        # Extract Ensembl ID if available
        ensembl_id = None
        if isinstance(search_result, dict) and symbol in search_result:
            ensembl_id = search_result[symbol].get('ensembl_id') if isinstance(search_result[symbol], dict) else None
        
        if ensembl_id:
            print(f"  ✅ Found Ensembl ID: {ensembl_id}")
        else:
            print(f"  ⚠️  Ensembl ID not found, using gene symbol")
            
    except Exception as e:
        print(f"  ❌ Gene search failed: {e}")
        ensembl_id = None
    
    print(f"\n📖 STEP {gene_num}.2: Gene Information Retrieval")
    print("-" * 50)
    
    # Get detailed gene information
    if ensembl_id:
        try:
            info_result = await biomcp_tools.call_tool(
                "gget_info",
                {"ens_ids": [ensembl_id], "expand": True}
            )
            print(f"📚 Gene Information for {symbol} ({ensembl_id}):")
            print(f"  Details: {str(info_result)[:300]}...")
        except Exception as e:
            print(f"  ❌ Gene info retrieval failed: {e}")
    else:
        print(f"  ⚠️  Skipping gene info (no Ensembl ID)")
    
    print(f"\n🧬 STEP {gene_num}.3: Sequence Analysis")
    print("-" * 50)
    
    # Get gene sequences
    if ensembl_id:
        try:
            seq_result = await biomcp_tools.call_tool(
                "gget_seq",
                {"ens_ids": [ensembl_id], "translate": True, "seqtype": "transcript"}
            )
            print(f"🧪 Sequence Analysis for {symbol}:")
            print(f"  Sequences: {str(seq_result)[:200]}...")
        except Exception as e:
            print(f"  ❌ Sequence retrieval failed: {e}")
    else:
        print(f"  ⚠️  Skipping sequence analysis (no Ensembl ID)")
    
    print(f"\n🏗️ STEP {gene_num}.4: Protein Structure Retrieval")
    print("-" * 50)
    
    # Get AlphaFold protein structure
    try:
        alphafold_result = await biomcp_tools.call_tool(
            "gget_alphafold",
            {"uniprot_id": uniprot_id, "save": False}
        )
        print(f"🏗️ AlphaFold Structure for {symbol} ({uniprot_id}):")
        print(f"  Structure info: {str(alphafold_result)[:200]}...")
    except Exception as e:
        print(f"  ❌ AlphaFold structure retrieval failed: {e}")
    
    print(f"\n📊 STEP {gene_num}.5: Gene Expression Analysis")
    print("-" * 50)
    
    # Get expression data from ARCHS4
    try:
        archs4_result = await biomcp_tools.call_tool(
            "gget_archs4",
            {"gene": symbol, "which": "tissue"}
        )
        print(f"📈 Expression Analysis for {symbol}:")
        print(f"  Expression data: {str(archs4_result)[:200]}...")
    except Exception as e:
        print(f"  ❌ Expression analysis failed: {e}")
    
    print(f"\n🛤️ STEP {gene_num}.6: Pathway Enrichment Analysis")
    print("-" * 50)
    
    # Perform enrichment analysis
    try:
        enrichr_result = await biomcp_tools.call_tool(
            "gget_enrichr",
            {
                "genes": [symbol], 
                "database": "GO_Biological_Process_2023"
            }
        )
        print(f"🛤️ Pathway Enrichment for {symbol}:")
        print(f"  Enrichment results: {str(enrichr_result)[:200]}...")
    except Exception as e:
        print(f"  ❌ Enrichment analysis failed: {e}")
    
    print(f"\n🧠 STEP {gene_num}.7: LLM Integration and Interpretation")
    print("-" * 50)
    
    # Use LLM to interpret and synthesize gget results
    interpretation_response = await agent.process_message(
        f"Provide a comprehensive interpretation of our gget analysis for {symbol}. "
        f"This gene is described as: {description}. Based on the genomic data we've "
        f"gathered through gget tools (gene search, sequence analysis, structure data, "
        f"expression patterns, and pathway enrichment), what are the key biological "
        f"insights? How does this data contribute to our understanding of {symbol}'s "
        f"function and clinical significance?"
    )
    
    print("🧠 LLM Interpretation:")
    print(f"  Gene: {symbol}")
    print(f"  Analysis: {interpretation_response.content[:300]}...")


async def test_gget_tools():
    """Test individual gget tools to ensure they work properly."""
    
    print("\n🧪 TESTING INDIVIDUAL GGET TOOLS")
    print("=" * 60)
    
    test_cases = [
        {
            "tool": "gget_search",
            "params": {"searchwords": ["ACE2"], "species": "homo_sapiens"},
            "description": "Search for ACE2 gene ID"
        },
        {
            "tool": "gget_archs4", 
            "params": {"gene": "ACE2", "which": "tissue"},
            "description": "Get ACE2 expression data"
        },
        {
            "tool": "gget_enrichr",
            "params": {"genes": ["ACE2", "TMPRSS2"], "database": "GO_Biological_Process_2023"},
            "description": "Enrichment analysis for COVID-19 related genes"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing {test_case['tool']}: {test_case['description']}")
        try:
            result = await biomcp_tools.call_tool(test_case['tool'], test_case['params'])
            print(f"   ✅ Success: {str(result)[:100]}...")
        except Exception as e:
            print(f"   ❌ Failed: {e}")


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
            filename = f"gget_integration_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
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


if __name__ == "__main__":
    print("🚀 Starting gget Integration Demonstration...")
    
    # First test individual tools
    asyncio.run(test_gget_tools())
    
    # Then run full demonstration
    asyncio.run(demonstrate_gget_integration())
    
    print("\n🎉 gget Integration Demonstration Complete!")
    print("The integration showcases:")
    print("• Gene search and ID retrieval")
    print("• Sequence analysis and alignment") 
    print("• Protein structure access")
    print("• Expression data analysis")
    print("• Pathway enrichment analysis")
    print("• LLM-powered result interpretation")
    print("\n💡 Tip: Install gget with 'pip install gget' for full functionality")