# TeacherDashboardPendingTasks

## Purpose
Dashboard widget component displaying pending tasks for teachers with quick actions and priority indicators.

## Location
`frontend/components/dashboard/TeacherDashboardPendingTasks.vue`

## Props

### Required Props
```typescript
interface Props {
  tasks?: PendingTask[]   // List of pending tasks
  loading?: boolean      // Loading state
  maxItems?: number      // Maximum items to display
}
```

### Task Data Structure
```typescript
interface PendingTask {
  id: string            // Task unique identifier
  type: 'assignment' | 'exam' | 'attendance' | 'notice' | 'grade'
  title: string         // Task title
  description: string   // Task description
  priority: 'high' | 'medium' | 'low' // Task priority
  dueDate?: string      // Due date (ISO string)
  count?: number        // Related count (submissions, etc.)
  total?: number        // Total count for progress
  actionLabel?: string  // Custom action button label
  metadata?: Record<string, any> // Additional task data
}
```

## Events

### Emitted Events
```typescript
interface Emits {
  'task-action': [task: PendingTask]     // Task action clicked
  'view-all': []                         // View all tasks clicked
  'refresh': []                          // Refresh tasks requested
}
```

## Slots

### Named Slots
- `task-item` - Custom task item rendering
- `empty` - Custom empty state content
- `header` - Custom header content

## Usage Examples

### Basic Usage
```vue
<template>
  <TeacherDashboardPendingTasks
    :tasks="pendingTasks"
    :loading="loading"
    @task-action="handleTaskAction"
    @view-all="navigateToTasks"
  />
</template>

<script setup>
const pendingTasks = [
  {
    id: 'assignment-1',
    type: 'assignment',
    title: 'Grade Mathematics Assignment',
    description: '10 submissions pending review',
    priority: 'high',
    dueDate: '2024-01-15',
    count: 10,
    total: 25
  }
]
</script>
```

### With Custom Task Rendering
```vue
<template>
  <TeacherDashboardPendingTasks :tasks="tasks">
    <template #task-item="{ task }">
      <div class="custom-task-item">
        <div class="task-icon">
          <Icon :name="getTaskIcon(task.type)" />
        </div>
        <div class="task-content">
          <h4>{{ task.title }}</h4>
          <p>{{ task.description }}</p>
          <div class="progress-bar" v-if="task.count && task.total">
            <div
              class="progress-fill"
              :style="{ width: `${(task.count / task.total) * 100}%` }"
            />
          </div>
        </div>
        <button @click="$emit('task-action', task)">
          {{ task.actionLabel || 'Action' }}
        </button>
      </div>
    </template>
  </TeacherDashboardPendingTasks>
</template>
```

## Features

### Task Display
- Priority-based color coding
- Due date indicators
- Progress bars for countable tasks
- Task type icons

### Quick Actions
- One-click task completion
- Direct navigation to task details
- Bulk action support
- Contextual action labels

### Status Indicators
- Overdue task highlighting
- Priority badges
- Completion percentages
- Time remaining display

### Responsive Design
- Mobile-optimized layout
- Collapsible task details
- Touch-friendly interactions
- Adaptive content display

## Styling

### CSS Classes
```css
.pending-tasks {
  /* Main container */
}

.task-item {
  /* Individual task item */
}

.task-item--high {
  /* High priority styling */
}

.task-item--medium {
  /* Medium priority styling */
}

.task-item--low {
  /* Low priority styling */
}

.task-item--overdue {
  /* Overdue task styling */
}

.task-progress {
  /* Progress bar container */
}

.task-actions {
  /* Action buttons container */
}
```

### Theme Variables
```css
:root {
  --task-high-color: #ef4444;
  --task-medium-color: #f59e0b;
  --task-low-color: #10b981;
  --task-overdue-color: #dc2626;
  --task-border-radius: 8px;
}
```

## Dependencies
- Vue 3 Composition API
- Date utilities for due date calculations
- Icon library for task type indicators
- Tailwind CSS for base styling

## Business Logic
- Tasks sorted by priority and due date
- Overdue detection based on current time
- Progress calculation for submissions/grades
- Action routing based on task type

## Performance Notes
- Virtual scrolling for large task lists
- Lazy loading of task details
- Debounced refresh actions
- Minimal re-renders on data updates