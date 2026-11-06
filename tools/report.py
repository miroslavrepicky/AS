#!/usr/bin/env python3
"""Turns JMH JSON (-rf json) into a table (ns per calculation).

mean = AverageTime mode (with JMH's 99.9 % error), p50/p99 = SampleTime mode.
  *  percentile < 1 000 ns: limited by timer resolution (e.g. 100 ns steps on Windows) -> use the mean only
  !  p50 and mean differ by > 1.5x although p50 >= 1 000 ns: result depends on the benchmark shape
     (JIT compiled the code differently in the two modes) -> do not draw conclusions from this row
x vs A = mean relative to variant A with the same N.

Usage: python3 tools/report.py results_scaling.json [results_baseline.json ...]"""
import json, sys
from collections import defaultdict

rows = defaultdict(dict)
for path in sys.argv[1:]:
    for r in json.loads(open(path).read(), strict=False):
        p = r["params"]
        key = (p.get("n", "-"), p["variant"])
        m = r["primaryMetric"]
        if r["mode"] == "avgt":
            rows[key]["mean"] = m["score"]
            err = m.get("scoreError")
            rows[key]["err"] = err if isinstance(err, (int, float)) else float("nan")
        else:
            pc = m["scorePercentiles"]
            rows[key]["p50"], rows[key]["p99"] = pc["50.0"], pc["99.0"]


def pct(v):
    return f"{v:>9.0f}{'*' if v < 1000 else ' '}"


print(f"{'N':>5} {'variant':>9} {'mean[ns]':>10} {'±err':>6} {'p50[ns]':>10} {'p99[ns]':>10}  {'x vs A':>7}")
flagged = False
for (n, v) in sorted(rows, key=lambda k: (int(k[0]) if k[0] != '-' else 0, k[1])):
    r = rows[(n, v)]
    a = rows.get((n, "A"), {}).get("mean")
    rel = f"{r['mean'] / a:6.2f}x" if a and "mean" in r else ""
    bad = "p50" in r and "mean" in r and max(r["p50"], r["mean"]) >= 1000 and not (1 / 1.5 <= r["p50"] / r["mean"] <= 1.5)
    flagged |= bad
    print(f"{n:>5} {v:>9} {r['mean']:>10.1f} {r['err']:>6.1f} {pct(r['p50'])} {pct(r['p99'])}  {rel:>7}{'  !' if bad else ''}")
print("\n* below 1000 ns: timer-limited, trust the mean only")
if flagged:
    print("! mean and p50 disagree (> 1.5x): benchmark-shape / JIT dependent, do not interpret")
