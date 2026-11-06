import pandas as pd

from data_pipeline.transform import clean, daily_revenue


def make_trips():
    return pd.DataFrame(
        {
            "lpep_pickup_datetime": pd.to_datetime(
                [
                    "2025-01-01 08:00",  # good
                    "2025-01-01 20:00",  # good, same day
                    "2025-01-02 09:00",  # good
                    "2025-01-02 10:00",  # negative amount -> dropped
                    "2024-12-31 23:00",  # before the window -> dropped
                    "2025-04-01 00:00",  # after the window (end is exclusive) -> dropped
                    None,  # missing pickup -> dropped
                    "2025-01-03 12:00",  # missing amount -> dropped
                ]
            ),
            "total_amount": [10.0, 5.5, 7.0, -3.0, 20.0, 20.0, 20.0, None],
        }
    )


def test_clean_drops_invalid_rows():
    cleaned = clean(make_trips(), start="2025-01-01", end="2025-04-01")
    assert len(cleaned) == 3
    assert (cleaned["total_amount"] > 0).all()


def test_daily_revenue_sums_per_day():
    result = daily_revenue(clean(make_trips(), start="2025-01-01", end="2025-04-01"))
    assert result["revenue"].tolist() == [15.5, 7.0]
    assert result["trip_count"].tolist() == [2, 1]
    assert result["date"].dt.strftime("%Y-%m-%d").tolist() == ["2025-01-01", "2025-01-02"]
