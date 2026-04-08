import { useState } from '#imports'
import { createResource } from '~/composables/api/useFrappeFetch'
import type { Ref } from 'vue'
import type { UserInfo } from '~/composables/api/types'

export interface UserProfileState {
  firstName: string
  lastName: string
  email: string
  fullName: string
  userImage: string
}

export interface UseUserProfileReturn {
  profileData: Ref<UserProfileState>
  userRole: Ref<string | null>
  isAuthenticated: Ref<boolean>
  isProfileLoading: Ref<boolean>
  loadProfile: () => Promise<void>
  clearProfile: () => void
}

const emptyProfile = (): UserProfileState => ({
  firstName: '',
  lastName: '',
  email: '',
  fullName: '',
  userImage: '',
})

export const useUserProfile = (): UseUserProfileReturn => {
  const profileData = useState<UserProfileState>('profileData', () => emptyProfile())
  const userRole = useState<string | null>('userRole', () => null)
  const isAuthenticated = useState<boolean>('isAuthenticated', () => false)
  const isProfileLoading = useState<boolean>('isProfileLoading', () => false)

  const loadProfile = async (): Promise<void> => {
    // prevent duplicate calls if already authenticated or already loading
    if (isAuthenticated.value && profileData.value.email) return
    if (isProfileLoading.value) return

    isProfileLoading.value = true

    try {
      // Use the correct whitelisted endpoint
      const url = 'vidyaan.api_folder.profile.get_user_info'

      const roleResource = createResource<UserInfo>({ url })

      const roleData = await roleResource.submit()

      if (roleData && roleData.email) {
        profileData.value = {
          firstName: roleData.first_name || '',
          lastName: roleData.last_name || '',
          email: roleData.email || '',
          fullName:
            roleData.full_name ||
            `${roleData.first_name || ''} ${roleData.last_name || ''}`.trim(),
          userImage: roleData.user_image || '',
        }

        // Normalize role to lowercase for RBAC consistency
        const rawRole = (roleData.role || '').toLowerCase()
        if (rawRole.includes('teacher') || rawRole.includes('instructor')) {
          userRole.value = 'teacher'
        } else if (rawRole.includes('student')) {
          userRole.value = 'student'
        } else {
          userRole.value = rawRole
        }

        isAuthenticated.value = true
        console.log('User Profile Loaded:', profileData.value)
      } else {
        isAuthenticated.value = false
        userRole.value = null
      }
    } catch (error) {
      console.error('Error loading profile:', error)
      isAuthenticated.value = false
      userRole.value = null
    } finally {
      isProfileLoading.value = false
    }
  }

  const clearProfile = (): void => {
    profileData.value = emptyProfile()
    userRole.value = null
    isAuthenticated.value = false
  }

  return { profileData, userRole, isAuthenticated, isProfileLoading, loadProfile, clearProfile }
}
