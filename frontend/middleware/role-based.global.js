import { useUserProfile } from '~/composables/useUserProfile'
import { useToast } from '~/composables/useToast'

export default defineNuxtRouteMiddleware(async (to, from) => {
  // Skip during SSR — profile is only loaded on the client
  if (process.server) return

  const { userRole, isAuthenticated, loadProfile } = useUserProfile()
  const { addToast } = useToast()

  // Ensure role is loaded if user is authenticated but state is missing
  if (isAuthenticated.value && !userRole.value) {
    await loadProfile()
  }

  // Use already loaded state (auth middleware handles loading for protected routes)
  if (!isAuthenticated.value) return


  const role = userRole.value?.toLowerCase()
  
  // Shared routes accessible by all roles
  const sharedPrefixes = ['/notices', '/events', '/library', '/login', '/dashboard']

  // Rules definition
  const roleAccess = {
    teacher: {
      allowedPrefixes: ['/teacher', '/profile', '/notices', '/events'],
    },
    instructor: {
      allowedPrefixes: ['/teacher', '/profile', '/notices', '/events'],
    },
    student: {
      allowedPrefixes: ['/academics', '/attendance', '/exam', '/applications', '/library', '/faculty', '/profile'],
    },
    admin: {
      allowedPrefixes: ['/admin'],
    },
    'institute admin': {
      allowedPrefixes: ['/admin'],
    },
    'system administrator': {
      allowedPrefixes: ['/admin'],
    },
  }

  const path = to.path

  // 1. Check if it's a shared route or home
  const isShared = sharedPrefixes.some(prefix => path === prefix || path.startsWith(prefix + '/'))
  const isHome = path === '/'

  if (isShared || isHome) return

  // 2. Check Role Specific Access
  const roleRules = roleAccess[role]
  const isAllowed = roleRules
    ? roleRules.allowedPrefixes.some(prefix => path.startsWith(prefix))
    : false

  // 3. Fallback: If not allowed, redirect to dashboard
  if (!isAllowed) {
    const redirectTo = '/dashboard'

    // Avoid infinite redirect if already at target
    if (path === redirectTo) return

    addToast('You do not have permission to access that area.', 'error')
    return navigateTo(redirectTo)
  }
})
