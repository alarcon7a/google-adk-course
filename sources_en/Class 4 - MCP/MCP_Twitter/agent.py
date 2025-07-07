# ./adk_agent_samples/mcp_agent/agent.py
import asyncio
from dotenv import load_dotenv
import os # Required for path operations
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters, StdioConnectionParams
# Load environment variables from .env file in the parent directory
# Place this near the top, before using env vars like API keys
load_dotenv()


root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='filesystem_assistant_agent',
    instruction='You are an assistant that helps me query and post on Twitter',
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command='npx',
                args=["-y",    # Arguments for the command
                      "@enescinar/twitter-mcp",
                      ],
                env={
                    "API_KEY": os.getenv("TW_API_KEY"),
                    "API_SECRET_KEY": os.getenv("TW_API_SECRET_KEY"),
                    "ACCESS_TOKEN": os.getenv("TW_ACCESS_TOKEN"),
                    "ACCESS_TOKEN_SECRET": os.getenv("TW_ACCESS_TOKEN_SECRET"),
                }
            ),
            timeout=60
            ),
            # Optional: Filter which tools from the MCP server are exposed
            # tool_filter=['list_directory', 'read_file']
        )
    ],
)