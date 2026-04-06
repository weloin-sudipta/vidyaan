# Mistakes Memory

Append-only log of agent mistakes. Used by neuro's pre-flight memory check.

## Format

Each mistake = one `.md` file or one block in `log.md`. Use this YAML:

```yaml
id: mistake_001
date: YYYY-MM-DD
type: mistake
agent: BACKEND          # which agent made it
description: "1 line root cause"
fix: "1 line fix that worked"
tags: [frappe, permissions, api]   # used for pre-flight match
occurrences: 1
promoted: false
```

## Rules

- Append only — never overwrite
- Max 5 lines per entry
- No task-specific data (names, IDs) — only reusable knowledge
- Deduplicate by tag+description before adding
- After 2 occurrences → update the responsible agent's rules
