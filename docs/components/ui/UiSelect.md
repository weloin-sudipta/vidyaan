# UiSelect

## Purpose
Styled select dropdown with label and error state, consistent with UiInput styling.

## Location
`frontend/components/ui/UiSelect.vue`

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `string \| number` | — | v-model binding |
| `options` | `{ label: string; value: string \| number }[]` | `[]` | Dropdown options |
| `label` | `string` | — | Field label |
| `placeholder` | `string` | `'Select...'` | Empty option text |
| `error` | `string` | — | Validation error message |
| `disabled` | `boolean` | `false` | Disabled state |

## Events
- `update:modelValue` — emitted on selection change

## Usage
```vue
<UiSelect
  v-model="selectedCourse"
  :options="courseOptions"
  label="Course"
  :error="errors.course"
/>
```

## Notes
- Added in the 2026-04-08 UI primitives refactor
