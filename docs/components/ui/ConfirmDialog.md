# ConfirmDialog

## Purpose
Global confirmation modal mounted once in `app.vue`. Instead of every page rendering
its own confirmation dialog, a single instance is controlled imperatively via the
`useConfirm()` composable.

## Location
`frontend/components/ui/ConfirmDialog.vue`

## Mounting
Mounted globally in `frontend/app.vue`:
```vue
<!-- app.vue -->
<NuxtPage />
<ConfirmDialog />
```

This means only one DOM node ever exists. No per-page registration required.

## Usage (via composable)

```ts
import { useConfirm } from '~/composables/ui/useConfirm'

const confirm = useConfirm()

async function handleDelete(id: string) {
  const ok = await confirm('Delete this item?', {
    title: 'Confirm deletion',
    confirmLabel: 'Delete',
    danger: true,
  })
  if (!ok) return
  await deleteItem(id)
}
```

## Data Flow
```
Page calls confirm(message, options)
  → useConfirm sets shared state (visible=true, message, options)
  → ConfirmDialog renders and shows modal
  → User clicks Confirm / Cancel
  → useConfirm resolves the Promise with true/false
  → visible=false, modal closes
```

## Options

| Field | Type | Description |
|-------|------|-------------|
| `title` | `string` | Modal title (optional) |
| `confirmLabel` | `string` | Confirm button text (default: "Confirm") |
| `cancelLabel` | `string` | Cancel button text (default: "Cancel") |
| `danger` | `boolean` | Uses danger variant for confirm button |

## Edge Cases
- Calling `confirm()` while a dialog is already open replaces the current dialog
- Navigating away (router push) auto-resolves to `false`

## Notes
- Added in the 2026-04-08 refactor (commit `a2c5a4e`)
- Paired with `composables/ui/useConfirm.ts`
