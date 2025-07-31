"""
BioMCP Client for connecting to and communicating with a local BioMCP server.

This client uses the biomcp-python package to directly invoke BioMCP tools.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from biomcp.individual_tools import (
    article_searcher, article_getter, 
    trial_searcher, trial_getter,
    variant_searcher, variant_getter,
    get_cbioportal_summary_for_genes
)

from ..core.models import Tool, ToolParameter, ToolCall, ToolResult

logger = logging.getLogger(__name__)


class BioMCPClient:
    """Client for direct communication with BioMCP tools via biomcp-python."""
    
    def __init__(self):
        self._tools = self._discover_tools()
        logger.info("BioMCP client initialized with direct tool access")

    def _discover_tools(self) -> Dict[str, Tool]:
        """Discover available BioMCP tools."""
        tools = {
            "pubmed_search": Tool(
                name="pubmed_search",
                description="Search PubMed for biomedical literature",
                server_id="biomcp_direct",
                parameters=[
                    ToolParameter(name="query", type="string", required=True),
                    ToolParameter(name="limit", type="integer", default=10)
                ]
            ),
            "get_article": Tool(
                name="get_article",
                description="Get details of a specific PubMed article by ID",
                server_id="biomcp_direct",
                parameters=[
                    ToolParameter(name="pmid", type="string", required=True)
                ]
            ),
            "clinical_trial_search": Tool(
                name="clinical_trial_search",
                description="Search ClinicalTrials.gov for relevant studies",
                server_id="biomcp_direct",
                parameters=[
                    ToolParameter(name="query", type="string", required=True),
                    ToolParameter(name="limit", type="integer", default=10)
                ]
            ),
            "get_clinical_trial": Tool(
                name="get_clinical_trial",
                description="Get details of a specific clinical trial by ID",
                server_id="biomcp_direct",
                parameters=[
                    ToolParameter(name="nct_id", type="string", required=True)
                ]
            ),
            "variant_search": Tool(
                name="variant_search",
                description="Search MyVariant.info for genomic variants",
                server_id="biomcp_direct",
                parameters=[
                    ToolParameter(name="query", type="string", required=True),
                    ToolParameter(name="limit", type="integer", default=10)
                ]
            ),
            "get_variant": Tool(
                name="get_variant",
                description="Get details of a specific genomic variant by ID",
                server_id="biomcp_direct",
                parameters=[
                    ToolParameter(name="variant_id", type="string", required=True)
                ]
            ),
            "cbioportal_summary": Tool(
                name="cbioportal_summary",
                description="Get cancer genomics summary from cBioPortal for a list of genes",
                server_id="biomcp_direct",
                parameters=[
                    ToolParameter(name="genes", type="list", required=True)
                ]
            )
        }
        return tools
    
    async def call_tool(self, tool_call: ToolCall) -> ToolResult:
        """Call a BioMCP tool directly."""
        tool_name = tool_call.tool_name
        params = tool_call.parameters
        
        try:
            logger.info(f"Calling BioMCP tool: {tool_name} with params: {params}")
            
            if tool_name == "pubmed_search":
                result = await article_searcher(**params)
            elif tool_name == "get_article":
                result = await article_getter(**params)
            elif tool_name == "clinical_trial_search":
                result = await trial_searcher(**params)
            elif tool_name == "get_clinical_trial":
                result = await trial_getter(**params)
            elif tool_name == "variant_search":
                result = await variant_searcher(**params)
            elif tool_name == "get_variant":
                result = await variant_getter(**params)
            elif tool_name == "cbioportal_summary":
                result = await get_cbioportal_summary_for_genes(**params)
            else:
                raise NotImplementedError(f"Tool {tool_name} not implemented in BioMCP client")
                
            return ToolResult(
                call_id=tool_call.call_id,
                success=True,
                result=result
            )
            
        except Exception as e:
            logger.error(f"Error calling BioMCP tool {tool_name}: {e}")
            return ToolResult(
                call_id=tool_call.call_id,
                success=False,
                error=str(e)
            )
    
    def get_available_tools(self) -> List[Tool]:
        """Get the list of available BioMCP tools."""
        return list(self._tools.values())
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a specific BioMCP tool by name."""
        return self._tools.get(tool_name)
