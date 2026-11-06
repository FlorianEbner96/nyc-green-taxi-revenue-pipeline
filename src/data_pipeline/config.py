"""Settings shared by all pipeline stages."""

from pathlib import Path

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
YEAR = 2025
MONTHS = [1, 2, 3]

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
OUTPUT_FILE = PROCESSED_DIR / "daily_revenue.csv"

# Trips are kept if the pickup falls in [WINDOW_START, WINDOW_END).
# Month files contain a few trips from neighbouring months, so we filter on
# the pickup time and not on the file name.
WINDOW_START = "2025-01-01"
WINDOW_END = "2025-04-01"

PICKUP_COL = "lpep_pickup_datetime"
REVENUE_COL = "total_amount"
