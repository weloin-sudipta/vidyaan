<template>
  <div class="bg-white dark:bg-slate-900 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-sm p-6 flex flex-col gap-5 transition-colors">
    <!-- Header flex -->
    <div class="flex items-center justify-between border-b border-slate-50 dark:border-slate-800/50 pb-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 bg-gradient-to-br from-rose-500 to-rose-400 rounded-2xl flex items-center justify-center text-white text-sm shadow-lg shadow-rose-200 dark:shadow-none">
          <i class="fa fa-bullhorn"></i>
        </div>
        <div>
          <h6 class="text-sm font-black text-slate-800 dark:text-slate-200 leading-tight tracking-tight">Announcements</h6>
          <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Pin-Board</span>
        </div>
      </div>
      <button class="text-[10px] font-black text-rose-600 dark:text-rose-400 uppercase tracking-widest bg-rose-50 dark:bg-rose-900/20 hover:bg-rose-100 dark:hover:bg-rose-900/40 transition-colors px-3 py-1.5 rounded-xl flex items-center gap-1.5">
        View All <i class="fa fa-arrow-right text-[9px]"></i>
      </button>
    </div>

    <!-- Quick Post Box -->
    <!-- <div class="bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-4 border border-slate-100 dark:border-slate-700/50 transition-colors focus-within:ring-2 focus-within:ring-rose-200 dark:focus-within:ring-rose-900/50">
       <textarea class="w-full bg-transparent text-xs text-slate-700 dark:text-slate-300 placeholder-slate-400 dark:placeholder-slate-500 resize-none outline-none border-none focus:ring-0" rows="2" placeholder="Post a quick announcement to your classes..."></textarea>
       <div class="flex justify-between items-center mt-2 pt-2 border-t border-slate-200 dark:border-slate-700">
          <div class="flex gap-2">
             <button class="w-8 h-8 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-400 hover:text-rose-500 transition-colors flex items-center justify-center shadow-sm"><i class="fa fa-paperclip text-xs"></i></button>
          </div>
          <button class="px-5 py-2 bg-slate-800 dark:bg-slate-100 text-white dark:text-slate-900 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-black dark:hover:bg-white transition-colors shadow-sm">Post Notice</button>
       </div>
    </div> -->

    <!-- Recent Posts -->
    <div class="space-y-4 mt-2">
       <h6 class="text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest mb-1">Recent Updates</h6>
       <div v-for="notice in recentNotices" :key="notice.id" class="flex gap-4 relative p-4 bg-slate-50 dark:bg-slate-800/30 rounded-2xl overflow-hidden group hover:bg-white dark:hover:bg-slate-800 border border-transparent hover:border-slate-200 dark:hover:border-slate-700 hover:shadow-md transition-all cursor-pointer">
          <div class="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-rose-400 to-rose-500"></div>
          <div class="pl-2 w-full">
             <div class="flex justify-between items-start mb-1">
                <p class="text-xs font-bold text-slate-700 dark:text-slate-200 leading-tight group-hover:text-rose-600 dark:group-hover:text-rose-400 transition-colors">{{ notice.title }}</p>
                <span class="text-[8px] font-black text-slate-400 dark:text-slate-500 uppercase whitespace-nowrap">{{ notice.date }}</span>
             </div>
             <p class="text-[10px] text-slate-500 dark:text-slate-400 leading-relaxed">{{ notice.desc }}</p>
          </div>
       </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  recentNotices: {
    type: Array,
    default: () => []
  }
})
</script>
