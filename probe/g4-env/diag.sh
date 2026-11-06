#!/usr/bin/env bash
# G4 environment probe v2 diagnostics (auditor-side). Always exits 0.
set -u
exec > >(tee -a diag-report.txt) 2>&1
echo "=== versions ==="; uname -a; python3 --version; id
echo "=== shell cgroup ==="; cat /proc/self/cgroup
echo "root controllers: [$(cat /sys/fs/cgroup/cgroup.controllers 2>&1)]"
echo "root subtree_control: [$(cat /sys/fs/cgroup/cgroup.subtree_control 2>&1)]"
CAND="/sys/fs/cgroup/g4-env-${GITHUB_RUN_ID:-local}-${GITHUB_RUN_ATTEMPT:-1}"
echo "=== setup candidate $CAND ==="
sudo mkdir "$CAND" && echo "mkdir ok"
sudo chown "$(id -u):$(id -g)" "$CAND" "$CAND/cgroup.procs" "$CAND/cgroup.subtree_control" && echo "chown ok"
printf '+memory +cpu\n' | sudo tee "$CAND/cgroup.subtree_control" > /dev/null && echo "subtree_control write ok"
echo "candidate controllers: [$(cat "$CAND/cgroup.controllers" 2>&1)]"
echo "candidate subtree_control: [$(cat "$CAND/cgroup.subtree_control" 2>&1)]"
echo "=== manual attach as runner ==="
mkdir "$CAND/t1" && echo "mkdir t1 ok"
sleep 30 & HOGPID=$!
if echo "$HOGPID" > "$CAND/t1/cgroup.procs" 2> attach-err.txt; then
  echo "manual attach: OK"
else
  echo "manual attach: FAILED"; cat attach-err.txt
fi
echo "t1 procs: [$(cat "$CAND/t1/cgroup.procs" 2>&1)]"
kill "$HOGPID" 2> /dev/null; wait "$HOGPID" 2> /dev/null
echo "=== supervisor as runner (candidate root) ==="
G4_DELEGATED_ROOT="$CAND" G4_RESULT_NAME="probe-result-runner.json" \
  python3 probe/g4-env/probe.py || echo "probe.py runner exit: $?"
echo "=== supervisor as root (candidate root) ==="
sudo G4_DELEGATED_ROOT="$CAND" G4_RESULT_NAME="probe-result-root.json" \
  python3 probe/g4-env/probe.py || echo "probe.py root exit: $?"
echo "=== systemd-run Delegate=yes (payload user runner) ==="
sudo systemd-run --scope -p Delegate=yes -p User=runner \
  bash probe/g4-env/systemd-inner.sh || echo "systemd variant exit: $?"
echo "=== cleanup ==="
sudo rmdir "$CAND/t1" 2> /dev/null || true
sudo rmdir "$CAND" 2> /dev/null || true
echo "DIAG DONE"
