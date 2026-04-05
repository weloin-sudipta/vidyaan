# DataTable

## Purpose
Reusable data table component providing sorting, filtering, pagination, and bulk actions for tabular data display.

## Location
`frontend/components/ui/DataTable.vue`

## Props

### Required Props
```typescript
interface Props {
  columns: Column[]       // Table column definitions
  data: any[]            // Table data array
  loading?: boolean      // Loading state
  selectable?: boolean   // Enable row selection
  pagination?: boolean   // Enable pagination
  sortable?: boolean     // Enable column sorting
}
```

### Column Definition Structure
```typescript
interface Column {
  key: string            // Data property key
  label: string          // Column header label
  sortable?: boolean     // Column is sortable
  filterable?: boolean   // Column is filterable
  width?: string         // Column width (CSS value)
  align?: 'left' | 'center' | 'right' // Text alignment
  format?: (value: any) => string // Value formatter function
  component?: string     // Custom component name for cell
}
```

### Optional Props
```typescript
interface Props {
  pageSize?: number      // Items per page (default: 10)
  totalItems?: number    // Total items for pagination
  currentPage?: number   // Current page (default: 1)
  emptyMessage?: string  // Message when no data
  striped?: boolean      // Alternating row colors
  bordered?: boolean     // Table borders
  compact?: boolean      // Compact row height
}
```

## Events

### Emitted Events
```typescript
interface Emits {
  'sort': [column: string, direction: 'asc' | 'desc'] // Sort changed
  'filter': [filters: Record<string, any>]           // Filters applied
  'select': [selectedRows: any[]]                    // Row selection changed
  'page-change': [page: number]                      // Page changed
  'row-click': [row: any, index: number]             // Row clicked
  'bulk-action': [action: string, selectedRows: any[]] // Bulk action triggered
}
```

## Slots

### Named Slots
- `header` - Custom table header content
- `footer` - Custom table footer content
- `empty` - Custom empty state content
- `loading` - Custom loading state content
- `column-{key}` - Custom cell content for specific column

## Usage Examples

### Basic Data Table
```vue
<template>
  <DataTable
    :columns="columns"
    :data="students"
    :loading="loading"
    @row-click="handleRowClick"
  />
</template>

<script setup>
const columns = [
  { key: 'name', label: 'Name', sortable: true },
  { key: 'class', label: 'Class', sortable: true },
  { key: 'grade', label: 'Grade', align: 'center' }
]

const students = [
  { name: 'John Doe', class: '10-A', grade: 'A' },
  { name: 'Jane Smith', class: '10-B', grade: 'B+' }
]
</script>
```

### With Selection and Bulk Actions
```vue
<template>
  <DataTable
    :columns="columns"
    :data="assignments"
    :selectable="true"
    @select="handleSelection"
    @bulk-action="handleBulkAction"
  >
    <template #header>
      <button @click="bulkDelete" :disabled="!selectedRows.length">
        Delete Selected
      </button>
    </template>
  </DataTable>
</template>
```

### With Custom Cell Rendering
```vue
<template>
  <DataTable :columns="columns" :data="notices">
    <template #column-status="{ row }">
      <span :class="`status-${row.status.toLowerCase()}`">
        {{ row.status }}
      </span>
    </template>
  </DataTable>
</template>

<script setup>
const columns = [
  { key: 'title', label: 'Title' },
  { key: 'status', label: 'Status', component: 'status' },
  { key: 'date', label: 'Date', format: (date) => formatDate(date) }
]
</script>
```

### With Pagination
```vue
<template>
  <DataTable
    :columns="columns"
    :data="currentPageData"
    :pagination="true"
    :total-items="totalStudents"
    :page-size="20"
    @page-change="handlePageChange"
  />
</template>
```

## Features

### Data Display
- Flexible column definitions
- Custom cell rendering
- Responsive design
- Empty state handling

### Sorting & Filtering
- Multi-column sorting
- Real-time filtering
- Custom filter components
- Sort state persistence

### Selection & Actions
- Single/multi-row selection
- Bulk action support
- Keyboard shortcuts
- Selection state management

### Pagination
- Server-side pagination support
- Page size options
- Navigation controls
- Page info display

### Performance
- Virtual scrolling for large datasets
- Lazy loading support
- Minimal re-renders
- Memory efficient

## Styling

### CSS Classes
```css
.data-table {
  /* Main table container */
}

.data-table__header {
  /* Table header */
}

.data-table__body {
  /* Table body */
}

.data-table__row {
  /* Table row */
}

.data-table__row--selected {
  /* Selected row */
}

.data-table__cell {
  /* Table cell */
}

.data-table__pagination {
  /* Pagination controls */
}
```

### Theme Variables
```css
:root {
  --table-border: #e5e7eb;
  --table-header-bg: #f9fafb;
  --table-row-hover: #f5f5f5;
  --table-row-selected: #e3f2fd;
  --table-text: #374151;
}
```

## Dependencies
- Vue 3 Composition API
- Lodash for data manipulation
- Tailwind CSS for styling
- Custom composables for state management

## Business Logic
- Sort/filter state maintained in URL params
- Selection state preserved during data updates
- Bulk actions validated for permissions
- Pagination handles large datasets efficiently

## Performance Notes
- Debounced filter input (200ms)
- Virtual scrolling for >1000 rows
- Column virtualization for wide tables
- Optimized re-rendering with computed properties