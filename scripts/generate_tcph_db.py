
import duckdb
import time

from common import SCALES, DATA_DIR, db_path

DATA_DIR.mkdir(exist_ok=True)

total_start = time.perf_counter()

for sf in SCALES:
    path = db_path(sf, "duckdb")

    if path.exists():
        print(f"\nSkipping SF{sf}: {path} already exists "
              f"(delete it to regenerate)")
        continue

    start = time.perf_counter()

    con = duckdb.connect(str(path))

    con.execute("INSTALL tpch;")
    con.execute("LOAD tpch;")

    print(f"\nGenerating TPC-H SF{sf}...")
    con.execute(f"CALL dbgen(sf = {sf});")

    print("Orders:", con.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0])

    print("Lineitems:", con.execute(
        "SELECT COUNT(*) FROM lineitem"
    ).fetchone()[0])

    con.close()

    print(f"SF{sf} finished in {time.perf_counter() - start:.1f} seconds")

print(f"\nAll done in {time.perf_counter() - total_start:.1f} seconds")
