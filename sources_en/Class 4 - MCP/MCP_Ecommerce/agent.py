# ecommerce_mcp_client/agent.py
"""
ADK Agent that consumes the e-commerce MCP server.
"""

import os
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.genai import types
from dotenv import load_dotenv
load_dotenv()

# IMPORTANT: Replace this with the absolute path to your MCP server
# For example: "/home/user/projects/ecommerce_mcp_server.py"
PATH_TO_MCP_SERVER = os.path.abspath("MCP_Ecommerce/ecommerce_mcp_server.py")

# Verify that the file exists
if not os.path.exists(PATH_TO_MCP_SERVER):
    print(f"⚠️ WARNING: MCP server not found at: {PATH_TO_MCP_SERVER}")
    print("Please update PATH_TO_MCP_SERVER with the correct path.")

# Create the agent with MCP server tools
root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='ecommerce_mcp_assistant',
    instruction=(
        "You are a professional shopping assistant that helps users with:\n"
        "1. 🔍 Search products in our catalog\n"
        "2. 🛒 Add products to cart\n"
        "3. 💰 Apply discount codes (WELCOME10, SAVE20, VIP30)\n"
        "4. 📊 View cart and calculate totals\n"
        "5. 🎯 Recommend popular products\n\n"
        "Special features:\n"
        "- Intelligent product search\n"
        "- Automatic tax calculation (8%)\n"
        "- Free shipping on orders over $100\n"
        "- Personalized recommendations\n\n"
        "Be friendly and proactive. If a user searches for something that doesn't exist exactly, "
        "suggest alternatives. Mention when they're close to free shipping."
    ),
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command='python3',  # or 'python' depending on your system
                args=[PATH_TO_MCP_SERVER],
                # Optional: pass environment variables if needed
                env={
                    "PYTHONUNBUFFERED": "1"  # To see logs in real time
                }
            ),
            # Optional: filter which tools to expose from the MCP server
            # tool_filter=['search_product', 'add_to_cart', 'view_cart']
        )
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=800,
        top_p=0.9
    )
)