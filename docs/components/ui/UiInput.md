# UiInput

## Purpose
Styled text input with integrated label, error message slot, and consistent focus ring.

## Location
`frontend/components/ui/UiInput.vue`

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `string` | `''` | v-model binding |
| `label` | `string` | — | Input label (optional) |
| `placeholder` | `string` | — | Placeholder text |
| `type` | `string` | `'text'` | HTML input type |
| `error` | `string` | — | Error message shown below input |
| `disabled` | `boolean` | `false` | Disabled state |

## Events
- `update:modelValue` — emitted on input for v-model

## Usage
```vue
<UiInput
  v-model="email"
  label="Email Address"
  type="email"
  placeholder="you@school.edu"
  :error="errors.email"
/>
```

## Edge Cases
- When `error` is set, input border turns red and error text appears below
- Works with native form validation via `type` prop

## Notes
- Added in the 2026-04-08 UI primitives refactor
