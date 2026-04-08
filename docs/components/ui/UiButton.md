# UiButton

## Purpose
Styled button component with predefined variants to ensure visual consistency across all pages.

## Location
`frontend/components/ui/UiButton.vue`

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'primary' \| 'secondary' \| 'danger' \| 'ghost'` | `'primary'` | Visual style |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Button size |
| `disabled` | `boolean` | `false` | Disabled state |
| `loading` | `boolean` | `false` | Shows spinner, disables click |
| `type` | `'button' \| 'submit' \| 'reset'` | `'button'` | HTML button type |

## Slots
- `default` — Button label content

## Usage
```vue
<UiButton variant="primary" @click="save">Save</UiButton>
<UiButton variant="danger" :loading="deleting" @click="confirmDelete">Delete</UiButton>
<UiButton variant="ghost" size="sm">Cancel</UiButton>
```

## Edge Cases
- `loading` prop automatically disables click and shows a spinner
- Use `type="submit"` inside `<form>` elements

## Notes
- Replaces ad-hoc button styling across pages
- Added in the 2026-04-08 UI primitives refactor
