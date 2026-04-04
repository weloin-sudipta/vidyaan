<template>
  <div class="bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm p-6 flex flex-col gap-5 transition-colors">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-slate-50 dark:border-slate-800/50 pb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-emerald-500 to-emerald-400 rounded-2xl flex items-center justify-center text-white text-sm shadow-lg shadow-emerald-200 dark:shadow-none">
          <i class="fa fa-users"></i>
        </div>
        <div>
          <h6 class="text-sm font-black text-slate-800 dark:text-slate-200 leading-tight tracking-tight">Rapid Attendance</h6>
          <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Mark Register</span>
        </div>
      </div>
      <button class="text-[10px] font-black text-emerald-600 dark:text-emerald-400 uppercase tracking-widest bg-emerald-50 dark:bg-emerald-900/20 hover:bg-emerald-100 dark:hover:bg-emerald-900/40 transition-colors px-4 py-2 rounded-xl">
        Mark All Present
      </button>
    </div>

    <!-- Quick Action List -->
    <div class="space-y-3">
       <div v-for="student in unMarkedStudents" :key="student.id" class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-700/50 transition-colors group hover:border-emerald-200 dark:hover:border-emerald-500/30">
          <div class="flex items-center gap-3">
             <img :src="student.avatar" class="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700" />
             <div>
                <p class="text-xs font-bold text-slate-700 dark:text-slate-300">{{ student.name }}</p>
                <p class="text-[10px] text-slate-400 dark:text-slate-500">Roll: {{ student.roll }}</p>
             </div>
          </div>
          <div class="flex gap-2 opacity-100 lg:opacity-0 group-hover:opacity-100 transition-opacity">
             <button class="w-8 h-8 rounded-xl bg-emerald-100 dark:bg-emerald-900/40 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-200 dark:hover:bg-emerald-900/60 transition-colors flex items-center justify-center">
               <i class="fa fa-check text-xs"></i>
             </button>
             <button class="w-8 h-8 rounded-xl bg-red-100 dark:bg-red-900/40 text-red-600 dark:text-red-400 hover:bg-red-200 dark:hover:bg-red-900/60 transition-colors flex items-center justify-center">
               <i class="fa fa-times text-xs"></i>
             </button>
             <button class="w-8 h-8 rounded-xl bg-amber-100 dark:bg-amber-900/40 text-amber-600 dark:text-amber-400 hover:bg-amber-200 dark:hover:bg-amber-900/60 transition-colors flex items-center justify-center" title="Leave">
               <i class="fa fa-clock-o text-xs"></i>
             </button>
          </div>
       </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  unMarkedStudents: {
    type: Array,
    default: () => []
  }
})
</script>
