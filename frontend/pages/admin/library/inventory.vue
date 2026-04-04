<template>
  <div class="space-y-6">

    <!-- Filters -->
    <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 p-6 transition-colors">
      <div class="flex flex-col lg:flex-row gap-4">
        <div class="flex-1">
          <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 block">Search Books</span>
          <div class="relative">
            <i class="fa fa-search absolute left-4 top-1/2 -translate-y-1/2 text-slate-300"></i>
            <input v-model="searchQuery" type="text" placeholder="Search by title, author, or ISBN..."
              class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl pl-12 pr-4 py-3 text-xs font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors" />
          </div>
        </div>
        <div class="w-full lg:w-48">
          <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 block">Category</span>
          <select v-model="selectedCategory"
            class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl px-4 py-3 text-xs font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors">
            <option value="">All Categories</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
      </div>
      <div class="flex gap-2 overflow-x-auto no-scrollbar pb-2 mt-4">
        <button v-for="f in stockFilters" :key="f.id" @click="activeFilter = f.id" :class="[
          activeFilter === f.id
            ? 'bg-slate-900 dark:bg-indigo-600 text-white shadow-lg'
            : 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-white dark:hover:bg-slate-700',
          'px-6 py-2.5 rounded-2xl text-[10px] font-black uppercase tracking-widest border transition-all whitespace-nowrap'
        ]">
          {{ f.label }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-3">
      <UiSkeleton v-for="i in 5" :key="i" height="h-16" class="rounded-2xl" />
    </div>

    <!-- Table -->
    <div v-else class="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 overflow-hidden transition-colors">
      <div class="p-6 border-b border-slate-50 dark:border-slate-800 flex justify-between items-center transition-colors">
        <div>
          <h3 class="text-sm font-black text-slate-800 dark:text-slate-100 uppercase tracking-widest transition-colors">Book Inventory</h3>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mt-1">{{ filteredBooks.length }} records</p>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50/50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800 transition-colors">
              <th class="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Book</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Category</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Type</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">ISBN</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Shelf</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest text-center">Copies</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-800 transition-colors">
            <tr v-for="book in filteredBooks" :key="book.name" class="hover:bg-slate-50/30 dark:hover:bg-slate-800/30 transition-colors">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="h-10 w-10 rounded-xl flex items-center justify-center text-white font-black text-sm"
                       :class="typeColor(book.book_type)">
                    <i class="fa" :class="book.book_type === 'Digital' ? 'fa-laptop' : 'fa-book'"></i>
                  </div>
                  <div>
                    <p class="text-sm font-black text-slate-700 dark:text-slate-200 transition-colors">{{ book.title }}</p>
                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter">{{ book.author || '—' }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-4">
                <span v-if="book.category" class="px-2 py-1 text-[9px] font-black uppercase rounded-lg border bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 transition-colors">
                  {{ book.category }}
                </span>
                <span v-else class="text-slate-300 text-xs">—</span>
              </td>
              <td class="px-4 py-4 text-[10px] font-black uppercase tracking-wider"
                  :class="book.book_type === 'Digital' ? 'text-cyan-600 dark:text-cyan-400' : 'text-slate-500 dark:text-slate-400'">
                {{ book.book_type }}
              </td>
              <td class="px-4 py-4 text-xs font-bold text-slate-600 dark:text-slate-300 transition-colors">{{ book.isbn || '—' }}</td>
              <td class="px-4 py-4 text-xs font-bold text-slate-600 dark:text-slate-300 transition-colors">{{ book.shelf || '—' }}</td>
              <td class="px-4 py-4">
                <div class="flex items-center justify-center gap-2">
                  <span class="text-xs font-bold text-slate-700 dark:text-slate-200 transition-colors">{{ book.available_copies || 0 }}/{{ book.total_copies || 0 }}</span>
                  <div v-if="book.total_copies > 0" class="w-16 h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden transition-colors">
                    <div class="h-full transition-all rounded-full"
                      :class="(book.available_copies / book.total_copies) > 0.5 ? 'bg-green-500' : (book.available_copies / book.total_copies) > 0 ? 'bg-amber-500' : 'bg-red-500'"
                      :style="{ width: Math.round((book.available_copies / book.total_copies) * 100) + '%' }"></div>
                  </div>
                </div>
              </td>
              <td class="px-4 py-4">
                <span :class="[
                  book.available_copies === 0 && book.total_copies > 0 ? 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-100 dark:border-red-800/50'
                    : book.available_copies <= 1 && book.total_copies > 1 ? 'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/50'
                      : 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-100 dark:border-green-800/50',
                  'px-2 py-1 text-[9px] font-black uppercase tracking-wider rounded-lg border transition-colors'
                ]">
                  {{ book.available_copies === 0 && book.total_copies > 0 ? 'Out of Stock' : book.available_copies <= 1 && book.total_copies > 1 ? 'Low Stock' : 'Available' }}
                </span>
              </td>
            </tr>
            <tr v-if="filteredBooks.length === 0">
              <td colspan="7" class="px-8 py-12 text-center">
                <i class="fa fa-inbox text-slate-200 dark:text-slate-700 text-5xl mb-4 block transition-colors"></i>
                <p class="text-sm font-black text-slate-400 uppercase">No books found</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useLibraryAdmin } from '~/composable/useLibraryAdmin';

const { inventory, loading, fetchInventory } = useLibraryAdmin();

const searchQuery = ref('');
const selectedCategory = ref('');
const activeFilter = ref('all');

const stockFilters = [
  { id: 'all', label: 'All Books' },
  { id: 'available', label: 'In Stock' },
  { id: 'low', label: 'Low Stock' },
  { id: 'outofstock', label: 'Out of Stock' },
];

const categories = computed(() => {
  const cats = new Set(inventory.value.map(b => b.category).filter(Boolean));
  return [...cats].sort();
});

const filteredBooks = computed(() => {
  let result = inventory.value;

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(b =>
      (b.title || '').toLowerCase().includes(q) ||
      (b.author || '').toLowerCase().includes(q) ||
      (b.isbn || '').includes(q)
    );
  }

  if (selectedCategory.value) {
    result = result.filter(b => b.category === selectedCategory.value);
  }

  switch (activeFilter.value) {
    case 'available':
      result = result.filter(b => b.available_copies > 1);
      break;
    case 'low':
      result = result.filter(b => b.available_copies <= 1 && b.available_copies > 0 && b.total_copies > 1);
      break;
    case 'outofstock':
      result = result.filter(b => b.available_copies === 0 && b.total_copies > 0);
      break;
  }

  return result;
});

const typeColor = (type) => {
  switch (type) {
    case 'Digital': return 'bg-cyan-600';
    case 'Both': return 'bg-purple-600';
    default: return 'bg-indigo-600';
  }
};

onMounted(() => fetchInventory());
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
</style>
