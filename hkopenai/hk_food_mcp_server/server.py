"""
Module for creating and running the HK OpenAI Food MCP Server.

This module provides functionality to configure and start the MCP server with tools
for accessing food-related data in Hong Kong.
"""

import argparse
from fastmcp import FastMCP
from hkopenai.hk_food_mcp_server import tool_wholesale_prices_of_major_fresh_food
from typing import Dict, List, Annotated, Optional
from pydantic import Field


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


def main():
    """
    Main function to run the MCP Server.
    
    Parses command line arguments to determine the mode of operation (SSE or stdio)
    and starts the server accordingly.
    """
    parser = argparse.ArgumentParser(description="MCP Server")
    parser.add_argument(
        "-s", "--sse", action="store_true", help="Run in SSE mode instead of stdio"
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host to bind the server to"
    )
    args = parser.parse_args()

    server = create_mcp_server()

    if args.sse:
        server.run(transport="streamable-http", host=args.host)
        print(f"MCP Server running in SSE mode on port 8000, bound to {args.host}")
    else:
        server.run()
        print("MCP Server running in stdio mode")


if __name__ == "__main__":
    main()
