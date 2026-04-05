# AppNavBar

## Purpose
Top navigation bar component providing global actions, breadcrumbs, search functionality, and user menu.

## Location
`frontend/components/ui/AppNavBar.vue`

## Props

### Required Props
```typescript
interface Props {
  title?: string          // Page title
  breadcrumbs?: Breadcrumb[] // Breadcrumb navigation
  showSearch?: boolean    // Show search bar
  showNotifications?: boolean // Show notification bell
  user?: User            // Current user object
}
```

### Breadcrumb Structure
```typescript
interface Breadcrumb {
  label: string          // Display label
  route?: string         // Route path (optional)
  icon?: string          // Icon name (optional)
}
```

## Events

### Emitted Events
```typescript
interface Emits {
  'search': [query: string]           // Search query submitted
  'toggle-sidebar': []                // Sidebar toggle requested
  'logout': []                        // User logout requested
  'profile-click': []                 // User profile clicked
  'notifications-click': []           // Notifications clicked
}
```

## Slots

### Named Slots
- `left` - Content on the left side (before breadcrumbs)
- `right` - Content on the right side (after user menu)
- `actions` - Custom action buttons in the center

## Usage Examples

### Basic Navigation Bar
```vue
<template>
  <AppNavBar
    title="Student Dashboard"
    :breadcrumbs="breadcrumbs"
    :user="currentUser"
    @search="handleSearch"
    @logout="handleLogout"
  />
</template>

<script setup>
const breadcrumbs = [
  { label: 'Home', route: '/' },
  { label: 'Assignments', route: '/assignments' },
  { label: 'Mathematics Assignment' }
]
</script>
```

### With Search and Notifications
```vue
<template>
  <AppNavBar
    :show-search="true"
    :show-notifications="true"
    :user="user"
    :breadcrumbs="breadcrumbs"
    @search="performSearch"
    @notifications-click="openNotifications"
  />
</template>
```

### Custom Actions
```vue
<template>
  <AppNavBar :user="user">
    <template #actions>
      <button @click="exportData" class="btn-primary">
        Export Data
      </button>
      <button @click="importData" class="btn-secondary">
        Import Data
      </button>
    </template>
  </AppNavBar>
</template>
```

## Features

### Breadcrumb Navigation
- Automatic breadcrumb generation
- Clickable navigation links
- Icon support for visual cues
- Responsive truncation on mobile

### Global Search
- Real-time search suggestions
- Keyboard shortcuts (Ctrl+K)
- Search history
- Category filtering

### User Menu
- Profile dropdown
- Quick actions
- Theme preferences
- Logout option

### Notification Center
- Unread count badge
- Quick preview
- Mark as read
- Notification settings

### Responsive Behavior
- Mobile hamburger menu
- Collapsible search bar
- Adaptive layout
- Touch gestures

## Styling

### CSS Classes
```css
.app-navbar {
  /* Main navbar container */
}

.navbar-breadcrumbs {
  /* Breadcrumb navigation */
}

.navbar-search {
  /* Search input container */
}

.navbar-actions {
  /* Action buttons container */
}

.user-menu {
  /* User dropdown menu */
}

.notification-bell {
  /* Notification button */
}
```

### Theme Variables
```css
:root {
  --navbar-height: 64px;
  --navbar-bg: #ffffff;
  --navbar-border: #e5e7eb;
  --breadcrumb-separator: #9ca3af;
  --search-focus: #3b82f6;
}
```

## Dependencies
- Vue 3 Composition API
- Nuxt 3 router integration
- Headless UI for dropdowns
- Lucide icons for UI elements
- Tailwind CSS for styling

## Business Logic
- Breadcrumbs auto-generated from route meta
- Search integrates with global search API
- Notifications fetched from notification service
- User menu respects role permissions

## Performance Notes
- Lazy loading of notification data
- Debounced search input (300ms)
- Icon sprites for faster loading
- Minimal re-renders on route changes