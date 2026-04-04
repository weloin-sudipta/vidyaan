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
          <h3 class="text-sm font-black text-slate-800 dark:text-slate-100 uppercase tracking-widest transition-colors">Book Requests</h3>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mt-1">{{ requests.length }} records</p>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50/50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800 transition-colors">
              <th class="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Member</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Book</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Date</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Queue</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Status</th>
              <th class="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-800 transition-colors">
            <tr v-for="req in requests" :key="req.name" class="hover:bg-slate-50/30 dark:hover:bg-slate-800/30 transition-colors">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="h-9 w-9 rounded-xl flex items-center justify-center font-black text-[10px] text-white bg-purple-600">
                    {{ initials(req.member_name) }}
                  </div>
                  <div>
                    <p class="text-xs font-black text-slate-700 dark:text-slate-200 transition-colors">{{ req.member_name }}</p>
                    <p class="text-[9px] font-bold text-slate-400 uppercase">{{ req.member_type }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-4">
                <p class="text-xs font-bold text-slate-700 dark:text-slate-200 transition-colors">{{ req.book_title }}</p>
                <p class="text-[9px] font-bold text-slate-400">{{ req.book_author }}</p>
              </td>
              <td class="px-4 py-4 text-xs font-bold text-slate-600 dark:text-slate-300 transition-colors">{{ formatDate(req.request_date) }}</td>
              <td class="px-4 py-4">
                <span v-if="req.priority" class="text-xs font-black text-indigo-600 dark:text-indigo-400 transition-colors">#{{ req.priority }}</span>
                <span v-else class="text-slate-300 text-xs">—</span>
              </td>
              <td class="px-4 py-4">
                <span :class="reqStatusBadge(req.status)" class="px-2 py-1 text-[9px] font-black uppercase tracking-wider rounded-lg border transition-colors">
                  {{ req.status }}
                </span>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="flex justify-end gap-2">
                  <template v-if="req.status === 'Pending'">
                    <button @click="handleApprove(req.name)" :disabled="actionLoading === req.name"
                      class="px-3 py-1.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-lg text-[9px] font-black uppercase hover:bg-green-600 hover:text-white transition-all">
                      <i class="fa fa-check mr-1"></i> Approve
                    </button>
                    <button @click="handleReject(req.name)" :disabled="actionLoading === req.name"
                      class="px-3 py-1.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg text-[9px] font-black uppercase hover:bg-red-600 hover:text-white transition-all">
                      <i class="fa fa-times mr-1"></i> Reject
                    </button>
                  </template>
                  <button v-if="req.status === 'Approved'" @click="handleIssue(req.name)" :disabled="actionLoading === req.name"
                    class="px-3 py-1.5 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-lg text-[9px] font-black uppercase hover:bg-indigo-600 hover:text-white transition-all">
                    <i class="fa fa-book mr-1"></i> Issue Book
                  </button>
                  <span v-if="req.status === 'Issued'" class="text-[9px] font-bold text-green-500 px-2 py-1.5">Completed</span>
                  <span v-if="req.status === 'Rejected'" class="text-[9px] font-bold text-red-400 px-2 py-1.5">Rejected</span>
                  <span v-if="req.status === 'Cancelled'" class="text-[9px] font-bold text-slate-400 px-2 py-1.5">Cancelled</span>
                </div>
              </td>
            </tr>
            <tr v-if="requests.length === 0">
              <td colspan="6" class="px-8 py-12 text-center">
                <i class="fa fa-inbox text-slate-200 dark:text-slate-700 text-5xl mb-4 block transition-colors"></i>
                <p class="text-sm font-black text-slate-400 uppercase">No requests found</p>
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

const { requests, loading, fetchRequests, approveRequest, rejectRequest, issueFromRequest } = useLibraryAdmin();
const activeFilter = ref('all');
const actionLoading = ref(null);

const filters = [
  { id: 'all', label: 'All Requests' },
  { id: 'Pending', label: 'Pending' },
  { id: 'Approved', label: 'Approved' },
  { id: 'Issued', label: 'Issued' },
  { id: 'Rejected', label: 'Rejected' },
];

const switchFilter = (id) => {
  activeFilter.value = id;
  fetchRequests(id === 'all' ? null : id);
};

const handleApprove = async (name) => {
  actionLoading.value = name;
  await approveRequest(name);
  await fetchRequests(activeFilter.value === 'all' ? null : activeFilter.value);
  actionLoading.value = null;
};

const handleReject = async (name) => {
  actionLoading.value = name;
  await rejectRequest(name);
  await fetchRequests(activeFilter.value === 'all' ? null : activeFilter.value);
  actionLoading.value = null;
};

const handleIssue = async (name) => {
  actionLoading.value = name;
  await issueFromRequest(name);
  await fetchRequests(activeFilter.value === 'all' ? null : activeFilter.value);
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

const reqStatusBadge = (status) => {
  const map = {
    Pending: 'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/50',
    Approved: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-blue-100 dark:border-blue-800/50',
    Issued: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-100 dark:border-green-800/50',
    Rejected: 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-100 dark:border-red-800/50',
    Cancelled: 'bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700',
  };
  return map[status] || map.Cancelled;
};

onMounted(() => fetchRequests());
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
</style>
