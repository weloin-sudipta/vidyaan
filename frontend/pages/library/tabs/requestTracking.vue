<template>
  <div class="space-y-8 p-4 lg:p-8 bg-slate-50/50 dark:bg-slate-950/50 min-h-screen transition-colors">
    <div class="mx-auto max-w-5xl">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h2 class="text-2xl font-black text-slate-800 dark:text-slate-100 tracking-tight transition-colors">My Book Requests</h2>
          <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest mt-1 transition-colors">
            Track your active and past physical book loans
          </p>
        </div>
        <div class="flex items-center gap-1">
          <!-- <NuxtLink to="/library/tracking" class="h-12 w-12 rounded-2xl bg-white shadow-sm border border-slate-200 flex items-center justify-center text-indigo-600 cursor-pointer hover:bg-indigo-50 transition-all">
            <i class="fa-solid fa-chart-line"></i>
          </NuxtLink> -->

          <div
            class="h-12 w-12 rounded-2xl bg-white dark:bg-slate-900 shadow-sm dark:shadow-none border border-slate-200 dark:border-slate-800 flex items-center justify-center text-indigo-600 dark:text-indigo-400 cursor-pointer hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-all">
            <i class="fa fa-history" :class="{ 'fa-spin': loading }"></i>
          </div>
        </div>
      </div>

      <div v-if="loading" class="space-y-4">
        <div v-for="i in 2" :key="i" class="h-48 w-full bg-slate-200 dark:bg-slate-800 animate-pulse rounded-[2.5rem] transition-colors"></div>
      </div>

      <div v-else-if="requestedBook && requestedBook.length > 0" class="space-y-6">
        <div v-for="request in requestedBook" :key="request.name"
          class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-8 shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 animate-in transition-colors">

          <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10">
            <div class="flex items-center gap-4">
              <div
                class="h-12 w-12 rounded-2xl bg-slate-900 dark:bg-slate-800 text-white flex items-center justify-center shadow-lg shadow-slate-200 dark:shadow-none transition-colors">
                <i class="fa fa-book"></i>
              </div>
              <div>
                <h3 class="text-sm font-black text-slate-800 dark:text-slate-200 uppercase tracking-wide transition-colors">{{ request.book_title }}</h3>
                <p class="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-tighter transition-colors">
                  ID: {{ request.book }} • Requested on {{ formatDate(request.request_date) }}
                </p>
              </div>
            </div>

            <div class="flex flex-col items-end gap-2">
              <div
                :class="['px-4 py-1.5 rounded-xl text-[9px] font-black uppercase tracking-widest border shadow-sm transition-all', statusTheme(request.status).bg]">
                {{ request.status }}
              </div>
              <button 
                v-if="request.status === 'Pending'" 
                @click="onCancelRequest(request)"
                class="text-xs px-3 py-1 rounded border border-red-200 text-red-600 bg-red-50 hover:bg-red-100 transition-colors"
                title="Cancel Request">
                <i class="fa fa-times mr-1"></i> Cancel
              </button>
            </div>
          </div>

          <div class="relative px-2 mb-4">
            <div class="absolute top-5 left-0 w-full h-[3px] bg-slate-100 dark:bg-slate-800 rounded-full transition-colors"></div>

            <div
              class="absolute top-5 left-0 h-[3px] bg-indigo-500 rounded-full transition-all duration-[1500ms] ease-in-out shadow-[0_0_10px_rgba(99,102,241,0.5)]"
              :style="{ width: getProgressWidth(request.status) }"></div>

            <div class="relative flex justify-between">
              <div v-for="(step, index) in steps" :key="index" class="flex flex-col items-center">
                <div :class="[
                  'w-10 h-10 rounded-2xl flex items-center justify-center border-4 transition-all duration-700 z-10',
                  isStepReached(request.status, step.key)
                    ? 'bg-indigo-600 border-white dark:border-slate-900 text-white rotate-[360deg] scale-110 shadow-md dark:shadow-none'
                    : 'bg-white dark:bg-slate-900 border-slate-50 dark:border-slate-800/50 text-slate-300 dark:text-slate-600'
                ]">
                  <i :class="[step.icon, 'text-xs']"></i>
                </div>
                <span :class="[
                  'mt-4 text-[9px] font-black uppercase tracking-widest transition-colors duration-500',
                  isStepReached(request.status, step.key) ? 'text-slate-800 dark:text-slate-300' : 'text-slate-300 dark:text-slate-600'
                ]">
                  {{ step.label }}
                </span>
              </div>
            </div>
          </div>

          <div v-if="request.remarks" class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800 transition-colors">
            <p class="text-[9px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-1 transition-colors">My Remarks</p>
            <p class="text-xs text-slate-600 dark:text-slate-400 italic transition-colors">"{{ request.remarks }}"</p>
          </div>
        </div>
      </div>

      <div v-else class="bg-white dark:bg-slate-900 rounded-[2.5rem] p-20 text-center border border-dashed border-slate-200 dark:border-slate-800 transition-colors">
        <i class="fa fa-folder-open text-slate-100 dark:text-slate-800/50 text-6xl mb-4 transition-colors"></i>
        <p class="text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest transition-colors">No active requests found</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useBooks } from '~/composable/useLibraryBooks'
import { useToast } from '~/composable/useToast'

const { addToast } = useToast()
const { requestedBook, fetchRequestedBook, cancelRequest } = useBooks();

const loading = ref(true);

onMounted(async () => {
    await fetchRequestedBook();
    loading.value = false;
});

const onCancelRequest = async (request) => {
    if (!confirm(`Are you sure you want to cancel the request for ${request.book_title}?`)) return;
    try {
        await cancelRequest(request.book, request.name);
        await fetchRequestedBook();
        addToast("Request cancelled successfully", "success");
    } catch(err) {
        addToast("Failed to cancel request.", "error");
    }
};

// ─── Steps ───────────────────────────────────────────────────────────────────
const steps = [
  { key: 'Pending', label: 'Pending', icon: 'fa fa-hourglass-start' },
  { key: 'Approved', label: 'Approved', icon: 'fa fa-check-circle' },
  { key: 'Issued', label: 'In My Possession', icon: 'fa fa-handshake-o' },
  { key: 'Returned', label: 'Returned', icon: 'fa fa-archive' }
];

// ─── Progress Bar Logic ──────────────────────────────────────────────────────
const getProgressWidth = (status) => {
  const mapping = {
    'Pending': '0%',
    'Approved': '33%',
    'Issued': '67%',
    'Returned': '100%',
    'Reserved': '50%',
    'Cancel': '0%'
  };
  return mapping[status] || '0%';
};

// ─── Step Highlight Logic ────────────────────────────────────────────────────
const isStepReached = (currentStatus, stepKey) => {
  const order = ['Pending', 'Approved', 'Issued', 'Returned'];
  return order.indexOf(currentStatus) >= order.indexOf(stepKey);
};

// ─── Status Theme ────────────────────────────────────────────────────────────
const statusTheme = (status) => {
  const themes = {
    'Pending': { bg: 'bg-amber-50 text-amber-600 border-amber-100' },
    'Approved': { bg: 'bg-blue-50 text-blue-600 border-blue-100' },
    'Issued': { bg: 'bg-indigo-50 text-indigo-600 border-indigo-100' },
    'Returned': { bg: 'bg-emerald-50 text-emerald-600 border-emerald-100' },
    'Reserved': { bg: 'bg-purple-50 text-purple-600 border-purple-100' },
    'Cancel': { bg: 'bg-red-50 text-red-600 border-red-100' }
  };
  return themes[status] || { bg: 'bg-slate-50 text-slate-500 border-slate-100' };
};

// ─── Date Formatter ──────────────────────────────────────────────────────────
const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};
</script>

<style scoped>
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-in {
  animation: slideUp 0.6s ease-out forwards;
}

/* Smoothly rotate the icon when reached */
.rotate-360 {
  transform: rotate(360deg);
}
</style>