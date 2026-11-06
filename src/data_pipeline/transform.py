"""Transform stage: clean trips and aggregate revenue per day.

Both functions work on any month of Green Taxi data: nothing here is tied to a
file name or a specific month.
"""

import pandas as pd

from data_pipeline.config import PICKUP_COL, REVENUE_COL, WINDOW_END, WINDOW_START


def clean(df: pd.DataFrame, start: str = WINDOW_START, end: str = WINDOW_END) -> pd.DataFrame:
    """Keep trips with a known pickup time and a positive amount, picked up in [start, end)."""
    df = df[[PICKUP_COL, REVENUE_COL]].dropna()
    in_window = (df[PICKUP_COL] >= start) & (df[PICKUP_COL] < end)
    return df[in_window & (df[REVENUE_COL] > 0)]


def daily_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Count the trips and sum the revenue per pickup day."""
    out = (
        df.groupby(df[PICKUP_COL].dt.normalize())[REVENUE_COL]
        .agg(trip_count="size", revenue="sum")
        .rename_axis("date")
        .reset_index()
    )
    out["revenue"] = out["revenue"].round(2)
    return out
