"""
Module for fetching and processing wholesale prices of major fresh food in Hong Kong.

This module provides functionality to retrieve data from the Agriculture, Fisheries 
and Conservation Department (AFCD) website and filter it based on date range and language.
"""

import csv
import requests
from io import StringIO
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import Field
from typing_extensions import Annotated

WHOLESALE_PRICES_URL = (
    "https://www.afcd.gov.hk/english/agriculture/agr_fresh/files/Wholesale_Prices.csv"
)


def fetch_wholesale_prices() -> List[Dict]:
    """Fetch wholesale prices data from AFCD website"""
    response = requests.get(WHOLESALE_PRICES_URL)
    csv_data = StringIO(response.text)

    # Read first line to get headers
    headers = csv_data.readline().strip().split(",")

    # Filter out any rows that match the header pattern
    filtered_rows = []
    for line in csv_data:
        if not line.strip() or line.strip().split(",") == headers:
            continue  # Skip empty lines or header duplicates
        filtered_rows.append(line)

    # Create DictReader from filtered data
    reader = csv.DictReader(StringIO("".join(filtered_rows)), fieldnames=headers)
    return list(reader)


def filter_by_date_range(
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
    """Get daily wholesale prices of major fresh food in Hong Kong

    Args:
        start_date: Optional start date for filtering (DD/MM/YYYY)
        end_date: Optional end date for filtering (DD/MM/YYYY)
        language: Output language (en for English, zh for Chinese)

    Returns:
        List of wholesale price records with selected language fields
    """
    data = fetch_wholesale_prices()
    filtered_data = filter_by_date_range(data, start_date, end_date)

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
