import { ref } from 'vue'
import { call } from '~/composable/useFrappeFetch'

export const useStudentDashboard = () => {
    const dashboardData = ref<any>(null)
    const loading = ref(false)
    const error = ref<any>(null)

    // Fetch dashboard data
    const loadDashboard = async () => {
        loading.value = true
        error.value = null

        try {
            const data = await call('vidyaan.api.get_student_dashboard_data')
            dashboardData.value = data
            console.log(data);
            
            return data
        } catch (err) {
            error.value = err
            console.error('Failed to load dashboard data', err)
        } finally {
            loading.value = false
        }
    }

    // Reload function
    const reload = async () => {
        return await loadDashboard()
    }

    // Reset data
    const reset = () => {
        dashboardData.value = null
        error.value = null
        loading.value = false
    }

    return {
        dashboardData,
        loading,
        error,
        loadDashboard,
        reload,
        reset,
    }
}