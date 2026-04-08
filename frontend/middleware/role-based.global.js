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
  
  // Shared routes accessible by both roles
  const sharedPrefixes = ['/notices', '/events', '/library', '/login']
  
  // Rules definition
  const roleAccess = {
    teacher: {
      allowedPrefixes: ['/teacher', '/teacher/'],
      dashboard: '/'
    },
    student: {
      allowedPrefixes: ['/academics', '/attendance', '/exam', '/applications', '/library', '/faculty', '/profile'],
      dashboard: '/'
    },
    shared: {
      allowedPrefixes: ['/notices', '/events', '/']
    }
  }

  const path = to.path

  // 1. Check if it's a shared route or home
  const isShared = sharedPrefixes.some(prefix => path === prefix || path.startsWith(prefix + '/'))
  const isHome = path === '/'
  
  if (isShared || isHome) return

  // 2. Check Role Specific Access
  let isAllowed = false
  
  if (role === 'teacher') {
    isAllowed = roleAccess.teacher.allowedPrefixes.some(prefix => path.startsWith(prefix))
  } else if (role === 'student') {
    isAllowed = roleAccess.student.allowedPrefixes.some(prefix => path.startsWith(prefix))
  }

  // 3. Fallback: If not allowed, redirect to own dashboard (always /)
  if (!isAllowed) {
    const redirectTo = '/'
    
    // Avoid infinite redirect if already at target
    if (path === redirectTo) return

    addToast('You do not have permission to access that area.', 'error')
    return navigateTo(redirectTo)
  }
})
