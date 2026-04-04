<template>
  <div class="bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm p-6 flex flex-col gap-5 transition-colors">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-slate-50 dark:border-slate-800/50 pb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-amber-500 to-amber-400 rounded-2xl flex items-center justify-center text-white text-sm shadow-lg shadow-amber-200 dark:shadow-none">
          <i class="fa fa-check-square-o"></i>
        </div>
        <div>
          <h6 class="text-sm font-black text-slate-800 dark:text-slate-200 leading-tight tracking-tight">Speed Grader Queue</h6>
          <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">{{ pendingItems.length }} Pending Tasks</span>
        </div>
      </div>
      <!-- <button class="text-[10px] font-black text-amber-600 dark:text-amber-400 uppercase tracking-widest bg-amber-50 dark:bg-amber-900/20 hover:bg-amber-100 dark:hover:bg-amber-900/40 transition-colors px-3 py-1.5 rounded-xl flex items-center gap-1.5">
        View all <i class="fa fa-arrow-right text-[9px]"></i>
      </button> -->
    </div>

    <!-- List -->
    <div class="flex flex-col gap-3 mt-1">
      <div v-for="item in pendingItems" :key="item.id" class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-700/50 hover:border-amber-200 dark:hover:border-amber-500/30 transition-all cursor-pointer group">
         <div class="flex justify-between items-center mb-0">
            <div>
               <p class="text-[13px] font-black text-slate-800 dark:text-slate-200 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">{{ item.title }}</p>
               <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-1">Class {{ item.class_name }} • <span class="text-amber-500 dark:text-amber-400 font-bold">{{ item.submissions }} Papers to Grade</span></p>
            </div>
            <button class="px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 shadow-sm group-hover:bg-amber-500 group-hover:text-white group-hover:border-transparent transition-all">Grade Now</button>
         </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  pendingItems: {
    type: Array,
    default: () => []
  }
})
</script>
