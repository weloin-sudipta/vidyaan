<template>
  <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 overflow-hidden animate-in fade-in duration-500 transition-colors">
    
    <div class="flex flex-col lg:flex-row justify-between items-center p-8 gap-6 border-b border-slate-50 dark:border-slate-800 transition-colors">
      <div class="flex items-center gap-4">
        <div class="flex flex-col">
          <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">View Count</span>
          <select v-model="itemsPerPage" class="bg-slate-50 border border-slate-100 rounded-xl px-4 py-2 text-xs font-bold text-slate-700 outline-none focus:ring-2 focus:ring-indigo-500/20">
            <option :value="10">10 Rows</option>
            <option :value="25">25 Rows</option>
            <option :value="50">50 Rows</option>
          </select>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row items-end gap-4 w-full lg:w-auto">
        <div class="w-full sm:w-72">
          <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5 block">Quick Search</span>
          <div class="relative">
            <i class="fa fa-search absolute left-4 top-1/2 -translate-y-1/2 text-slate-300"></i>
            <input 
              v-model="searchQuery"
              type="search" 
              placeholder="Student Name or Email..." 
              class="w-full bg-slate-50 border border-slate-100 rounded-xl pl-10 pr-4 py-2 text-xs font-bold text-slate-700 outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all"
            />
          </div>
        </div>
        
        <div class="flex gap-2 w-full sm:w-auto">
          <button class="btn-icon h-10 w-10"><i class="fa fa-download"></i></button>
          <button class="btn-primary flex items-center gap-2">
            <i class="fa fa-plus"></i> Add New Student
          </button>
        </div>
      </div>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-slate-50/50">
            <th class="px-8 py-5 w-12"><input type="checkbox" class="rounded-lg border-slate-200 text-indigo-600 focus:ring-indigo-500"></th>
            <th class="px-6 py-5 text-[10px] font-black uppercase text-slate-400 tracking-widest">Student</th>
            <th class="px-6 py-5 text-[10px] font-black uppercase text-slate-400 tracking-widest">Course / Batch</th>
            <th class="px-6 py-5 text-[10px] font-black uppercase text-slate-400 tracking-widest">Billing Plan</th>
            <th class="px-6 py-5 text-[10px] font-black uppercase text-slate-400 tracking-widest">Status</th>
            <th class="px-6 py-5 text-[10px] font-black uppercase text-slate-400 tracking-widest text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-50">
          <tr v-for="user in paginatedUsers" :key="user.id" class="hover:bg-slate-50/30 transition-colors group">
            <td class="px-8 py-5"><input type="checkbox" class="rounded-lg border-slate-200"></td>
            <td class="px-6 py-5">
              <div class="flex items-center gap-4">
                <div class="relative">
                  <img v-if="user.avatar" :src="user.avatar" class="h-10 w-10 rounded-2xl object-cover ring-2 ring-white shadow-sm" />
                  <div v-else class="h-10 w-10 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-black text-xs uppercase border border-indigo-100">
                    {{ user.initials }}
                  </div>
                  <div class="absolute -bottom-1 -right-1 w-3 h-3 border-2 border-white rounded-full" :class="user.status === 'Active' ? 'bg-green-500' : 'bg-slate-300'"></div>
                </div>
                <div class="flex flex-col">
                  <span class="text-sm font-black text-slate-700 group-hover:text-indigo-600 cursor-pointer transition-colors">{{ user.name }}</span>
                  <span class="text-[10px] font-bold text-slate-400">{{ user.email }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-5">
              <div class="flex flex-col gap-1">
                <div class="flex items-center gap-2">
                   <i :class="['fa', user.roleIcon === 'bx-user' ? 'fa-user' : 'fa-graduation-cap', 'text-indigo-400 text-xs']"></i>
                   <span class="text-xs font-black text-slate-600">{{ user.role }}</span>
                </div>
                <span class="text-[10px] font-bold text-slate-300 uppercase tracking-tighter">{{ user.plan }}</span>
              </div>
            </td>
            <td class="px-6 py-5">
              <div class="flex flex-col">
                <span class="text-xs font-bold text-slate-600">{{ user.billing }}</span>
                <span class="text-[10px] text-slate-300 font-bold uppercase tracking-tighter">Automatic Sync</span>
              </div>
            </td>
            <td class="px-6 py-5">
              <span :class="['px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-tighter shadow-sm border', statusStyles[user.status]]">
                {{ user.status }}
              </span>
            </td>
            <td class="px-6 py-5 text-right">
              <div class="flex justify-end gap-2">
                <button class="btn-action-gray" title="View"><i class="fa fa-eye"></i></button>
                <button class="btn-action-gray" title="Edit"><i class="fa fa-pencil"></i></button>
                <button class="btn-action-red" title="Delete"><i class="fa fa-trash"></i></button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="flex flex-col md:flex-row justify-between items-center p-8 bg-slate-50/30 border-t border-slate-100 gap-4">
      <span class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
        Showing {{ (currentPage - 1) * itemsPerPage + 1 }} - 
        {{ Math.min(currentPage * itemsPerPage, filteredUsers.length) }} of 
        {{ filteredUsers.length }} Students
      </span>
      
      <div class="flex items-center gap-2">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="p-2 w-10 h-10 rounded-xl bg-white border border-slate-200 disabled:opacity-30 disabled:cursor-not-allowed hover:border-indigo-500 transition-all shadow-sm"
        >
          <i class="fa fa-chevron-left text-xs text-slate-400"></i>
        </button>
        
        <div class="flex gap-1">
          <button 
            v-for="page in totalPages" 
            :key="page"
            @click="currentPage = page"
            :class="[
              'w-10 h-10 rounded-xl text-xs font-black transition-all shadow-sm', 
              currentPage === page 
                ? 'bg-slate-900 text-white shadow-slate-200' 
                : 'bg-white text-slate-500 border border-slate-200 hover:border-indigo-400'
            ]"
          >
            {{ page }}
          </button>
        </div>

        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="p-2 w-10 h-10 rounded-xl bg-white border border-slate-200 disabled:opacity-30 disabled:cursor-not-allowed hover:border-indigo-500 transition-all shadow-sm"
        >
          <i class="fa fa-chevron-right text-xs text-slate-400"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const searchQuery = ref('');
const itemsPerPage = ref(10);
const currentPage = ref(1);

// Mock Data
const users = ref([
  { id: 1, name: 'Zsazsa McCleverty', email: 'zmcclevertye@soundcloud.com', role: 'Maintainer', plan: 'Enterprise', billing: 'Auto Debit', status: 'Active', avatar: 'https://i.pravatar.cc/150?u=1', roleIcon: 'bx-user', color: 'green' },
  { id: 2, name: 'Yoko Pottie', email: 'ypottiec@privacy.gov.au', role: 'Subscriber', plan: 'Basic', billing: 'Auto Debit', status: 'Inactive', avatar: 'https://i.pravatar.cc/150?u=2', roleIcon: 'bx-crown', color: 'blue' },
  { id: 3, name: 'Wesley Burland', email: 'wburlandj@uiuc.edu', role: 'Editor', plan: 'Team', billing: 'Auto Debit', status: 'Inactive', avatar: 'https://i.pravatar.cc/150?u=3', roleIcon: 'bx-pie-chart-alt', color: 'cyan' },
  { id: 4, name: 'Vladamir Koschek', email: 'vkoschek17@abc.net.au', role: 'Author', plan: 'Team', billing: 'Manual - Paypal', status: 'Active', initials: 'VK', roleIcon: 'bx-edit', color: 'orange' },
  { id: 5, name: 'Tyne Widmore', email: 'twidmore12@bravesites.com', role: 'Subscriber', plan: 'Team', billing: 'Manual - Cash', status: 'Pending', initials: 'TW', roleIcon: 'bx-crown', color: 'blue' },
]);

// Search Logic
const filteredUsers = computed(() => {
  return users.value.filter(user => 
    user.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    user.email.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// Pagination Logic
const totalPages = computed(() => Math.ceil(filteredUsers.value.length / itemsPerPage.value) || 1);
const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  return filteredUsers.value.slice(start, start + itemsPerPage.value);
});

const statusStyles = {
  Active: 'bg-green-50 text-green-600 border-green-100',
  Inactive: 'bg-slate-50 text-slate-500 border-slate-100',
  Pending: 'bg-amber-50 text-amber-600 border-amber-100'
};
</script>

<style scoped>
.btn-primary {
  @apply px-6 py-2.5 bg-indigo-600 text-white rounded-xl text-[10px] font-black uppercase tracking-[0.2em] shadow-xl shadow-indigo-100 hover:bg-indigo-700 active:scale-95 transition-all;
}

.btn-icon {
  @apply flex items-center justify-center bg-white border border-slate-200 text-slate-400 rounded-xl hover:text-indigo-600 hover:border-indigo-100 transition-all;
}

.btn-action-gray {
  @apply w-8 h-8 flex items-center justify-center bg-white border border-slate-100 text-slate-400 rounded-lg hover:bg-slate-900 hover:text-white transition-all shadow-sm;
}

.btn-action-red {
  @apply w-8 h-8 flex items-center justify-center bg-white border border-slate-100 text-slate-400 rounded-lg hover:bg-red-500 hover:text-white transition-all shadow-sm;
}

.btn-action-gray i, .btn-action-red i {
  @apply text-xs;
}
</style>