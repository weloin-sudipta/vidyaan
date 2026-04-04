<template>
  <div
    class="bg-white dark:bg-slate-900 rounded-[2rem] lg:rounded-[2.5rem] shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 overflow-hidden animate-in fade-in duration-500 transition-colors">

    <div class="p-5 lg:p-8 border-b border-slate-50 dark:border-slate-800/50 space-y-6 transition-colors">
      <div class="flex flex-col lg:flex-row justify-between items-end gap-6">

        <div class="flex flex-col">
          <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5 ml-1">View Count</span>
          <select v-model="itemsPerPage"
            class="bg-slate-50 border border-slate-100 rounded-xl px-4 py-2.5 text-xs font-bold text-slate-700 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-all w-32">
            <option :value="5">5 Rows</option>
            <option :value="10">10 Rows</option>
            <option :value="25">25 Rows</option>
          </select>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full lg:w-auto flex-1 max-w-4xl">
          <div class="sm:col-span-1">
            <span class="filter-label">Search Catalog</span>
            <div class="relative">
              <i class="fa fa-search absolute left-4 top-1/2 -translate-y-1/2 text-slate-300 dark:text-slate-500 transition-colors"></i>
              <input v-model="searchQuery" type="text" placeholder="Title or Author..." class="filter-input" />
            </div>
          </div>

          <div>
            <span class="filter-label">Category</span>
            <select v-model="selectedCategory" class="filter-input !pl-4">
              <option value="All">All Categories</option>
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>
          </div>

          <div>
            <span class="filter-label">Type</span>
            <select v-model="selectedType" class="filter-input !pl-4">
              <option value="All">All Types</option>
              <option value="Physical">Physical</option>
              <option value="Online">Online</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div class="min-h-[400px] relative">
      <div v-if="loading" class="grid grid-cols-1 gap-2 p-6">
        <UiSkeleton height="h-16" v-for="i in 5" :key="i" />
      </div>

      <table class="w-full text-left border-collapse hidden md:table transition-colors">
        <thead>
          <tr class="bg-slate-50/50 dark:bg-slate-800/50 transition-colors">
            <th class="px-6 py-5 th-style">Book Information</th>
            <th class="px-6 py-5 th-style">Category</th>
            <th class="px-6 py-5 th-style">Copy Type</th>
            <th class="px-6 py-5 th-style text-center">Availability</th>
            <th class="px-6 py-5 th-style text-right">Action</th>
          </tr>
        </thead>

        <tbody class="divide-y divide-slate-50 dark:divide-slate-800/50">
          <tr v-for="book in paginatedCatalog" :key="book.name" class="hover:bg-slate-50/30 dark:hover:bg-slate-800/30 transition-colors group">
            <td class="px-6 py-5">
              <div class="flex items-center gap-4">
                <div
                  class="h-10 w-10 rounded-xl bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center border border-indigo-100 dark:border-indigo-900/30 group-hover:bg-slate-900 dark:group-hover:bg-slate-700 group-hover:text-white transition-all">
                  <i :class="book.copy_type === 'Online' ? 'fa fa-laptop' : 'fa fa-book'" class="text-xs"></i>
                </div>
                <div class="flex flex-col">
                  <span class="text-sm font-black text-slate-700 dark:text-slate-300 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{{
                    book.title }}</span>
                  <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase transition-colors">By {{ book.author }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-5">
              <span class="text-[9px] font-black text-indigo-400 dark:text-indigo-500 uppercase tracking-widest ml-1 transition-colors">{{ book.category ||
                'General' }}</span>
            </td>
            <td class="px-6 py-5">
              <span
                :class="['type-badge', book.copy_type === 'Online' ? 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 border-purple-100 dark:border-purple-900/30' : 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-blue-100 dark:border-blue-900/30']">
                {{ book.copy_type }}
              </span>
            </td>
            <td class="px-6 py-5 text-center">
              <div class="flex flex-col items-center justify-center gap-1.5">
                <span
                  :class="['status-badge', isAvailable(book) ? 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-100 dark:border-green-900/30' : 'bg-rose-50 dark:bg-rose-900/20 text-rose-600 dark:text-rose-400 border-rose-100 dark:border-rose-900/30']">
                  {{ isAvailable(book) ? 'Available' : 'Issued Out' }}
                </span>
                <span v-if="book.copy_type !== 'Online'" class="text-[9px] font-bold text-slate-400 dark:text-slate-500 tracking-wider transition-colors">
                  {{ book.available_copies }} / {{ book.total_copies }} copies
                </span>
              </div>
            </td>
            <td class="px-6 py-5 text-right">
              <!--
                Button logic:
                1. Online book       → always "Read Now" (blue/active)
                2. Pending request   → "Cancel Request" (red)
                3. Available book    → "Request" (indigo)
                4. Unavailable book  → "Reserve" (purple)
              -->
              <template v-if="book.copy_type === 'Online'">
                <button @click="handleBookRequest(book, true)" class="btn-action-active"
                  :disabled="bookRequest.loading.value">
                  <i v-if="bookRequest.loading.value" class="fa fa-spinner fa-spin mr-2"></i>
                  Read Now
                </button>
              </template>

              <!-- Pending Request -->
              <template v-else-if="bookRequest.requeststatus.value[book.name] === 'Pending'">
                <button @click="handleBookRequest(book, isAvailable(book))" class="btn-cancel"
                  :disabled="bookRequest.loading.value">
                  <i v-if="bookRequest.loading.value" class="fa fa-spinner fa-spin mr-2"></i>
                  {{ isAvailable(book) ? 'Cancel Request' : 'Cancel Reservation' }}
                </button>
              </template>

              <!-- Approved Request -->
              <template v-else-if="bookRequest.requeststatus.value[book.name] === 'Approved'">
                <button @click="handleBookRequest(book, isAvailable(book))" class="btn-approved"
                  :disabled="bookRequest.loading.value">
                  <i v-if="bookRequest.loading.value" class="fa fa-spinner fa-spin mr-2"></i>
                  Accepted
                </button>
              </template>

              <template v-else>
                <!-- No request yet → Request (available) or Reserve (unavailable) -->
                <button @click="handleBookRequest(book, isAvailable(book))"
                  :class="isAvailable(book) ? 'btn-action-active' : 'btn-reserve'"
                  :disabled="bookRequest.loading.value">
                  <i v-if="bookRequest.loading.value" class="fa fa-spinner fa-spin mr-2"></i>
                  {{ isAvailable(book) ? 'Request' : 'Reserve' }}
                </button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="!loading && filteredCatalog.length === 0" class="p-20 text-center">
        <i class="fa fa-folder-open-o text-slate-200 dark:text-slate-700 text-3xl mb-4 transition-colors"></i>
        <p class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest transition-colors">No books found matching your criteria
        </p>
      </div>
    </div>

    <div
      class="flex flex-col md:flex-row justify-between items-center p-8 bg-slate-50/30 border-t border-slate-100 gap-4">
      <span class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
        Showing {{ filteredCatalog.length === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1 }} -
        {{ Math.min(currentPage * itemsPerPage, filteredCatalog.length) }} of
        {{ filteredCatalog.length }} Resources
      </span>

      <div v-if="totalPages > 0" class="flex items-center gap-2">
        <button @click="currentPage--" :disabled="currentPage === 1" class="page-btn-fixed">
          <i class="fa fa-chevron-left text-xs"></i>
        </button>

        <div class="flex gap-1">
          <button v-for="page in totalPages" :key="page" @click="currentPage = page" :class="['w-10 h-10 rounded-xl text-xs font-black transition-all shadow-sm flex items-center justify-center',
            currentPage === page ? 'bg-slate-900 text-white shadow-slate-200' : 'bg-white text-slate-500 border border-slate-200 hover:border-indigo-400'
          ]">
            {{ page }}
          </button>
        </div>

        <button @click="currentPage++" :disabled="currentPage === totalPages" class="page-btn-fixed">
          <i class="fa fa-chevron-right text-xs"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useBooks } from '~/composable/useLibraryBooks';

const { allBooks, fetchAllBooks, data, fetchData, bookRequest, isBookRequested, toggleBookRequest } = useBooks();

onMounted(async () => {
    loading.value = true;
    await Promise.all([
        fetchAllBooks(),
        fetchData(),
        bookRequest.loadUserRequests()
    ]);
    loading.value = false;
});

// ─── UI State ────────────────────────────────────────────────────────────────
const loading = ref(true);
const searchQuery = ref('');
const selectedCategory = ref('All');
const selectedType = ref('All');
const selectedStatus = ref('All');
const itemsPerPage = ref(10);
const currentPage = ref(1);

// ─── Request Logic is handled via Composables ──────────────────────────────────────────────
const isAvailable = (book) =>
  book.copy_type === 'Online' || book.available_copies > 0;

const handleBookRequest = async (book, available) => {
  if (book.copy_type === 'Online') {
    window.open(book.url || '#', '_blank');
    return;
  }
  await toggleBookRequest(book);
};

// ─── Categories ──────────────────────────────────────────────────────────────
const categories = computed(() => {
  const cats = allBooks.value.map(b => b.category).filter(Boolean);
  return [...new Set(cats)].sort();
});

// ─── Filtering ───────────────────────────────────────────────────────────────
const isBookIssuedToUser = (bookId) => {
  if (!data.value || !Array.isArray(data.value)) return false;
  return data.value.some(issue => issue.book === bookId && issue.status === 'Issued');
};

const filteredCatalog = computed(() => {
  return allBooks.value.filter(book => {
    if (isBookIssuedToUser(book.name)) {
      return false;
    }

    const query = searchQuery.value.toLowerCase();

    const matchesSearch =
      book.title?.toLowerCase().includes(query) ||
      book.author?.toLowerCase().includes(query);

    const matchesCat =
      selectedCategory.value === 'All' ||
      book.category === selectedCategory.value;

    const matchesType =
      selectedType.value === 'All' ||
      (book.copy_type || 'Physical') === selectedType.value;

    const matchesStatus =
      selectedStatus.value === 'All' ||
      (selectedStatus.value === 'Available'
        ? isAvailable(book)
        : !isAvailable(book));

    return matchesSearch && matchesCat && matchesType && matchesStatus;
  });
});

// ─── Pagination ──────────────────────────────────────────────────────────────
const totalPages = computed(() =>
  Math.ceil(filteredCatalog.value.length / itemsPerPage.value) || 0
);

const paginatedCatalog = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  return filteredCatalog.value.slice(start, start + itemsPerPage.value);
});

// ─── Reset Page on Filter Change ─────────────────────────────────────────────
watch(
  [searchQuery, selectedCategory, selectedType, selectedStatus, itemsPerPage],
  () => {
    currentPage.value = 1;
  }
);
</script>

<style scoped>
.filter-label {
  @apply text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-1.5 block ml-1 transition-colors;
}

.filter-input {
  @apply w-full bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 rounded-xl px-4 py-2.5 text-xs font-bold text-slate-700 dark:text-slate-300 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-all pl-12;
}

.th-style {
  @apply text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest transition-colors;
}

.type-badge {
  @apply px-3 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest border shadow-sm dark:shadow-none transition-colors;
}

.status-badge {
  @apply px-3 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-tighter shadow-sm dark:shadow-none border transition-colors;
}

.btn-action-active {
  @apply px-5 py-3 rounded-xl bg-indigo-600 text-white text-[10px] font-black uppercase tracking-widest hover:bg-slate-900 dark:hover:bg-indigo-500 shadow-sm dark:shadow-none transition-all active:scale-95;
}

.btn-reserve {
  @apply px-5 py-3 rounded-xl bg-purple-600 text-white text-[10px] font-black uppercase tracking-widest hover:bg-slate-900 dark:hover:bg-purple-500 shadow-sm dark:shadow-none transition-all active:scale-95;
}

.btn-cancel {
  @apply px-5 py-3 rounded-xl bg-red-600 text-white text-[10px] font-black uppercase tracking-widest hover:bg-red-700 dark:hover:bg-red-500 shadow-sm dark:shadow-none transition-all active:scale-95;
}
.btn-approved {
  @apply px-5 py-3 rounded-xl bg-slate-400 dark:bg-slate-600 text-white text-[10px] font-black uppercase tracking-widest hover:bg-slate-700 dark:hover:bg-slate-500 shadow-sm dark:shadow-none transition-all active:scale-95;
}
.page-btn-fixed {
  @apply p-2 w-10 h-10 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 disabled:opacity-30 disabled:cursor-not-allowed hover:border-indigo-500 transition-all shadow-sm dark:shadow-none flex items-center justify-center text-slate-400 dark:text-slate-500;
}
</style>