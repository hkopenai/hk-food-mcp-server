"""
Module for creating and running the HK OpenAI Food MCP Server.

This module provides functionality to configure and start the MCP server with tools
for accessing food-related data in Hong Kong.
"""

from fastmcp import FastMCP
from hkopenai.hk_food_mcp_server import tool_wholesale_prices_of_major_fresh_food


def create_mcp_server():
    """Create and configure the MCP server"""
    mcp = FastMCP(name="HK OpenAI food Server")

    tool_wholesale_prices_of_major_fresh_food.register(mcp)

    return mcp


def server(host: str, port: int, sse: bool):
    """
    Main function to run the MCP Server.

    Args:
        args: Command line arguments passed to the function.
    """
    server = create_mcp_server()

    if sse:
        server.run(transport="streamable-http", host=host, port=port)
        print(f"MCP Server running in SSE mode on port {port}, bound to {host}")
    else:
        server.run()
        print("MCP Server running in stdio mode")
