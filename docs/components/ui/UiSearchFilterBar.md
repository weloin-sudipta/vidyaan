# UiSearchFilterBar

## Purpose
Combined search input and filter controls bar, used at the top of list pages
(library catalog, student list, assignment list, etc.) to keep the UI consistent.

## Location
`frontend/components/ui/UiSearchFilterBar.vue`

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | `string` | `''` | Search text (v-model) |
| `placeholder` | `string` | `'Search...'` | Input placeholder |
| `filters` | `{ label: string; value: string }[]` | `[]` | Filter chip options |
| `activeFilter` | `string` | `''` | Currently active filter value |

## Events
- `update:modelValue` — search text changed
- `update:activeFilter` — filter chip selected

## Usage
```vue
<UiSearchFilterBar
  v-model="searchQuery"
  v-model:activeFilter="activeFilter"
  placeholder="Search books..."
  :filters="[
    { label: 'All', value: '' },
    { label: 'Available', value: 'available' },
    { label: 'Issued', value: 'issued' },
  ]"
/>
```

## Data Flow
Search text and active filter are both reactive refs in the parent page.
The parent handles the actual filtering logic — this component is purely presentational.

## Notes
- Added in the 2026-04-08 UI primitives refactor
