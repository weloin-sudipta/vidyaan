import { ref, computed } from "vue"

export function useHolidays() {
    const holidays = ref([])
    const loading = ref(false)
    const error = ref(null)
    const selectedMonth = ref(null)

    const cache = new Map()

    // ✅ Normalized for the calendar
    const normalizedHolidays = computed(() =>
        (holidays.value || []).map(h => ({
            date: h.start?.date || h.start?.dateTime?.slice(0, 10),
            title: h.summary,
            type: "holiday",
            icon: "fa fa-calendar"
        }))
    )

    const fetchHolidays = async (year) => {
        if (cache.has(year)) {
            holidays.value = cache.get(year)
            return
        }
        loading.value = true
        error.value = null
        try {
            const config = useRuntimeConfig()
            const res = await fetch(`https://www.googleapis.com/calendar/v3/calendars/en.indian%23holiday@group.v.calendar.google.com/events?key=${config.public.googleCalendarApiKey}`)
            const data = await res.json()
            console.log(data);

            cache.set(year, data.items || [])
            holidays.value = data.items || []
        } catch (err) {
            error.value = err.message
        } finally {
            loading.value = false
        }
    }

    return {
        holidays: normalizedHolidays,
        loading,
        error,
        selectedMonth,
        fetchHolidays
    }
}