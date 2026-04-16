import { ref, computed } from 'vue'
import { call } from '~/composables/api/useFrappeFetch'

export type UserRole = 'student' | 'teacher' | 'admin' | 'unknown'

interface UseUserRoleReturn {
  userRole: Ref<UserRole>
  isStudent: ComputedRef<boolean>
  isTeacher: ComputedRef<boolean>
  isAdmin: ComputedRef<boolean>
  roleError: Ref<string | null>
  isLoading: Ref<boolean>
  refreshUserRole: () => Promise<void>
  initialized: Ref<boolean>
}

let cachedRole: UserRole | null = null
let cacheInitialized = false
let initPromise: Promise<UserRole> | null = null

/**
 * Detect user role by probing role-specific APIs
 * Strategy: Try student → Try teacher → Check admin → Fallback student
 * Results are cached to avoid repeated API calls
 */
export const useUserRole = (): UseUserRoleReturn => {
  const userRole = ref<UserRole>('unknown')
  const roleError = ref<string | null>(null)
  const isLoading = ref(false)
  const initialized = ref(false)

  const isStudent = computed(() => userRole.value === 'student')
  const isTeacher = computed(() => userRole.value === 'teacher')
  const isAdmin = computed(() => userRole.value === 'admin')

  const detectUserRole = async (): Promise<UserRole> => {
    // Return cached role if available
    if (cacheInitialized && cachedRole) {
      return cachedRole
    }

    isLoading.value = true
    roleError.value = null

    try {
      // Step 1: Try to fetch student assignments
      try {
        await call('vidyaan.api_folder.assignments.get_student_assignments')
        cachedRole = 'student'
        cacheInitialized = true
        initialized.value = true
        return 'student'
      } catch (studentErr) {
        const errorMsg = (studentErr as Error).message || ''
        // 403 Forbidden likely means no Student record
        if (errorMsg.includes('403') || errorMsg.includes('No Student record')) {
          console.warn('[useUserRole] Student probe failed, trying teacher...')
        } else {
          console.error('[useUserRole] Student probe error:', studentErr)
        }
      }

      // Step 2: Try to fetch teacher courses
      try {
        await call('vidyaan.api_folder.assignments.get_instructor_courses')
        cachedRole = 'teacher'
        cacheInitialized = true
        initialized.value = true
        return 'teacher'
      } catch (teacherErr) {
        const errorMsg = (teacherErr as Error).message || ''
        if (errorMsg.includes('403') || errorMsg.includes('No Instructor record')) {
          console.warn('[useUserRole] Teacher probe failed, checking admin...')
        } else {
          console.error('[useUserRole] Teacher probe error:', teacherErr)
        }
      }

      // Step 3: Check for admin roles (would read from Frappe context)
      // For now, if both student and teacher failed, check if we can proceed
      // Admin users typically have access to both APIs, but let's be safe
      try {
        // Attempt a benign admin API call
        const result = await call('frappe.client.get_list', {
          doctype: 'User'
        })
        // If this succeeds without 403, likely admin
        cachedRole = 'admin'
        cacheInitialized = true
        initialized.value = true
        return 'admin'
      } catch (adminErr) {
        console.warn('[useUserRole] Admin check failed:', adminErr)
      }

      // Step 4: Fallback to student view
      console.warn('[useUserRole] All role detections failed, defaulting to student')
      cachedRole = 'student'
      cacheInitialized = true
      initialized.value = true
      return 'student'
    } catch (err) {
      const msg = (err as Error).message ?? 'Unknown error during role detection'
      roleError.value = msg
      console.error('[useUserRole] Unexpected error:', err)
      
      // Still fallback to student on unexpected error
      cachedRole = 'student'
      cacheInitialized = true
      initialized.value = true
      return 'student'
    } finally {
      isLoading.value = false
    }
  }

  const refreshUserRole = async () => {
    cacheInitialized = false
    cachedRole = null
    initialized.value = false
    const role = await detectUserRole()
    userRole.value = role
  }

  // Auto-detect on first call, cache promise to avoid multiple calls
  const initialize = async () => {
    if (!initPromise) {
      initPromise = detectUserRole()
    }
    const role = await initPromise
    userRole.value = role
    return role
  }

  // Start initialization immediately but don't block
  initialize().catch(err => console.error('[useUserRole] Init error:', err))

  return {
    userRole,
    isStudent,
    isTeacher,
    isAdmin,
    roleError,
    isLoading,
    initialized,
    refreshUserRole
  }
}

/**
 * Normalize various date formats to YYYY-MM-DD string
 * Safely handles null, undefined, various date formats
 */
export const formatDateString = (dateInput: any): string | null => {
  if (!dateInput) return null

  // Already in correct format
  if (typeof dateInput === 'string' && dateInput.match(/^\d{4}-\d{2}-\d{2}/)) {
    const parts = dateInput.split(' ')
    return parts[0] ?? null
  }

  // Parse as date
  try {
    let date: Date

    if (dateInput instanceof Date) {
      date = dateInput
    } else if (typeof dateInput === 'string') {
      date = new Date(dateInput)
    } else if (typeof dateInput === 'number') {
      date = new Date(dateInput)
    } else {
      return null
    }

    // Validate date
    if (isNaN(date.getTime())) {
      return null
    }

    // Return in YYYY-MM-DD format
    const isoString = date.toISOString()
    const parts = isoString.split('T')
    return parts[0] ?? null
  } catch (err) {
    console.warn('[formatDateString] Failed to parse date:', dateInput, err)
    return null
  }
}
