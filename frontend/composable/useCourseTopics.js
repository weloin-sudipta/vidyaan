import { ref } from 'vue'
import { createResource } from './useFrappeFetch'

export const useCourseTopics = () => {
    const topics = ref([])
    const loading = ref(false)
    const error = ref(null)

    const fetchCourseTopics = async () => {
        loading.value = true
        error.value = null
        try {
            const resource = createResource({
                url: 'vidyaan.api_folder.study_materials.get_study_materials',
            })
            const res = await resource.submit()
            topics.value = res || []
            return res
        } catch (err) {
            console.error('Failed to load exams:', err)
            error.value = err.message || 'Unknown error'
        } finally {
            loading.value = false
        }
    }
    return { topics, fetchCourseTopics, loading, error }
}