import { ref, type Ref } from 'vue'
import { createResource } from '~/composables/api/useFrappeFetch'

export interface FacultyMember {
  name: string
  employee_name?: string
  designation?: string
  department?: string
  image?: string
  email?: string
  [key: string]: unknown
}

export interface UseFacultyMemberReturn {
  loading: Ref<boolean>
  error: Ref<string | null>
  members: Ref<FacultyMember[]>
  fetchMember: () => Promise<void>
}

export const useFacultyMember = (): UseFacultyMemberReturn => {
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)
  const members: Ref<FacultyMember[]> = ref([])

  const fetchMember = async (): Promise<void> => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource<FacultyMember[]>({
        url: 'vidyaan.api_folder.faculty.get_all_faculty_data',
      })
      const res = await resource.fetch()
      console.log('Member Data: ', res)

      members.value = res ?? []
    } catch (err) {
      console.error('Failed to load allExams:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }
  return { loading, error, members, fetchMember }
}
