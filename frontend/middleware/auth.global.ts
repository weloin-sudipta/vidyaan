import { useUserProfile } from '~/composables/student/useUserProfile'

export default defineNuxtRouteMiddleware(async (to, from) => {
  // Skip auth check during SSR — $fetch cannot use the Nitro proxy on the server.
  // Auth will be enforced on the client after hydration.
  if (process.server) return

  const { isAuthenticated, loadProfile } = useUserProfile()

  // Public routes that don't require authentication
  const publicRoutes = ['/auth']
  const isPublicRoute = publicRoutes.some(route => to.path.startsWith(route))

  // 1. Public route — allow immediately; redirect home if already logged in
  if (isPublicRoute) {
    if (isAuthenticated.value) {
      return navigateTo('/')
    }
    return
  }

  // 2. Protected route — load profile if we haven't yet
  if (!isAuthenticated.value) {
    await loadProfile()
  }

  // 3. Still not authenticated → send to login
  if (!isAuthenticated.value) {
    return navigateTo(`/auth/login?redirect=${encodeURIComponent(to.fullPath)}`)
  }
})
