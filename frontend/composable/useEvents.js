import { ref, computed } from 'vue'
import { createResource } from '~/composable/useFrappeFetch'

export const useEvents = () => {
  const events = ref([])
  const eventTags = ref([])
  const loading = ref(true)
  const errorMessage = ref(null)

  const categoryStyles = {
    Academic: 'bg-indigo-50 text-indigo-600 border-indigo-100',
    Sports: 'bg-green-50 text-green-600 border-green-100',
    Arts: 'bg-purple-50 text-purple-600 border-purple-100',
    Holiday: 'bg-red-50 text-red-600 border-red-100',
    Workshop: 'bg-amber-50 text-amber-600 border-amber-100',
    Music: 'bg-pink-50 text-pink-600 border-pink-100',
    Science: 'bg-cyan-50 text-cyan-600 border-cyan-100',
    General: 'bg-slate-50 text-slate-600 border-slate-100'
  }

  const getCategoryStyle = (tag) => categoryStyles[tag] || categoryStyles.General

  const getEventStatus = (dateStr) => {
    if (!dateStr) return 'General'
    const eventDate = new Date(dateStr)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    eventDate.setHours(0, 0, 0, 0)

    if (eventDate.getTime() === today.getTime()) return 'Ongoing'
    if (eventDate > today) return 'Upcoming'
    return 'Past'
  }

  const formatEventData = (rawList) => {
    if (!rawList || !Array.isArray(rawList)) return []

    return rawList.map(item => {
      const eventDate = item.date ? new Date(item.date) : null
      const timeStr = (item.start_time && item.end_time)
        ? `${item.start_time} - ${item.end_time}`
        : item.start_time || null

      return {
        id: item.name,
        day: eventDate ? eventDate.getDate().toString().padStart(2, '0') : '--',
        month: eventDate ? eventDate.toLocaleString('default', { month: 'short' }).toUpperCase() : '',
        fullDate: item.date,
        title: item.event_name || 'Untitled Event',
        tags: item.tags || [],
        time: timeStr,
        location: item.room || null,
        description: item.description || '',
        programs: item.programs || [],
        studentGroups: item.student_groups || [],
        status: getEventStatus(item.date)
      }
    })
  }

  const loadEvents = async () => {
    loading.value = true
    errorMessage.value = null
    try {
      const resource = createResource({
        url: 'vidyaan.api_folder.event.get_all_events',
      })
      const data = await resource.submit()

      if (data && data.success !== false) {
        const rawEvents = data.events || []
        events.value = formatEventData(rawEvents)
        if (data.tags && Array.isArray(data.tags)) {
          eventTags.value = data.tags
        }
      } else if (data && data.success === false) {
        if (data.message === 'No student record found') {
          events.value = []
          eventTags.value = []
        } else {
          errorMessage.value = data.message || 'Failed to load events'
        }
      } else {
        if (Array.isArray(data)) {
          events.value = formatEventData(data)
        } else {
          events.value = []
        }
      }
    } catch (error) {
      console.error('Failed to fetch events:', error)
      errorMessage.value = 'Failed to connect to the server'
    } finally {
      loading.value = false
    }
  }

  // Dynamic filters — Upcoming first, History last
  const dynamicFilters = computed(() => {
    const base = ['Upcoming', 'Ongoing', 'All Events', 'History']
    const tagFilters = eventTags.value.filter(t => !base.includes(t))
    return [...base, ...tagFilters]
  })

  // Filtered events by active filter
  const getFilteredEvents = (activeFilter) => {
    return computed(() => {
      const f = activeFilter.value

      // History — only past events, newest first
      if (f === 'History') {
        return [...events.value]
          .filter(e => e.status === 'Past')
          .sort((a, b) => new Date(b.fullDate) - new Date(a.fullDate))
      }

      // All Events — today (Ongoing) + future (Upcoming) only, sorted ascending
      if (f === 'All Events') {
        return [...events.value]
          .filter(e => e.status === 'Upcoming' || e.status === 'Ongoing')
          .sort((a, b) => new Date(a.fullDate) - new Date(b.fullDate))
      }

      // Upcoming — future only, ascending
      if (f === 'Upcoming') {
        return [...events.value]
          .filter(e => e.status === 'Upcoming')
          .sort((a, b) => new Date(a.fullDate) - new Date(b.fullDate))
      }

      // Ongoing — today only
      if (f === 'Ongoing') {
        return events.value.filter(e => e.status === 'Ongoing')
      }

      // Tag filter — exclude past
      return events.value.filter(e =>
        e.status !== 'Past' &&
        e.tags.some(tag => tag.toLowerCase() === f.toLowerCase())
      )
    })
  }

  // Sidebar: next 7 days
  const upcomingDeadlines = computed(() => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const weekLater = new Date(today)
    weekLater.setDate(weekLater.getDate() + 7)

    return events.value
      .filter(e => {
        if (!e.fullDate) return false
        const d = new Date(e.fullDate)
        d.setHours(0, 0, 0, 0)
        return d >= today && d <= weekLater
      })
      .sort((a, b) => new Date(a.fullDate) - new Date(b.fullDate))
      .slice(0, 5)
      .map(e => ({
        id: e.id,
        title: e.title,
        date: formatDeadlineDate(e.fullDate)
      }))
  })

  const formatDeadlineDate = (dateStr) => {
    if (!dateStr) return ''
    const eventDate = new Date(dateStr)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    eventDate.setHours(0, 0, 0, 0)

    const diffDays = Math.round((eventDate - today) / (1000 * 60 * 60 * 24))
    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Tomorrow'
    if (diffDays < 0) return `${Math.abs(diffDays)} days ago`
    return `In ${diffDays} days`
  }

  // Today's events
  const todaysEvents = computed(() => {
    const todayStr = new Date().toISOString().split('T')[0]
    return events.value.filter(e => e.fullDate === todayStr)
  })

  // Calendar dot checker
  const isEventDate = (date, calendarDate) => {
    const year = calendarDate.value.getFullYear()
    const month = calendarDate.value.getMonth()
    return events.value.some(e => {
      if (!e.fullDate) return false
      const d = new Date(e.fullDate)
      return d.getFullYear() === year && d.getMonth() === month && d.getDate() === date
    })
  }

  return {
    events,
    eventTags,
    loading,
    errorMessage,
    categoryStyles,
    getCategoryStyle,
    loadEvents,
    dynamicFilters,
    getFilteredEvents,
    upcomingDeadlines,
    todaysEvents,
    isEventDate,
  }
}