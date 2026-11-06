# R2-M-A G3-2 — Linux fresh child / raw cost accounting

id: R2-M-A-G3-2-FRESH-CHILD-COST-20261106
status: implemented_candidate / engineering_only / supervisor_review_pending / owner_merge_pending
updated: 2026-11-06
tags: r2-m-a, g3-2, fresh-process, pdeathsig, process-group, wait4, cgroup-v2, cost, negative-tests

## Authority and scope

- [PR #183 Owner decision](https://github.com/ryonakayama234/DekaSugi/pull/183#issuecomment-6675971478) is controlling, incorporating DIAG-R-20261106-10 and Muse R-20261106-11. G3-1 is merged by [PR #184](https://github.com/ryonakayama234/DekaSugi/pull/184), merge commit `028ad73049a3fe07143c0e1663130129e1da286d`; this G3-2 branch is based exactly on that main.
- The G2 anchors are unchanged: main `cf844094fb5907a37bb496760e206f9061deb021`, prereg SHA-256 `865fd8cf13e61e028d97c1eaf7997a15d101e80e25bb6c105e575207843cda68`.
- This PR implements **only synthetic engineering child supervision and raw cost bookkeeping**. It does not instantiate G5 order/seed, invoke 448 fresh experiment children, make a Q001 remote commitment, commit a pre-score ledger, acquire external sources, evaluate private USE labels, or execute G4/G5/G6. Both an actual scientific entry point and real evaluator gate remain RUN_BLOCK. An explicit `engineering_only=True` is mandatory and never authorizes science.

## Trust and isolation diagram

~~~mermaid
flowchart TD
    P["Parent: validated five-field ChildRequest"] --> A{"Delegated cgroup v2 memory controller, writable and verified?"}
    A -->|"No"| X["RUN_BLOCK before spawn; no fallback"]
    A -->|"Yes"| R["O_EXCL one-attempt reservation + fresh cwd"]
    R --> S["Popen: new session / new process group + sanitized env"]
    S --> K["Child: PR_SET_PDEATHSIG; verify actual parent"]
    K --> W["Child blocks on pipe release gate"]
    S --> C["Parent attaches PID to cgroup with memory.max 512,000,000 + swap.max 0"]
    C -->|"attach fail"| X2["killpg + cgroup.kill + reap; RUN_BLOCK"]
    C -->|"success"| G["Release child gate, send exactly five public JSON fields"]
    G --> I["Child: audit/meta_path guard before dispatch and controls"]
    I --> D["Unmodified F00/F10 dispatch or one of five independent controls"]
    D --> T["Exclusive raw UseTrace; existing CATALOG_PREPARATION_* reused"]
    G --> M["Parent monotonic wall + /proc live CPU watchdog"]
    M --> L["wait4 per child: CPU=user+system and peak RSS KiB × 1024"]
    L --> Z["killpg + cgroup.kill even after normal leader exit"]
    Z --> E["Raw process totals + cgroup memory.peak/events separately"]
    E --> Y["No score, no retry, no projection materialization"]
~~~

## Linux safeguards / limitations

- `Popen(start_new_session=True)` makes the child a session/process-group leader. The child immediately sets `prctl(PR_SET_PDEATHSIG, SIGKILL)`, verifies the original parent PID to close the pre-prctl parent-death race, and blocks on an inherited pipe until cgroup membership is confirmed. If parent dies without releasing, EOF or PDEATHSIG stops the child. The extra parent PID/gate FD are **transport-only infrastructure**; research input is exactly `ChildRequest.as_dict()` (Snapshot absolute path, expected bytes SHA-256, arm, USE coordinate, exclusive trace absolute path). No law/seed/truth/score in the request or child environment; path-content leakage still requires G4 exact-head taint audit.
- Parent fails closed unless Linux `wait4`, `/proc` clock and a delegated **cgroup v2 memory** controller are available. Requires kernel `cgroup.procs`, `cgroup.kill`, `memory.max`, `memory.swap.max`, `memory.oom.group`, `memory.events`, `memory.peak`; readback verifies 512,000,000 bytes, swap disabled and group OOM handling. It does **not** enable host controllers, silently switch to RLIMIT_AS, or pretend `RLIMIT_RSS` enforces RSS. A future RLIMIT_AS alternative would need explicit G4 fault-injection evidence and Owner decision.
- Wall cap: parent `time.monotonic()` from just before subprocess spawn until `wait4` reap, with watchdog and full process-group kill, including descendants. Live CPU: `/proc/PID/stat` utime+stime checked by independent parent watchdog; `RLIMIT_CPU(5,6)` provides a second signal/hard-limit guard. Ignoring SIGXCPU does **not** disable the parent CPU monitor. `wait4` reports the **individual child** `ru_utime + ru_stime` and `ru_maxrss × 1024` (Linux KiB). The cgroup memory peak, OOM events and parent wall/CPU values are not substituted for wait4 process RSS.
- If wall or CPU >5 seconds in final raw observations, `RESOURCE_STOP` regardless of limiter behavior. Kernel scheduling/tick granularity, D-state uninterruptible tasks and cgroup cache charges preclude a claim of strict zero-overshoot guarantees. Missing `wait4`, live CPU observation, cgroup capability, release confirmation or cleanup is **RUN_BLOCK**, not a successful sample. A killed/unreaped process is reported as RUN_BLOCK, never quietly accepted. Cgroup `memory.max` controls group memory, not exactly process RSS.
- RSS SI guard is 512,000,000 bytes; **inclusive 512,000,000–536,870,912 bytes** `wait4` process RSS is labeled `BOUNDARY_REVIEW` alongside the raw bytes. OOM/resource kill still carries its RESOURCE_STOP indication. G4 audit and Owner determine borderline disposition. No unilateral reinterpretation of MB as MiB.
- Local `<trace>.attempt` marker is `O_EXCL` + fsync to block a repeat on the same destination even after failure. A new destination could still be created by a faulty caller: G3-3 must enforce **global slot-level one-shot custody** before scientific execution. No retries are implemented here; no 448-slot loop/runner exists.

## Raw accounting — no import-cost erasure

- The existing `r2_m_eng.controls` module is imported **in every fresh child for all seven arms**, with its existing import-time 16-entry MACRO_CATALOG unchanged. `CATALOG_PREPARATION_CPU_SECONDS`, `CATALOG_PREPARATION_WALL_SECONDS`, `CATALOG_SERIALIZED_BYTES` and `len(MACRO_CATALOG)` are **read and reused**; the catalog is not remeasured or reconstructed in this G3-2 layer.
- Parent process totals (`wall_seconds`, `wait4_cpu_seconds`, `wait4_peak_rss_bytes`) are reported as raw, independent resources. Child `actual_import_cpu_s/wall_s` is a startup-to-import-complete descriptive subset, not a separate additive cost; catalog preparation is a further subset. Neither is subtracted from parent totals. Trace raw bytes and cgroup memory peak are separate dimensions. Existing dispatch/controls call-site breakdown `restore/use` remains unchanged.
- `one_off_preparation.actual_cpu_s/wall_s/bytes = UNMEASURED` until genuine source-independent off-line preparation exists and is observed. Projection for `n={1,4,16,64}` is **not computed in this PR**; no unsupported amortization or weighted scalar of unlike units. Ledger rows preserve `charge_scope, observed_or_projected, phase, arm, law, child_slot, metric_unit, value_or_UNMEASURED, causal_origin, included_in_process_total, allocation_rule_version, raw_receipt_sha256`. Law and slot metadata exist **parent-side only**.

## Fault-injection tests / non-claims

- `tests/test_r2_m_a_g3_2_supervisor.py` checks cgroup absence or fake directories block before spawn; empty child gate refuses dispatch; real synthetic SIGXCPU-ignoring spin is killed by the independent CPU watchdog; a grandchild in the same group is killed with its leader. The **required negative** intentionally kills a parent and detects an **unprotected surviving child**, then compares against the protected `PDEATHSIG` child that must die. Every helper is bounded and cleaned up; no source/score and no scientific measurement.
- Accounting tests inspect SI boundary raw values, separate cgroup peak, one-off UNMEASURED and required row fields. G4 must still perform exact-head actual-path/import-graph/taint/metric/fault audits and assess delegated environment capabilities; unit fault injection is not G4 approval.
- Frozen statuses unchanged: `M_use=NOT_CERTIFIED`, `M_gap=UNKNOWN`, `N_rep/U/T=NOT_EVALUATED`, `closure=UNKNOWN`, `F01/F11=NOT_EVALUATED`, `B=NO-GO`. No reviewer acceptance or Owner merge approval is implied by submitting this code PR.
