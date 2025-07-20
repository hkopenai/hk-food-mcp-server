"""
Module for creating and running the HK OpenAI Food MCP Server.

This module provides functionality to configure and start the MCP server with tools
for accessing food-related data in Hong Kong.
"""

from fastmcp import FastMCP
from .tools import wholesale_prices_of_major_fresh_food


def server():
    """Create and configure the MCP server"""
    mcp = FastMCP(name="HK OpenAI food Server")

    wholesale_prices_of_major_fresh_food.register(mcp)

    return mcp
