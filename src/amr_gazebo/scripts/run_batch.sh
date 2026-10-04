#!/usr/bin/env bash
# usage: run_batch.sh <name> <runs>      e.g.  run_batch.sh static 10
NAME=${1:-static}
N=${2:-10}
source ~/amr_ws/install/setup.bash
CSV=~/amr_ws/docs/mission_runs.csv
rm -f "$CSV"
for i in $(seq 1 "$N"); do
  echo "=== run $i/$N ==="
  ros2 run amr_mission mission_executor --ros-args -p use_sim_time:=true 2>&1 | grep -E "COMPLETE|FAILED|Unknown"
done
mv "$CSV" ~/amr_ws/docs/mission_runs_${NAME}.csv
echo "saved docs/mission_runs_${NAME}.csv"
