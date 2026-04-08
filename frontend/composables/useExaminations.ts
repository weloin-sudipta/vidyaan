import { ref, type Ref } from 'vue'
import { createResource } from '~/composables/useFrappeFetch'

// ─── Exam shapes ───────────────────────────────────────────────────────────
export interface ExamRecord {
  name?: string
  exam_name?: string
  exam_type?: string
  date?: string
  start_time?: string
  end_time?: string
  course?: string
  room?: string
  [key: string]: unknown
}

export interface ExamResultRecord {
  name?: string
  exam?: string
  course?: string
  marks?: number
  total?: number
  grade?: string
  [key: string]: unknown
}

// Direct async profile fetch (used in index.vue)
export const useExams = async (): Promise<ExamRecord[] | undefined> => {
  const examResource = createResource<ExamRecord[]>({
    url: 'vidyaan.api_folder.exam.get_exams',
  })
  const exams = await examResource.submit()
  return exams
}

export const useExamResults = async (): Promise<ExamResultRecord[] | undefined> => {
  const resultResource = createResource<ExamResultRecord[]>({
    url: 'vidyaan.api_folder.exam.get_results',
  })
  const results = await resultResource.submit()
  return results
}

export interface UseExaminationReturn {
  loading: Ref<boolean>
  error: Ref<string | null>
  exams: Ref<ExamRecord[]>
  results: Ref<ExamResultRecord[]>
  fetchExams: () => Promise<void>
  fetchResults: () => Promise<void>
}

export const useExamination = (): UseExaminationReturn => {
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)
  const exams: Ref<ExamRecord[]> = ref([])
  const results: Ref<ExamResultRecord[]> = ref([])

  const fetchExams = async (): Promise<void> => {
    ;(loading.value = true), (error.value = null)
    try {
      const resource = createResource<ExamRecord[]>({
        url: 'vidyaan.api_folder.exam.get_exams',
      })
      const res = await resource.fetch()
      console.log(res)

      exams.value = res ?? []
    } catch (err) {
      console.error('Failed to load allExams:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  const fetchResults = async (): Promise<void> => {
    ;(loading.value = true), (error.value = null)
    try {
      const resource = createResource<ExamResultRecord[]>({
        url: 'vidyaan.api_folder.exam.get_results',
      })
      const res = await resource.fetch()
      console.log(res)

      results.value = res ?? []
    } catch (err) {
      console.error('Failed to load results:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return { loading, error, exams, fetchExams, results, fetchResults }
}
