#!/usr/bin/env python3
"""usage: summarize_missions.py static dynamic"""
import csv, os, statistics, sys

for name in sys.argv[1:] or ['static', 'dynamic']:
    path = os.path.expanduser(f'~/amr_ws/docs/mission_runs_{name}.csv')
    if not os.path.exists(path):
        print(f'{name}: no file')
        continue
    rows = list(csv.DictReader(open(path)))
    ok = [r for r in rows if r['success'] == '1']
    times = [float(r['sim_seconds']) for r in ok]
    retries = sum(int(r['retries']) for r in rows)
    print(f'{name:8s} runs={len(rows)}  success={len(ok)}/{len(rows)} ({100 * len(rows and ok) / len(rows):.0f}%)  '
          f'median={statistics.median(times):.0f}s  mean={statistics.mean(times):.0f}s  '
          f'min={min(times):.0f}s  max={max(times):.0f}s  retries={retries}')
