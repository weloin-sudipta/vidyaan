<template>
  <div class="min-h-screen bg-[#f8fafc] dark:bg-slate-950 p-4 lg:p-10 font-sans text-slate-900 dark:text-slate-100 transition-colors">
    <div class="max-w-[1600px] mx-auto space-y-8">

      <!-- Header -->
      <header class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <h1 class="text-3xl font-black tracking-tight">Library Management</h1>
          <p class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mt-1">Librarian Control Panel</p>
        </div>
        <div class="flex p-1.5 bg-slate-200/50 dark:bg-slate-800/50 rounded-2xl backdrop-blur-sm transition-colors">
          <button v-for="tab in tabs" :key="tab.id" @click="currentTab = tab.id"
            :class="[
              'px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all duration-300',
              currentTab === tab.id
                ? 'bg-white dark:bg-slate-700 text-indigo-600 dark:text-indigo-400 shadow-sm'
                : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'
            ]">
            <i :class="tab.icon" class="mr-1.5"></i> {{ tab.label }}
            <span v-if="tab.badge" class="ml-1.5 px-1.5 py-0.5 text-[8px] font-black rounded-md bg-red-500 text-white">
              {{ tab.badge }}
            </span>
          </button>
        </div>
      </header>

      <!-- Stats row -->
      <div v-if="stats" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <div v-for="s in statCards" :key="s.label"
             class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-200/60 dark:border-slate-800 shadow-sm dark:shadow-none transition-colors">
          <div class="flex items-center justify-between mb-2">
            <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest">{{ s.label }}</span>
            <i :class="[s.icon, s.color]" class="text-lg"></i>
          </div>
          <p class="text-2xl font-black" :class="s.valueColor || 'text-slate-800 dark:text-slate-100'">{{ s.prefix || '' }}{{ s.value }}</p>
        </div>
      </div>

      <!-- Tab content -->
      <Inventory v-if="currentTab === 'inventory'" />
      <Issuance v-else-if="currentTab === 'issuance'" />
      <Requests v-else-if="currentTab === 'requests'" />
      <Members v-else-if="currentTab === 'members'" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useLibraryAdmin } from '~/composables/library/useLibraryAdmin';
import Inventory from './inventory.vue';
import Issuance from './issuance.vue';
import Requests from './requests.vue';
import Members from './members.vue';

const { stats, fetchStats } = useLibraryAdmin();

const currentTab = ref('inventory');

const tabs = computed(() => [
  { id: 'inventory', label: 'Inventory', icon: 'fa fa-book' },
  { id: 'issuance', label: 'Issuance', icon: 'fa fa-exchange', badge: stats.value?.overdue_issues || null },
  { id: 'requests', label: 'Requests', icon: 'fa fa-inbox', badge: stats.value?.pending_requests || null },
  { id: 'members', label: 'Members', icon: 'fa fa-users' },
]);

const statCards = computed(() => {
  if (!stats.value) return [];
  const s = stats.value;
  return [
    { label: 'Total Books', value: s.total_books, icon: 'fa fa-book', color: 'text-indigo-500' },
    { label: 'Available', value: s.available_copies, icon: 'fa fa-check-circle', color: 'text-green-500', valueColor: 'text-green-600' },
    { label: 'Issued', value: s.issued_copies, icon: 'fa fa-hand-paper-o', color: 'text-amber-500', valueColor: 'text-amber-600' },
    { label: 'Overdue', value: s.overdue_issues, icon: 'fa fa-exclamation-triangle', color: 'text-red-500', valueColor: 'text-red-600' },
    { label: 'Pending', value: s.pending_requests, icon: 'fa fa-clock-o', color: 'text-blue-500', valueColor: 'text-blue-600' },
    { label: 'Fines', value: s.total_fines, icon: 'fa fa-money', color: 'text-amber-500', prefix: '₹', valueColor: 'text-amber-600' },
  ];
});

onMounted(() => fetchStats());
</script>
