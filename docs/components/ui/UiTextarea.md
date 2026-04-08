# UiTextarea

## Purpose
Styled multi-line text input with label and error state, matching UiInput visual style.

## Location
`frontend/components/ui/UiTextarea.vue`

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `string` | `''` | v-model binding |
| `label` | `string` | — | Field label |
| `placeholder` | `string` | — | Placeholder text |
| `rows` | `number` | `4` | Number of visible rows |
| `error` | `string` | — | Validation error message |
| `disabled` | `boolean` | `false` | Disabled state |

## Events
- `update:modelValue` — emitted on input

## Usage
```vue
<UiTextarea
  v-model="description"
  label="Assignment Description"
  :rows="6"
  :error="errors.description"
/>
```

## Notes
- Added in the 2026-04-08 UI primitives refactor
