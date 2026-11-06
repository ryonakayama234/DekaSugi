#!/usr/bin/env bash
# Runs INSIDE a systemd scope with Delegate=yes (payload user = runner).
CG=$(cut -d: -f3 /proc/self/cgroup)
echo "scope cgroup: $CG"
id
echo "scope controllers: [$(cat "/sys/fs/cgroup$CG/cgroup.controllers" 2>&1)]"
echo "scope subtree_control: [$(cat "/sys/fs/cgroup$CG/cgroup.subtree_control" 2>&1)]"
G4_DELEGATED_ROOT="/sys/fs/cgroup$CG" G4_RESULT_NAME="probe-result-systemd.json" \
  python3 probe/g4-env/probe.py
