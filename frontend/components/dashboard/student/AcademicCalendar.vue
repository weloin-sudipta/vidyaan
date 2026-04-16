<template>
  <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-6 border border-slate-200 dark:border-slate-800 shadow-sm dark:shadow-none transition-colors">
    
    <!-- Header -->
    <div class="flex items-center justify-between mb-3">
      <div>
        <h3 class="text-[9px] font-black uppercase tracking-[0.2em] text-slate-400 dark:text-slate-500">
          Academic Timeline
        </h3>
        <p class="text-base font-black text-slate-800 dark:text-white tracking-tight leading-tight">
          {{ monthYear }}
        </p>
      </div>

      <div class="flex gap-1.5">
        <button @click="prevMonth" class="w-7 h-7 rounded-lg bg-slate-50 dark:bg-slate-800/50 flex items-center justify-center text-slate-400 dark:text-slate-500 hover:bg-indigo-600 dark:hover:bg-indigo-500 hover:text-white transition-colors">
          <i class="fa fa-chevron-left text-[9px]"></i>
        </button>
        <button @click="nextMonth" class="w-7 h-7 rounded-lg bg-slate-50 dark:bg-slate-800/50 flex items-center justify-center text-slate-400 dark:text-slate-500 hover:bg-indigo-600 dark:hover:bg-indigo-500 hover:text-white transition-colors">
          <i class="fa fa-chevron-right text-[9px]"></i>
        </button>
      </div>
    </div>

    <!-- Week Days -->
    <div class="grid grid-cols-7 gap-1.5 mb-2">
      <div v-for="day in ['S','M','T','W','T','F','S']" :key="day" 
           class="text-center text-[8px] font-black text-slate-300 dark:text-slate-600 uppercase py-0.5">
        {{ day }}
      </div>

      <!-- Calendar Days -->
      <div v-for="date in calendarDays" :key="date.date || Math.random()"
           @click="selectDate(date)"
           class="relative aspect-square flex flex-col items-center justify-center rounded-xl cursor-pointer border border-transparent dark:border-slate-800 text-slate-700 dark:text-slate-300 transition-all"
           :class="[
             date.isToday ? 'bg-indigo-600 text-white scale-[0.98] !border-none' : 'hover:bg-slate-50 dark:hover:bg-slate-800',
             selectedDate === date.date ? 'ring-1 ring-indigo-400' : ''
           ]"
           :title="date.events.map(e => e.title).join(', ')">
        
        <span class="text-[12px] font-semibold">{{ date.day }}</span>

        <div v-if="date.events.length" class="absolute bottom-1 flex gap-[1px]">
          <div v-for="e in date.events.slice(0,2)" :key="e.title" 
               class="w-[4px] h-[4px] rounded-full"
               :class="{
                 'bg-red-500': e.type === 'exam',
                 'bg-green-400': e.type === 'holiday',
                 'bg-indigo-400': e.type === 'event',
                 'bg-rose-400': e.type === 'assignment',
                 'bg-white': date.isToday
               }"></div>
        </div>
      </div>
    </div>

    <!-- Selected Day Events -->
    <div class="border-t dark:border-slate-800 pt-3 mt-1">
      <p class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase mb-1.5">
        Selected Day Events
      </p>

      <div v-if="!selectedEvents.length" class="text-[9px] text-slate-400 dark:text-slate-500 py-1">
        No events for this day
      </div>

      <div v-for="item in selectedEvents" :key="item.title + item.date"
           class="flex items-center gap-2 mb-1.5">
        
        <div class="w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0"
             :class="getTypeStyles(item.type)">
          <i :class="item.icon" class="text-[10px]"></i>
        </div>

        <div class="min-w-0 flex-1">
          <h4 class="text-[10px] font-bold text-slate-800 dark:text-slate-200 truncate">
            {{ item.title }}
          </h4>
          <p class="text-[7px] text-slate-400 dark:text-slate-500 uppercase">
            {{ item.type }}
          </p>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue"
import { useExamination } from '~/composables/academics/useExaminations'
import { useEvents } from '~/composables/academics/useEvents'
import { useHolidays } from '~/composables/academics/useHolidays'
import { useAssignments } from '~/composables/academics/useAssignments'
import { useTeacherAssignments } from '~/composables/teacher/useTeacherAssignments'
import { useUserRole, formatDateString } from '~/composables/auth/useUserRole'

// Composables
const { fetchExams, exams } = useExamination()
const { loadEvents, events: frappeEvents } = useEvents()
const { holidays, fetchHolidays } = useHolidays()
const { userRole, isStudent, isTeacher, initialized, refreshUserRole } = useUserRole()

// Conditional assignment loading based on role
const studentAssignmentsLoader = ref(null)
const teacherAssignmentsLoader = ref(null)
const assignments = ref([])
const assignmentsFetchError = ref(null)

// State
const today = new Date()
const currentMonth = ref(today.getMonth())
const currentYear = ref(today.getFullYear())
const selectedDate = ref(null)
const selectedEvents = ref([])

// Helper - normalize dates and format events
const formatEvents = (items, type, icon, dateField = 'date') => 
  (items.value || [])
    .map(item => {
      const rawDate = item[dateField]
      const normalizedDate = formatDateString(rawDate)
      return {
        date: normalizedDate,
        title: item.title || item.subject,
        type,
        icon
      }
    })
    .filter(e => e.date !== null) // Remove events with invalid dates

// Events
const examEvents = computed(() => formatEvents(exams, 'exam', 'fa fa-pencil', 'date'))
const otherEvents = computed(() => formatEvents(frappeEvents, 'event', 'fa fa-microphone', 'fullDate'))
const assignmentEvents = computed(() => formatEvents(assignments, 'assignment', 'fa fa-book', 'due_date'))

const allEvents = computed(() => [
  ...examEvents.value,
  ...otherEvents.value,
  ...assignmentEvents.value,
  ...(holidays.value || [])
])

// Month label
const monthYear = computed(() => 
  new Date(currentYear.value, currentMonth.value)
    .toLocaleString('default', { month: 'long', year: 'numeric' })
)

// Calendar
const calendarDays = computed(() => {
  const days = []
  const firstDay = new Date(currentYear.value, currentMonth.value, 1).getDay()
  const totalDays = new Date(currentYear.value, currentMonth.value + 1, 0).getDate()

  for (let i = 0; i < firstDay; i++) {
    days.push({ day: '', date: null, events: [] })
  }

  for (let d = 1; d <= totalDays; d++) {
    const dateStr = `${currentYear.value}-${String(currentMonth.value + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`

    const dayEvents = allEvents.value.filter(e => e.date === dateStr)

    const isToday =
      d === today.getDate() &&
      currentMonth.value === today.getMonth() &&
      currentYear.value === today.getFullYear()

    days.push({
      day: d,
      date: dateStr,
      events: dayEvents,
      isToday
    })
  }

  return days
})

// Actions
const selectDate = (date) => {
  if (!date.date) return
  selectedDate.value = date.date
  selectedEvents.value = date.events
}

const prevMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

// Styles
const getTypeStyles = (type) => {
  const styles = {
    exam: 'bg-rose-50 dark:bg-rose-900/20 text-rose-500 dark:text-rose-400',
    assignment: 'bg-amber-50 dark:bg-amber-900/20 text-amber-500 dark:text-amber-400',
    holiday: 'bg-green-50 dark:bg-green-900/20 text-green-500 dark:text-green-400'
  }
  return styles[type] || 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-500 dark:text-indigo-400'
}

// Lifecycle
onMounted(async () => {
  try {
    // Load common events first (no role dependency)
    await fetchExams()
    loadEvents()
    await fetchHolidays(currentYear.value)

    // Wait for role detection if not already initialized
    if (!initialized.value) {
      console.log('[AcademicCalendar] Waiting for role detection...')
      // Give role detection a moment, check every 100ms for up to 5 seconds
      let waitCount = 0
      while (!initialized.value && waitCount < 50) {
        await new Promise(resolve => setTimeout(resolve, 100))
        waitCount++
      }
      if (!initialized.value) {
        console.warn('[AcademicCalendar] Role detection timeout, defaulting to student')
      }
    }

    console.log('[AcademicCalendar] Detected role:', userRole.value)

    // Load assignments based on detected role
    if (isStudent.value) {
      try {
        const studentComposable = useAssignments()
        await studentComposable.fetchAssignments()
        assignments.value = studentComposable.assignments?.value || []
        console.log('[AcademicCalendar] Loaded student assignments:', assignments.value)
      } catch (err) {
        console.warn('[AcademicCalendar] Failed to load student assignments:', err)
        assignmentsFetchError.value = 'Could not load assignments'
        assignments.value = []
      }
    } else if (isTeacher.value) {
      try {
        const teacherComposable = useTeacherAssignments()
        await teacherComposable.fetchAssignments() // Get all teacher assignments
        assignments.value = teacherComposable.assignments?.value || []
        console.log('[AcademicCalendar] Loaded teacher assignments:', assignments.value)
      } catch (err) {
        console.warn('[AcademicCalendar] Failed to load teacher assignments:', err)
        assignmentsFetchError.value = 'Could not load assignments'
        assignments.value = []
      }
    } else {
      console.warn('[AcademicCalendar] Unknown role:', userRole.value, ' - skipping assignments')
      assignments.value = []
    }
  } catch (err) {
    console.error('[AcademicCalendar] Error in lifecycle hook:', err)
  }
})

watch(currentYear, (year) => fetchHolidays(year))
</script>