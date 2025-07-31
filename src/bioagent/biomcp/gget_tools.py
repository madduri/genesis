"""
gget Tools wrapper to expose gget functionality to the biomedical agent framework.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
import json

from ..core.models import Tool, ToolParameter

logger = logging.getLogger(__name__)

# Try to import gget, handle if not installed
try:
    import gget
    GGET_AVAILABLE = True
    logger.info("gget package available")
except ImportError:
    GGET_AVAILABLE = False
    logger.warning("gget package not available. Install with: pip install gget")


class GgetTools:
    """Wrapper for gget genomic database tools."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._discover_gget_tools()

    def _discover_gget_tools(self):
        """Discover and register gget tools."""
        if not GGET_AVAILABLE:
            logger.warning("gget not available, skipping gget tools")
            return
            
        # Define gget tools with their parameters
        gget_tool_definitions = [
            {
                "name": "gget_ref",
                "description": "Fetch reference genome and annotation files for a species",
                "parameters": [
                    ToolParameter(name="species", type="string", required=True, description="Species name (e.g., 'homo_sapiens')"),
                    ToolParameter(name="which", type="string", required=False, default="all", description="Which files to fetch (gtf, fna, etc.)"),
                    ToolParameter(name="release", type="integer", required=False, description="Ensembl release version")
                ]
            },
            {
                "name": "gget_search", 
                "description": "Search for Ensembl gene IDs based on gene symbols",
                "parameters": [
                    ToolParameter(name="searchwords", type="array", required=True, description="List of gene symbols to search"),
                    ToolParameter(name="species", type="string", required=False, default="homo_sapiens", description="Species name"),
                    ToolParameter(name="id_type", type="string", required=False, default="gene", description="ID type to return")
                ]
            },
            {
                "name": "gget_info",
                "description": "Get detailed information about genes or transcripts", 
                "parameters": [
                    ToolParameter(name="ens_ids", type="array", required=True, description="List of Ensembl IDs"),
                    ToolParameter(name="expand", type="boolean", required=False, default=False, description="Expand output with additional info")
                ]
            },
            {
                "name": "gget_seq",
                "description": "Fetch gene or transcript sequences",
                "parameters": [
                    ToolParameter(name="ens_ids", type="array", required=True, description="List of Ensembl gene/transcript IDs"),
                    ToolParameter(name="translate", type="boolean", required=False, default=False, description="Translate to protein sequence"),
                    ToolParameter(name="seqtype", type="string", required=False, default="transcript", description="Sequence type (gene, transcript, protein)")
                ]
            },
            {
                "name": "gget_blast",
                "description": "Perform BLAST sequence similarity search",
                "parameters": [
                    ToolParameter(name="sequence", type="string", required=True, description="Query sequence"),
                    ToolParameter(name="program", type="string", required=False, default="blastp", description="BLAST program (blastp, blastn, etc.)"),
                    ToolParameter(name="database", type="string", required=False, default="nr", description="Database to search"),
                    ToolParameter(name="limit", type="integer", required=False, default=50, description="Maximum results")
                ]
            },
            {
                "name": "gget_blat",
                "description": "Find genomic location of a nucleotide or amino acid sequence",
                "parameters": [
                    ToolParameter(name="sequence", type="string", required=True, description="Query sequence"),
                    ToolParameter(name="seqtype", type="string", required=False, default="DNA", description="Sequence type (DNA, protein, translated%20RNA, translated%20DNA)"),
                    ToolParameter(name="assembly", type="string", required=False, default="human", description="Genome assembly")
                ]
            },
            {
                "name": "gget_muscle",
                "description": "Perform multiple sequence alignment using MUSCLE",
                "parameters": [
                    ToolParameter(name="sequences", type="array", required=True, description="List of sequences to align"),
                    ToolParameter(name="super5", type="boolean", required=False, default=False, description="Use Super5 algorithm for large alignments")
                ]
            },
            {
                "name": "gget_enrichr", 
                "description": "Perform gene ontology and pathway enrichment analysis",
                "parameters": [
                    ToolParameter(name="genes", type="array", required=True, description="List of gene symbols"),
                    ToolParameter(name="database", type="string", required=False, default="GO_Biological_Process_2023", description="Enrichment database")
                ]
            },
            {
                "name": "gget_archs4",
                "description": "Get gene expression data from ARCHS4",
                "parameters": [
                    ToolParameter(name="gene", type="string", required=True, description="Gene symbol"),
                    ToolParameter(name="which", type="string", required=False, default="tissue", description="Data type (tissue, cell_line, cancer)")
                ]
            },
            {
                "name": "gget_pdb",
                "description": "Fetch protein structures from PDB",
                "parameters": [
                    ToolParameter(name="pdb_id", type="string", required=True, description="PDB ID"),
                    ToolParameter(name="identifier", type="string", required=False, description="Specific chain or identifier"),
                    ToolParameter(name="save", type="boolean", required=False, default=False, description="Save structure file")
                ]
            },
            {
                "name": "gget_alphafold",
                "description": "Fetch predicted protein structures from AlphaFold",
                "parameters": [
                    ToolParameter(name="uniprot_id", type="string", required=True, description="UniProt ID"),
                    ToolParameter(name="save", type="boolean", required=False, default=False, description="Save structure file")
                ]
            },
            {
                "name": "gget_elm",
                "description": "Find protein sequence motifs using ELM database", 
                "parameters": [
                    ToolParameter(name="sequence", type="string", required=True, description="Protein sequence"),
                    ToolParameter(name="taxonomy", type="string", required=False, default="Homo sapiens", description="Taxonomic context")
                ]
            }
        ]
        
        # Register all gget tools
        for tool_def in gget_tool_definitions:
            tool = Tool(
                name=tool_def["name"],
                description=tool_def["description"], 
                server_id="gget_direct",
                parameters=tool_def["parameters"]
            )
            self._tools[tool_def["name"]] = tool
            logger.info(f"Registered gget tool: {tool_def['name']}")

    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Call a gget tool asynchronously."""
        if not GGET_AVAILABLE:
            return {"error": "gget package not available. Install with: pip install gget"}
            
        if tool_name not in self._tools:
            raise NotImplementedError(f"gget tool {tool_name} not found")
        
        try:
            # Run gget functions in thread pool since they're synchronous
            loop = asyncio.get_event_loop()
            
            if tool_name == "gget_ref":
                result = await loop.run_in_executor(
                    None, 
                    lambda: gget.ref(
                        species=params["species"],
                        which=params.get("which", "all"),
                        release=params.get("release")
                    )
                )
            elif tool_name == "gget_search":
                result = await loop.run_in_executor(
                    None,
                    lambda: gget.search(
                        searchwords=params["searchwords"],
                        species=params.get("species", "homo_sapiens"),
                        id_type=params.get("id_type", "gene")
                    )
                )
            elif tool_name == "gget_info":
                result = await loop.run_in_executor(
                    None,
                    lambda: gget.info(
                        ens_ids=params["ens_ids"],
                        expand=params.get("expand", False)
                    )
                )
            elif tool_name == "gget_seq":
                result = await loop.run_in_executor(
                    None,
                    lambda: gget.seq(
                        ens_ids=params["ens_ids"],
                        translate=params.get("translate", False),
                        seqtype=params.get("seqtype", "transcript")
                    )
                )
            elif tool_name == "gget_blast":
                result = await loop.run_in_executor(
                    None,
                    lambda: gget.blast(
                        sequence=params["sequence"],
                        program=params.get("program", "blastp"),
                        database=params.get("database", "nr"),
                        limit=params.get("limit", 50)
                    )
                )
            elif tool_name == "gget_blat":
                result = await loop.run_in_executor(
                    None,
                    lambda: gget.blat(
                        sequence=params["sequence"],
                        seqtype=params.get("seqtype", "DNA"),
                        assembly=params.get("assembly", "human")
                    )
                )
            elif tool_name == "gget_muscle":
                result = await loop.run_in_executor(
                    None,
                    lambda: gget.muscle(
                        sequences=params["sequences"],
                        super5=params.get("super5", False)
                    )
                )
            elif tool_name == "gget_enrichr":
                result = await loop.run_in_executor(
                    None,
                    lambda: gget.enrichr(
                        genes=params["genes"],
                        database=params.get("database", "GO_Biological_Process_2023")
                        # Note: gget.enrichr doesn't have organism parameter
                    )
                )
            elif tool_name == "gget_archs4":
                result = await loop.run_in_executor(
                    None,
                    lambda: gget.archs4(
                        gene=params["gene"],
                        which=params.get("which", "tissue")
                    )
                )
            elif tool_name == "gget_pdb":
                result = await loop.run_in_executor(
                    None,
                    lambda: gget.pdb(
                        pdb_id=params["pdb_id"],
                        identifier=params.get("identifier"),
                        save=params.get("save", False)
                    )
                )
            elif tool_name == "gget_alphafold":
                result = await loop.run_in_executor(
                    None,
                    lambda: gget.alphafold(
                        uniprot_ids=params["uniprot_id"],  # gget expects 'uniprot_ids' parameter
                        save=params.get("save", False)
                    )
                )
            elif tool_name == "gget_elm":
                result = await loop.run_in_executor(
                    None,
                    lambda: gget.elm(
                        sequence=params["sequence"],
                        taxonomy=params.get("taxonomy", "Homo sapiens")
                    )
                )
            else:
                raise NotImplementedError(f"gget tool {tool_name} not implemented")
            
            # Convert result to JSON-serializable format
            if hasattr(result, 'to_dict'):
                return result.to_dict()
            elif hasattr(result, 'to_json'):
                return json.loads(result.to_json())
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Error calling gget tool {tool_name}: {e}")
            return {"error": f"gget tool error: {str(e)}"}

    def get_available_tools(self) -> List[Tool]:
        """Get all available gget tools."""
        return list(self._tools.values())
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a specific gget tool by name.""" 
        return self._tools.get(tool_name)


# Singleton instance of GgetTools
gget_tools = GgetTools()