import { ref, computed, type Ref, type ComputedRef } from 'vue'
import { createResource } from '~/composables/api/useFrappeFetch'

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
  const holidays: Ref<Holiday[]> = ref([])
  const loading = ref(false)
  const error: Ref<string | null> = ref(null)
  const selectedMonth: Ref<number | null> = ref(null)

  const cache = new Map<number | string, Holiday[]>()

  const fetchHolidays = async (year: number | string): Promise<void> => {
    if (cache.has(year)) {
      holidays.value = cache.get(year) ?? []
      return
    }
    loading.value = true
    error.value = null
    try {
      const resource = createResource<Holiday[]>({
        url: 'vidyaan.api.get_holidays',
        params: { year }
      })
      const data = await resource.submit()
      
      const holidayItems = (Array.isArray(data) ? data : []) as Holiday[]
      
      cache.set(year, holidayItems)
      holidays.value = holidayItems
    } catch (err) {
      error.value = (err as Error).message
    } finally {
      loading.value = false
    }
  }

  return {
    holidays: computed(() => holidays.value),
    loading,
    error,
    selectedMonth,
    fetchHolidays,
  }
}
