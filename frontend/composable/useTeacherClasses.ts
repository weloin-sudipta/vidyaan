import { ref, type Ref } from 'vue'
import { createResource } from '~/composable/useFrappeFetch'

// Local YYYY-MM-DD (avoid UTC drift)
const todayISO = (): string => {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

// ─── Schedule shapes ───────────────────────────────────────────────────────
export interface TeacherClassItem {
  name?: string
  course?: string
  course_schedule?: string
  start_time?: string
  end_time?: string
  room?: string
  student_group?: string
  [key: string]: unknown
}

interface ClassScheduleResponse {
  classes?: TeacherClassItem[]
  date?: string
  latest_available_date?: string | null
  [key: string]: unknown
}

// ─── Bulk attendance ──────────────────────────────────────────────────────
export interface AttendanceStudentInput {
  id?: string
  status?: string
  [key: string]: unknown
}

interface BulkAttendancePayloadRow {
  student: string
  status: string
}

interface BulkAttendanceResponse {
  success?: boolean
  failed?: unknown[]
  saved?: unknown[]
  [key: string]: unknown
}

export interface UseTeacherClassesReturn {
  classes: Ref<TeacherClassItem[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  currentDate: Ref<string>
  latestAvailableDate: Ref<string | null>
  fetchclassSchedule: (date?: string) => Promise<ClassScheduleResponse | undefined>
  saveAttendanceBulk: (
    course_schedule: string,
    students: AttendanceStudentInput[]
  ) => Promise<BulkAttendanceResponse | undefined>
  todayISO: () => string
}

export const useTeacherClasses = (): UseTeacherClassesReturn => {
  const classes: Ref<TeacherClassItem[]> = ref([])
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)
  const currentDate: Ref<string> = ref(todayISO())
  const latestAvailableDate: Ref<string | null> = ref(null)

  // Fetch classes for the given date (defaults to today)
  const fetchclassSchedule = async (date?: string): Promise<ClassScheduleResponse | undefined> => {
    loading.value = true
    error.value = null
    const targetDate = date || todayISO()
    try {
      const resource = createResource<ClassScheduleResponse>({
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
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  // Bulk save attendance for one course schedule
  const saveAttendanceBulk = async (
    course_schedule: string,
    students: AttendanceStudentInput[]
  ): Promise<BulkAttendanceResponse | undefined> => {
    loading.value = true
    error.value = null
    try {
      const payload: BulkAttendancePayloadRow[] = students
        .filter((s): s is AttendanceStudentInput & { id: string } => Boolean(s.id))
        .map(s => ({
          student: s.id,
          status: s.status
            ? s.status.charAt(0).toUpperCase() + s.status.slice(1)
            : 'Present',
        }))

      const resource = createResource<BulkAttendanceResponse>({
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
      error.value = (err as Error).message || 'Unknown error'
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
