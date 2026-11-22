
import sqlite3
import duckdb

from common import SCALES, TABLES, db_path

for sf in SCALES:
    print(f"\n===== SF{sf} =====")

    sqlite = sqlite3.connect(
        f"{db_path(sf, 'sqlite').as_uri()}?mode=ro",
        uri=True
    )
    duck = duckdb.connect(
        str(db_path(sf, "duckdb")),
        read_only=True
    )

    for table in TABLES:
        sqlite_count = sqlite.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        duck_count = duck.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        status = "OK" if sqlite_count == duck_count else "MISMATCH"

        print(
            f"{table:10} SQLite={sqlite_count:>12,} "
            f"DuckDB={duck_count:>12,} {status}"
        )

    sqlite.close()
    duck.close()
