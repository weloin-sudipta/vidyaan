import { ref, computed, type Ref, type ComputedRef } from 'vue'
import { useRuntimeConfig } from '#imports'

interface GoogleCalendarEventDate {
  date?: string
  dateTime?: string
}

interface GoogleCalendarEvent {
  id?: string
  summary?: string
  start?: GoogleCalendarEventDate
  end?: GoogleCalendarEventDate
}

interface GoogleCalendarResponse {
  items?: GoogleCalendarEvent[]
}

export interface Holiday {
  date: string | undefined
  title: string | undefined
  type: 'holiday'
  icon: string
}

export interface UseHolidaysReturn {
  holidays: ComputedRef<Holiday[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  selectedMonth: Ref<number | null>
  fetchHolidays: (year: number | string) => Promise<void>
}

export function useHolidays(): UseHolidaysReturn {
  const holidays: Ref<GoogleCalendarEvent[]> = ref([])
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)
  const selectedMonth: Ref<number | null> = ref(null)

  const cache = new Map<number | string, GoogleCalendarEvent[]>()

  // Normalized for the calendar
  const normalizedHolidays: ComputedRef<Holiday[]> = computed(() =>
    (holidays.value || []).map(h => ({
      date: h.start?.date || h.start?.dateTime?.slice(0, 10),
      title: h.summary,
      type: 'holiday' as const,
      icon: 'fa fa-calendar',
    }))
  )

  const fetchHolidays = async (year: number | string): Promise<void> => {
    if (cache.has(year)) {
      holidays.value = cache.get(year) ?? []
      return
    }
    loading.value = true
    error.value = null
    try {
      const config = useRuntimeConfig()
      const apiKey = (config.public as { googleCalendarApiKey?: string })
        .googleCalendarApiKey
      const res = await fetch(
        `https://www.googleapis.com/calendar/v3/calendars/en.indian%23holiday@group.v.calendar.google.com/events?key=${apiKey}`
      )
      const data: GoogleCalendarResponse = await res.json()
      console.log(data)

      cache.set(year, data.items || [])
      holidays.value = data.items || []
    } catch (err) {
      error.value = (err as Error).message
    } finally {
      loading.value = false
    }
  }

  return {
    holidays: normalizedHolidays,
    loading,
    error,
    selectedMonth,
    fetchHolidays,
  }
}
