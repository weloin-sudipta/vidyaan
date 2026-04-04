<template>
  <div class="p-6 lg:p-10 max-w-7xl mx-auto custom-scrollbar animate-in fade-in slide-in-from-bottom-4 duration-500">
    <HeroHeader title="Faculty Library" subtitle="Digital Resources & Rentals" icon="fa fa-book">
      <div class="flex gap-2">
        <button class="bg-indigo-600 dark:bg-indigo-500 text-white px-6 py-2 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors shadow-lg shadow-indigo-200 dark:shadow-none"><i class="fa fa-search"></i> Browse Catalog</button>
      </div>
    </HeroHeader>

    <div v-if="loading" class="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
      <UiSkeleton height="h-64" class="rounded-[2.5rem]" />
      <UiSkeleton height="h-64" class="rounded-[2.5rem]" />
    </div>

    <div v-else class="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Active Rentals -->
      <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 shadow-sm p-8">
        <h3 class="text-xs font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest mb-6 border-b border-slate-50 dark:border-slate-800/50 pb-4">My Issued Resources</h3>
        
        <div class="space-y-4">
          <div v-for="book in issuedBooks" :key="book.id" class="flex items-start gap-4 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-700/50 shadow-sm">
            <div class="w-12 h-16 bg-slate-200 dark:bg-slate-700 rounded border border-slate-300 dark:border-slate-600 flex items-center justify-center shrink-0">
               <i class="fa fa-book text-slate-400"></i>
             </div>
             <div>
               <h4 class="text-sm font-black text-slate-800 dark:text-slate-200 mb-1 leading-tight">{{ book.title }}</h4>
               <p class="text-[10px] text-slate-500 dark:text-slate-400 font-bold mb-2">Issue Date: {{ book.issued }}</p>
               <span class="text-[8px] font-black uppercase tracking-widest px-2 py-0.5 rounded"
                     :class="book.daysLeft < 3 ? 'bg-amber-50 text-amber-500 dark:bg-amber-900/30' : 'bg-green-50 text-green-500 dark:bg-green-900/30'">
                 {{ book.daysLeft }} days remaining
               </span>
             </div>
          </div>
        </div>
      </div>

      <!-- Resource Requests -->
      <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-100 dark:border-slate-800 shadow-sm p-8">
        <div class="flex justify-between items-center mb-6 border-b border-slate-50 dark:border-slate-800/50 pb-4">
          <h3 class="text-xs font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest">Digital Subscriptions</h3>
          <button class="text-[10px] font-black text-indigo-500 uppercase">Request Access</button>
        </div>
        
        <div class="bg-slate-50 dark:bg-slate-800/50 p-6 rounded-2xl border border-slate-100 dark:border-slate-700/50 text-center flex flex-col items-center">
           <div class="w-16 h-16 rounded-full bg-indigo-100 dark:bg-indigo-900/40 text-indigo-500 flex items-center justify-center mb-4">
             <i class="fa fa-laptop text-2xl"></i>
           </div>
           <h4 class="text-sm font-black text-slate-800 dark:text-slate-200 mb-2">IEEE Xplore Digital Library</h4>
           <p class="text-xs text-slate-500 dark:text-slate-400 mb-4 max-w-sm">You have active campus-wide access to IEEE research papers and journals.</p>
           <button class="px-6 py-2 rounded-xl bg-slate-800 dark:bg-slate-100 text-white dark:text-slate-900 text-[10px] font-black uppercase tracking-widest">Go to Portal</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import HeroHeader from '~/components/ui/HeroHeader.vue'

const loading = ref(true)

const issuedBooks = ref([
  { id: 1, title: 'Introduction to Algorithms (4th Edition)', issued: 'Oct 10, 2026', daysLeft: 15 },
  { id: 2, title: 'Head First Design Patterns', issued: 'Oct 05, 2026', daysLeft: 2 }
])

onMounted(() => {
  setTimeout(() => loading.value = false, 500)
})
</script>
