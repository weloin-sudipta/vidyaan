<template>
  <div class="min-h-screen bg-[#f8fafc] dark:bg-slate-950 p-4 lg:p-8 font-sans text-slate-900 dark:text-slate-100 transition-colors">
    <div class="max-w-[1440px] mx-auto space-y-6 animate-in fade-in duration-500">

    <UiCard class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-black text-slate-800 dark:text-slate-100 tracking-tight transition-colors">School Events & Calendar</h2>
        <p class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mt-1 transition-colors">Academic Year 2025-26</p>
      </div>
      <div class="flex gap-2">
        <button @click="showCalendarModal = true" class="btn-icon h-12 w-12">
          <i class="fa fa-calendar-o"></i>
        </button>
      </div>
    </UiCard>

    <!-- Loading State -->
    <div v-if="loading" class="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full">
      <div class="lg:col-span-8 flex flex-col gap-6">
        <UiSkeleton height="h-32" />
        <UiSkeleton height="h-32" />
      </div>
      <div class="lg:col-span-4 flex flex-col gap-6">
        <UiSkeleton height="h-64" />
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="errorMessage" class="bg-red-50 dark:bg-red-900/20 rounded-[2.5rem] p-8 border border-red-100 dark:border-red-900/30 text-center transition-colors">
      <i class="fa fa-exclamation-triangle text-red-400 text-2xl mb-3"></i>
      <p class="text-sm font-bold text-red-600 dark:text-red-400 transition-colors">{{ errorMessage }}</p>
      <button @click="loadEvents" class="mt-4 px-6 py-2 bg-red-100 dark:bg-red-800/40 text-red-700 dark:text-red-300 rounded-xl text-xs font-bold hover:bg-red-200 dark:hover:bg-red-700/50 transition-colors">
        Retry
      </button>
    </div>

    <template v-else>
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 animate-in">
        <div class="lg:col-span-8 space-y-6">

          <!-- Filter Tabs -->
          <div class="flex gap-2 overflow-x-auto no-scrollbar pb-2">
            <button
              v-for="filter in dynamicFilters"
              :key="filter"
              @click="activeFilter = filter"
              :class="[
                activeFilter === filter
                  ? isHistoryFilter(filter)
                    ? 'bg-slate-800 dark:bg-slate-700 text-white shadow-lg shadow-slate-200 dark:shadow-none'
                    : 'bg-indigo-600 dark:bg-indigo-500 text-white shadow-lg shadow-indigo-100 dark:shadow-none'
                  : 'bg-white dark:bg-slate-900 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-800',
                'px-6 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest border transition-all whitespace-nowrap flex items-center gap-2'
              ]"
            >
              <i v-if="filter === 'History'" class="fa fa-clock-o"></i>
              {{ filter }}
            </button>
          </div>

          <!-- History Banner -->
          <div v-if="activeFilter === 'History'" class="bg-slate-800 dark:bg-slate-800/80 rounded-[2rem] px-6 py-4 flex items-center gap-4 transition-colors">
            <div class="w-8 h-8 bg-slate-700 dark:bg-slate-900 rounded-xl flex items-center justify-center shrink-0 transition-colors">
              <i class="fa fa-history text-slate-300 dark:text-slate-500 text-sm transition-colors"></i>
            </div>
            <div>
              <p class="text-xs font-black text-white">Past Events</p>
              <p class="text-[10px] text-slate-400 dark:text-slate-500 font-medium transition-colors">Showing events that have already taken place, newest first.</p>
            </div>
          </div>

          <!-- Empty State -->
          <UiCard v-if="filteredEvents.length === 0" padding="p-12" class="text-center transition-colors">
            <i :class="[
              'text-slate-300 dark:text-slate-700 text-4xl mb-4 transition-colors',
              activeFilter === 'History' ? 'fa fa-history' : 'fa fa-calendar-check-o'
            ]"></i>
            <p class="text-sm font-bold text-slate-500 dark:text-slate-400 transition-colors">No events found</p>
            <p class="text-xs text-slate-400 dark:text-slate-500 mt-1 transition-colors">{{ emptyMessage }}</p>
          </UiCard>

          <!-- Event Cards -->
          <UiCard
            v-for="event in filteredEvents"
            :key="event.id"
            padding="p-6"
            :class="[
              'flex flex-col md:flex-row gap-6 hover:shadow-md dark:hover:shadow-none transition-all group',
              event.status === 'Past'
                ? 'border-slate-100 dark:border-slate-800 opacity-75 hover:opacity-100'
                : 'border-slate-200/60 dark:border-slate-700/60'
            ]"
          >
            <!-- Date Box -->
            <div :class="[
              'flex flex-col items-center justify-center rounded-3xl w-full md:w-24 h-24 border shrink-0 transition-colors',
              event.status === 'Past'
                ? 'bg-slate-100 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700/50'
                : 'bg-slate-50 dark:bg-slate-800 border-slate-100 dark:border-slate-700/50'
            ]">
              <span :class="[
                'text-[10px] font-black uppercase tracking-widest transition-colors',
                event.status === 'Past' ? 'text-slate-400 dark:text-slate-500' : 'text-indigo-500 dark:text-indigo-400'
              ]">{{ event.month }}</span>
              <span :class="[
                'text-3xl font-black transition-colors',
                event.status === 'Past' ? 'text-slate-400 dark:text-slate-500' : 'text-slate-800 dark:text-slate-200'
              ]">{{ event.day }}</span>
            </div>

            <div class="flex-1">
              <div class="flex justify-between items-start mb-2">
                <div class="flex flex-wrap gap-1">
                  <!-- Past badge -->
                  <span v-if="event.status === 'Past'"
                    class="px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter border bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-500 border-slate-200 dark:border-slate-700 transition-colors">
                    Past
                  </span>
                  <span
                    v-for="tag in event.tags"
                    :key="tag"
                    :class="[
                      'px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter border',
                      event.status === 'Past' ? 'opacity-50' : '',
                      getCategoryStyle(tag)
                    ]"
                  >
                    {{ tag }}
                  </span>
                  <span
                    v-if="event.tags.length === 0 && event.status !== 'Past'"
                    :class="['px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter border', categoryStyles.General]"
                  >
                    General
                  </span>
                </div>
                <span v-if="event.time" class="text-[10px] font-bold text-slate-400 dark:text-slate-500 whitespace-nowrap ml-2 transition-colors">
                  <i class="fa fa-clock-o mr-1"></i> {{ event.time }}
                </span>
              </div>

              <h3 :class="[
                'text-lg font-black transition-colors',
                event.status === 'Past'
                  ? 'text-slate-500 dark:text-slate-400 group-hover:text-slate-700 dark:group-hover:text-slate-200'
                  : 'text-slate-800 dark:text-slate-100 group-hover:text-indigo-600 dark:group-hover:text-indigo-400'
              ]">
                {{ event.title }}
              </h3>
              <p v-if="event.description" class="text-xs font-medium text-slate-500 dark:text-slate-400 mt-2 leading-relaxed line-clamp-2 transition-colors">
                {{ event.description }}
              </p>

              <div class="flex items-center gap-4 mt-4">
                <div v-if="event.location" class="flex items-center gap-1 text-[10px] font-bold text-slate-400 dark:text-slate-500 transition-colors">
                  <i class="fa fa-map-marker text-indigo-400"></i> {{ event.location }}
                </div>
                <div v-if="event.programs && event.programs.length > 0" class="flex items-center gap-1 text-[10px] font-bold text-slate-400 dark:text-slate-500 transition-colors">
                  <i class="fa fa-graduation-cap text-purple-400"></i> {{ event.programs.join(', ') }}
                </div>
              </div>
            </div>
          </UiCard>

        </div>

        <!-- Sidebar -->
        <div class="lg:col-span-4 space-y-6">

          <!-- Upcoming Events Panel -->
          <UiCard variant="dark">
            <h3 class="text-xs font-black uppercase tracking-widest opacity-40 mb-6">Next 7 Days</h3>
            <div v-if="upcomingDeadlines.length > 0" class="space-y-6">
              <div v-for="deadline in upcomingDeadlines" :key="deadline.id" class="flex gap-4">
                <div class="w-1 h-10 bg-indigo-500 rounded-full shrink-0"></div>
                <div>
                  <p class="text-xs font-bold">{{ deadline.title }}</p>
                  <p class="text-[10px] opacity-50 font-medium">{{ deadline.date }}</p>
                </div>
              </div>
            </div>
            <div v-else class="text-xs opacity-40 font-medium">No events in the next 7 days</div>
          </UiCard>

          <!-- Activity Tags -->
          <UiCard>
            <h3 class="text-xs font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-6 transition-colors">Activity Tags</h3>
            <div v-if="eventTags.length > 0" class="flex flex-wrap gap-2">
              <span
                v-for="tag in eventTags"
                :key="tag"
                @click="activeFilter = tag"
                :class="[
                  activeFilter === tag
                    ? 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 border-indigo-100 dark:border-indigo-900/30'
                    : 'bg-slate-50 dark:bg-slate-800/50 text-slate-500 dark:text-slate-400 border-slate-100 dark:border-slate-700/50',
                  'px-3 py-1 text-[10px] font-bold rounded-lg border cursor-pointer hover:bg-indigo-50 dark:hover:bg-indigo-900/40 hover:text-indigo-600 dark:hover:text-indigo-300 transition-colors'
                ]"
              >
                #{{ tag }}
              </span>
            </div>
            <p v-else class="text-xs text-slate-400 dark:text-slate-500 transition-colors">No tags available</p>
          </UiCard>
        </div>
      </div>
    </template>

    <!-- Calendar Modal -->
    <div v-if="showCalendarModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" @click="showCalendarModal = false"></div>

      <div class="relative bg-white dark:bg-slate-900 w-full max-w-md rounded-[2.5rem] shadow-2xl overflow-hidden animate-modal transition-colors">
        <div class="p-8 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center transition-colors">
          <div class="flex items-center gap-4">
            <button @click="changeMonth(-1)" class="w-8 h-8 bg-slate-50 dark:bg-slate-800 text-slate-400 dark:text-slate-500 rounded-xl hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors flex items-center justify-center">
              <i class="fa fa-chevron-left text-xs"></i>
            </button>
            <div>
              <h3 class="text-xl font-black text-slate-800 dark:text-slate-100 tracking-tight transition-colors">{{ currentMonthName }} {{ currentYear }}</h3>
              <p class="text-[9px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mt-1 transition-colors">Event Calendar</p>
            </div>
            <button @click="changeMonth(1)" class="w-8 h-8 bg-slate-50 dark:bg-slate-800 text-slate-400 dark:text-slate-500 rounded-xl hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors flex items-center justify-center">
              <i class="fa fa-chevron-right text-xs"></i>
            </button>
          </div>
          <button @click="showCalendarModal = false" class="w-10 h-10 bg-slate-50 dark:bg-slate-800 text-slate-400 dark:text-slate-500 rounded-2xl hover:text-rose-500 dark:hover:text-rose-400 transition-colors">
            <i class="fa fa-times"></i>
          </button>
        </div>

        <div class="p-8">
          <div class="grid grid-cols-7 gap-2 mb-4">
            <div v-for="(day, idx) in ['S','M','T','W','T','F','S']" :key="'day-'+idx"
                 class="text-center text-[10px] font-black text-slate-300 uppercase">
              {{ day }}
            </div>
          </div>
          <div class="grid grid-cols-7 gap-2">
            <div v-for="i in firstDayOfMonth" :key="'empty'+i" class="h-10"></div>
            <div
              v-for="date in daysInMonth"
              :key="date"
              :class="[
                isEventDateForCalendar(date) ? 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 border-indigo-100 dark:border-indigo-900/30 shadow-sm dark:shadow-none' :
                isToday(date) ? 'bg-slate-900 dark:bg-indigo-600 text-white' :
                'text-slate-400 dark:text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800',
                'h-10 rounded-xl flex flex-col items-center justify-center text-xs font-bold border border-transparent transition-all cursor-pointer relative'
              ]"
            >
              {{ date }}
              <div v-if="isEventDateForCalendar(date)" class="absolute bottom-1.5 w-1 h-1 bg-indigo-500 dark:bg-indigo-400 rounded-full transition-colors"></div>
            </div>
          </div>
        </div>

        <div class="px-8 pb-8">
          <div class="bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-4 border border-slate-100 dark:border-slate-800 transition-colors">
            <p class="text-[9px] font-black text-slate-400 dark:text-slate-500 uppercase mb-3 transition-colors">Today's Events</p>
            <div v-if="todaysEvents.length > 0" class="space-y-2">
              <div v-for="ev in todaysEvents" :key="ev.id" class="flex items-center gap-3">
                <div class="w-2 h-2 rounded-full bg-indigo-500 dark:bg-indigo-400 transition-colors"></div>
                <div>
                  <p class="text-xs font-black text-slate-700 dark:text-slate-200 transition-colors">{{ ev.title }}</p>
                  <p v-if="ev.time" class="text-[10px] text-slate-400 dark:text-slate-500 transition-colors">{{ ev.time }}</p>
                </div>
              </div>
            </div>
            <div v-else class="flex items-center gap-3">
              <div class="w-2 h-2 rounded-full bg-emerald-500 dark:bg-emerald-400 transition-colors"></div>
              <p class="text-xs font-black text-slate-700 dark:text-slate-300 transition-colors">No events scheduled for today</p>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useEvents } from '~/composables/useEvents'

const {
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
} = useEvents()

const showCalendarModal = ref(false)
const activeFilter = ref('Upcoming') // default
const calendarDate = ref(new Date())

const filteredEvents = getFilteredEvents(activeFilter)

const isHistoryFilter = (f) => f === 'History'

const emptyMessage = computed(() => {
  const msgs = {
    Upcoming: 'No upcoming events scheduled.',
    Ongoing: 'No events are happening today.',
    History: 'No past events found.',
    'All Events': 'No current or upcoming events scheduled.',
  }
  return msgs[activeFilter.value] || `No events match the "${activeFilter.value}" filter.`
})

// Calendar helpers
const currentMonthName = computed(() => calendarDate.value.toLocaleString('default', { month: 'long' }))
const currentYear = computed(() => calendarDate.value.getFullYear())
const daysInMonth = computed(() => new Date(calendarDate.value.getFullYear(), calendarDate.value.getMonth() + 1, 0).getDate())
const firstDayOfMonth = computed(() => new Date(calendarDate.value.getFullYear(), calendarDate.value.getMonth(), 1).getDay())

const changeMonth = (delta) => {
  const d = new Date(calendarDate.value)
  d.setMonth(d.getMonth() + delta)
  calendarDate.value = d
}

const isEventDateForCalendar = (date) => isEventDate(date, calendarDate)

const isToday = (date) => {
  const today = new Date()
  return calendarDate.value.getFullYear() === today.getFullYear()
    && calendarDate.value.getMonth() === today.getMonth()
    && date === today.getDate()
}

onMounted(() => {
  loadEvents()
})
</script>

<style scoped>
.btn-primary { @apply px-6 py-3 bg-indigo-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest shadow-xl shadow-indigo-100 dark:shadow-none hover:bg-indigo-700 dark:hover:bg-indigo-500 transition-colors; }
.btn-icon { @apply flex items-center justify-center bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-400 dark:text-slate-500 rounded-2xl hover:text-indigo-600 dark:hover:text-indigo-400 hover:border-indigo-100 dark:hover:border-indigo-800 transition-colors; }
.btn-action-gray { @apply w-10 h-10 flex items-center justify-center bg-slate-50 dark:bg-slate-800/50 text-slate-400 dark:text-slate-500 rounded-xl hover:bg-slate-900 dark:hover:bg-slate-700 hover:text-white dark:hover:text-slate-200 transition-colors; }
.btn-action-indigo { @apply px-5 py-2 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 rounded-xl text-[10px] font-black uppercase hover:bg-indigo-600 dark:hover:bg-indigo-500 hover:text-white transition-colors; }
.no-scrollbar::-webkit-scrollbar { display: none; }

@keyframes modalEntry {
  from { opacity: 0; transform: scale(0.9) translateY(20px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}
.animate-modal { animation: modalEntry 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
</style>