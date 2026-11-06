"""Prefect version of the pipeline: the same stage functions, run as tasks inside a flow.

    uv run python -m data_pipeline.flow
"""

from pathlib import Path

import pandas as pd
from prefect import flow, get_run_logger, task

from data_pipeline.config import MONTHS, YEAR
from data_pipeline.extract import download_month, read_staged
from data_pipeline.load import write_daily_revenue
from data_pipeline.transform import clean, daily_revenue


# Only the download talks to the outside world, so only it gets retries.
@task(retries=3, retry_delay_seconds=10)
def download_month_task(year: int, month: int) -> Path:
    return download_month(year, month)


@task
def read_staged_task() -> pd.DataFrame:
    return read_staged()


@task
def clean_task(raw: pd.DataFrame) -> pd.DataFrame:
    cleaned = clean(raw)
    logger = get_run_logger()
    logger.info("rows before cleaning: %d", len(raw))
    logger.info("rows after cleaning: %d (%d dropped)", len(cleaned), len(raw) - len(cleaned))
    return cleaned


@task
def daily_revenue_task(cleaned: pd.DataFrame) -> pd.DataFrame:
    return daily_revenue(cleaned)


@task
def write_task(result: pd.DataFrame) -> Path:
    path = write_daily_revenue(result)
    get_run_logger().info(
        "wrote %d days to %s (total revenue %.2f)", len(result), path, result["revenue"].sum()
    )
    return path


@flow(name="green-taxi-daily-revenue")
def green_taxi_flow(year: int = YEAR, months: list[int] = MONTHS) -> Path:
    for month in months:
        download_month_task(year, month)
    raw = read_staged_task()
    cleaned = clean_task(raw)
    result = daily_revenue_task(cleaned)
    return write_task(result)


if __name__ == "__main__":
    green_taxi_flow()
