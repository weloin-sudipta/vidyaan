import { ref, type Ref } from 'vue'
import { createResource } from '~/composables/useFrappeFetch'

export interface ProfileData {
  [key: string]: unknown
}

export interface FeesData {
  [key: string]: unknown
}

export interface UseProfileLoaderReturn {
  profileData: Ref<ProfileData | null>
  loading: Ref<boolean>
  error: Ref<string | null>
  loadProfile: () => Promise<ProfileData | null | undefined>
}

export type UpdateProfileResult = ProfileData | { error: string } | undefined

export type GetFeesResult =
  | { success: true; data: FeesData | null | undefined }
  | { success: false; data: null }

// Direct async profile fetch (used in index.vue)
export const useProfile = async (): Promise<ProfileData | undefined> => {
  const profileResource = createResource<ProfileData>({
    url: 'vidyaan.api_folder.profile.get_profile',
  })
  const profile = await profileResource.submit()
  return profile
}

// Reactive profile loader (used in edit.vue)
export const useProfileLoader = (): UseProfileLoaderReturn => {
  const profileData: Ref<ProfileData | null> = ref(null)
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  const loadProfile = async (): Promise<ProfileData | null | undefined> => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource<ProfileData>({
        url: 'vidyaan.api_folder.profile.get_profile',
      })
      const res = await resource.submit()
      profileData.value = res ?? null
      return res
    } catch (err) {
      console.error('Failed to load profile:', err)
      error.value = (err as Error).message || 'Unknown error'
      profileData.value = null
    } finally {
      loading.value = false
    }
  }

  return { profileData, loading, error, loadProfile }
}

// Update profile
export const updateProfile = async (
  payload: Record<string, unknown>
): Promise<UpdateProfileResult> => {
  try {
    const resource = createResource<ProfileData>({
      url: 'vidyaan.api_folder.profile.update_profile',
    })
    const res = await resource.submit({ data: JSON.stringify(payload) })
    return res
  } catch (err) {
    console.error('Failed to update profile:', err)
    return { error: (err as Error).message || 'Unknown error' }
  }
}

interface FeesEnvelope {
  message?: FeesData
  data?: FeesData
}

export const getFees = async (): Promise<GetFeesResult> => {
  try {
    const feesResource = createResource<FeesData | FeesEnvelope>({
      url: 'vidyaan.api_folder.fees.get_my_fee',
    })

    const res = await feesResource.submit()

    let data: FeesData | null | undefined
    if (res && typeof res === 'object' && 'message' in res && (res as FeesEnvelope).message !== undefined) {
      data = (res as FeesEnvelope).message
    } else if (res && typeof res === 'object' && 'data' in res && (res as FeesEnvelope).data !== undefined) {
      data = (res as FeesEnvelope).data
    } else {
      data = res as FeesData | undefined
    }

    return {
      success: true,
      data,
    }
  } catch (error) {
    console.error('getFees error:', error)

    return {
      success: false,
      data: null,
    }
  }
}
