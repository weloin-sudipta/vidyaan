<template>
  <div class="bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm dark:shadow-none overflow-hidden transition-colors">

    <div class="p-6 flex flex-col gap-5">

      <!-- HEADER -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-400 rounded-[0.85rem] flex items-center justify-center text-white text-sm shadow-lg shadow-green-200 dark:shadow-none">
            <i class="fa fa-bar-chart"></i>
          </div>
          <div>
            <h6 class="text-sm font-black text-slate-800 dark:text-white leading-tight tracking-tight transition-colors">Attendance</h6>
            <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest transition-colors">{{ totalDays }} total days</span>
          </div>
        </div>
        <span class="text-[10px] font-black uppercase tracking-widest px-3 py-1.5 rounded-full transition-colors"
          :class="percentage >= 75
            ? 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400'
            : 'bg-red-50 dark:bg-red-900/20 text-red-500 dark:text-red-400'">
          {{ percentage >= 75 ? 'Good' : 'Low' }}
        </span>
      </div>

      <!-- CIRCULAR PROGRESS -->
      <div class="flex justify-center py-2">
        <div class="relative w-36 h-36">
          <svg class="w-full h-full -rotate-90" viewBox="0 0 36 36">
            <!-- Track -->
            <circle
              cx="18" cy="18" r="16"
              fill="none"
              stroke="currentColor"
              stroke-width="3.5"
              class="text-slate-100 dark:text-slate-800 transition-colors"
            />
            <!-- Progress -->
            <circle
              cx="18" cy="18" r="16"
              fill="none"
              :stroke="percentage >= 75 ? '#22c55e' : '#ef4444'"
              stroke-width="3.5"
              stroke-linecap="round"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="dashOffset"
              class="transition-all duration-700 ease-out"
            />
          </svg>

          <!-- Center -->
          <div class="absolute inset-0 flex flex-col items-center justify-center">
            <span class="text-3xl font-black text-slate-800 dark:text-white leading-none transition-colors">{{ percentage }}%</span>
            <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mt-1 transition-colors">Present</span>
          </div>
        </div>
      </div>

      <!-- DOT + LINE STATS -->
      <div class="flex flex-col">

        <div class="flex items-start gap-3 py-3">
          <div class="flex flex-col items-center flex-shrink-0 w-4 pt-1">
            <div class="relative w-3.5 h-3.5 flex-shrink-0">
              <div class="absolute inset-0 rounded-full border-2 border-slate-200 dark:border-slate-700 transition-colors"></div>
              <div class="absolute inset-[3px] rounded-full bg-green-500"></div>
            </div>
            <div class="w-px flex-1 min-h-[20px] mt-1 bg-gradient-to-b from-slate-200 dark:from-slate-700 to-transparent transition-colors"></div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-[13px] font-black text-slate-800 dark:text-slate-100 leading-tight mb-0.5 transition-colors">Present Days</p>
            <p class="text-[11px] text-slate-400 dark:text-slate-500 transition-colors">Days attended in class</p>
          </div>
          <span class="text-sm font-black text-green-500 dark:text-green-400 flex-shrink-0 pt-0.5 transition-colors">{{ presentDays }}</span>
        </div>

        <div class="flex items-start gap-3 py-3">
          <div class="flex flex-col items-center flex-shrink-0 w-4 pt-1">
            <div class="relative w-3.5 h-3.5 flex-shrink-0">
              <div class="absolute inset-0 rounded-full border-2 border-slate-200 dark:border-slate-700 transition-colors"></div>
              <div class="absolute inset-[3px] rounded-full bg-red-500"></div>
            </div>
            <div class="w-px flex-1 min-h-[20px] mt-1 bg-gradient-to-b from-slate-200 dark:from-slate-700 to-transparent transition-colors"></div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-[13px] font-black text-slate-800 dark:text-slate-100 leading-tight mb-0.5 transition-colors">Absent Days</p>
            <p class="text-[11px] text-slate-400 dark:text-slate-500 transition-colors">Days missed without leave</p>
          </div>
          <span class="text-sm font-black text-red-500 dark:text-red-400 flex-shrink-0 pt-0.5 transition-colors">{{ absentDays }}</span>
        </div>

        <div class="flex items-start gap-3 py-3">
          <div class="flex flex-col items-center flex-shrink-0 w-4 pt-1">
            <div class="relative w-3.5 h-3.5 flex-shrink-0">
              <div class="absolute inset-0 rounded-full border-2 border-slate-200 dark:border-slate-700 transition-colors"></div>
              <div class="absolute inset-[3px] rounded-full bg-amber-400"></div>
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-[13px] font-black text-slate-800 dark:text-slate-100 leading-tight mb-0.5 transition-colors">Leave Days</p>
            <p class="text-[11px] text-slate-400 dark:text-slate-500 transition-colors">Approved leave taken</p>
          </div>
          <span class="text-sm font-black text-amber-500 dark:text-amber-400 flex-shrink-0 pt-0.5 transition-colors">{{ leaveDays }}</span>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  attendance: {
    type: Object,
    required: true,
    default: () => ({
      present_days: 0,
      absent_days: 0,
      leave_days: 0,
      total_days: 0
    })
  }
})

const presentDays = computed(() => props.attendance.present_days || 0)
const absentDays  = computed(() => props.attendance.absent_days  || 0)
const leaveDays   = computed(() => props.attendance.leave_days   || 0)
const totalDays   = computed(() => props.attendance.total_days   || 0)

const percentage = computed(() => {
  if (!totalDays.value) return 0
  return Math.round((presentDays.value / totalDays.value) * 100)
})

const circumference = computed(() => 2 * Math.PI * 16)

const dashOffset = computed(() => {
  return circumference.value * (1 - percentage.value / 100)
})
</script>