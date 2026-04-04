<template>
  <div class="space-y-6">

    <!-- Search -->
    <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 p-6 transition-colors">
      <div class="flex flex-col lg:flex-row gap-4">
        <div class="flex-1">
          <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 block">Search Members</span>
          <div class="relative">
            <i class="fa fa-search absolute left-4 top-1/2 -translate-y-1/2 text-slate-300"></i>
            <input v-model="searchQuery" type="text" placeholder="Search by name, email, or phone..."
              class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl pl-12 pr-4 py-3 text-xs font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors" />
          </div>
        </div>
        <div class="w-full lg:w-48">
          <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 block">Type</span>
          <select v-model="selectedType"
            class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl px-4 py-3 text-xs font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors">
            <option value="">All Types</option>
            <option v-for="t in ['Student', 'Teacher', 'Staff', 'External']" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
        <div class="w-full lg:w-48">
          <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3 block">Status</span>
          <select v-model="selectedStatus"
            class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 rounded-2xl px-4 py-3 text-xs font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors">
            <option value="">All</option>
            <option v-for="s in ['Active', 'Suspended', 'Expired']" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
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
          <h3 class="text-sm font-black text-slate-800 dark:text-slate-100 uppercase tracking-widest transition-colors">Library Members</h3>
          <p class="text-[10px] font-bold text-slate-400 uppercase tracking-tighter mt-1">{{ filteredMembers.length }} members</p>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-slate-50/50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800 transition-colors">
              <th class="px-6 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Member</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Type</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Contact</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Joined</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest text-center">Books</th>
              <th class="px-4 py-4 text-[10px] font-black uppercase text-slate-400 tracking-widest">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-800 transition-colors">
            <tr v-for="m in filteredMembers" :key="m.name" class="hover:bg-slate-50/30 dark:hover:bg-slate-800/30 transition-colors">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="h-9 w-9 rounded-xl flex items-center justify-center font-black text-[10px] text-white"
                       :class="typeAvatarColor(m.member_type)">
                    {{ initials(m.member_name) }}
                  </div>
                  <div>
                    <p class="text-xs font-black text-slate-700 dark:text-slate-200 transition-colors">{{ m.member_name }}</p>
                    <p class="text-[9px] font-bold text-slate-400">{{ m.name }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-4">
                <span :class="typeBadge(m.member_type)" class="px-2 py-1 text-[9px] font-black uppercase tracking-wider rounded-lg border transition-colors">
                  {{ m.member_type }}
                </span>
              </td>
              <td class="px-4 py-4">
                <p class="text-xs font-bold text-slate-600 dark:text-slate-300 transition-colors">{{ m.email || '—' }}</p>
                <p class="text-[9px] font-bold text-slate-400">{{ m.phone || '' }}</p>
              </td>
              <td class="px-4 py-4 text-xs font-bold text-slate-600 dark:text-slate-300 transition-colors">{{ formatDate(m.join_date) }}</td>
              <td class="px-4 py-4 text-center">
                <span class="text-sm font-black" :class="m.current_issued_books >= m.max_books_allowed ? 'text-red-600' : 'text-slate-700 dark:text-slate-200'">
                  {{ m.current_issued_books || 0 }}
                </span>
                <span class="text-[9px] font-bold text-slate-400"> / {{ m.max_books_allowed }}</span>
              </td>
              <td class="px-4 py-4">
                <span :class="memberStatusBadge(m.status)" class="px-2 py-1 text-[9px] font-black uppercase tracking-wider rounded-lg border transition-colors">
                  {{ m.status }}
                </span>
              </td>
            </tr>
            <tr v-if="filteredMembers.length === 0">
              <td colspan="6" class="px-8 py-12 text-center">
                <i class="fa fa-users text-slate-200 dark:text-slate-700 text-5xl mb-4 block transition-colors"></i>
                <p class="text-sm font-black text-slate-400 uppercase">No members found</p>
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

const { members, loading, fetchMembers } = useLibraryAdmin();

const searchQuery = ref('');
const selectedType = ref('');
const selectedStatus = ref('');

const filteredMembers = computed(() => {
  let result = members.value;

  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter(m =>
      (m.member_name || '').toLowerCase().includes(q) ||
      (m.email || '').toLowerCase().includes(q) ||
      (m.phone || '').includes(q)
    );
  }

  if (selectedType.value) {
    result = result.filter(m => m.member_type === selectedType.value);
  }

  if (selectedStatus.value) {
    result = result.filter(m => m.status === selectedStatus.value);
  }

  return result;
});

const initials = (name) => {
  if (!name) return '?';
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
};

const formatDate = (d) => {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
};

const typeAvatarColor = (type) => {
  const map = { Student: 'bg-indigo-600', Teacher: 'bg-green-600', Staff: 'bg-amber-600', External: 'bg-slate-600' };
  return map[type] || 'bg-slate-600';
};

const typeBadge = (type) => {
  const map = {
    Student: 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 border-indigo-100 dark:border-indigo-800/50',
    Teacher: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-100 dark:border-green-800/50',
    Staff: 'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/50',
    External: 'bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700',
  };
  return map[type] || map.External;
};

const memberStatusBadge = (status) => {
  const map = {
    Active: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-100 dark:border-green-800/50',
    Suspended: 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-100 dark:border-red-800/50',
    Expired: 'bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700',
  };
  return map[status] || map.Expired;
};

onMounted(() => fetchMembers());
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
</style>
