"""Entry point: run extract -> transform -> load in order.

    uv run python -m data_pipeline.pipeline
"""

from data_pipeline.extract import extract, read_staged
from data_pipeline.load import write_daily_revenue
from data_pipeline.transform import clean, daily_revenue


def run() -> None:
    extract()

    raw = read_staged()
    cleaned = clean(raw)
    print(f"rows before cleaning: {len(raw):>8}")
    print(f"rows after cleaning:  {len(cleaned):>8}  ({len(raw) - len(cleaned)} dropped)")

    result = daily_revenue(cleaned)
    path = write_daily_revenue(result)
    print(f"wrote {len(result)} days to {path} (total revenue {result['revenue'].sum():,.2f})")


if __name__ == "__main__":
    run()
