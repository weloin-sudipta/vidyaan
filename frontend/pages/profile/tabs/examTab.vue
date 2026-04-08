<template>
  <div>
    <!-- SKELETON LOADING -->
    <div v-if="loading" class="space-y-6 animate-in fade-in duration-500">
      <UiSkeleton height="h-4" width="w-64" class="ml-6" />
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div v-for="i in 2" :key="i" class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200/60 dark:border-slate-800 shadow-sm dark:shadow-none space-y-6 transition-colors">
          <div class="flex justify-between items-start">
            <div class="space-y-3 w-1/2">
               <UiSkeleton height="h-4" width="w-16" />
               <UiSkeleton height="h-6" width="w-48" />
               <UiSkeleton height="h-3" width="w-24" />
            </div>
            <UiSkeleton height="h-20" width="w-24" class="rounded-2xl shrink-0" />
          </div>
          <div class="space-y-3">
            <UiSkeleton height="h-20" class="rounded-[1.5rem]" v-for="j in 2" :key="'exam-'+j" />
          </div>
        </div>
      </div>
    </div>

    <!-- CONTENT -->
    <div v-else class="space-y-6 animate-in fade-in duration-500">
      <div v-if="Object.keys(groupedResults).length > 0" class="px-6 flex items-center gap-3">
      <span class="w-2 h-2 rounded-full bg-indigo-500"></span>
      <h2 class="text-xs font-black text-slate-400 uppercase tracking-widest">
        Academic History • {{ Object.keys(groupedResults).length }} Assessment Groups Found
      </h2>
    </div>

    <div class="grid grid-cols-1 xl:grid-cols-2 gap-6">
      
      <div v-for="(exams, groupName) in groupedResults" :key="groupName" 
           class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 border border-slate-200/60 dark:border-slate-800 shadow-sm dark:shadow-none transition-all hover:shadow-md dark:hover:shadow-none relative overflow-hidden group">
        
        <i class="fa fa-graduation-cap absolute -right-4 -top-4 text-8xl opacity-[0.03] -rotate-12 transition-transform group-hover:rotate-0"></i>

        <div class="relative z-10">
          <div class="flex justify-between items-start mb-8">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="w-2 h-2 rounded-full bg-indigo-500"></span>
                <p class="text-[10px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-widest transition-colors">
                  {{ exams[0].academic_year }}
                </p>
              </div>
              <h3 class="text-xl font-black text-slate-800 dark:text-slate-100 uppercase tracking-tight transition-colors">{{ groupName }}</h3>
              <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mt-1 transition-colors">
                {{ exams[0].academic_term }}
              </p>
            </div>

            <div class="bg-slate-900 dark:bg-slate-800 text-white px-6 py-3 rounded-2xl flex flex-col items-center shadow-xl shadow-slate-200 dark:shadow-none transition-colors">
              <span class="text-[9px] font-black opacity-50 uppercase tracking-widest">Status</span>
              <span class="text-xl font-black">PASSED</span>
            </div>
          </div>

          <div class="space-y-3">
            <div v-for="sub in exams" :key="sub.name" 
                 class="flex justify-between items-center p-5 bg-slate-50 dark:bg-slate-800/50 rounded-[1.5rem] group/item hover:bg-white dark:hover:bg-slate-800 hover:shadow-sm dark:hover:shadow-none border border-transparent hover:border-slate-100 dark:hover:border-slate-700 transition-all">
              <div class="flex items-center gap-4">
                <div :class="[getGradeColor(sub.grade), 'w-10 h-10 rounded-xl flex items-center justify-center text-white text-[10px] font-black shadow-sm dark:shadow-none']">
                  {{ sub.grade }}
                </div>
                <div class="flex flex-col">
                  <span class="text-sm font-black text-slate-700 dark:text-slate-200 capitalize transition-colors">{{ sub.course }}</span>
                  <span class="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-tighter transition-colors">{{ sub.grading_scale }}</span>
                </div>
              </div>
              <div class="text-right">
                <span class="text-base font-black text-slate-900 dark:text-slate-100 transition-colors">{{ sub.total_score }}</span>
                <span class="text-[10px] text-slate-400 dark:text-slate-500 font-bold ml-1 transition-colors">/ {{ sub.maximum_score }}</span>
              </div>
            </div>
          </div>

          <div v-if="exams.some(e => e.comment)" class="mt-8 pt-6 border-t border-slate-100 dark:border-slate-700 transition-colors">
            <p class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-2 transition-colors">Academic Remarks</p>
            <p class="text-xs font-bold text-slate-600 dark:text-slate-400 leading-relaxed italic transition-colors">
              "{{ exams.find(e => e.comment)?.comment || 'Consistent performance maintained throughout the term.' }}"
            </p>
          </div>
        </div>
      </div>

      <div v-if="Object.keys(groupedResults).length === 0" 
           class="col-span-full py-20 text-center bg-white dark:bg-slate-900 rounded-[2.5rem] border border-dashed border-slate-200 dark:border-slate-800 transition-colors">
        <i class="fa fa-folder-open-o text-4xl text-slate-200 dark:text-slate-600 mb-4 transition-colors"></i>
        <p class="text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] transition-colors">No performance data available yet</p>
      </div>
    </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useExamResults } from '~/composables/useExaminations';

const rawData = ref([]);
const loading = ref(true);

// 1. Group the flat API array by 'assessment_group'
const groupedResults = computed(() => {
  return rawData.value.reduce((acc, item) => {
    const group = item.assessment_group;
    if (!acc[group]) acc[group] = [];
    acc[group].push(item);
    return acc;
  }, {});
});

// 2. Dynamic Grade Colors
const getGradeColor = (grade) => {
  const g = grade?.toUpperCase();
  if (['A', 'A+', 'O'].includes(g)) return 'bg-emerald-500';
  if (['B', 'B+'].includes(g)) return 'bg-indigo-500';
  if (['C', 'C+'].includes(g)) return 'bg-amber-500';
  return 'bg-rose-500';
};

onMounted(async () => {
  try {
    const response = await useExamResults();
    // Ensure response is an array
    rawData.value = Array.isArray(response) ? response : [];
  } catch (error) {
    console.error("Failed to fetch results:", error);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.animate-in {
  animation: fadeIn 0.6s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>