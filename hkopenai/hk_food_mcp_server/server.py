"""
Module for creating and running the HK OpenAI Food MCP Server.

This module provides functionality to configure and start the MCP server with tools
for accessing food-related data in Hong Kong.
"""

from typing import Dict, List, Annotated, Optional
from fastmcp import FastMCP
from pydantic import Field
from hkopenai.hk_food_mcp_server import tool_wholesale_prices_of_major_fresh_food


def create_mcp_server():
    """Create and configure the MCP server"""
    mcp = FastMCP(name="HK OpenAI food Server")

    @mcp.tool(
        description="Daily wholesale prices of major fresh food in Hong Kong from Agriculture, Fisheries and Conservation Department"
    )
    def get_wholesale_prices(
        start_date: Annotated[
            Optional[str], Field(description="Start date in DD/MM/YYYY format")
        ] = None,
        end_date: Annotated[
            Optional[str], Field(description="End date in DD/MM/YYYY format")
        ] = None,
        language: Annotated[
            str, Field(description="Language for output (en/zh)", pattern="^(en|zh)$")
        ] = "en",
    ) -> List[Dict]:
        return tool_wholesale_prices_of_major_fresh_food.get_wholesale_prices(
            start_date, end_date, language
        )

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
