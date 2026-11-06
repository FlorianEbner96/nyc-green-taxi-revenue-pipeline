"""Load stage: write the result to the output location."""

from pathlib import Path

import pandas as pd

from data_pipeline.config import OUTPUT_FILE


def write_daily_revenue(df: pd.DataFrame, path: Path = OUTPUT_FILE) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path
