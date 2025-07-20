"""
Module for testing the wholesale prices tool functionality.

This module contains unit tests to verify the correct behavior of functions related
to fetching and processing wholesale prices data.
"""

import unittest
from unittest.mock import patch, MagicMock
from hkopenai.hk_food_mcp_server.tools.wholesale_prices_of_major_fresh_food import (
    _get_wholesale_prices,
    register,
)


class TestWholesalePrices(unittest.TestCase):
    """
    Test class for verifying the functionality of wholesale prices tools.

    This class contains test cases to ensure the correct fetching, filtering,
    and processing of wholesale prices data.
    """

    CSV_DATA = [
        {
            "ENGLISH CATEGORY": "Average Wholesale Prices",
            "中文類別": "平均批發價",
            "FRESH FOOD CATEGORY": "Livestock / Poultry",
            "鮮活食品類別": "牲畜及家禽",
            "FOOD TYPE": "Live pig",
            "食品種類": "活豬",
            "PRICE (THIS MORNING)": "12.44",
            "價錢 (今早)": "12.44",
            "UNIT": "($ / Catty)",
            "單位": "(元／斤)",
            "INTAKE DATE": "(Yesterday)",
            "來貨日期": "(昨日)",
            "SOURCE OF SUPPLY (IF APPROPRIATE)": "-",
            "供應來源 (如適用)": "-",
            "PROVIDED BY": "Slaughterhouses",
            "資料來源": "屠房",
            "Last Revision Date": "29/05/2025",
            "最後更新日期": "29/05/2025",
        },
        {
            "ENGLISH CATEGORY": "Average Wholesale Prices",
            "中文類別": "平均批發價",
            "FRESH FOOD CATEGORY": "Livestock / Poultry",
            "鮮活食品類別": "牲畜及家禽",
            "FOOD TYPE": "Live cattle",
            "食品種類": "活牛",
            "PRICE (THIS MORNING)": "是日沒有供應",
            "價錢 (今早)": "是日沒有供應",
            "UNIT": "($ / Catty)",
            "單位": "(元／斤)",
            "INTAKE DATE": "(Yesterday)",
            "來貨日期": "(昨日)",
            "SOURCE OF SUPPLY (IF APPROPRIATE)": "-",
            "供應來源 (如適用)": "-",
            "PROVIDED BY": "Ng Fung Hong",
            "資料來源": "五豐行",
            "Last Revision Date": "30/05/2025",
            "最後更新日期": "30/05/2025",
        },
        {
            "ENGLISH CATEGORY": "Average Wholesale Prices",
            "中文類別": "平均批發價",
            "FRESH FOOD CATEGORY": "Marine fish",
            "鮮活食品類別": "鹹水魚",
            "FOOD TYPE": "Golden thread",
            "食品種類": "紅衫",
            "PRICE (THIS MORNING)": "80",
            "價錢 (今早)": "80",
            "UNIT": "($ / Catty)",
            "單位": "(元／斤)",
            "INTAKE DATE": "(Yesterday)",
            "來貨日期": "(昨日)",
            "SOURCE OF SUPPLY (IF APPROPRIATE)": "-",
            "供應來源 (如適用)": "-",
            "PROVIDED BY": "Major wholesalers",
            "資料來源": "主要批發商",
            "Last Revision Date": "01/06/2025",
            "最後更新日期": "01/06/2025",
        },
    ]

    def test_get_wholesale_prices_english(self):
        """
        Test getting wholesale prices data in English.

        Verifies that the data is correctly formatted for English output.
        """
        with patch(
            "hkopenai.hk_food_mcp_server.tools.wholesale_prices_of_major_fresh_food.fetch_csv_from_url"
        ) as mock_fetch_csv_from_url:
            mock_fetch_csv_from_url.return_value = self.CSV_DATA
            result = _get_wholesale_prices(language="zh")
            result = _get_wholesale_prices(language="en")
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0]["category"], "Average Wholesale Prices")
            self.assertEqual(result[1]["food_type"], "Live cattle")
            self.assertEqual(result[2]["price"], "80")

    def test_get_wholesale_prices_chinese(self):
        """
        Test getting wholesale prices data in Chinese.

        Verifies that the data is correctly formatted for Chinese output.
        """
        with patch(
            "hkopenai.hk_food_mcp_server.tools.wholesale_prices_of_major_fresh_food.fetch_csv_from_url"
        ) as mock_fetch_csv_from_url:
            mock_fetch_csv_from_url.return_value = self.CSV_DATA
            result = _get_wholesale_prices(language="zh")
            self.assertEqual(len(result), 3)
            self.assertEqual(result[0]["類別"], "平均批發價")
            self.assertEqual(result[1]["食品種類"], "活牛")
            self.assertEqual(result[2]["價錢"], "80")

    def test_get_wholesale_prices_with_dates(self):
        """
        Test getting wholesale prices data with specific date range.

        Verifies that the data is correctly filtered by the specified dates.
        """
        with patch(
            "hkopenai.hk_food_mcp_server.tools.wholesale_prices_of_major_fresh_food.fetch_csv_from_url"
        ) as mock_fetch_csv_from_url:
            mock_fetch_csv_from_url.return_value = self.CSV_DATA
            result = _get_wholesale_prices(
                start_date="30/05/2025", end_date="30/05/2025"
            )
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["food_type"], "Live cattle")

    def test_register_tool(self):
        """
        Test the registration of the get_wholesale_prices tool.

        This test verifies that the register function correctly registers the tool
        with the FastMCP server and that the registered tool calls the underlying
        _get_wholesale_prices function.
        """
        mock_mcp = MagicMock()

        # Call the register function
        register(mock_mcp)

        # Verify that mcp.tool was called with the correct description
        mock_mcp.tool.assert_called_once_with(
            description="Daily wholesale prices of major fresh food in Hong Kong from Agriculture, Fisheries and Conservation Department"
        )

        # Get the mock that represents the decorator returned by mcp.tool
        mock_decorator = mock_mcp.tool.return_value

        # Verify that the mock decorator was called once (i.e., the function was decorated)
        mock_decorator.assert_called_once()

        # The decorated function is the first argument of the first call to the mock_decorator
        decorated_function = mock_decorator.call_args[0][0]

        # Verify the name of the decorated function
        self.assertEqual(decorated_function.__name__, "get_wholesale_prices")

        # Call the decorated function and verify it calls _get_wholesale_prices
        # Call the decorated function and verify it calls _get_wholesale_prices
        with patch(
            "hkopenai.hk_food_mcp_server.tools.wholesale_prices_of_major_fresh_food._get_wholesale_prices"
        ) as mock_get_wholesale_prices:
            decorated_function(
                start_date="01/01/2023", end_date="31/01/2023", language="en"
            )
            mock_get_wholesale_prices.assert_called_once_with(
                "01/01/2023", "31/01/2023", "en"
            )


if __name__ == "__main__":
    unittest.main()
