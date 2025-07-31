#!/usr/bin/env python3
"""
Test to check BioMCP output format.
"""

import asyncio
import json
from bioagent.biomcp.tools import biomcp_tools

async def test_biomcp_output():
    """Test the output format of BioMCP tools."""
    
    try:
        print("Testing article_searcher output format...")
        result = await biomcp_tools.call_tool(
            "article_searcher", 
            {"keywords": "CRISPR", "page_size": 2}
        )
        
        print(f"Type: {type(result)}")
        print(f"First 200 chars: {str(result)[:200]}...")
        
        # Try to parse as JSON
        if isinstance(result, str):
            try:
                parsed = json.loads(result)
                print(f"Successfully parsed JSON. Keys: {list(parsed.keys())}")
                
                if 'results' in parsed:
                    print(f"Found {len(parsed['results'])} articles")
                    if parsed['results']:
                        first_article = parsed['results'][0]
                        print(f"First article keys: {list(first_article.keys())}")
                        print(f"Title: {first_article.get('title', 'No title')}")
                        
            except json.JSONDecodeError as e:
                print(f"Failed to parse as JSON: {e}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_biomcp_output())
