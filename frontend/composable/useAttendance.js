import { ref } from 'vue'
import { createResource } from '~/composable/useFrappeFetch'

export const useAttendance = () => {
  const attendanceMap = ref({})
  const loading = ref(false)
  const error = ref(null)

  const fetchAttendance = async (month, year) => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource({
        url: 'vidyaan.api_folder.attendance.get_attendance',
      })
      const res = await resource.submit({ month, year })
      attendanceMap.value = res || {}
      return res
    } catch (err) {
      console.error('Failed to load attendance:', err)
      error.value = err.message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return { attendanceMap, loading, error, fetchAttendance }
}

export const useAttendanceSummary = () => {
  const summary = ref(null)
  const loading = ref(false)
  const error = ref(null)

  const fetchSummary = async () => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource({
        url: 'vidyaan.api_folder.attendance.get_attendance_summary',
      })
      const res = await resource.submit()
      summary.value = res
      return res
    } catch (err) {
      console.error('Failed to load attendance summary:', err)
      error.value = err.message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return { summary, loading, error, fetchSummary }
}
