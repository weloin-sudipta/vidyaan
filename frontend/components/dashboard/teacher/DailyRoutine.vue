<template>
  <div class="bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm p-6 flex flex-col gap-5 transition-colors">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-slate-50 dark:border-slate-800/50 pb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-indigo-500 to-indigo-400 rounded-2xl flex items-center justify-center text-white text-sm shadow-lg shadow-indigo-200 dark:shadow-none">
          <i class="fa fa-calendar"></i>
        </div>
        <div>
          <h6 class="text-sm font-black text-slate-800 dark:text-slate-200 leading-tight tracking-tight">Classes & Routine</h6>
          <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">{{ classes.length }} Classes Today</span>
        </div>
      </div>
      <NuxtLink to="/teacher/academics/my-classes">
        <button class="text-[10px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-widest bg-indigo-50 dark:bg-indigo-900/20 hover:bg-indigo-100 dark:hover:bg-indigo-900/40 transition-colors px-3 py-1.5 rounded-xl flex items-center gap-1.5">
          Full Schedule <i class="fa fa-arrow-right text-[9px]"></i>
        </button>
      </NuxtLink>
    </div>

    <!-- Timeline List -->
    <div class="relative mt-2 pl-4 border-l-2 border-slate-100 dark:border-slate-800 ml-5 space-y-8 py-2">
      <div v-for="(cls, i) in classes" :key="i" class="relative group cursor-pointer">
         <!-- Dot -->
         <div class="absolute -left-[23px] top-1 w-4 h-4 rounded-full border-4 border-white dark:border-slate-900 bg-slate-300 dark:bg-slate-600 group-hover:bg-indigo-500 transition-colors z-10"></div>
         
         <div class="pl-2 -mt-1.5">
            <p class="text-[10px] font-black text-slate-400 dark:text-slate-500 group-hover:text-indigo-500 uppercase tracking-widest mb-1 transition-colors">{{ cls.time }}</p>
            <div class="bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-4 border border-slate-100 dark:border-slate-700/50 group-hover:border-indigo-200 dark:group-hover:border-indigo-500/30 transition-all flex justify-between items-center shadow-sm hover:shadow">
               <div>
                  <h4 class="text-sm font-black text-slate-800 dark:text-slate-200">{{ cls.subject }}</h4>
                  <p class="text-[11px] text-slate-400 dark:text-slate-500 mt-0.5">Section {{ cls.section }}</p>
               </div>
               <div class="bg-white dark:bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 shadow-sm text-center">
                 <span class="block text-[8px] font-black text-slate-400 uppercase tracking-widest">Room</span>
                 <span class="block text-xs font-black text-slate-700 dark:text-slate-200">{{ cls.room }}</span>
               </div>
            </div>
         </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  classes: {
    type: Array,
    default: () => []
  }
})
</script>
