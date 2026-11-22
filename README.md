# TPC-H-Query-Benchmark
CS-542 Group 8 - TPC-H Benchmark

Compares **SQLite** and **DuckDB** query performance on the 22 TPC-H queries at
scale factors **SF1** and **SF10**.

## Project layout

```
TPC-H-Query-Benchmark/
├── data/                 # Generated databases (tpch_sf1.duckdb, tpch_sf1.sqlite, ...)
├── queries/
│   ├── q1.sql ... q22.sql    # TPC-H queries, SQLite dialect
│   └── duckdb/
│       └── q1.sql ... q22.sql  # Same queries, DuckDB dialect
├── results/              # Benchmark CSVs and query plans (created by the scripts)
└── scripts/
    ├── common.py             # Shared paths, scale factors and helpers
    ├── generate_tcph_db.py   # Generate TPC-H data into DuckDB
    ├── export_db_to_sqlite.py# Copy each DuckDB database to SQLite
    ├── verify_data.py        # Check row counts match between engines
    ├── benchmark.py          # Time a query on both engines
    └── explain_query.py      # Save execution plans for a query
```

## Requirements

- Python 3.9 or newer
- [DuckDB](https://duckdb.org/) Python package (tested with 2.0.0)
- SQLite comes with Python's built-in `sqlite3` module; nothing extra to install

```
pip install duckdb
```

The scripts install DuckDB's `tpch` and `sqlite` extensions the first time they
run, so an internet connection is needed on the first run.

**Disk space:** SF10 is large. Allow roughly **15 GB** free for all four
databases (SF1 and SF10, DuckDB and SQLite). The SQLite copies are much bigger
than the DuckDB ones.

## Setup

Run these from the project root, in order. Every script uses paths relative to
the project, so you can also run them from any other folder.

### 1. Generate the TPC-H data (DuckDB)

```
python scripts/generate_tcph_db.py
```

Creates `data/tpch_sf1.duckdb` and `data/tpch_sf10.duckdb` using DuckDB's
built-in `dbgen`. SF10 takes several minutes.

### 2. Export to SQLite

```
python scripts/export_db_to_sqlite.py
```

Copies each DuckDB database into `data/tpch_sf1.sqlite` and
`data/tpch_sf10.sqlite`. SF10 is the slowest step, since `lineitem` has about
60 million rows.

### 3. Verify the data

```
python scripts/verify_data.py
```

Prints the row count of each table in both engines. Every line should end in
`OK`.

Steps 1 and 2 skip any database that already exists. To rebuild one, delete its
file from `data/` and run the step again.

## Running the benchmark

```
python scripts/benchmark.py
```

You'll be asked which query to run (enter `1`–`22`, or `q6` style). The query
is run on SQLite and DuckDB at SF1 and SF10: one warm-up run, then 5 timed
runs. Results are saved to `results/q<N>_baseline.csv` with the median, minimum
and maximum time for each engine and scale factor.

DuckDB is limited to a single thread (`SET threads = 1`) so that it is compared
fairly with single-threaded SQLite.

## Viewing execution plans

```
python scripts/explain_query.py
```

Asks which query to explain, then saves each engine's plan at each scale factor
to `results/plans/`, e.g. `sqlite_sf1_q6.txt` and `duckdb_sf1_q6.txt`.

## Notes

- **Two query dialects.** SQLite and DuckDB write date arithmetic differently
  (`date('1997-01-01', '+1 years')` vs `date '1997-01-01' + interval '1 years'`),
  so each engine has its own copy of every query. If you edit a query, update
  both `queries/qN.sql` and `queries/duckdb/qN.sql`. All 22 queries were
  checked to return the same results on both engines.
- **Decimal columns in SQLite.** The export stores TPC-H's decimal columns
  (prices, quantities, discounts, balances) as SQLite `REAL`. Without this they
  would be stored as text and numeric filters such as `l_quantity < 24` would
  give wrong results.
- **Changing scale factors.** Edit `SCALES` in `scripts/common.py`, then
  re-run the setup steps.
