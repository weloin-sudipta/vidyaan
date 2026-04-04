<template>
  <div class="p-6 lg:p-10 max-w-7xl mx-auto custom-scrollbar animate-in fade-in slide-in-from-bottom-4 duration-500">
    <HeroHeader title="Report Card Remarks" subtitle="End of Term Feedback" icon="fa fa-commenting-o">
      <div class="flex gap-2">
        <select class="bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 px-4 py-2 rounded-xl text-xs font-bold border border-slate-200 dark:border-slate-800 outline-none">
          <option>CS-101 (Section A)</option>
        </select>
        <button class="bg-indigo-600 dark:bg-indigo-500 text-white px-6 py-2 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors shadow-lg shadow-indigo-200 dark:shadow-none"><i class="fa fa-paper-plane"></i> Submit to Admin</button>
      </div>
    </HeroHeader>

    <div v-if="loading" class="mt-8 space-y-6">
      <UiSkeleton v-for="n in 3" :key="n" height="h-32" class="rounded-[2.5rem]" />
    </div>

    <div v-else class="mt-8 space-y-6">
      <!-- Search -->
      <div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-100 dark:border-slate-800 p-4 flex items-center gap-4 shadow-sm">
        <i class="fa fa-search text-slate-400 pl-4"></i>
        <input type="text" placeholder="Search students by name or roll number..." class="w-full bg-transparent border-none outline-none text-sm text-slate-700 dark:text-slate-200 font-bold placeholder-slate-300 dark:placeholder-slate-600">
      </div>

      <!-- Remarks List -->
      <div v-for="student in students" :key="student.id" class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 shadow-sm p-6 lg:p-8 flex flex-col md:flex-row gap-8 transition-colors">
         <div class="flex items-center gap-4 w-64 shrink-0 border-r border-slate-50 dark:border-slate-800/50 pr-4">
            <img :src="student.avatar" class="w-14 h-14 rounded-2xl bg-slate-200 dark:bg-slate-700 object-cover" />
            <div>
               <h4 class="text-sm font-black text-slate-800 dark:text-slate-200 leading-tight">{{ student.name }}</h4>
               <p class="text-[10px] text-slate-400 dark:text-slate-500 font-bold tracking-widest mt-1">Roll: {{ student.roll }}</p>
               <span class="inline-block mt-2 px-2 py-0.5 rounded text-[8px] font-black uppercase tracking-widest border"
                     :class="student.grade === 'A' ? 'bg-green-50 border-green-200 text-green-600 dark:bg-green-900/30 dark:border-green-800 dark:text-green-400' : 'bg-slate-100 border-slate-200 text-slate-500 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-400'">
                 Grade: {{ student.grade }}
               </span>
            </div>
         </div>
         <div class="flex-1">
            <h5 class="text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-3">Teacher's Remark</h5>
            <textarea v-model="student.remark" rows="3" class="w-full bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-4 text-xs font-medium text-slate-700 dark:text-slate-300 border border-transparent focus:border-indigo-300 dark:focus:border-indigo-600 outline-none transition-all resize-none placeholder-slate-400 dark:placeholder-slate-500" placeholder="Write a constructive remark for the student's report card..."></textarea>
            <div class="flex gap-2 mt-3">
              <button class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-[9px] font-bold text-slate-500 dark:text-slate-400 hover:text-indigo-500 hover:border-indigo-200 transition-colors shadow-sm" @click="student.remark = 'Excellent performance. Keep it up!'">Excellent</button>
              <button class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-[9px] font-bold text-slate-500 dark:text-slate-400 hover:text-indigo-500 hover:border-indigo-200 transition-colors shadow-sm" @click="student.remark = 'Good effort, but needs to participate more in class.'">Needs Participation</button>
              <button class="px-3 py-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-[9px] font-bold text-slate-500 dark:text-slate-400 hover:text-indigo-500 hover:border-indigo-200 transition-colors shadow-sm" @click="student.remark = 'Needs to improve focus and complete assignments on time.'">Improve Focus</button>
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

const students = ref([
  { id: 1, name: 'Alice Smith', roll: 'CS01', avatar: 'https://i.pravatar.cc/150?u=1', grade: 'A', remark: '' },
  { id: 2, name: 'Bob Jones', roll: 'CS02', avatar: 'https://i.pravatar.cc/150?u=2', grade: 'B', remark: '' },
  { id: 3, name: 'Charlie Brown', roll: 'CS03', avatar: 'https://i.pravatar.cc/150?u=3', grade: 'F', remark: '' }
])

onMounted(() => {
  setTimeout(() => loading.value = false, 600)
})
</script>
