# Neuro Metrics

Lightweight observability — tells you whether neuro is actually getting better.
Update after every task. Append-only weekly snapshots; rolling counters at top.

## Rolling Counters (current period)

```yaml
period_start: 2026-04-06
tasks_total: 0
tasks_simple: 0
tasks_standard: 0
tasks_advanced: 0

failures_total: 0
failures_transient: 0
failures_contract: 0
failures_permission: 0
failures_logic: 0
failures_unknown: 0

retries_attempted: 0
retries_succeeded: 0
hot_swaps: 0
budget_exhausted_count: 0

memory_hits: 0          # pre-flight check matched a known mistake
memory_writes: 0        # new mistakes/patterns added
self_corrections: 0     # agent rules auto-updated
```

## How to Use

- Increment counters inline as events happen
- Every 15 tasks, snapshot to history below + reset rolling counters
- If `failures_total / tasks_total > 0.3` → failure handling is degrading, investigate
- If `memory_hits / tasks_total < 0.1` after 20 tasks → pre-flight check is not effective, audit tags
- If `budget_exhausted_count > 2` in a period → budget is too tight OR root issue not being fixed

## History

<!-- Snapshots appended below every 15 tasks -->
