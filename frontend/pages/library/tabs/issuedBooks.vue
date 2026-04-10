<template>
  <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 overflow-hidden animate-in fade-in duration-500 transition-colors">

    <!-- Header -->
    <div class="flex flex-col lg:flex-row justify-between items-center p-8 gap-6 border-b border-slate-50 dark:border-slate-800/50 transition-colors">
      
      <!-- Rows per page -->
      <div class="flex items-center gap-4">
        <div class="flex flex-col">
          <span class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-1.5 transition-colors">View Count</span>
          <select v-model="itemsPerPage" class="bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 rounded-xl px-4 py-2 text-xs font-bold text-slate-700 dark:text-slate-300 outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all">
            <option :value="5">5 Rows</option>
            <option :value="10">10 Rows</option>
            <option :value="25">25 Rows</option>
          </select>
        </div>
      </div>

      <!-- Search & Buttons -->
      <div class="flex flex-col sm:flex-row items-end gap-4 w-full lg:w-auto">
        <div class="w-full sm:w-72">
          <span class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-1.5 block transition-colors">Search My Books</span>
          <div class="relative">
            <i class="fa fa-search absolute left-4 top-1/2 -translate-y-1/2 text-slate-300 dark:text-slate-500 transition-colors"></i>
            <input 
              v-model="searchQuery"
              type="search" 
              placeholder="Title or isbn No..." 
              class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 rounded-xl pl-10 pr-4 py-2 text-xs font-bold text-slate-700 dark:text-slate-300 outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="space-y-4">
      <UiSkeleton height="h-16" v-for="i in 5" :key="i" class="rounded-2xl" />
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto min-h-[300px]">
      <table class="w-full text-left border-collapse hidden md:table transition-colors">
        <thead>
          <tr class="bg-slate-50/50 dark:bg-slate-800/50 transition-colors">
            <th class="px-6 py-5 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest transition-colors">Book Details</th>
            <th class="px-6 py-5 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest transition-colors">ISBN</th>
            <th class="px-6 py-5 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest transition-colors">Issue Date</th>
            <th class="px-6 py-5 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest transition-colors">Due Date</th>
            <th class="px-6 py-5 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest transition-colors">Days Left</th>
            <th class="px-6 py-5 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 tracking-widest text-center transition-colors">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-50 dark:divide-slate-800/50 transition-colors">
          <tr v-for="book in paginatedBooks" :key="book.name" class="hover:bg-slate-50/30 dark:hover:bg-slate-800/30 transition-colors group">
            
            <!-- Book Details -->
            <td class="px-6 py-5">
              <div class="flex items-center gap-4">
                <div class="h-10 w-10 rounded-2xl bg-slate-50 dark:bg-slate-800/50 text-slate-400 dark:text-slate-500 flex items-center justify-center border border-slate-100 dark:border-slate-700/50 shrink-0 group-hover:bg-indigo-50 dark:group-hover:bg-indigo-900/20 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                  <i class="fa fa-book text-xs"></i>
                </div>
                <div class="flex flex-col">
                  <span class="text-sm font-black text-slate-700 dark:text-slate-300 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{{ book.book_title }}</span>
                  <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 transition-colors">Renewed: {{ book.renewal_count || 0 }}x</span>
                </div>
              </div>
            </td>

            <!-- ISBN -->
            <td class="px-6 py-5">
              <span class="text-xs font-black text-slate-600 dark:text-slate-300 px-3 py-1 bg-slate-100 dark:bg-slate-800 rounded-lg border border-slate-200/50 dark:border-slate-700/50 uppercase transition-colors">{{ book.book_isbn }}</span>
            </td>

            <!-- Issue Date -->
            <td class="px-6 py-5">
              <span class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest transition-colors">{{ formatDate(book.issue_date) }}</span>
            </td>

            <!-- Due Date -->
            <td class="px-6 py-5">
              <span :class="['text-xs font-black transition-colors', book.is_overdue ? 'text-red-600 dark:text-red-400' : 'text-slate-700 dark:text-slate-300']">
                {{ formatDate(book.due_date) }}
              </span>
            </td>

            <!-- Days Left -->
            <td class="px-6 py-5">
              <div v-if="book.is_overdue" class="flex flex-col gap-1.5">
                <span class="w-fit px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter shadow-sm dark:shadow-none border bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-100 dark:border-red-900/30 transition-colors">
                  {{ book.days_overdue }} days overdue
                </span>
                <span v-if="book.fine_amount > 0" class="text-[10px] font-bold text-red-500 dark:text-red-400">
                  Fine: ${{ book.fine_amount }}
                </span>
              </div>
              <div v-else-if="book.days_left <= 3" class="flex items-center gap-2">
                <span class="px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter shadow-sm dark:shadow-none border bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-900/30 transition-colors">
                  {{ book.days_left }} days left
                </span>
              </div>
              <div v-else>
                <span class="px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter shadow-sm dark:shadow-none border bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-100 dark:border-green-900/30 transition-colors">
                  {{ book.days_left }} days left
                </span>
              </div>
            </td>

            <!-- Actions -->
            <td class="px-6 py-5 text-center">
              <div class="flex items-center justify-center gap-2">
                <button 
                  @click="renewBook(book.name)"
                  :disabled="book.has_reservation || renewingBook === book.name || book.renew_requested"
                  :title="book.has_reservation ? 'Cannot renew: book has pending reservation' : (book.renew_requested ? 'Renewal pending approval' : 'Request Renew')"
                  class="px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-tighter transition-all"
                  :class="book.has_reservation 
                    ? 'bg-slate-50 text-slate-400 cursor-not-allowed opacity-50'
                    : book.renew_requested
                      ? 'bg-amber-50 text-amber-600 border border-amber-100 cursor-not-allowed'
                      : 'bg-indigo-50 text-indigo-600 border border-indigo-100 hover:bg-indigo-600 hover:text-white'
                  "
                >
                  <i v-if="renewingBook === book.name" class="fa fa-spinner fa-spin mr-1"></i>
                  {{ book.renew_requested ? 'Pending Approval' : (book.has_reservation ? 'Reserved' : 'Request Renew') }}
                </button>
              </div>
            </td>
          </tr>

          <!-- No Records -->
          <tr v-if="filteredBooks.length === 0">
            <td colspan="6" class="px-8 py-20 text-center">
               <i class="fa fa-folder-open-o text-slate-200 text-3xl mb-4"></i>
               <p class="text-xs font-black text-slate-400 uppercase tracking-widest">No matching issued books found</p>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Mobile View -->
      <div class="md:hidden space-y-4 p-4">
        <div v-for="book in paginatedBooks" :key="book.name" class="bg-slate-50 rounded-2xl p-4 border border-slate-100">
          <div class="flex items-start justify-between mb-3">
            <div>
              <h3 class="text-sm font-black text-slate-800">{{ book.book_title }}</h3>
              <p class="text-[10px] font-bold text-slate-400">ISBN: {{ book.book_isbn }}</p>
            </div>
            <button 
              @click="renewBook(book.name)"
              :disabled="book.has_reservation || renewingBook === book.name || book.renew_requested"
              class="px-3 py-1.5 rounded-lg text-[9px] font-black uppercase transition-all"
              :class="book.has_reservation 
                ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                : book.renew_requested
                  ? 'bg-amber-100 text-amber-600 cursor-not-allowed'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              "
            >
              {{ book.renew_requested ? 'Pending Approval' : 'Renew' }}
            </button>
          </div>
          <div class="grid grid-cols-2 gap-2 text-[10px] font-bold mt-2">
            <div><span class="text-slate-400">Issued:</span> {{ formatDate(book.issue_date) }}</div>
            <div><span class="text-slate-400">Due:</span> {{ formatDate(book.due_date) }}</div>
            <div :class="book.is_overdue ? 'text-red-600' : 'text-slate-700'">
              <span class="text-slate-400">Remaining:</span> {{ book.is_overdue ? `${book.days_overdue} days overdue` : `${book.days_left} days left` }}
            </div>
            <div><span class="text-slate-400">Renewals:</span> {{ book.renewal_count || 0 }}x</div>
            <div v-if="book.is_overdue && book.fine_amount > 0" class="col-span-2 text-red-500 mt-1 pb-1 border-t border-red-100 pt-2">
              <i class="fa fa-exclamation-circle mr-1"></i>
              Accrued Fine: ${{ book.fine_amount }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="!loading && totalPages > 1" class="flex flex-col md:flex-row justify-between items-center p-8 bg-slate-50/30 border-t border-slate-100 gap-4">
      <span class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
        Showing {{ filteredBooks.length === 0 ? 0 : (currentPage - 1) * itemsPerPage + 1 }} - 
        {{ Math.min(currentPage * itemsPerPage, filteredBooks.length) }} of 
        {{ filteredBooks.length }} Issued Books
      </span>
      
      <div class="flex items-center gap-2">
        <button @click="currentPage--" :disabled="currentPage === 1" class="page-btn-fixed">
          <i class="fa fa-chevron-left text-xs text-slate-400"></i>
        </button>
        
        <div class="flex gap-1">
          <button v-for="page in totalPages" :key="page" @click="currentPage = page"
            :class="[ 'w-10 h-10 rounded-xl text-xs font-black transition-all shadow-sm', 
              currentPage === page ? 'bg-slate-900 text-white shadow-slate-200' : 'bg-white text-slate-500 border border-slate-200 hover:border-indigo-400'
            ]">
            {{ page }}
          </button>
        </div>

        <button @click="currentPage++" :disabled="currentPage === totalPages" class="page-btn-fixed">
          <i class="fa fa-chevron-right text-xs text-slate-400"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { useBooks } from '~/composables/library/useLibraryBooks';
import { createResource } from '~/composables/api/useFrappeFetch';
import { useToast } from '~/composables/ui/useToast';

const { addToast } = useToast();

const { data: borrowedBooks, fetchData } = useBooks();

const searchQuery = ref('');
const itemsPerPage = ref(5);
const currentPage = ref(1);
const loading = ref(true);
const renewingBook = ref(null);

onMounted(async () => {
    await fetchData();
    loading.value = false;
});

/* ---------------- RENEW BOOK (API DEMO) ---------------- */
const renewBook = async (bookIssueName) => {
  renewingBook.value = bookIssueName;
  try {
     const resource = createResource({ url: 'vidyaan.library.api.renew_book' });
     await resource.submit({ issue_name: bookIssueName });
     await fetchData(); // Refresh data
     addToast("Book renewal requested successfully", "success");
  } catch(e) {
     addToast(e.message || "Failed to renew book.", "error");
  } finally {
     renewingBook.value = null;
  }
};

/* ---------------- FILTER ---------------- */

const filteredBooks = computed(() => {
  return borrowedBooks.value.filter(b =>
    (b.book_title || '').toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    (b.book_isbn || '').toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

/* ---------------- PAGINATION ---------------- */

const totalPages = computed(() =>
  Math.ceil(filteredBooks.value.length / itemsPerPage.value) || 0
);

const paginatedBooks = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  return filteredBooks.value.slice(start, start + itemsPerPage.value);
});

/* ---------------- WATCHERS ---------------- */

watch(searchQuery, () => currentPage.value = 1);
watch(itemsPerPage, () => currentPage.value = 1);

/* ---------------- DATE FORMAT ---------------- */

const formatDate = (dateStr) => {
  if (!dateStr) return '';

  const date = new Date(dateStr);

  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};
</script>

<style scoped>
.btn-primary { @apply px-6 py-2.5 bg-indigo-600 text-white rounded-xl text-[10px] font-black uppercase tracking-[0.2em] shadow-xl shadow-indigo-100 hover:bg-indigo-700 active:scale-95 transition-all; }
.btn-icon { @apply flex items-center justify-center bg-white border border-slate-200 text-slate-400 rounded-xl hover:text-indigo-600 hover:border-indigo-100 transition-all; }
.page-btn-fixed { @apply p-2 w-10 h-10 rounded-xl bg-white border border-slate-200 disabled:opacity-30 disabled:cursor-not-allowed hover:border-indigo-500 transition-all shadow-sm flex items-center justify-center; }
</style>