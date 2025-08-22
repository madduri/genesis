#!/usr/bin/env -S uv --quiet run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "mcp",
# ]
# ///

# Scripts to reproduce this page:
# https://biomcp.org/mcp_integration/

import asyncio

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import TextContent

import asyncio
import ollama
from dataclasses import dataclass
from typing import List, Dict, Union

@dataclass
class TextContent:
    type: str
    text: str


@dataclass
class ToolResult:
    isError: bool
    content: Union[str, List[TextContent]]


class OllamaAgent:
    def __init__(self, model: str = "phi3:mini"):
        self.model = model

    async def initialize(self):
        print("Ollama: Agent initialized.")

    async def list_prompts(self) -> List[str]:
        return ["Default prompt (internal)"]

    async def list_tools(self) -> List[str]:
        return ["think", "fetch"]

    async def call_tool(self, tool: str, args: dict) -> ToolResult:
        if tool == "think":
            prompt = (
                f"Planning analysis for variant: {args.get('thought')}\n"
                f"Step {args.get('thoughtNumber')} of {args.get('totalThoughts')}.\n"
                f"Next thought needed: {args.get('nextThoughtNeeded')}."
            )
        elif tool == "fetch":
            prompt = (
                f"Analyze variant {args.get('id')} in domain {args.get('domain')} (e.g., gene: BRAF).\n"
                f"Return type, clinical significance, and disease associations in markdown format."
            )
        else:
            return ToolResult(isError=True, content=f"Unknown tool: {tool}")

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            message = response["message"]["content"]
            return ToolResult(
                isError=False,
                content=[TextContent(type="text", text=message)]
            )
        except Exception as e:
            return ToolResult(isError=True, content=str(e))


class BioMCPAgent:
    def __init__(self):
        self.server_params = StdioServerParameters(
        command="uv",
        args=["run", "--with", "biomcp-python", "biomcp", "run"],
    )
    #
    # Run with local code
    # server_params = StdioServerParameters(
    #     command="python",
    #     args=["-m", "biomcp", "run"],
    # )
        self.session = None

    async def initialize(self):
        async with (stdio_client(self.server_params) as (read, write),
                    ClientSession(read, write) as session):
            await session.initialize()
            self.session = session
            
            # list prompts
            prompts = await self.session.list_prompts()
            print("Available prompts:", prompts)
    
            # list resources
            resources = await self.session.list_resources()
            print("Available resources:", resources)
    
            # list tools
            tool_result = await self.session.list_tools()
            tools = tool_result.tools
            print("Available tools:", tools)

    async def list_prompts(self) -> List[str]:
        return ["Default prompt (internal)"]

    async def list_tools(self) -> List[str]:
        return ["think", "fetch"]

    async def call_tool(self, tool: str, arg: dict):
        async with (stdio_client(self.server_params) as (read, write),
            ClientSession(read, write) as session):
            await session.initialize()
            if tool == "think":
                try:
                    think_result = await session.call_tool(
                        tool,
                        arg,
                    )
                    assert (
                        think_result.isError is False
                    )
                except Exception as e:
                    return ToolResult(isError=True, content=str(e))
                return think_result
            elif tool == "fetch":
                try:
                    result = await self.call_tool(tool, arg)
                    assert result.isError is False, f"Error: {result.content}"
            
                    # --- Assertions ---
                    # 1. Check the call was successful (not an error)
                    assert (
                        result.isError is False
                    ), f"Tool call resulted in error: {result.content}"
            
                    # 2. Check there is content
                    assert result.content is not None
                    assert len(result.content) >= 1
            
                    # 3. Check the type of the first content block
                    content_block = result.content[0]
                    assert isinstance(content_block, TextContent)
            
                    markdown_output = content_block.text
                    print(markdown_output)
                    assert isinstance(markdown_output, str)
                    assert "rs113488022" in markdown_output
                    assert "BRAF" in markdown_output
                    #assert "Pathogenic" in markdown_output
                    print(f"Successfully called tool '{tool_name}' with args {tool_args}")
                except Exception as e:
                    return ToolResult(isError=True, content=str(e))
    
                return result
            else:
                return ToolResult(isError=True, content=f"Unknown tool: {tool}")



async def main():
    ollama_agent = OllamaAgent()
    await ollama_agent.initialize()

    bio_agent = BioMCPAgent()
    await bio_agent.initialize()

    print("Available tools in ollama:", await ollama_agent.list_tools())
    print("Available tools in biomcp:", await bio_agent.list_tools())

    
    think_result_1 = await bio_agent.call_tool("think", {
        "thought": "rs113488022 in BRAF gene",
        "thoughtNumber": 1,
        "totalThoughts": 2,
        "nextThoughtNeeded": True,
    })

    think_result_2 = await ollama_agent.call_tool("think", {
        "thought": "rs113488022 in BRAF gene",
        "thoughtNumber": 1,
        "totalThoughts": 2,
        "nextThoughtNeeded": True,
    })

    if think_result_2.isError:
        print("Think tool ollama failed:", think_result_2.content)
        #return
    if think_result_1.isError:
        print("Think tool bio mcp failed:", think_result_1.content)
        
    print("\nThink Output bio:\n", think_result_1)
    print("\nThink Output ollama:\n", think_result_2)
    

    fetch_result_1 = await bio_agent.call_tool("fetch", {
        "domain": "variant",
        "id": "rs113488022",
    })

    fetch_result_2 = await ollama_agent.call_tool("fetch", {
        "domain": "variant",
        "id": "rs113488022",
    })

    if fetch_result_1.isError:
        print("Fetch tool failed bio:", fetch_result_1.content)
        
    if fetch_result_2.isError:
        print("Fetch tool failed ollama:", fetch_result_2.content)

    print("\nFetch Output:\n", fetch_result_1)

    print("\nFetch Output:\n", fetch_result_2)


if __name__ == "__main__":
    asyncio.run(main())
