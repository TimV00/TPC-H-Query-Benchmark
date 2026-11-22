
import duckdb
import time

from common import SCALES, TABLES, db_path


def sqlite_select_list(con, table):
    """Build a SELECT list that casts DECIMAL columns to DOUBLE.

    DuckDB's sqlite extension writes DECIMAL columns as VARCHAR, so SQLite
    would store prices/quantities as text and numeric comparisons
    (e.g. l_quantity < 24) would silently return wrong results.
    """
    columns = con.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_schema = 'main' AND table_name = ? "
        "ORDER BY ordinal_position",
        [table]
    ).fetchall()

    return ", ".join(
        f"CAST({name} AS DOUBLE) AS {name}"
        if dtype.upper().startswith("DECIMAL") else name
        for name, dtype in columns
    )


for sf in SCALES:
    duckdb_path = db_path(sf, "duckdb")
    sqlite_path = db_path(sf, "sqlite")

    if not duckdb_path.exists():
        print(f"\nSkipping SF{sf}: {duckdb_path} not found "
              f"(run generate_tcph_db.py first)")
        continue

    if sqlite_path.exists():
        print(f"\nSkipping SF{sf}: {sqlite_path} already exists "
              f"(delete it to re-export)")
        continue

    print(f"\nExporting SF{sf} to SQLite...")
    start = time.perf_counter()

    con = duckdb.connect(str(duckdb_path))

    try:
        con.execute("INSTALL sqlite;")
        con.execute("LOAD sqlite;")

        con.execute(f"""
            ATTACH '{sqlite_path.as_posix()}'
            AS sqlite_db (TYPE sqlite)
        """)

        for table in TABLES:
            print(f"Copying {table}...", flush=True)
            con.execute(f"""
                CREATE TABLE sqlite_db.{table} AS
                SELECT {sqlite_select_list(con, table)} FROM main.{table}
            """)

        con.execute("DETACH sqlite_db")
    except BaseException:
        # Don't leave a half-written SQLite file that would be skipped next run
        con.close()
        sqlite_path.unlink(missing_ok=True)
        raise

    con.close()
    print(f"SF{sf} export finished in "
          f"{time.perf_counter() - start:.1f} seconds")

print("\nSQLite export complete.")
