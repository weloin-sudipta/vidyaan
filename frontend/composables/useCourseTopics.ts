import { ref, type Ref } from 'vue'
import { createResource } from './useFrappeFetch'

export interface Topic {
  name?: string
  topic_name?: string
  description?: string
  [key: string]: unknown
}

export interface CourseWithTopics {
  name?: string
  course_name?: string
  topics?: Topic[]
  [key: string]: unknown
}

export interface UseCourseTopicsReturn {
  topics: Ref<CourseWithTopics[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchCourseTopics: () => Promise<CourseWithTopics[] | undefined>
}

export const useCourseTopics = (): UseCourseTopicsReturn => {
  const topics: Ref<CourseWithTopics[]> = ref([])
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  const fetchCourseTopics = async (): Promise<CourseWithTopics[] | undefined> => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource<CourseWithTopics[]>({
        url: 'vidyaan.api_folder.study_materials.get_instructor_courses_with_topics',
      })
      const res = await resource.submit()
      topics.value = res || []
      return res
    } catch (err) {
      console.error('Failed to load exams:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }
  return { topics, fetchCourseTopics, loading, error }
}
