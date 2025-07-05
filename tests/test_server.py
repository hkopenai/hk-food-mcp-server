"""
Module for testing the MCP server creation and functionality.

This module contains unit tests to verify the correct setup and behavior of the MCP server.
"""

import unittest
from unittest.mock import patch, Mock
from hkopenai.hk_food_mcp_server.server import create_mcp_server


class TestApp(unittest.TestCase):
    """
    Test class for verifying MCP server creation and tool integration.
    
    This class contains test cases to ensure the server is properly initialized
    and that tools are correctly registered and functional.
    """
    @patch("hkopenai.hk_food_mcp_server.server.FastMCP")
    @patch(
        "hkopenai.hk_food_mcp_server.server.tool_wholesale_prices_of_major_fresh_food"
    )
    def test_create_mcp_server(
        self, mock_tool_wholesale_prices_of_major_fresh_food, mock_fastmcp
    ):
        """
        Test the creation of the MCP server and tool registration.
        
        Args:
            mock_tool_wholesale_prices_of_major_fresh_food: Mock object for the wholesale prices tool.
            mock_fastmcp: Mock object for the FastMCP class.
        """
        # Setup mocks
        mock_server = Mock()

        # Configure mock_server.tool to return a mock that acts as the decorator
        # This mock will then be called with the function to be decorated
        mock_server.tool.return_value = Mock()
        mock_fastmcp.return_value = mock_server

        # Test server creation
        server = create_mcp_server()

        # Verify server creation
        mock_fastmcp.assert_called_once()
        self.assertEqual(server, mock_server)

        # Verify that the tool decorator was called for each tool function
        self.assertEqual(mock_server.tool.call_count, 1)

        # Get all decorated functions
        decorated_funcs = {
            call.args[0].__name__: call.args[0]
            for call in mock_server.tool.return_value.call_args_list
        }
        self.assertEqual(len(decorated_funcs), 1)

        # Call each decorated function and verify that the correct underlying function is called

        decorated_funcs["get_wholesale_prices"](
            start_date="01/01/2023", end_date="31/01/2023", language="en"
        )
        mock_tool_wholesale_prices_of_major_fresh_food.get_wholesale_prices.assert_called_once_with(
            "01/01/2023", "31/01/2023", "en"
        )


if __name__ == "__main__":
    unittest.main()
