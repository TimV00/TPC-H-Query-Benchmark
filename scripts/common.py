"""Shared paths and helpers for the TPC-H benchmark scripts."""

from pathlib import Path

# Project root (this file lives in <root>/scripts/)
ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"
QUERY_DIR = ROOT / "queries"
RESULTS_DIR = ROOT / "results"

SCALES = [1, 10]
ENGINES = ["sqlite", "duckdb"]

TABLES = [
    "region", "nation", "supplier", "customer",
    "part", "partsupp", "orders", "lineitem"
]

# Each engine has its own SQL dialect (e.g. date arithmetic differs)
ENGINE_QUERY_DIRS = {
    "sqlite": QUERY_DIR,
    "duckdb": QUERY_DIR / "duckdb",
}


def db_path(sf, engine):
    """Path to the database file for a scale factor and engine."""
    return DATA_DIR / f"tpch_sf{sf}.{engine}"


def load_query(query_num, engine):
    """Read the SQL text of query `query_num` in `engine`'s dialect."""
    path = ENGINE_QUERY_DIRS[engine] / f"q{query_num}.sql"
    return path.read_text(encoding="utf-8")


def prompt_query_number(action="benchmark"):
    """Ask the user which TPC-H query to use; re-prompt until valid."""
    available = sorted(
        int(p.stem[1:]) for p in QUERY_DIR.glob("q*.sql")
        if p.stem[1:].isdigit()
    )
    if not available:
        raise SystemExit(
            f"No query files (q1.sql, q2.sql, ...) in {QUERY_DIR}"
        )

    while True:
        choice = input(
            f"Which TPC-H query would you like to {action}? "
            f"({available[0]}-{available[-1]}): "
        ).strip().lower().removeprefix("q")

        if choice.isdigit() and int(choice) in available:
            return int(choice)

        print(f"Invalid choice '{choice}'. Enter a number from "
              f"{available[0]} to {available[-1]}.")
