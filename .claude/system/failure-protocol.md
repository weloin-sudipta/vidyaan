# Failure Protocol

Loaded by neuro on-demand: when an agent fails, OR before high-risk delegation.
Keep this file authoritative — neuro.md only references it.

## Pre-flight Memory Check (BEFORE delegating)

1. Extract tags from task (e.g. [frappe, permissions, api])
2. Grep `memory/mistakes/log.md` for entries matching ANY tag
3. Inject top 3 matching mistakes into agent prompt as "KNOWN PITFALLS — avoid these:"
4. If a previous mistake exactly matches current task signature → also inject the prior fix
5. Increment `metrics.md → memory_hits` if a match was injected

## Failure Taxonomy

| Type | Signal | Recovery | Budget cost |
|------|--------|----------|-------------|
| `transient` | timeout, network, rate limit, file lock | Retry immediately | 0.5 |
| `contract` | API shape mismatch, field/type error between agents | Re-run SYNC CHECK, re-plan, retry | 1.0 |
| `permission` | 403, role missing, auth, file ACL | STOP — ask user | 0.0 |
| `logic` | wrong output, test fail, broken behavior | Hot-swap or split task | 1.0 |
| `unknown` | uncategorized | OBSERVER diagnoses, then re-classify | 1.0 |

## Failure Budget (hard caps per task)

- Max **3.0 failures total**
- Max **2 retries per agent**
- Max **1 hot-swap per task**
- When exhausted → STOP, return FAILURE REPORT, ask user

## Recovery Flow

```
1. Agent fails
2. Classify → {transient | contract | permission | logic | unknown}
3. Check budget → if exhausted, STOP and report
4. Save checkpoint (partial output + context)
5. Apply recovery for that type
6. Retry with: prior failure injected as "AVOID THIS" + any fixes
7. If success → log lesson to memory/mistakes/log.md, increment metrics.memory_writes
8. If fail → increment budget, re-classify, repeat or escalate
```

## Structured Failure Report (shown when budget exhausted)

```
FAILURE REPORT
──────────────
Task        : [original request]
Failed at   : [step / agent]
Type        : [transient / contract / permission / logic / unknown]
Why         : [root cause in 1 line]
Tried       : [list of recovery attempts]
Budget used : [x.x / 3.0]
Checkpoint  : [saved / not saved]

Options:
1. Retry with hint — provide guidance, resume from checkpoint
2. Workaround — [if known alternative exists]
3. Skip — log and move on
4. Abort — discard checkpoint
```

## Self-Correction Trigger

IF same failure signature appears 2+ times across tasks:
- Update the responsible agent's `.md` rules to prevent recurrence
- Bump agent version +0.1
- Increment `metrics.md → self_corrections`
- Log: "Agent [name] self-corrected: [what changed]"

## Hot-Swap

Trigger: same agent fails 2+ times on same task.

1. Pause failing agent
2. Save partial output + context (checkpoint)
3. Route to alternate agent OR split task differently
4. Resume from last good checkpoint
5. Log to memory/mistakes/log.md
6. Increment `metrics.md → hot_swaps`

## Metrics Updates

After every failure event, update `memory/metrics.md`:
- `failures_total += 1`
- `failures_<type> += 1`
- `retries_attempted` / `retries_succeeded`
- `budget_exhausted_count` if STOP triggered
