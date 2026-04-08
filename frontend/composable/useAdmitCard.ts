import { ref, type Ref } from 'vue'
import { createResource } from './useFrappeFetch'

export interface AdmitCardData {
  name?: string
  exam_type?: string
  student_name?: string
  roll_number?: string
  exam_date?: string
  exam_center?: string
  [key: string]: unknown
}

export interface UseAdmitCardReturn {
  data: Ref<AdmitCardData[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchAdmit: (exam_type?: string) => Promise<void>
}

export const useAdmitCard = (): UseAdmitCardReturn => {
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)
  const data: Ref<AdmitCardData[]> = ref([])

  // fetchAdmit now accepts exam_type as a parameter
  const fetchAdmit = async (exam_type: string = ''): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      const resource = createResource<AdmitCardData[]>({
        url: 'vidyaan.api_folder.exam.get_admit_data',
        params: { exam_type },
      })

      const res = await resource.fetch()
      console.log('Fetched Admit Data:', res)
      data.value = res ?? []
    } catch (err) {
      console.error('Failed to load exams:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, fetchAdmit }
}
