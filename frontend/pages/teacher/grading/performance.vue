<template>
  <div class="p-6 lg:p-10 max-w-7xl mx-auto custom-scrollbar animate-in fade-in slide-in-from-bottom-4 duration-500">
    <HeroHeader title="Performance Analysis" subtitle="Data-Driven Insights" icon="fa fa-line-chart">
      <div class="flex gap-2">
        <select class="bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 px-4 py-2 rounded-xl text-xs font-bold border border-slate-200 dark:border-slate-800 outline-none">
          <option>All Sections</option>
          <option>Section A</option>
          <option>Section B</option>
        </select>
        <button class="bg-indigo-600 dark:bg-indigo-500 text-white px-6 py-2 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors shadow-lg shadow-indigo-200 dark:shadow-none"><i class="fa fa-download"></i> Export Report</button>
      </div>
    </HeroHeader>

    <div v-if="loading" class="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
      <UiSkeleton height="h-64" class="lg:col-span-2 rounded-[2.5rem]" />
      <UiSkeleton height="h-64" class="rounded-[2.5rem]" />
      <UiSkeleton height="h-96" class="lg:col-span-3 rounded-[2.5rem]" />
    </div>

    <div v-else class="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Chart Area -->
      <div class="lg:col-span-2 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 shadow-sm p-8">
        <h3 class="text-xs font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest mb-8 border-b border-slate-50 dark:border-slate-800/50 pb-4">Grade Distribution</h3>
        <div class="h-64 flex items-end justify-between gap-2 px-2">
          <!-- CSS Bar Chart Mock -->
          <div v-for="bin in distribution" :key="bin.label" class="w-full flex flex-col items-center group cursor-pointer">
            <div class="w-full bg-indigo-50 dark:bg-indigo-900/20 rounded-t-2xl hover:bg-indigo-400 dark:hover:bg-indigo-500 transition-all relative" :style="{ height: `${bin.pct}%` }">
               <span class="absolute -top-10 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[10px] font-bold py-1 px-2 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10">
                 {{ bin.count }} Students
               </span>
            </div>
            <span class="text-[9px] font-black uppercase text-slate-400 dark:text-slate-500 mt-3">{{ bin.label }}</span>
          </div>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="space-y-6">
        <div class="bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-[2.5rem] p-8 shadow-xl shadow-indigo-200 dark:shadow-none text-white overflow-hidden relative">
          <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-white/10 rounded-full blur-2xl"></div>
          <div class="relative z-10">
            <h4 class="text-[10px] font-black uppercase tracking-widest text-indigo-200 mb-6">Class Average</h4>
            <div class="flex items-baseline gap-2">
              <span class="text-6xl font-black">74.5</span>
              <span class="text-xl font-bold text-indigo-200">%</span>
            </div>
            <p class="text-[10px] font-bold mt-4 bg-white/20 inline-block px-3 py-1 rounded-full"><i class="fa fa-arrow-up"></i> +2.3% from last term</p>
          </div>
        </div>
        <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 shadow-sm p-8 flex items-center justify-between">
           <div>
             <h4 class="text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-1">Pass Rate</h4>
             <span class="text-2xl font-black text-slate-800 dark:text-slate-100">85%</span>
           </div>
           <div class="w-12 h-12 rounded-full border-4 border-slate-100 dark:border-slate-800 flex items-center justify-center text-green-500"><i class="fa fa-check"></i></div>
        </div>
      </div>

      <!-- At-Risk Radar -->
      <div class="lg:col-span-3 bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 shadow-sm p-8">
        <div class="flex items-center justify-between mb-8 border-b border-slate-50 dark:border-slate-800/50 pb-4">
          <h3 class="text-xs font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest flex items-center gap-2">
             <i class="fa fa-exclamation-triangle text-amber-500"></i> At-Risk Student Radar
          </h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="student in atRisk" :key="student.id" class="p-5 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-700/50 hover:bg-white dark:hover:bg-slate-800 transition-colors group cursor-pointer border border-transparent hover:border-amber-200 dark:hover:border-amber-500/30">
            <div class="flex justify-between items-start mb-4">
              <img :src="student.avatar" class="w-10 h-10 rounded-xl bg-slate-200 dark:bg-slate-700" />
              <span class="bg-red-50 dark:bg-red-900/20 text-red-500 dark:text-red-400 text-[9px] font-black uppercase tracking-widest px-2 py-1 rounded-lg">{{ student.reason }}</span>
            </div>
            <h4 class="text-sm font-black text-slate-800 dark:text-slate-200 group-hover:text-amber-600 dark:group-hover:text-amber-500 transition-colors">{{ student.name }}</h4>
            <p class="text-[10px] text-slate-400 dark:text-slate-500 font-bold tracking-widest">Curr Avg: <span class="text-slate-800 dark:text-slate-300">{{ student.avg }}%</span></p>
            <button class="mt-4 w-full py-2 bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-lg text-[9px] font-black uppercase tracking-widest group-hover:bg-amber-500 group-hover:text-white transition-colors">Contact Guardian</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'

const loading = ref(true)

const distribution = ref([
 { label: '0-40', count: 3, pct: 10 },
 { label: '41-50', count: 5, pct: 20 },
 { label: '51-60', count: 8, pct: 30 },
 { label: '61-70', count: 12, pct: 50 },
 { label: '71-80', count: 18, pct: 75 },
 { label: '81-90', count: 15, pct: 60 },
 { label: '91-100', count: 7, pct: 25 },
])

const atRisk = ref([
  { id: 1, name: 'Charlie Brown', avg: 35, reason: 'Failing Grade', avatar: 'https://i.pravatar.cc/150?u=3' },
  { id: 2, name: 'Dana Evans', avg: 45, reason: 'Poor Attendance', avatar: 'https://i.pravatar.cc/150?u=11' },
  { id: 3, name: 'Greg House', avg: 48, reason: 'Missed Assignments', avatar: 'https://i.pravatar.cc/150?u=12' }
])

onMounted(() => {
  setTimeout(() => loading.value = false, 700)
})
</script>
