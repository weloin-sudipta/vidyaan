# UiEmptyState

## Purpose
Standardised empty-state block displayed when a list or data fetch returns no results.
Provides a consistent illustration, heading, and optional action slot.

## Location
`frontend/components/ui/UiEmptyState.vue`

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `title` | `string` | `'Nothing here'` | Primary empty-state heading |
| `message` | `string` | — | Secondary description |
| `icon` | `string` | — | Font Awesome icon class (e.g. `'fa-book'`) |

## Slots
- `action` — Optional CTA button or link rendered below the message

## Usage
```vue
<UiEmptyState
  title="No assignments yet"
  message="Your teacher hasn't published any assignments."
  icon="fa-clipboard-list"
>
  <template #action>
    <UiButton variant="ghost" @click="refresh">Refresh</UiButton>
  </template>
</UiEmptyState>
```

## Edge Cases
- Should be shown after loading completes, not during
- Pair with `UiSkeleton` during loading states

## Notes
- Added in the 2026-04-08 UI primitives refactor
