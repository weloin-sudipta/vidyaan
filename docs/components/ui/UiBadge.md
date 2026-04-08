# UiBadge

## Purpose
Inline badge for status labels, counts, and category tags with semantic colour variants.

## Location
`frontend/components/ui/UiBadge.vue`

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'default' \| 'success' \| 'warning' \| 'danger' \| 'info'` | `'default'` | Colour theme |
| `size` | `'sm' \| 'md'` | `'md'` | Badge size |

## Slots
- `default` — Badge text

## Usage
```vue
<UiBadge variant="success">Present</UiBadge>
<UiBadge variant="danger">Overdue</UiBadge>
<UiBadge variant="warning">Pending</UiBadge>
```

## Notes
- Replaces inline Tailwind class combinations for status colours
- Added in the 2026-04-08 UI primitives refactor
- Previously a `UiStatusBadge.vue` existed but was removed in the same refactor; `UiBadge` is the replacement
