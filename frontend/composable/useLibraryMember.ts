import { ref, type Ref } from 'vue'
import { createResource } from './useFrappeFetch'

export interface LibraryMember {
  name?: string
  member_name?: string
  email?: string
  membership_id?: string
  membership_status?: string
  joined_on?: string
  expiry_date?: string
  [key: string]: unknown
}

export interface UseLibraryMemberReturn {
  loading: Ref<boolean>
  error: Ref<string | null>
  memberData: Ref<LibraryMember[]>
  fetchMemberData: () => Promise<void>
}

export const useLibraryMember = (): UseLibraryMemberReturn => {
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)
  const memberData: Ref<LibraryMember[]> = ref([])

  const fetchMemberData = async (): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const resource = createResource<LibraryMember[]>({
        url: 'vidyaan.library.api.get_member_details',
      })

      const res = await resource.fetch()

      memberData.value = res ?? []

      console.log('Clean data:', memberData.value)
    } catch (err) {
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return { loading, error, memberData, fetchMemberData }
}
