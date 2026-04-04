import { auth, createResource } from '~/composable/useFrappeFetch'

export const useUserProfile = () => {

  const profileData = useState('profileData', () => ({
    firstName: '',
    lastName: '',
    email: '',
    fullName: '',
    userImage: ''
  }))

  const userRole = useState('userRole', () => null)
  const isAuthenticated = useState('isAuthenticated', () => false)
  const isProfileLoading = useState('isProfileLoading', () => false)

  const loadProfile = async () => {
    // prevent duplicate calls if already authenticated or already loading
    if (isAuthenticated.value && profileData.value.email) return
    if (isProfileLoading.value) return

    isProfileLoading.value = true

    try {
      // Use the correct whitelisted endpoint
      const url = 'vidyaan.api_folder.profile.get_user_info'
      
      const roleResource = createResource({ url })

      const roleData = await roleResource.submit()

      if (roleData && roleData.email) {
        profileData.value = {
          firstName: roleData.first_name || '',
          lastName: roleData.last_name || '',
          email: roleData.email || '',
          fullName: roleData.full_name || `${roleData.first_name || ''} ${roleData.last_name || ''}`.trim(),
          userImage: roleData.user_image || ''
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


  const clearProfile = () => {
    profileData.value = {
      firstName: '',
      lastName: '',
      email: '',
      fullName: '',
      userImage: ''
    }
    userRole.value = null
    isAuthenticated.value = false
  }

  return { profileData, userRole, isAuthenticated, isProfileLoading, loadProfile, clearProfile }
}