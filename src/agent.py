#!/usr/bin/env python3
import sys
import os
from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams, SseConnectionParams
from mcp import StdioServerParameters

# Get configuration from environment variables
MODEL_NAME = os.getenv('MODEL_NAME', 'llama3.2:3b')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
MCP_URL = os.getenv('MCP_URL', None)
MCP_LOCAL_PATH = os.getenv('MCP_LOCAL_PATH', None)

# Configure MCP connection based on environment
if MCP_URL:
    # Use HTTP/SSE connection for Docker deployment
    mcp_connection = SseConnectionParams(url=MCP_URL)
elif MCP_LOCAL_PATH:
    # Use stdio connection for local development
    mcp_connection = StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[MCP_LOCAL_PATH],
        ),
    )
else:
    raise ValueError("Either MCP_URL or MCP_LOCAL_PATH must be set")

root_agent = Agent(
    model=LiteLlm(
        model=f'ollama_chat/{MODEL_NAME}',
        api_base=OLLAMA_HOST,
        max_tokens=50,
        temperature=0.0
    ),
    name="system_administration",
    description="File system administrator",
    instruction="""You are a file system assistant. Answer in ONE short sentence.

When user asks about a file:
- Call the tool ONCE
- Say the answer in ONE sentence
- DONE

Example: User: "what is in test.txt?"
You: Call get_file_content("test.txt"), get "This is a test file", then say: "It contains: This is a test file" DONE.""",
    tools=[
        McpToolset(connection_params=mcp_connection)
    ]
)
