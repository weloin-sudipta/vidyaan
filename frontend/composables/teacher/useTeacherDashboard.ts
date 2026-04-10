import { ref, type Ref } from 'vue'
import { createResource } from '~/composables/api/useFrappeFetch'

// ─── Teacher profile ──────────────────────────────────────────────────────
export interface TeacherProfile {
  name?: string
  full_name?: string
  email?: string
  employee?: string
  department?: string
  designation?: string
  image?: string
  [key: string]: unknown
}

// ─── Pending tasks ────────────────────────────────────────────────────────
export interface PendingTaskItem {
  name?: string
  course?: string
  course_schedule?: string
  date?: string
  [key: string]: unknown
}

export interface PendingTasksState {
  attendance_pending: PendingTaskItem[]
  mark_entry_pending: PendingTaskItem[]
  review_pending: PendingTaskItem[]
  application_pending: PendingTaskItem[]
}

interface PendingTasksResponse {
  success?: boolean
  attendance_pending?: PendingTaskItem[]
  mark_entry_pending?: PendingTaskItem[]
  review_pending?: PendingTaskItem[]
  application_pending?: PendingTaskItem[]
}

export interface UseTeacherDashboardReturn {
  data: Ref<TeacherProfile | null>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchTeacherData: () => Promise<TeacherProfile | undefined>
  pendingTasks: Ref<PendingTasksState>
  loadingTasks: Ref<boolean>
  tasksError: Ref<string | null>
  fetchPendingTasks: () => Promise<PendingTasksResponse | undefined>
}

export const useTeacherDashboard = (): UseTeacherDashboardReturn => {
  const data: Ref<TeacherProfile | null> = ref(null)
  const loading = ref(true)
  const error: Ref<string | null> = ref(null)

  // Pending Tasks state
  const pendingTasks: Ref<PendingTasksState> = ref({
    attendance_pending: [],
    mark_entry_pending: [],
    review_pending: [],
    application_pending: [],
  })
  const loadingTasks = ref(false)
  const tasksError: Ref<string | null> = ref(null)

  const fetchTeacherData = async (): Promise<TeacherProfile | undefined> => {
    loading.value = true
    error.value = null

    try {
      const resource = createResource<TeacherProfile>({
        url: 'vidyaan.api_folder.teacher_data.get_my_profile',
      })

      const res = await resource.submit()
      console.log('Teacher Data:', res)

      data.value = res || null
      return res
    } catch (err) {
      console.error('Failed to load teacher data:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  const fetchPendingTasks = async (): Promise<PendingTasksResponse | undefined> => {
    loadingTasks.value = true
    tasksError.value = null

    try {
      const resource = createResource<PendingTasksResponse>({
        url: 'vidyaan.api_folder.teacher_data.get_teacher_pending_tasks',
      })

      const res = await resource.submit()

      if (res && res.success) {
        pendingTasks.value = {
          attendance_pending: res.attendance_pending || [],
          mark_entry_pending: res.mark_entry_pending || [],
          review_pending: res.review_pending || [],
          application_pending: res.application_pending || [],
        }
      }
      return res
    } catch (err) {
      console.error('Failed to load pending tasks:', err)
      tasksError.value = (err as Error).message || 'Failed to fetch pending tasks'
    } finally {
      loadingTasks.value = false
    }
  }

  return {
    data,
    loading,
    error,
    fetchTeacherData,
    pendingTasks,
    loadingTasks,
    tasksError,
    fetchPendingTasks,
  }
}
