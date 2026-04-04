import { ref } from 'vue'
import { createResource } from './useFrappeFetch'

export const useTeacherDashboard = () => {
    const data = ref(null)
    const loading = ref(true)
    const error = ref(null)

    // Pending Tasks state
    const pendingTasks = ref({
        attendance_pending: [],
        mark_entry_pending: [],
        review_pending: []
    })
    const loadingTasks = ref(false)
    const tasksError = ref(null)

    const fetchTeacherData = async () => {
        loading.value = true
        error.value = null

        try {
            const resource = createResource({
                url: 'vidyaan.api_folder.teacher_data.get_my_profile',
            })

            const res = await resource.submit()
            console.log('Teacher Data:', res)

            data.value = res || null
            return res
        } catch (err) {
            console.error('Failed to load teacher data:', err)
            error.value = err.message || 'Unknown error'
        } finally {
            loading.value = false
        }
    }

    const fetchPendingTasks = async () => {
        loadingTasks.value = true
        tasksError.value = null

        try {
            const resource = createResource({
                url: 'vidyaan.api_folder.teacher_data.get_teacher_pending_tasks',
            })

            const res = await resource.submit()

            if (res && res.success) {
                pendingTasks.value = {
                    attendance_pending: res.attendance_pending || [],
                    mark_entry_pending: res.mark_entry_pending || [],
                    review_pending: res.review_pending || []
                }
            }
            return res
        } catch (err) {
            console.error('Failed to load pending tasks:', err)
            tasksError.value = err.message || 'Failed to fetch pending tasks'
        } finally {
            loadingTasks.value = false
        }
    }

    return { 
        data, loading, error, fetchTeacherData,
        pendingTasks, loadingTasks, tasksError, fetchPendingTasks 
    }
}