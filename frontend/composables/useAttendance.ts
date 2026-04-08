import { ref, type Ref } from 'vue'
import { createResource } from '~/composables/useFrappeFetch'

// ─── Attendance map ─────────────────────────────────────────────────────────
// `get_attendance` returns a calendar map.  We treat it as a generic
// string-keyed structure of either status strings or nested day objects.
export type AttendanceDayValue = string | number | boolean | null | Record<string, unknown>
export type AttendanceMap = Record<string, AttendanceDayValue>

export interface UseAttendanceReturn {
  attendanceMap: Ref<AttendanceMap>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchAttendance: (month: number | string, year: number | string) => Promise<AttendanceMap | undefined>
}

export const useAttendance = (): UseAttendanceReturn => {
  const attendanceMap: Ref<AttendanceMap> = ref({})
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  const fetchAttendance = async (
    month: number | string,
    year: number | string
  ): Promise<AttendanceMap | undefined> => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource<AttendanceMap>({
        url: 'vidyaan.api_folder.attendance.get_attendance',
      })
      const res = await resource.submit({ month, year })
      attendanceMap.value = res || {}
      return res
    } catch (err) {
      console.error('Failed to load attendance:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return { attendanceMap, loading, error, fetchAttendance }
}

// ─── Attendance summary ────────────────────────────────────────────────────
export interface AttendanceSummary {
  total_days?: number
  present?: number
  absent?: number
  late?: number
  half_day?: number
  percentage?: number
  [key: string]: unknown
}

export interface UseAttendanceSummaryReturn {
  summary: Ref<AttendanceSummary | null>
  loading: Ref<boolean>
  error: Ref<string | null>
  fetchSummary: () => Promise<AttendanceSummary | undefined>
}

export const useAttendanceSummary = (): UseAttendanceSummaryReturn => {
  const summary: Ref<AttendanceSummary | null> = ref(null)
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)

  const fetchSummary = async (): Promise<AttendanceSummary | undefined> => {
    loading.value = true
    error.value = null
    try {
      const resource = createResource<AttendanceSummary>({
        url: 'vidyaan.api_folder.attendance.get_attendance_summary',
      })
      const res = await resource.submit()
      summary.value = res ?? null
      return res
    } catch (err) {
      console.error('Failed to load attendance summary:', err)
      error.value = (err as Error).message || 'Unknown error'
    } finally {
      loading.value = false
    }
  }

  return { summary, loading, error, fetchSummary }
}
