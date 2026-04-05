# AppSideBar

## Purpose
Main application sidebar component providing navigation menu, user info display, and quick access to key features.

## Location
`frontend/components/ui/AppSideBar.vue`

## Props

### Required Props
```typescript
interface Props {
  collapsed?: boolean      // Whether sidebar is collapsed
  user?: User             // Current user object
  navigation?: NavItem[]  // Navigation menu items
}
```

### Navigation Item Structure
```typescript
interface NavItem {
  name: string           // Unique identifier
  label: string          // Display label
  icon: string           // Icon name/class
  route: string          // Route path
  badge?: number         // Notification badge count
  children?: NavItem[]   // Sub-menu items
  permission?: string    // Required permission
}
```

## Events

### Emitted Events
```typescript
interface Emits {
  'toggle-collapse': []              // Sidebar collapse toggle
  'navigate': [route: string]        // Navigation triggered
  'logout': []                       // User logout requested
}
```

## Slots

### Named Slots
- `header` - Custom header content above navigation
- `footer` - Custom footer content below navigation
- `user-info` - Custom user information display

## Usage Examples

### Basic Sidebar
```vue
<template>
  <AppSideBar
    :user="currentUser"
    :navigation="menuItems"
    @navigate="handleNavigate"
    @logout="handleLogout"
  />
</template>

<script setup>
const menuItems = [
  {
    name: 'dashboard',
    label: 'Dashboard',
    icon: 'dashboard',
    route: '/dashboard'
  },
  {
    name: 'assignments',
    label: 'Assignments',
    icon: 'assignment',
    route: '/assignments',
    badge: pendingCount.value
  }
]
</script>
```

### Collapsible Sidebar
```vue
<template>
  <AppSideBar
    :collapsed="sidebarCollapsed"
    :user="user"
    :navigation="navigation"
    @toggle-collapse="sidebarCollapsed = !sidebarCollapsed"
  />
</template>
```

### With Custom User Info
```vue
<template>
  <AppSideBar :user="user" :navigation="navigation">
    <template #user-info>
      <div class="custom-user-info">
        <img :src="user.avatar" class="avatar" />
        <div class="user-details">
          <h4>{{ user.full_name }}</h4>
          <p>{{ user.role }}</p>
        </div>
      </div>
    </template>
  </AppSideBar>
</template>
```

## Features

### Responsive Design
- Auto-collapse on mobile devices
- Touch-friendly navigation
- Keyboard navigation support

### Navigation Management
- Active route highlighting
- Sub-menu expansion
- Badge notifications
- Permission-based menu filtering

### User Interface
- User avatar and info display
- Quick logout action
- Theme toggle support
- Search functionality

### Accessibility
- ARIA labels and roles
- Keyboard shortcuts
- Screen reader support
- Focus management

## Styling

### CSS Classes
```css
.app-sidebar {
  /* Main sidebar container */
}

.app-sidebar--collapsed {
  /* Collapsed state */
}

.sidebar-nav {
  /* Navigation menu */
}

.nav-item {
  /* Individual menu item */
}

.nav-item--active {
  /* Active menu item */
}

.nav-item--has-children {
  /* Item with sub-menu */
}

.user-info {
  /* User information section */
}
```

### Theme Variables
```css
:root {
  --sidebar-width: 280px;
  --sidebar-collapsed-width: 64px;
  --sidebar-bg: #ffffff;
  --nav-item-hover: #f5f5f5;
  --nav-item-active: #e3f2fd;
}
```

## Dependencies
- Vue 3 Composition API
- Nuxt 3 router integration
- Icon library (Lucide/Material Icons)
- Tailwind CSS for styling

## Business Logic
- Menu items filtered by user role
- Badge counts updated in real-time
- Route changes trigger active state updates
- Logout clears session and redirects

## Performance Notes
- Lazy loading of sub-menu items
- Debounced search input
- Virtual scrolling for large menus
- Icon preloading for smooth animations