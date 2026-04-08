import { useRouter, useRoute } from '#imports'
import { auth } from '~/composable/useFrappeFetch'
import { useUserProfile } from './useUserProfile'
import type { LoginResponse, LogoutResponse } from '~/composable/types/api'

export const logout = async (): Promise<void> => {
  const { clearProfile } = useUserProfile()
  const router = useRouter()

  try {
    const data: LogoutResponse = await auth.logout()
    void data
    clearProfile()
    // Use router for client-side navigation, fallback to window for total reset if needed
    if (process.client) {
      router.push('/auth/login')
    }
  } catch (error) {
    console.error('Error during logout:', error)
    // Even if API fails, we should clear local state and redirect
    clearProfile()
    if (process.client) {
      router.push('/auth/login')
    }
    throw error
  }
}

export const login = async (usr: string, pwd: string): Promise<void> => {
  const { loadProfile } = useUserProfile()
  const router = useRouter()
  const route = useRoute()

  try {
    const data: LoginResponse = await auth.login(usr, pwd)
    void data

    await loadProfile()

    if (process.client) {
      // Use redirect query param if present, otherwise always go to / (index.vue handles role-based dashboard)
      const redirectQuery = route.query.redirect
      const redirectTo =
        typeof redirectQuery === 'string' && redirectQuery ? redirectQuery : '/'
      router.push(redirectTo)
    }
    console.log('Logged in successfully')
  } catch (error) {
    console.error('Error during login:', error)
    throw error
  }
}
