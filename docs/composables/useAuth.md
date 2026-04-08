# useAuth

## Purpose
Authentication state management composable handling user login, logout, session persistence, and role-based access control.

## Location
`frontend/composables/auth/useAuth.ts`

## State Management

### Reactive State
```javascript
const user = ref(null)           // Current user object
const isAuthenticated = ref(false)  // Authentication status
const userRole = ref(null)       // User role (student/teacher/admin)
const loading = ref(false)       // Auth operation loading state
```

### User Object Structure
```javascript
interface User {
  name: string           // User ID
  full_name: string      // Display name
  email: string          // Email address
  role_profile_name: string  // Role (Student, Teacher, etc.)
  user_image: string     // Profile image URL
  company: string        // Tenant company
}
```

## API Methods

### login(credentials)
Authenticates user and establishes session.

**Parameters:**
```javascript
{
  usr: string,     // Username/email
  pwd: string      // Password
}
```

**Returns:** Promise<User>

### logout()
Clears session and redirects to login.

**Returns:** Promise<void>

### checkAuth()
Validates current session and refreshes user data.

**Returns:** Promise<User | null>

### getUserRole()
Determines user role from role profile.

**Returns:** 'student' | 'teacher' | 'admin' | null

## Usage Examples

### Login Form
```javascript
const { login, loading, error } = useAuth()

const handleLogin = async () => {
  try {
    await login({
      usr: form.email,
      pwd: form.password
    })
    navigateTo('/dashboard')
  } catch (err) {
    showError('Login failed')
  }
}
```

### Route Guard
```javascript
const { isAuthenticated, userRole } = useAuth()

// In page setup
if (!isAuthenticated.value) {
  return navigateTo('/login')
}

if (userRole.value !== 'teacher') {
  return navigateTo('/unauthorized')
}
```

### User Profile Display
```javascript
const { user } = useAuth()

// Template
<div v-if="user">
  <img :src="user.user_image" :alt="user.full_name" />
  <h3>{{ user.full_name }}</h3>
  <p>{{ user.email }}</p>
</div>
```

## Features

### Session Persistence
- Automatic session restoration on app load
- Cookie-based session management
- Session validation on route changes

### Role-Based Access
- Student/Teacher/Admin role detection
- Route-level access control
- Component-level permission checks

### Error Handling
- Login failure handling
- Session expiry detection
- Network error recovery

### Reactive Updates
- Real-time authentication state
- Automatic UI updates on login/logout
- Cross-component state sharing

## Dependencies
- Nuxt 3 `useCookie`, `navigateTo`
- Vue 3 `ref`, `computed`
- Frappe authentication API

## Security Notes
- Passwords never stored in client state
- Session cookies with httpOnly flags
- Automatic logout on session expiry
- CSRF protection via Frappe framework

## Error Cases
- Invalid credentials
- Network connectivity issues
- Session timeout
- Permission denied scenarios