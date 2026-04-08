<template>
  <div class="min-h-screen bg-[#f8fafc] dark:bg-slate-950 p-4 lg:p-8 font-sans text-slate-900 dark:text-slate-100 transition-colors animate-in fade-in duration-500">
    <div class="max-w-[1440px] mx-auto space-y-6">

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

        <div class="lg:col-span-8 space-y-6">
          <UiCard padding="none" class="overflow-hidden mb-6">

            <div class="p-8 border-b border-slate-50 dark:border-slate-800/50 flex justify-between items-center transition-colors">
              <div class="flex items-center gap-4">
                <div class="w-12 h-12 bg-indigo-600 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-indigo-100 dark:shadow-none transition-colors">
                  <i class="fa fa-calendar text-xl"></i>
                </div>
                <h2 class="text-xl font-black text-slate-800 dark:text-slate-100 tracking-tight transition-colors">
                  {{ monthNames[currentMonth] }} <span class="text-slate-300 dark:text-slate-600 transition-colors">{{ currentYear }}</span>
                </h2>
              </div>

              <div class="flex items-center gap-2 bg-slate-50 dark:bg-slate-800/50 p-1.5 rounded-2xl transition-colors">
                <button @click="changeMonth(-1)" class="btn-nav"><i class="fa fa-chevron-left"></i></button>
                <button @click="setToday" class="px-4 py-2 text-[10px] font-black uppercase text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">Today</button>
                <button @click="changeMonth(1)" class="btn-nav"><i class="fa fa-chevron-right"></i></button>
              </div>
            </div>

            <div class="p-8">
              <div v-if="loading" class="grid grid-cols-7 gap-3 mb-6">
                <UiSkeleton height="h-10" v-for="i in 35" :key="i" class="aspect-square rounded-2xl" />
              </div>
              <template v-else>
                <div class="animate-in">
                  <div class="grid grid-cols-7 mb-6">
                  <div v-for="day in weekDays" :key="day" class="text-center text-[10px] font-black text-slate-300 dark:text-slate-600 uppercase tracking-widest transition-colors">{{ day }}</div>
                </div>

                <div class="grid grid-cols-7 gap-3">
                  <div v-for="empty in firstDayOfMonth" :key="'empty-'+empty" class="aspect-square"></div>

                  <div v-for="date in daysInMonth" :key="date"
                       class="aspect-square rounded-[1.5rem] flex flex-col items-center justify-center relative transition-all cursor-pointer hover:shadow-md dark:hover:shadow-none"
                       :class="getDayStatusClass(date)">

                    <span class="text-xs font-black transition-colors" :class="isToday(date) ? 'text-indigo-600 dark:text-indigo-400' : 'text-slate-400 dark:text-slate-500'">{{ date }}</span>

                    <div class="mt-2">
                      <div v-if="getAttendanceStatus(date) === 'P'" class="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                      <div v-else-if="getAttendanceStatus(date) === 'A'" class="w-1.5 h-1.5 bg-red-400 rounded-full"></div>
                      <div v-else-if="getAttendanceStatus(date) === 'L'" class="w-1.5 h-1.5 bg-amber-500 rounded-full"></div>
                    </div>
                  </div>
                </div>
                </div>
              </template>
            </div>

            <div class="px-8 py-4 bg-slate-50/50 dark:bg-slate-800/50 border-t border-slate-50 dark:border-slate-800/50 flex gap-6 transition-colors">
              <div v-for="l in ['Present', 'Absent', 'Leave']" :key="l" class="flex items-center gap-2">
                <span :class="['w-2 h-2 rounded-full transition-colors', l === 'Present' ? 'bg-green-500 dark:bg-green-400' : l === 'Absent' ? 'bg-red-400 dark:bg-red-500' : 'bg-amber-500 dark:bg-amber-400']"></span>
                <span class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-tighter transition-colors">{{ l }}</span>
              </div>
            </div>
          </UiCard>
        </div>

        <div class="lg:col-span-4 space-y-6">

          <UiCard variant="dark" class="shadow-slate-200">
            <h3 class="text-xs font-black uppercase opacity-40 mb-8 tracking-widest text-center">Monthly Score</h3>
            <div class="relative w-32 h-32 mx-auto mb-6 flex items-center justify-center">
               <svg class="w-full h-full transform -rotate-90">
                 <circle cx="64" cy="64" r="58" stroke="currentColor" stroke-width="8" fill="transparent" class="text-white/10" />
                 <circle cx="64" cy="64" r="58" stroke="currentColor" stroke-width="8" fill="transparent" class="text-indigo-500"
                   :stroke-dasharray="364.4"
                   :stroke-dashoffset="364.4 - (364.4 * monthlyPercent / 100)" />
               </svg>
               <span class="absolute text-2xl font-black">{{ monthlyPercent }}%</span>
            </div>
            <p class="text-center text-[10px] font-bold opacity-60">High attendance improves student performance by up to 12%.</p>
          </UiCard>

          <UiCard>
            <h3 class="text-xs font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest mb-6 transition-colors">Attendance Summary</h3>
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase transition-colors">Total Present</span>
                <span class="text-sm font-black text-green-600 dark:text-green-500 transition-colors">{{ monthlyPresent }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase transition-colors">Total Absent</span>
                <span class="text-sm font-black text-red-500 transition-colors">{{ monthlyAbsent }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase transition-colors">Leave</span>
                <span class="text-sm font-black text-amber-500 dark:text-amber-400 transition-colors">{{ monthlyLeave }}</span>
              </div>
            </div>
          </UiCard>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useAttendance } from '~/composables/useAttendance'

const config = useRuntimeConfig()
useSeoMeta({
    title: `Attendance - ${config.public.appName}`,
})

const { attendanceMap, loading, fetchAttendance } = useAttendance()

const today = new Date();
const currentMonth = ref(today.getMonth());
const currentYear = ref(today.getFullYear());

const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const daysInMonth = computed(() => new Date(currentYear.value, currentMonth.value + 1, 0).getDate());
const firstDayOfMonth = computed(() => new Date(currentYear.value, currentMonth.value, 1).getDay());

const loadAttendanceData = () => {
  fetchAttendance(currentMonth.value, currentYear.value)
}

onMounted(() => {
  loadAttendanceData()
})

const changeMonth = (step) => {
  currentMonth.value += step;
  if (currentMonth.value > 11) { currentMonth.value = 0; currentYear.value++; }
  else if (currentMonth.value < 0) { currentMonth.value = 11; currentYear.value--; }
  loadAttendanceData()
};

const setToday = () => {
  currentMonth.value = today.getMonth();
  currentYear.value = today.getFullYear();
  loadAttendanceData()
};

const isToday = (date) => date === today.getDate() && currentMonth.value === today.getMonth() && currentYear.value === today.getFullYear();

const getAttendanceStatus = (date) => attendanceMap.value[`${currentYear.value}-${currentMonth.value}-${date}`] || null;

const getDayStatusClass = (date) => {
  const status = getAttendanceStatus(date);
  if (status === 'P') return 'bg-green-50/50 dark:bg-green-900/10 border border-green-100 dark:border-green-900/30';
  if (status === 'A') return 'bg-red-50/50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/30';
  if (status === 'L') return 'bg-amber-50/50 dark:bg-amber-900/10 border border-amber-100 dark:border-amber-900/30';
  return 'bg-white dark:bg-slate-900 border border-slate-50 dark:border-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-800';
};

const monthlyPresent = computed(() => Object.values(attendanceMap.value).filter(v => v === 'P').length)
const monthlyAbsent = computed(() => Object.values(attendanceMap.value).filter(v => v === 'A').length)
const monthlyLeave = computed(() => Object.values(attendanceMap.value).filter(v => v === 'L').length)
const monthlyPercent = computed(() => {
  const total = monthlyPresent.value + monthlyAbsent.value + monthlyLeave.value
  return total > 0 ? Math.round((monthlyPresent.value / total) * 100) : 0
})
</script>

<style scoped>
.btn-primary { @apply px-8 py-3 bg-indigo-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] shadow-xl shadow-indigo-100 dark:shadow-none hover:bg-indigo-700 active:scale-95 transition-all; }
.btn-icon { @apply flex items-center justify-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-400 dark:text-slate-500 rounded-2xl hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors; }
.btn-nav { @apply w-10 h-10 flex items-center justify-center bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-700/50 rounded-xl hover:shadow-md dark:hover:shadow-none transition-all text-slate-400 dark:text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400; }
</style>
