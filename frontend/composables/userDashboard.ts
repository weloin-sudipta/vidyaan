import { ref, type Ref } from 'vue'
import { call } from '~/composables/useFrappeFetch'
import type { FrappeFetchError } from './types/api'

/**
 * Loose shape for the student dashboard payload — the backend returns a
 * heterogeneous bag of widgets so we keep this as an open record rather than
 * locking it to a specific schema. Consumers can narrow at the call site.
 */
export type StudentDashboardData = Record<string, unknown>

export const useStudentDashboard = () => {
    const dashboardData: Ref<StudentDashboardData | null> = ref(null)
    const loading = ref(false)
    const error: Ref<FrappeFetchError | Error | null> = ref(null)

    // Fetch dashboard data
    const loadDashboard = async (): Promise<StudentDashboardData | undefined> => {
        loading.value = true
        error.value = null

        try {
            const data = await call<StudentDashboardData>('vidyaan.api.get_student_dashboard_data')
            dashboardData.value = data
            console.log(data);

            return data
        } catch (err) {
            error.value = err as FrappeFetchError | Error
            console.error('Failed to load dashboard data', err)
            return undefined
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