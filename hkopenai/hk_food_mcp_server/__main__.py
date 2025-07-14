"""
Main entry point for the HK OpenAI Food MCP Server.

This module serves as the starting point for running the server application.
"""

from hkopenai_common.cli_utils import cli_main
from .server import server

if __name__ == "__main__":
    cli_main(server, "HK Food MCP Server")
