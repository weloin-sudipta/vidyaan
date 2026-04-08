// composables/useTimetable.ts
import { ref, computed, onMounted, type Ref, type ComputedRef } from 'vue'
import { call } from '~/composables/api/useFrappeFetch'
import { renderTimetableHtml } from '~/utils/pdf-templates/timetable'
import type { PdfGenerationResult } from '~/composables/api/types'

// ─── Local shapes ─────────────────────────────────────────────────────────
export interface ScheduleSlot {
  startTime: string
  endTime: string
  subject?: string
  teacher?: string
  room?: string
  category?: string
  [key: string]: unknown
}

export type WeeklyTimetable = Record<string, ScheduleSlot[]>

export interface StudentScheduleResponse {
  success?: boolean
  timetable?: WeeklyTimetable
  student_group?: string
  [key: string]: unknown
}

export type CategoryStyles = Record<string, string>

export interface UseTimetableReturn {
  // State
  activeDay: Ref<string>
  weekDays: string[]
  categoryStyles: CategoryStyles
  timetableData: Ref<WeeklyTimetable>
  isLoading: Ref<boolean>
  studentGroup: Ref<string>
  showPdfModal: Ref<boolean>
  isDownloading: Ref<boolean>
  pdfContentRef: Ref<HTMLElement | null>
  // Computed
  currentDaySchedule: ComputedRef<ScheduleSlot[]>
  uniqueTimeSlots: ComputedRef<string[]>
  // Methods
  getSlot: (day: string, timeRange: string) => ScheduleSlot | undefined
  fetchSchedule: () => Promise<void>
  downloadPdf: () => Promise<void>
}

export function useTimetable(): UseTimetableReturn {
  const activeDay = ref('')
  const weekDays: string[] = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday',
  ]

  const categoryStyles: CategoryStyles = {
    Lecture: 'bg-indigo-50 text-indigo-600 border-indigo-100',
    Lab: 'bg-green-50 text-green-600 border-green-100',
    Break: 'bg-slate-50 text-slate-400 border-slate-100',
    Activity: 'bg-amber-50 text-amber-600 border-amber-100',
  }

  function setToday(): void {
    const today = new Date().getDay()
    const index = today === 0 ? 6 : today - 1
    activeDay.value = weekDays[index] ?? 'Monday'
  }
  onMounted(() => {
    setToday()
  })

  const timetableData: Ref<WeeklyTimetable> = ref({})
  const isLoading = ref(true)
  const studentGroup = ref('Academic Timetable')

  const showPdfModal = ref(false)
  const isDownloading = ref(false)
  const pdfContentRef: Ref<HTMLElement | null> = ref(null)

  // ── Computed ────────────────────────────────────────────────────────────────

  const currentDaySchedule: ComputedRef<ScheduleSlot[]> = computed(() => {
    return timetableData.value[activeDay.value] || []
  })

  const uniqueTimeSlots: ComputedRef<string[]> = computed(() => {
    const times = new Set<string>()
    Object.values(timetableData.value).forEach(daySlots => {
      daySlots.forEach(slot => times.add(`${slot.startTime} - ${slot.endTime}`))
    })
    return Array.from(times).sort()
  })

  // ── Helpers ─────────────────────────────────────────────────────────────────

  const getSlot = (day: string, timeRange: string): ScheduleSlot | undefined => {
    const daySlots = timetableData.value[day] || []
    return daySlots.find(s => `${s.startTime} - ${s.endTime}` === timeRange)
  }

  // ── API ──────────────────────────────────────────────────────────────────────

  const fetchSchedule = async (): Promise<void> => {
    try {
      const res = await call<StudentScheduleResponse>('vidyaan.api.get_student_schedule')
      if (res?.success) {
        timetableData.value = res.timetable || {}
        if (res.student_group) {
          studentGroup.value = `Academic Timetable • ${res.student_group}`
        }
        // If current day has no classes, default to first day that does
        if (
          !timetableData.value[activeDay.value] ||
          (timetableData.value[activeDay.value]?.length ?? 0) === 0
        ) {
          const firstDayWithClasses = weekDays.find(
            d => timetableData.value[d] && timetableData.value[d].length > 0
          )
          if (firstDayWithClasses) {
            activeDay.value = firstDayWithClasses
          }
        }
      }
    } catch (err) {
      console.error('Failed to load schedule', err)
    } finally {
      isLoading.value = false
    }
  }

  // ── PDF ──────────────────────────────────────────────────────────────────────

  const downloadPdf = async (): Promise<void> => {
    isDownloading.value = true
    try {
      const tableHtml = pdfContentRef.value?.innerHTML ?? ''

      const htmlContent = renderTimetableHtml({
        tableHtml,
        studentGroup: studentGroup.value,
      })

      const res = await call<PdfGenerationResult>(
        'vidyaan.api_folder.pdf.generate_pdf_from_html',
        {
          html: htmlContent,
          filename: 'Academic_Timetable.pdf',
          options: JSON.stringify({
            format: 'A4',
            landscape: 'True',
            margin: { top: '15mm', bottom: '15mm', left: '15mm', right: '15mm' },
          }),
        }
      )

      if (res?.file_url) {
        window.open(res.file_url, '_blank')
        showPdfModal.value = false
      }
    } catch (e) {
      console.error('PDF Generate Error', e)
    } finally {
      isDownloading.value = false
    }
  }

  return {
    // State
    activeDay,
    weekDays,
    categoryStyles,
    timetableData,
    isLoading,
    studentGroup,
    showPdfModal,
    isDownloading,
    pdfContentRef,
    // Computed
    currentDaySchedule,
    uniqueTimeSlots,
    // Methods
    getSlot,
    fetchSchedule,
    downloadPdf,
  }
}
