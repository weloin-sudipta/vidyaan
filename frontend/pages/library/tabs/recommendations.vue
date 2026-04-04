<template>
  <div class="space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700">

    <div class="bg-slate-900 rounded-[2.5rem] p-8 lg:p-12 overflow-hidden relative shadow-2xl">
      <div class="relative z-10 max-w-2xl">
        <span class="text-indigo-400 text-[10px] font-black uppercase tracking-[0.3em] mb-4 block">Tailored for you</span>
        <h1 class="text-3xl lg:text-5xl font-black text-white leading-tight mb-4">
          Recommended <br/> <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">Reading List</span>
        </h1>
        <p class="text-slate-400 text-sm font-medium max-w-md leading-relaxed">
          Based on your enrollment and your recent interests.
        </p>
      </div>
      <div class="absolute -right-20 -top-20 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl"></div>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-12">
      <div v-for="i in 3" :key="i" class="space-y-6">
        <div class="px-2">
          <UiSkeleton height="h-6" class="w-48 mb-2 rounded" />
          <UiSkeleton height="h-3" class="w-64 rounded" />
        </div>
        <div class="flex gap-6 overflow-x-auto pb-6">
          <UiSkeleton height="h-96" v-for="j in 4" :key="j" class="min-w-[280px] rounded-3xl" />
        </div>
      </div>
    </div>

    <!-- Recommendation sections -->
    <div v-for="(section, index) in sections" :key="index" class="space-y-6">
      <div class="flex items-end justify-between px-2">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <h2 class="text-xl font-black text-slate-800 dark:text-slate-100 tracking-tight transition-colors">{{ section.title }}</h2>
            <span class="px-2 py-0.5 text-[8px] font-black uppercase tracking-wider rounded-md bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 border border-indigo-100 dark:border-indigo-800/50 transition-colors">
              {{ section.badge }}
            </span>
          </div>
          <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mt-1 transition-colors">{{ section.subtitle }}</p>
        </div>
      </div>

      <div class="flex gap-6 overflow-x-auto pb-6 scrollbar-hide snap-x">
        <div v-for="book in section.books" :key="book.id"
             class="min-w-[280px] group bg-white dark:bg-slate-900 rounded-3xl border border-slate-100 dark:border-slate-800 p-5 hover:shadow-xl hover:shadow-indigo-500/5 dark:hover:shadow-none transition-all duration-300 snap-start">

          <div class="relative mb-4 aspect-[3/4] overflow-hidden rounded-2xl bg-slate-100 dark:bg-slate-800 transition-colors">
             <div class="absolute top-3 left-3 z-10">
                <span class="px-2.5 py-1.5 rounded-lg bg-white/90 dark:bg-slate-800/90 backdrop-blur-md border border-slate-100 dark:border-slate-700/50 text-[8px] font-black uppercase tracking-tighter text-slate-800 dark:text-slate-200 shadow-sm transition-colors">
                  <i :class="section.icon" class="mr-1 text-indigo-500 dark:text-indigo-400 transition-colors"></i> {{ section.badge }}
                </span>
             </div>

             <!-- Cover image or placeholder -->
             <img v-if="book.cover_image" :src="book.cover_image" :alt="book.title"
                  class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
             <div v-else class="w-full h-full flex items-center justify-center group-hover:scale-110 transition-transform duration-500">
                <i class="fa fa-book text-4xl text-slate-200 dark:text-slate-700 transition-colors"></i>
             </div>

             <div class="absolute inset-0 bg-slate-900/40 dark:bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                <button @click="handleRequest(book)"
                        class="px-4 py-2 rounded-full bg-indigo-600 dark:bg-indigo-500 text-white text-[10px] font-black uppercase tracking-widest transition-colors hover:bg-indigo-700">
                  {{ book.book_type === 'Digital' ? 'Read Now' : 'Request' }}
                </button>
             </div>
          </div>

          <div class="space-y-1">
            <h3 class="font-black text-slate-800 dark:text-slate-200 truncate transition-colors">{{ book.title }}</h3>
            <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase transition-colors">{{ book.author }}</p>
          </div>

          <div class="mt-4 pt-4 border-t border-slate-50 dark:border-slate-800/50 flex items-center justify-between transition-colors">
            <span v-if="book.category" class="text-[9px] font-black text-indigo-500 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20 px-2 py-1 rounded-md uppercase transition-colors">
              {{ book.category }}
            </span>
            <span class="text-[9px] font-black uppercase tracking-wider px-2 py-1 rounded-md transition-colors"
                  :class="book.book_type === 'Digital' ? 'text-cyan-600 bg-cyan-50 dark:text-cyan-400 dark:bg-cyan-900/20' : 'text-slate-500 bg-slate-50 dark:text-slate-400 dark:bg-slate-800'">
              {{ book.book_type }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!loading && sections.length === 0" class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-12 text-center border border-dashed border-slate-200 dark:border-slate-800 transition-colors">
      <i class="fa fa-inbox text-slate-100 dark:text-slate-800/50 text-6xl mb-4 block transition-colors"></i>
      <p class="text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest transition-colors">No recommendations available yet</p>
      <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-2 transition-colors">We'll personalize recommendations as you borrow more books</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useBooks } from "~/composable/useLibraryBooks";
import { useBookRequest } from "~/composable/useBookRequest";

const { recommendations: apiRecommendations, fetchRecommendations, loading } = useBooks();
const { requestBook } = useBookRequest();

const sections = ref([]);

const handleRequest = (book) => {
  if (book.book_type === 'Digital' && book.external_link) {
    window.open(book.external_link, '_blank');
    return;
  }
  requestBook({ name: book.id, library: book.library, title: book.title });
};

onMounted(async () => {
  await fetchRecommendations();
  sections.value = apiRecommendations.value || [];
});
</script>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
