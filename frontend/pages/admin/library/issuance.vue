<template>
  <div class="space-y-6">

    <!-- Filters -->
    <div class="flex gap-2 overflow-x-auto no-scrollbar pb-2">
      <button v-for="f in filters" :key="f.id" @click="switchFilter(f.id)" :class="[
        activeFilter === f.id
          ? 'bg-slate-900 dark:bg-indigo-600 text-white shadow-lg'
          : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700',
        'px-6 py-3 rounded-2xl text-[10px] font-black uppercase tracking-widest border transition-all whitespace-nowrap'
      ]">
        {{ f.label }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-3">
      <UiSkeleton v-for="i in 5" :key="i" height="h-16" class="rounded-2xl" />
    </div>

    <!-- Table -->
    <div v-else class="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 overflow-hidden transition-colors">
      <div class="p-6 border-b border-slate-50 dark:border-slate-800 flex justify-between items-center transition-colors">
        <div>
          <h3 class="text-sm font-black text-slate-800 dark:text-slate-100 uppercase tracking-widest transition-colors">Book Issues</h3>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mt-1">{{ issues.length }} records</p>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50/50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800 transition-colors">
              <th class="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Borrower</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Book</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Issued</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Due Date</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Status</th>
              <th class="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-800 transition-colors">
            <tr v-for="issue in issues" :key="issue.name" class="hover:bg-slate-50/30 dark:hover:bg-slate-800/30 transition-colors">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="h-9 w-9 rounded-xl flex items-center justify-center font-black text-[10px] text-white bg-indigo-600">
                    {{ initials(issue.member_name) }}
                  </div>
                  <div>
                    <p class="text-xs font-black text-slate-700 dark:text-slate-200 transition-colors">{{ issue.member_name }}</p>
                    <p class="text-[9px] font-bold text-slate-400 uppercase">{{ issue.member_type }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-4">
                <p class="text-xs font-bold text-slate-700 dark:text-slate-200 transition-colors">{{ issue.book_title }}</p>
                <p class="text-[9px] font-bold text-slate-400">{{ issue.book_author }}</p>
              </td>
              <td class="px-4 py-4 text-xs font-bold text-slate-600 dark:text-slate-300 transition-colors">{{ formatDate(issue.issue_date) }}</td>
              <td class="px-4 py-4">
                <span :class="issue.is_overdue ? 'text-red-600 font-black' : 'text-slate-600 dark:text-slate-300 font-bold'" class="text-xs transition-colors">
                  {{ formatDate(issue.due_date) }}
                </span>
                <p v-if="issue.is_overdue" class="text-[9px] font-bold text-red-500 uppercase">{{ issue.days_overdue }} days late</p>
                <p v-else-if="issue.status === 'Issued'" class="text-[9px] font-bold text-green-500">{{ issue.days_left }} days left</p>
              </td>
              <td class="px-4 py-4">
                <span :class="statusBadge(issue)" class="px-2 py-1 text-[9px] font-black uppercase tracking-wider rounded-lg border transition-colors">
                  {{ issue.is_overdue ? 'Overdue' : issue.status }}
                </span>
                <span v-if="issue.renew_requested" class="ml-1 px-2 py-0.5 text-[8px] font-black uppercase rounded bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 border border-purple-100 dark:border-purple-800/50 transition-colors">
                  Renewal
                </span>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="flex justify-end gap-2">
                  <button v-if="issue.renew_requested && issue.status === 'Issued'"
                    @click="handleApproveRenewal(issue.name)"
                    :disabled="actionLoading === issue.name"
                    class="px-3 py-1.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-lg text-[9px] font-black uppercase hover:bg-purple-600 hover:text-white transition-all">
                    <i class="fa fa-refresh mr-1"></i> Approve Renew
                  </button>
                  <button v-if="issue.status === 'Issued'"
                    @click="handleReturn(issue.name)"
                    :disabled="actionLoading === issue.name"
                    class="px-3 py-1.5 bg-slate-900 dark:bg-indigo-600 text-white rounded-lg text-[9px] font-black uppercase hover:bg-indigo-600 dark:hover:bg-indigo-500 transition-all">
                    <i class="fa fa-reply mr-1"></i> Return
                  </button>
                  <span v-if="issue.status === 'Returned' && issue.fine_amount > 0"
                    class="text-[9px] font-black text-amber-600 dark:text-amber-400 px-2 py-1.5">
                    Fine: ₹{{ issue.fine_amount }}
                  </span>
                </div>
              </td>
            </tr>
            <tr v-if="issues.length === 0">
              <td colspan="6" class="px-8 py-12 text-center">
                <i class="fa fa-inbox text-slate-200 dark:text-slate-700 text-5xl mb-4 block transition-colors"></i>
                <p class="text-sm font-black text-slate-400 uppercase">No issues found</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useLibraryAdmin } from '~/composable/useLibraryAdmin';

const { issues, loading, fetchIssues, returnBook, approveRenewal } = useLibraryAdmin();
const activeFilter = ref('all');
const actionLoading = ref(null);

const filters = [
  { id: 'all', label: 'All Issues' },
  { id: 'Issued', label: 'Active' },
  { id: 'Overdue', label: 'Overdue' },
  { id: 'Returned', label: 'Returned' },
];

const switchFilter = (id) => {
  activeFilter.value = id;
  fetchIssues(id === 'all' ? null : id);
};

const handleReturn = async (name) => {
  actionLoading.value = name;
  await returnBook(name);
  await fetchIssues(activeFilter.value === 'all' ? null : activeFilter.value);
  actionLoading.value = null;
};

const handleApproveRenewal = async (name) => {
  actionLoading.value = name;
  await approveRenewal(name);
  await fetchIssues(activeFilter.value === 'all' ? null : activeFilter.value);
  actionLoading.value = null;
};

const initials = (name) => {
  if (!name) return '?';
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
};

const formatDate = (d) => {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
};

const statusBadge = (issue) => {
  if (issue.is_overdue) return 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-100 dark:border-red-800/50';
  if (issue.status === 'Returned') return 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-100 dark:border-green-800/50';
  return 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-blue-100 dark:border-blue-800/50';
};

onMounted(() => fetchIssues());
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
</style>
