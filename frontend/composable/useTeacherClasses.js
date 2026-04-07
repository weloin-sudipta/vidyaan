import { ref } from 'vue'
import { createResource } from '~/composable/useFrappeFetch'

// Local YYYY-MM-DD (avoid UTC drift)
const todayISO = () => {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

export const useTeacherClasses = () => {
  const classes = ref([])
  const loading = ref(false)
  const error = ref(null)
  const currentDate = ref(todayISO())
  const latestAvailableDate = ref(null)

  // Fetch classes for the given date (defaults to today)
  const fetchclassSchedule = async (date) => {
    loading.value = true
    error.value = null
    const targetDate = date || todayISO()
    try {
      const resource = createResource({
        url: 'vidyaan.api_folder.teachers_classes.get_my_classes',
      })
      const res = await resource.submit({ date: targetDate })
      classes.value = res?.classes || []
      currentDate.value = res?.date || targetDate
      latestAvailableDate.value = res?.latest_available_date || null
      console.log('classes', res)
      return res
    } catch (err) {
      console.error('Failed to load classes:', err)
      error.value = err.message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  // Bulk save attendance for one course schedule
  const saveAttendanceBulk = async (course_schedule, students) => {
    loading.value = true
    error.value = null
    try {
      const payload = students
        .filter(s => s.id)
        .map(s => ({
          student: s.id,
          status: s.status
            ? s.status.charAt(0).toUpperCase() + s.status.slice(1)
            : 'Present',
        }))

      const resource = createResource({
        url: 'vidyaan.api_folder.teachers_classes.mark_attendance_bulk',
      })

      const res = await resource.submit({
        course_schedule,
        students: payload,
      })

      console.log('Attendance result:', res)
      if (res?.failed?.length) console.warn('Some records failed:', res.failed)
      return res
    } catch (err) {
      console.error('Failed to save attendance:', err)
      error.value = err.message || 'Unknown error'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    classes,
    loading,
    error,
    currentDate,
    latestAvailableDate,
    fetchclassSchedule,
    saveAttendanceBulk,
    todayISO,
  }
}
