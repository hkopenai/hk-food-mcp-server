"""
Module for testing the wholesale prices tool functionality.

This module contains unit tests to verify the correct behavior of functions related
to fetching and processing wholesale prices data.
"""

import unittest
from unittest.mock import patch
from hkopenai.hk_food_mcp_server.tool_wholesale_prices_of_major_fresh_food import (
    fetch_wholesale_prices,
    filter_by_date_range,
    get_wholesale_prices,
)


class TestWholesalePrices(unittest.TestCase):
    """
    Test class for verifying the functionality of wholesale prices tools.
    
    This class contains test cases to ensure the correct fetching, filtering,
    and processing of wholesale prices data.
    """
    CSV_DATA = """ENGLISH CATEGORY,中文類別,FRESH FOOD CATEGORY,鮮活食品類別,FOOD TYPE,食品種類,PRICE (THIS MORNING),價錢 (今早),UNIT,單位,INTAKE DATE,來貨日期,SOURCE OF SUPPLY (IF APPROPRIATE),供應來源 (如適用),PROVIDED BY,資料來源,Last Revision Date,最後更新日期
Average Wholesale Prices,平均批發價,Livestock / Poultry,牲畜及家禽,Live pig,活豬,12.44,12.44,($ / Catty),(元／斤),(Yesterday),(昨日),-,-,Slaughterhouses,屠房,29/05/2025,29/05/2025
Average Wholesale Prices,平均批發價,Livestock / Poultry,牲畜及家禽,Live cattle,活牛,是日沒有供應,是日沒有供應,($ / Catty),(元／斤),(Yesterday),(昨日),-,-,Ng Fung Hong,五豐行,30/05/2025,30/05/2025
ENGLISH CATEGORY,中文類別,FRESH FOOD CATEGORY,鮮活食品類別,FOOD TYPE,食品種類,PRICE (THIS MORNING),價錢 (今早),UNIT,單位,INTAKE DATE,來貨日期,SOURCE OF SUPPLY (IF APPROPRIATE),供應來源 (如適用),PROVIDED BY,資料來源,Last Revision Date,最後更新日期
Average Wholesale Prices,平均批發價,Marine fish,鹹水魚,Golden thread,紅衫,80,80,($ / Catty),(元／斤),(Yesterday),(昨日),-,-,Major wholesalers,主要批發商,01/06/2025,01/06/2025
"""

    def setUp(self):
        """
        Set up test environment before each test method.
        
        Configures mock responses for HTTP requests to simulate data retrieval.
        """
        self.mock_requests = patch("requests.get").start()
        mock_response = self.mock_requests.return_value
        mock_response.text = self.CSV_DATA
        self.addCleanup(patch.stopall)

    def test_fetch_wholesale_prices(self):
        """
        Test fetching wholesale prices data.
        
        Verifies that the data is correctly retrieved and parsed from the mock response.
        """
        result = fetch_wholesale_prices()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["ENGLISH CATEGORY"], "Average Wholesale Prices")
        self.assertEqual(result[1]["FOOD TYPE"], "Live cattle")
        self.assertEqual(result[2]["PRICE (THIS MORNING)"], "80")

    def test_filter_by_date_range(self):
        """
        Test filtering wholesale prices data by date range.
        
        Verifies that the data is correctly filtered based on start and end dates.
        """
        data = fetch_wholesale_prices()

        # No date range
        filtered = filter_by_date_range(data, None, None)
        self.assertEqual(len(filtered), 3)

        # Start date only
        filtered = filter_by_date_range(data, "30/05/2025", None)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["FOOD TYPE"], "Live cattle")

        # End date only
        filtered = filter_by_date_range(data, None, "30/05/2025")
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[1]["FOOD TYPE"], "Live cattle")

        # Both dates
        filtered = filter_by_date_range(data, "29/05/2025", "30/05/2025")
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0]["FOOD TYPE"], "Live pig")

    def test_get_wholesale_prices_english(self):
        """
        Test getting wholesale prices data in English.
        
        Verifies that the data is correctly formatted for English output.
        """
        result = get_wholesale_prices(language="en")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["category"], "Average Wholesale Prices")
        self.assertEqual(result[1]["food_type"], "Live cattle")
        self.assertEqual(result[2]["price"], "80")

    def test_get_wholesale_prices_chinese(self):
        """
        Test getting wholesale prices data in Chinese.
        
        Verifies that the data is correctly formatted for Chinese output.
        """
        result = get_wholesale_prices(language="zh")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["類別"], "平均批發價")
        self.assertEqual(result[1]["食品種類"], "活牛")
        self.assertEqual(result[2]["價錢"], "80")

    def test_get_wholesale_prices_with_dates(self):
        """
        Test getting wholesale prices data with specific date range.
        
        Verifies that the data is correctly filtered by the specified dates.
        """
        result = get_wholesale_prices(start_date="30/05/2025", end_date="30/05/2025")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["food_type"], "Live cattle")


if __name__ == "__main__":
    unittest.main()
