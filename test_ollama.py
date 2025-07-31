#!/usr/bin/env python3
"""
Test script to debug Ollama integration.
"""

import asyncio
import httpx
import traceback

async def test_ollama():
    """Test direct Ollama API call."""
    
    client = httpx.AsyncClient(
        base_url="http://localhost:11434",
        timeout=httpx.Timeout(180.0)  # 180 second timeout
    )
    
    try:
        # Test connection
        response = await client.get("/api/tags")
        print(f"Tags response: {response.status_code}")
        print(f"Available models: {response.json()}")
        
        # Test generation
        response = await client.post("/api/generate", json={
            "model": "llama3.1:latest",
            "prompt": "What is the gut-brain axis in Parkinson's disease?",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 500
            }
        })
        
        print(f"Generate response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', 'No response')}")
        else:
            print(f"Error: {response.text}")
    
    except httpx.RequestError as e:
        print(f"An error occurred while requesting from {e.request.url!r}.")
    except httpx.HTTPStatusError as e: 
        print(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
    
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_ollama())
