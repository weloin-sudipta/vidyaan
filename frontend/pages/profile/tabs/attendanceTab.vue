<template>
  <div class="space-y-6 animate-in fade-in duration-500">

    <div v-if="loading" class="space-y-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <UiSkeleton height="h-24" v-for="i in 4" :key="i" class="rounded-[2rem]" />
      </div>
      <UiSkeleton height="h-64" class="rounded-[2.5rem]" />
    </div>

    <template v-else>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div v-for="stat in attendanceStats" :key="stat.label"
             :class="['p-6 rounded-[2rem] border shadow-sm', stat.bgClass]">
          <p :class="['text-[10px] font-black uppercase tracking-widest mb-1', stat.textClass]">{{ stat.label }}</p>
          <p :class="['text-2xl font-black', stat.textClass]">{{ stat.value }}</p>
        </div>
      </div>

      <UiCard padding="none" class="overflow-hidden">
        <div class="px-8 py-6 border-b border-slate-50 dark:border-slate-800/50 flex justify-between items-center transition-colors">
          <h3 class="text-sm font-black text-slate-800 dark:text-slate-100 uppercase tracking-wider transition-colors">Attendance Register</h3>
          <div class="flex gap-2">
             <span class="flex items-center gap-1 text-[10px] font-bold text-slate-400 dark:text-slate-500 transition-colors"><i class="fa fa-circle text-green-500 dark:text-green-400"></i> Present</span>
             <span class="flex items-center gap-1 text-[10px] font-bold text-slate-400 dark:text-slate-500 transition-colors"><i class="fa fa-circle text-red-500 dark:text-red-400"></i> Absent</span>
             <span class="flex items-center gap-1 text-[10px] font-bold text-slate-400 dark:text-slate-500 transition-colors"><i class="fa fa-circle text-amber-500 dark:text-amber-400"></i> Leave</span>
          </div>
        </div>

        <table class="w-full text-left border-collapse">
          <thead class="bg-slate-50 dark:bg-slate-800/50 transition-colors">
            <tr>
              <th class="p-6 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 transition-colors">Month</th>
              <th class="p-6 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 transition-colors">P</th>
              <th class="p-6 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 transition-colors">A</th>
              <th class="p-6 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 transition-colors">L</th>
              <th class="p-6 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 text-right transition-colors">Percentage</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-800/50 text-sm font-bold text-slate-700 dark:text-slate-300 transition-colors">
            <tr v-for="month in attendanceLog" :key="month.name" class="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
              <td class="p-6 font-black text-slate-800 dark:text-slate-100 transition-colors">{{ month.name }}</td>
              <td class="p-6 text-green-600 dark:text-green-400 transition-colors">{{ month.present }}</td>
              <td class="p-6 text-red-500 dark:text-red-400 transition-colors">{{ month.absent }}</td>
              <td class="p-6 text-amber-500 dark:text-amber-400 transition-colors">{{ month.leave }}</td>
              <td class="p-6 text-right">
                <div class="flex items-center justify-end gap-3">
                  <span class="text-xs">{{ month.percent }}%</span>
                  <div class="w-16 bg-slate-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden transition-colors">
                    <div class="bg-indigo-600 dark:bg-indigo-500 h-full transition-colors" :style="{ width: month.percent + '%' }"></div>
                  </div>
                </div>
              </td>
            </tr>
            <tr v-if="attendanceLog.length === 0">
              <td colspan="5" class="p-6 text-center text-slate-400 dark:text-slate-500 text-xs transition-colors">No attendance records found</td>
            </tr>
          </tbody>
        </table>
      </UiCard>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAttendanceSummary } from '~/composables/academics/useAttendance'

const { summary, loading, fetchSummary } = useAttendanceSummary()

onMounted(() => {
  fetchSummary()
})

const attendanceStats = computed(() => {
  if (!summary.value) {
    return [
      { label: 'Attendance Rate', value: '--%', bgClass: 'bg-indigo-600 dark:bg-indigo-700/80 transition-colors', textClass: 'text-white' },
      { label: 'Total Present', value: '-- Days', bgClass: 'bg-white dark:bg-slate-900 border-slate-200/60 dark:border-slate-800 transition-colors border', textClass: 'text-slate-800 dark:text-slate-100 transition-colors' },
      { label: 'Total Absent', value: '-- Days', bgClass: 'bg-red-50 dark:bg-red-900/20 border-red-100 dark:border-red-900/30 transition-colors', textClass: 'text-red-600 dark:text-red-400 transition-colors' },
      { label: 'Medical Leave', value: '-- Days', bgClass: 'bg-amber-50 dark:bg-amber-900/20 border-amber-100 dark:border-amber-900/30 transition-colors', textClass: 'text-amber-600 dark:text-amber-400 transition-colors' },
    ]
  }
  const s = summary.value
  return [
    { label: 'Attendance Rate', value: `${s.rate}%`, bgClass: 'bg-indigo-600 dark:bg-indigo-700/80 transition-colors border border-indigo-600 dark:border-indigo-700/80', textClass: 'text-white' },
    { label: 'Total Present', value: `${s.total_present} Days`, bgClass: 'bg-white dark:bg-slate-900 border-slate-200/60 dark:border-slate-800 transition-colors border', textClass: 'text-slate-800 dark:text-slate-100 transition-colors' },
    { label: 'Total Absent', value: `${String(s.total_absent).padStart(2, '0')} Days`, bgClass: 'bg-red-50 dark:bg-red-900/20 border-red-100 dark:border-red-900/30 transition-colors', textClass: 'text-red-600 dark:text-red-400 transition-colors' },
    { label: 'Medical Leave', value: `${String(s.total_leave).padStart(2, '0')} Days`, bgClass: 'bg-amber-50 dark:bg-amber-900/20 border-amber-100 dark:border-amber-900/30 transition-colors', textClass: 'text-amber-600 dark:text-amber-400 transition-colors' },
  ]
})

const attendanceLog = computed(() => {
  return summary.value?.months || []
})
</script>
