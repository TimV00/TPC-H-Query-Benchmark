
import sqlite3
import duckdb
import time
import statistics
import csv

from common import (
    SCALES, ENGINES, RESULTS_DIR,
    db_path, load_query, prompt_query_number,
)

RUNS = 5

query_num = prompt_query_number("benchmark")
query_name = f"Q{query_num}"
queries = {engine: load_query(query_num, engine) for engine in ENGINES}

results = []

for sf in SCALES:
    for engine in ENGINES:

        query = queries[engine]
        path = db_path(sf, engine)

        if engine == "sqlite":
            con = sqlite3.connect(
                f"{path.as_uri()}?mode=ro",
                uri=True
            )
        else:
            con = duckdb.connect(
                str(path),
                read_only=True
            )
            con.execute("SET threads = 1")
            con.execute("SET memory_limit = '16GB'")

        print(f"\nTesting {query_name} on {engine} SF{sf}")

        # Warm-up
        con.execute(query).fetchall()

        times = []
        reference_result = None

        for i in range(RUNS):
            start = time.perf_counter()
            result = con.execute(query).fetchall()
            elapsed = time.perf_counter() - start

            if reference_result is None:
                reference_result = result
            elif result != reference_result:
                raise ValueError("Inconsistent query results")

            times.append(elapsed)
            print(f"Run {i+1}: {elapsed:.4f}s")

        results.append({
            "engine": engine,
            "scale": sf,
            "query": query_name,
            "median_seconds": statistics.median(times),
            "min_seconds": min(times),
            "max_seconds": max(times),
            "result": str(reference_result)
        })

        con.close()

RESULTS_DIR.mkdir(exist_ok=True)
output_file = RESULTS_DIR / f"q{query_num}_baseline.csv"

with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)

print(f"\nBenchmark complete. Results saved to {output_file}")
