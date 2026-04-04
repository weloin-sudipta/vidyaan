<template>
  <div class="min-h-screen bg-[#f8fafc] dark:bg-slate-950 p-4 lg:p-8 font-sans text-slate-900 dark:text-slate-100 transition-colors duration-300">
    <div class="max-w-[1440px] mx-auto space-y-6">

      <HeroHeader title="Class Schedule" :subtitle="studentGroup" icon="fa fa-graduation-cap">
        <button @click="toggleDarkMode" class="btn-icon h-12 w-12 dark:bg-slate-800 dark:border-slate-700 dark:text-yellow-400" title="Toggle Theme">
          <i :class="isDark ? 'fa fa-sun-o' : 'fa fa-moon-o'"></i>
        </button>
        <button @click="showPdfModal = true" class="btn-icon h-12 w-12 dark:bg-slate-800 dark:border-slate-700" title="Print Schedule">
          <i class="fa fa-print"></i>
        </button>
        <button @click="showPdfModal = true" class="btn-primary">Download PDF</button>
      </HeroHeader>

      <nav class="flex items-center gap-2 overflow-x-auto no-scrollbar pb-2">
        <button v-for="day in weekDays" :key="day" @click="activeDay = day" :class="[
          activeDay === day
            ? 'bg-slate-900 dark:bg-indigo-600 text-white shadow-xl shadow-slate-200 dark:shadow-indigo-900/20'
            : 'bg-white dark:bg-slate-900 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800',
          'px-8 py-3 rounded-2xl text-xs font-black uppercase tracking-widest transition-all border whitespace-nowrap'
        ]">
          {{ day }}
        </button>
      </nav>

      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div class="lg:col-span-8 space-y-4">
          <div v-if="currentDaySchedule.length > 0" class="space-y-4">
            <div v-for="(period, index) in currentDaySchedule" :key="index"
              class="group relative bg-white dark:bg-slate-900 rounded-[2rem] p-6 border border-slate-200/60 dark:border-slate-800 shadow-sm flex flex-col md:flex-row items-center gap-6 hover:border-indigo-200 dark:hover:border-indigo-500/50 transition-all">

              <div class="w-full md:w-32 flex flex-col items-center md:items-start shrink-0">
                <span class="text-sm font-black text-slate-800 dark:text-slate-100">{{ period.startTime }}</span>
                <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-tighter">{{ period.endTime }}</span>
              </div>

              <div class="hidden md:block w-px h-12 bg-slate-100 dark:bg-slate-800"></div>

              <div class="flex-1 text-center md:text-left">
                <div class="flex flex-col md:flex-row md:items-center gap-2 mb-1">
                  <h3 class="text-lg font-black text-slate-800 dark:text-slate-100 tracking-tight">{{ period.subject }}</h3>
                  <span :class="['px-2 py-0.5 rounded-md text-[9px] font-black uppercase tracking-tighter border', categoryStyles[period.type]]">
                    {{ period.type }}
                  </span>
                </div>
                <p class="text-xs font-bold text-slate-400 dark:text-slate-500 flex items-center justify-center md:justify-start gap-2">
                  <i class="fa fa-user-circle-o text-indigo-400 dark:text-indigo-500"></i> {{ period.teacher }}
                </p>
              </div>

              <div class="bg-slate-50 dark:bg-slate-800 px-6 py-3 rounded-2xl border border-slate-100 dark:border-slate-700 shrink-0">
                <span class="block text-[10px] font-black text-slate-300 dark:text-slate-600 uppercase tracking-widest mb-1 text-center">Room</span>
                <span class="block text-sm font-black text-slate-700 dark:text-slate-300 text-center">{{ period.room }}</span>
              </div>
            </div>
          </div>

          <div v-else class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-20 border border-dashed border-slate-200 dark:border-slate-800 text-center">
            <i class="fa fa-coffee text-slate-200 dark:text-slate-800 text-4xl mb-4"></i>
            <p class="text-sm font-black text-slate-400 dark:text-slate-600 uppercase tracking-widest">No classes scheduled</p>
          </div>
        </div>

        <div class="lg:col-span-4 space-y-6">
          <div class="bg-indigo-600 dark:bg-indigo-700 rounded-[2.5rem] p-8 text-white shadow-xl shadow-indigo-100 dark:shadow-none">
            <p class="text-[10px] font-black uppercase tracking-widest opacity-60 mb-6">Class Coordinator</p>
            <div class="flex items-center gap-4">
              <img src="https://i.pravatar.cc/150?u=teacher" class="w-14 h-14 rounded-2xl border-2 border-indigo-400 shadow-lg" />
              <div>
                <p class="text-lg font-black leading-tight">Prof. Sarah Jenkins</p>
                <p class="text-xs font-medium opacity-70">sarah.j@school.edu</p>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200/60 dark:border-slate-800 shadow-sm">
            <h3 class="text-xs font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest mb-6">Weekly Load</h3>
            <div class="space-y-4 text-slate-600 dark:text-slate-400">
              <div v-for="stat in ['Core Subjects: 18h', 'Labs: 4h', 'Extracurricular: 2h']" :key="stat" class="flex items-center gap-3">
                <div class="w-1.5 h-1.5 rounded-full bg-indigo-500"></div>
                <span class="text-xs font-bold">{{ stat }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showPdfModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-md">
      <div class="bg-white dark:bg-slate-900 rounded-[2rem] shadow-2xl w-full max-w-6xl max-h-[90vh] flex flex-col overflow-hidden animate-fade-in-up border dark:border-slate-800">
        <div class="px-8 py-6 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center bg-slate-50/50 dark:bg-slate-800/50">
          <div>
            <h2 class="text-xl font-black text-slate-800 dark:text-white tracking-tight">Routine Matrix</h2>
            <p class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mt-1">Preview Mode</p>
          </div>
          <button @click="showPdfModal = false" class="w-10 h-10 rounded-2xl bg-white dark:bg-slate-800 text-slate-400 hover:text-red-500 transition-all flex items-center justify-center border dark:border-slate-700">
            <i class="fa fa-times"></i>
          </button>
        </div>

        <div class="p-8 overflow-y-auto flex-1 dark:bg-slate-950 custom-scrollbar" ref="pdfContentRef">
          <div class="timetable-print-wrapper overflow-x-auto">
            <table class="w-full border-collapse text-center text-sm border dark:border-slate-800 rounded-xl overflow-hidden shadow-sm">
              <thead>
                <tr class="bg-slate-50/80 dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-bold uppercase text-[10px] tracking-widest border-b dark:border-slate-800">
                  <th class="p-5 bg-white dark:bg-slate-900 font-black text-indigo-900 dark:text-indigo-400 w-32 border-r dark:border-slate-800">Day \ Time</th>
                  <th v-for="time in uniqueTimeSlots" :key="time" class="p-5 border-r dark:border-slate-800 whitespace-nowrap">{{ time }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="day in weekDays" :key="day" class="border-b dark:border-slate-800 hover:bg-slate-50/50 dark:hover:bg-slate-800 transition-colors">
                  <td class="p-5 font-black text-slate-700 dark:text-slate-300 bg-slate-50/50 dark:bg-slate-800 w-32 border-r dark:border-slate-800">{{ day }}</td>
                  <td v-for="time in uniqueTimeSlots" :key="time" class="p-3 border-r dark:border-slate-800 relative min-w-[140px]">
                    <div v-if="getSlot(day, time)" class="flex flex-col gap-1 p-3 rounded-2xl bg-indigo-50/80 dark:bg-indigo-900/20 border border-indigo-100/50 dark:border-indigo-500/20 shadow-sm">
                      <span class="font-black text-indigo-900 dark:text-indigo-300 text-[13px]">{{ getSlot(day, time).subject }}</span>
                      <span class="text-[10px] text-indigo-500 dark:text-indigo-400 font-bold italic">{{ getSlot(day, time).teacher }}</span>
                      <span class="text-[9px] text-slate-400 dark:text-slate-500 font-black uppercase tracking-widest bg-white/60 dark:bg-slate-800 px-2 py-0.5 rounded-lg">{{ getSlot(day, time).room }}</span>
                    </div>
                    <span v-else class="text-slate-200 dark:text-slate-800 font-bold text-2xl">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="px-8 py-5 bg-slate-50/80 dark:bg-slate-800 border-t dark:border-slate-800 flex justify-end gap-4">
          <button @click="showPdfModal = false" class="px-6 py-3 font-bold text-slate-500 dark:text-slate-400 hover:text-slate-700 text-xs uppercase tracking-widest">Cancel</button>
          <button @click="downloadPdf" :disabled="isDownloading" class="btn-primary flex items-center gap-3">
            <i :class="isDownloading ? 'fa fa-spinner fa-spin' : 'fa fa-download'"></i>
            {{ isDownloading ? 'Processing...' : 'Export PDF' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import HeroHeader from '~/components/ui/HeroHeader.vue';
import { useTimetable } from '~/composable/useTimetable';

const config = useRuntimeConfig();
useSeoMeta({
  title: `Timetable - ${config.public.appName}`,
  description: `Explore your academic roadmap with Vidyaan's comprehensive breakdown of subjects, chapters, and lesson details.`,
  keywords: 'subjects, chapters, lessons, learning path, academic roadmap, exam preparation'
});

const {
  activeDay,
  weekDays,
  categoryStyles,
  isLoading,
  studentGroup,
  showPdfModal,
  isDownloading,
  pdfContentRef,
  currentDaySchedule,
  uniqueTimeSlots,
  getSlot,
  fetchSchedule,
  downloadPdf,
} = useTimetable();

onMounted(fetchSchedule);
</script>

<style scoped>
.btn-primary {
  @apply px-8 py-3 bg-indigo-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-[0.2em] shadow-xl shadow-indigo-100 hover:bg-indigo-700 transition-all active:scale-95;
}

.btn-icon {
  @apply flex items-center justify-center bg-white border border-slate-200 text-slate-400 rounded-2xl hover:text-indigo-600 transition-all shadow-sm;
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  @apply bg-slate-50 rounded-full;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  @apply bg-slate-200 rounded-full hover:bg-slate-300;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
.animate-fade-in-up {
  animation: fadeInUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>