<template>
  <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 overflow-hidden animate-in fade-in duration-700 transition-colors">
    
    <div class="p-8 border-b border-slate-50 dark:border-slate-800 flex flex-col md:flex-row justify-between items-end gap-6 bg-slate-50/30 dark:bg-slate-800/20 transition-colors">
      <div>
        <h3 class="text-[10px] font-black uppercase tracking-[0.3em] text-slate-400 dark:text-slate-500 mb-1">Financial Records</h3>
        <p class="text-2xl font-black text-slate-800 dark:text-white tracking-tight">Payment Slips</p>
      </div>

      <div class="flex gap-3 w-full md:w-auto">
        <select class="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-[10px] font-black text-slate-500 dark:text-slate-400 uppercase tracking-widest outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors shadow-sm dark:shadow-none">
          <option>All Semesters</option>
          <option>Semester 3</option>
          <option>Semester 2</option>
        </select>
        <button class="bg-slate-900 dark:bg-indigo-600 text-white px-6 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-indigo-600 dark:hover:bg-indigo-500 transition-all shadow-lg dark:shadow-none active:scale-95">
          <i class="fa fa-filter mr-2"></i> Filter
        </button>
      </div>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse transition-colors">
        <thead>
          <tr class="bg-slate-50/50 dark:bg-slate-800/50">
            <th class="px-8 py-5 th-style">Reference ID</th>
            <th class="px-8 py-5 th-style">Date</th>
            <th class="px-8 py-5 th-style text-center">Status</th>
            <th class="px-8 py-5 th-style text-right">Amount</th>
            <!-- <th class="px-8 py-5 th-style text-right">Action</th> -->
          </tr>
        </thead>

        <tbody class="divide-y divide-slate-50 dark:divide-slate-800/50">
          <tr v-for="slip in paymentHistory" :key="slip.id" class="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors group">
            
            <td class="px-8 py-6">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-[10px] font-black transition-colors">
                  #{{ slip.id.slice(-2) }}
                </div>
                <span class="text-xs font-black text-slate-700 dark:text-slate-300 uppercase tracking-tighter">{{ slip.id }}</span>
              </div>
            </td>

            <td class="px-8 py-6">
              <span class="text-xs font-bold text-slate-500">{{ slip.date }}</span>
            </td>

            <td class="px-8 py-6 text-center">
              <span :class="getStatusStyles(slip.status)" class="px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest border shadow-sm">
                {{ slip.status }}
              </span>
            </td>

            <td class="px-8 py-6 text-right">
              <span class="text-sm font-black text-slate-900 dark:text-slate-100">
                {{ slip.amount.toLocaleString() }} {{ currency }}
              </span>
            </td>

            <td class="px-8 py-6 text-right">
              <button class="w-10 h-10 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-400 dark:text-slate-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:border-indigo-200 dark:hover:border-indigo-500/50 hover:shadow-md dark:hover:shadow-none transition-all">
                <i class="fa fa-download"></i>
              </button>
            </td>

          </tr>
        </tbody>
      </table>
    </div>

    <div class="p-8 bg-slate-50/30 dark:bg-slate-800/20 border-t border-slate-100 dark:border-slate-800 flex justify-between items-center transition-colors">
      <p class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">
        Total Outstanding: {{ totalOutstanding }} {{ currency }}
      </p>
      <!-- <button class="text-[10px] font-black text-indigo-600 dark:text-indigo-400 uppercase tracking-[0.2em] hover:text-slate-900 dark:hover:text-white transition-colors">
        Statement of Account <i class="fa fa-arrow-right ml-2"></i>
      </button> -->
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

/* PROPS FROM PARENT */
const props = defineProps({
  fees: {
    type: Object,
    default: () => ({
      fees: [],
      total_outstanding: 0,
      currency: "INR",
    }),
  },
});

/* EXTRACT DATA */
const paymentHistory = computed(() => {
  const list = props.fees?.fees || [];

  return list.slice(0, 3).map((fee) => ({
    id: fee.name,
    date: fee.posting_date,
    status: fee.status,
    amount: fee.grand_total,
  }));
});

const totalOutstanding = computed(() => props.fees?.outstanding || props.fees?.total_outstanding || 0);
const currency = computed(() => props.fees?.currency || "INR");

/* STATUS STYLES */
const getStatusStyles = (status) => {
  switch (status) {
    case 'Completed':
      return 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-100 dark:border-green-900/30';
    case 'Unpaid':
      return 'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-900/30';
    case 'Refunded':
      return 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-blue-100 dark:border-blue-900/30';
    default:
      return 'bg-slate-50 dark:bg-slate-800/50 text-slate-600 dark:text-slate-400 border-slate-100 dark:border-slate-700/50';
  }
};
</script>

<style scoped>
.th-style { 
  @apply text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 tracking-[0.2em]; 
}
</style>