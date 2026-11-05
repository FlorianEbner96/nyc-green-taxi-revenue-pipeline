"""Extract stage: download Green Taxi trip files into the local staging directory."""

from pathlib import Path

import requests

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
YEAR = 2025
MONTHS = [1, 2, 3]
RAW_DIR = Path("data/raw")


def build_url(year: int, month: int) -> str:
    return f"{BASE_URL}/green_tripdata_{year}-{month:02d}.parquet"


def download_month(year: int, month: int, target_dir: Path = RAW_DIR) -> Path:
    """Download one month. Skips the download if the file already exists (idempotent)."""
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"green_tripdata_{year}-{month:02d}.parquet"
    if target.exists():
        print(f"skip   {target} (already staged)")
        return target

    # Write to a temp name first so a failed download never leaves a half-written file.
    tmp = target.with_suffix(".part")
    with requests.get(build_url(year, month), stream=True, timeout=60) as response:
        response.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
    tmp.rename(target)
    print(f"saved  {target}")
    return target


def extract(year: int = YEAR, months: list[int] = MONTHS) -> list[Path]:
    return [download_month(year, m) for m in months]


if __name__ == "__main__":
    extract()
