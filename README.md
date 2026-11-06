# NYC Green Taxi: Daily Revenue Pipeline

A small ETL pipeline that downloads the NYC **Green Taxi** trip records for January to March 2025, cleans them, and calculates the **revenue per day**.

```
download (extract) -> data/raw/*.parquet -> clean + aggregate (transform) -> data/processed/daily_revenue.csv (load)
```

Result for Jan-Mar 2025: 90 days, 3,401,753.17 total revenue, from 145,743 of 146,486 trips (743 dropped during cleaning).

## How to run

Requirements: [uv](https://docs.astral.sh/uv/getting-started/installation/) and the Python version in [`.python-version`](.python-version).

```bash
uv sync                                  # install dependencies and the package
uv run python -m data_pipeline.pipeline  # run the whole pipeline
uv run pytest                            # run the tests
```

Running the pipeline again is safe: files that are already in `data/raw/` are not downloaded a second time.

## Project structure

```
data/
  raw/                  staged downloads, never edited (ignored by git)
  processed/            daily_revenue.csv (ignored by git)
exploration_notebooks/  01_explore_green_taxi.ipynb: data exploration only, not part of the pipeline
src/data_pipeline/
  config.py             URL, months, folders, date window, column names
  extract.py            download the monthly files, read the staged files
  transform.py          clean() and daily_revenue(): pure functions, no file paths
  load.py               write the result to data/processed/
  pipeline.py           entry point, runs the stages in order
tests/
  test_transform.py     tests for the cleaning and aggregation
```

## Design decisions

**ETL, not ELT.** The data is small (about 146k rows, 3 MB per file), so we transform it in pandas before writing the result. There is no database to load raw data into, which is what ELT would need. With a warehouse and dbt, loading the raw data first and transforming it in SQL would also make sense.

**Extract is repeatable.** Each file is written to a `.part` file first and renamed only when the download is complete, so a failed download never looks like a good file. A file that already exists is skipped.

**Cleaning rules** (found in the exploration notebook, valid for any month):

| Rule | Why |
|---|---|
| Revenue = `total_amount` | It is the amount charged to the customer. See "Data quality" below. |
| A trip belongs to the day of its **pickup** | The pickup is when the trip started and is never later than the dropoff. |
| Keep trips with a pickup from 2025-01-01 up to (not including) 2025-04-01 | The monthly files contain trips from neighbouring months (e.g. 43 February trips sit in the January file). We filter on the date, not on the file name. |
| Drop rows with a missing pickup time or amount | They cannot be assigned to a day or summed. |
| Drop rows with `total_amount <= 0` | Refunds, disputes and no-charge trips, not revenue. |

Rows with a missing `payment_type` (about 4%) are kept: their amounts are valid.

`clean()` and `daily_revenue()` do not depend on a month or a file name, so they work on any month of Green Taxi data. The date window is a setting in `config.py`.

## Data quality: what we did not fix

In about 14% of the rows `total_amount` is not equal to the sum of `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount` and the surcharges. The differences come in a few fixed sizes (for example -1.00, -3.75, +2.75), which points to systematic recording differences, for instance `mta_tax` recorded as 1.50 while the total only includes 0.50, and surcharges that appear inside `extra` as well as in their own columns. These explanations come from the arithmetic only; we have not confirmed them.

We therefore:

- use **only** `total_amount` and the pickup time, and leave the component columns out of the output,
- do **not** drop rows because their parts disagree with the total,
- do **not** try to repair the component columns, since that would mean guessing.

> **In a real-world setting** we would not stop here. We would contact the people who produce or know the data, such as the taxi company, the licensing authority (the TLC) or whoever operates the data collection, because they have domain knowledge we lack. They can tell us what `extra` and `mta_tax` really contain, whether surcharges are meant to be counted twice, and which values are errors and which are legitimate. Getting this clarified and, if needed, fixed at the source matters as soon as we want to use these columns later, for example for tip or fare analysis, features for a machine learning model, or any production pipeline that others depend on. Until then, the safest choice is to rely on the one column that is consistent and to document what we did not trust.

Note that `total_amount` includes tips, and cash tips are not recorded in this data.

## Status

- [x] Step 1: Extract
- [x] Step 2: Explore
- [x] Step 3: Transform and load, with tests
- [ ] Step 4 (bonus): Prefect flow

## Review questions

*Draft answers, to be revised before handing in.*

**1. What are the steps you took to complete the project?**
Wrote a download script that stages the three monthly files, explored one file in a notebook (columns, types, missing values, date and amount ranges), wrote down the cleaning rules, then built the transform (`clean`, `daily_revenue`), the load step and an entry point, with tests for the transform. Finally, compared the row counts before and after cleaning (146,486 to 145,743).

**2. What challenges did you face?**
The monthly files are not clean month by month: they contain trips from neighbouring months, negative amounts and rows with missing payment types. The component amount columns also do not add up to `total_amount`, so the question was which column to trust and what to do with the rest (see "Data quality").

**3. What would you do differently if you had more time?**
Ask a domain expert about the inconsistent amount columns, add more tests (the loading and the download), and extend the pipeline with a Prefect flow with retries on the download.
