import { ref } from 'vue'
import { createResource } from '~/composable/useFrappeFetch'

export const useTeacherClasses = () => {
  const classes = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Fetch today's classes
  const fetchclassSchedule = async () => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource({
        url: 'vidyaan.api_folder.teachers_classes.get_my_classes',
      })
      const res = await resource.submit()
      classes.value = res?.classes || []
      console.log(res);
      
      return res
    } catch (err) {
      console.error('Failed to load classes:', err)
      error.value = err.message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  // Bulk save attendance
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
            : 'Present'
        }))

      const resource = createResource({
        url: 'vidyaan.api_folder.teachers_classes.mark_attendance_bulk',
      })

      const res = await resource.submit({
        course_schedule,
        students: payload 
      })

      console.log("Attendance result:", res)

      if (res?.failed?.length) {
        console.warn("Some records failed:", res.failed)
      }

      return res

    } catch (err) {
      console.error('Failed to save attendance:', err)
      error.value = err.message || 'Unknown error'
      throw err
    } finally {
      loading.value = false
    }
  }

  return { classes, loading, error, fetchclassSchedule, saveAttendanceBulk }
}