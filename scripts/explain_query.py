
import sqlite3
import duckdb

from common import (
    SCALES, RESULTS_DIR,
    db_path, load_query, prompt_query_number,
)

query_num = prompt_query_number("explain")

output = RESULTS_DIR / "plans"
output.mkdir(parents=True, exist_ok=True)

sqlite_query = load_query(query_num, "sqlite")
duckdb_query = load_query(query_num, "duckdb")

for sf in SCALES:
    sqlite_path = db_path(sf, "sqlite")
    duckdb_path = db_path(sf, "duckdb")

    sqlite = sqlite3.connect(
        f"{sqlite_path.as_uri()}?mode=ro",
        uri=True
    )

    # Rows are (id, parent, notused, detail); indent by tree depth
    sqlite_plan = sqlite.execute(
        "EXPLAIN QUERY PLAN " + sqlite_query
    ).fetchall()

    depth = {0: -1}
    lines = []
    for node_id, parent, _, detail in sqlite_plan:
        depth[node_id] = depth.get(parent, -1) + 1
        lines.append("  " * depth[node_id] + detail)

    sqlite_file = output / f"sqlite_sf{sf}_q{query_num}.txt"
    sqlite_file.write_text("\n".join(lines), encoding="utf-8")
    sqlite.close()

    duck = duckdb.connect(str(duckdb_path), read_only=True)
    duck.execute("SET threads = 1")

    duck_plan = duck.execute(
        "EXPLAIN " + duckdb_query
    ).fetchall()

    duckdb_file = output / f"duckdb_sf{sf}_q{query_num}.txt"
    duckdb_file.write_text(
        "\n\n".join(str(row[1]) for row in duck_plan),
        encoding="utf-8"
    )
    duck.close()

    print(f"SF{sf}: saved {sqlite_file.name} and {duckdb_file.name}")

print(f"\nQ{query_num} execution plans saved to {output}")
