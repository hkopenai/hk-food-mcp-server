"""
Module for fetching and processing wholesale prices of major fresh food in Hong Kong.

This module provides functionality to retrieve data from the Agriculture, Fisheries
and Conservation Department (AFCD) website and filter it based on date range and language.
"""

from typing import List, Dict, Optional
from datetime import datetime
from pydantic import Field
from typing_extensions import Annotated
from hkopenai_common.csv_utils import fetch_csv_from_url


WHOLESALE_PRICES_URL = (
    "https://www.afcd.gov.hk/english/agriculture/agr_fresh/files/Wholesale_Prices.csv"
)


def register(mcp):
    """Registers the wholesale prices tool with the FastMCP server."""

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
    ) -> List[Dict] | Dict:
        """Get daily wholesale prices of major fresh food in Hong Kong

        Args:
            start_date: Optional start date for filtering (DD/MM/YYYY)
            end_date: Optional end date for filtering (DD/MM/YYYY)
            language: Output language (en for English, zh for Chinese)

        Returns:
            List of wholesale price records with selected language fields
        """
        return _get_wholesale_prices(start_date, end_date, language)


def _filter_by_date_range(
    data: List[Dict], start_date: Optional[str], end_date: Optional[str]
) -> List[Dict]:
    """Filter data by date range"""
    if not start_date and not end_date:
        return data

    filtered = []
    for row in data:
        row_date = datetime.strptime(row["Last Revision Date"], "%d/%m/%Y")

        if start_date:
            start = datetime.strptime(start_date, "%d/%m/%Y")
            if row_date < start:
                continue

        if end_date:
            end = datetime.strptime(end_date, "%d/%m/%Y")
            if row_date > end:
                continue

        filtered.append(row)
    return filtered


def _get_wholesale_prices(
    start_date: Annotated[
        Optional[str], Field(description="Start date in DD/MM/YYYY format")
    ] = None,
    end_date: Annotated[
        Optional[str], Field(description="End date in DD/MM/YYYY format")
    ] = None,
    language: Annotated[
        str, Field(description="Language for output (en/zh)", pattern="^(en|zh)$")
    ] = "en",
) -> List[Dict] | Dict:
    """Get daily wholesale prices of major fresh food in Hong Kong

    Args:
        start_date: Optional start date for filtering (DD/MM/YYYY)
        end_date: Optional end date for filtering (DD/MM/YYYY)
        language: Output language (en for English, zh for Chinese)

    Returns:
        List of wholesale price records with selected language fields
    """
    data = fetch_csv_from_url(WHOLESALE_PRICES_URL)
    if "error" in data:
        return {"type": "Error", "error": data["error"]}
    filtered_data = _filter_by_date_range(data, start_date, end_date)

    # Select appropriate columns based on language
    if language == "zh":
        return [
            {
                "類別": row["中文類別"],
                "鮮活食品類別": row["鮮活食品類別"],
                "食品種類": row["食品種類"],
                "價錢": row["價錢 (今早)"],
                "單位": row["單位"],
                "來貨日期": row["來貨日期"],
                "供應來源": row["供應來源 (如適用)"],
                "資料來源": row["資料來源"],
                "最後更新日期": row["最後更新日期"],
            }
            for row in filtered_data
        ]
    else:  # English
        return [
            {
                "category": row["ENGLISH CATEGORY"],
                "fresh_food_category": row["FRESH FOOD CATEGORY"],
                "food_type": row["FOOD TYPE"],
                "price": row["PRICE (THIS MORNING)"],
                "unit": row["UNIT"],
                "intake_date": row["INTAKE DATE"],
                "source": row["SOURCE OF SUPPLY (IF APPROPRIATE)"],
                "provided_by": row["PROVIDED BY"],
                "last_revision_date": row["Last Revision Date"],
            }
            for row in filtered_data
        ]
