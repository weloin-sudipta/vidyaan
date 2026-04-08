<template>
  <div>
    <!-- SKELETON LOADING -->
    <div v-if="loading" class="space-y-6 animate-in fade-in duration-500">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <UiSkeleton height="h-28" class="rounded-[2rem]" v-for="i in 2" :key="'fee-card-'+i" />
      </div>
      <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-200/60 dark:border-slate-800 shadow-sm overflow-hidden p-8 space-y-6 transition-colors">
        <UiSkeleton height="h-6" width="w-1/4" class="mb-4" />
        <UiSkeleton height="h-16" class="rounded-xl w-full" v-for="i in 4" :key="'fee-row-'+i" />
      </div>
    </div>

    <!-- EMPTY / ERROR STATE -->
    <div v-else-if="hasError || fees.length === 0"
      class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-dashed border-slate-200 dark:border-slate-800 p-24 flex flex-col items-center gap-3 text-center transition-colors">
      <div class="w-16 h-16 bg-slate-50 dark:bg-slate-800 rounded-2xl flex items-center justify-center mb-2 transition-colors">
        <i class="fa fa-file-text-o text-slate-300 dark:text-slate-600 text-2xl transition-colors"></i>
      </div>
      <p class="text-sm font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest transition-colors">
        No Fee Data Available
      </p>
      <p class="text-xs text-slate-300 dark:text-slate-600 font-medium transition-colors">
        Your fee records could not be loaded. Please try again later.
      </p>
    </div>

    <!-- CONTENT -->
    <div v-else class="space-y-6 animate-in fade-in duration-500">

      <!-- SUMMARY CARDS -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white dark:bg-slate-900 p-6 rounded-[2rem] border border-slate-200/60 dark:border-slate-800 shadow-sm transition-colors">
          <p class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-1 transition-colors">
            Total Program Fees
          </p>
          <p class="text-2xl font-black text-slate-800 dark:text-slate-100 transition-colors">
            ₹{{ totalFees.toLocaleString() }}
          </p>
        </div>

        <div class="bg-red-50 dark:bg-red-900/20 p-6 rounded-[2rem] border border-red-100 dark:border-red-900/30 shadow-sm transition-colors">
          <p class="text-[10px] font-black text-red-600 dark:text-red-400 uppercase tracking-widest mb-1 transition-colors">
            Outstanding Balance
          </p>
          <p class="text-2xl font-black text-red-700 dark:text-red-300 transition-colors">
            ₹{{ balanceDue.toLocaleString() }}
          </p>
        </div>
      </div>

      <!-- TABLE -->
      <div class="bg-white dark:bg-slate-900 rounded-[2.5rem] border border-slate-200/60 dark:border-slate-800 shadow-sm overflow-hidden transition-colors">
        <div class="px-8 py-6 border-b border-slate-50 dark:border-slate-800/50 transition-colors">
          <h3 class="text-sm font-black text-slate-800 dark:text-slate-100 uppercase tracking-wider">
            Fee Details & History
          </h3>
        </div>

        <table class="w-full text-left border-collapse">
          <thead class="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800/50">
            <tr>
              <th class="p-6 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500">
                Program / Enrollment
              </th>
              <th class="p-6 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500">
                Due Date
              </th>
              <th class="p-6 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500">
                Total Amount
              </th>
              <th class="p-6 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500">
                Status
              </th>
              <!-- <th class="p-6 text-[10px] font-black uppercase text-slate-400 dark:text-slate-500 text-right">
                Action
              </th> -->
            </tr>
          </thead>

          <tbody class="divide-y divide-slate-50 dark:divide-slate-800/50 text-sm font-bold text-slate-700 dark:text-slate-300">
            <template v-for="fee in fees" :key="fee.id">
              <tr
                @click="toggleExpand(fee.id)"
                class="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 cursor-pointer group"
                :class="{ 'bg-indigo-50/30 dark:bg-indigo-900/20': expandedId === fee.id }">

                <td class="p-6">
                  <div class="flex items-center gap-4">
                    <div
                      :class="[
                        'w-8 h-8 rounded-xl flex items-center justify-center',
                        expandedId === fee.id
                          ? 'bg-indigo-600 text-white'
                          : 'bg-slate-100 dark:bg-slate-800 text-slate-400'
                      ]">
                      <i :class="['fa', expandedId === fee.id ? 'fa-minus' : 'fa-plus', 'text-[10px]']"></i>
                    </div>

                    <div>
                      <span class="block text-slate-800 dark:text-slate-100">
                        {{ fee.program_name }}
                      </span>
                      <span class="text-[10px] text-slate-400 dark:text-slate-500 uppercase">
                        {{ fee.transactionId }}
                      </span>
                    </div>
                  </div>
                </td>

                <td class="p-6">{{ fee.date }}</td>

                <td class="p-6">
                  ₹{{ fee.amount.toLocaleString() }}
                </td>

                <td class="p-6">
                  <span :class="[
                    fee.status === 'Paid'
                      ? 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'
                      : 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400',
                    'px-3 py-1 rounded-lg text-[10px] font-black uppercase'
                  ]">
                    {{ fee.status }}
                  </span>
                </td>

                <!-- <td class="p-6 text-right">
                  <button
                    v-if="fee.status === 'Unpaid'"
                    class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-[10px] font-black uppercase shadow-md active:scale-95">
                    Pay Now
                  </button>

                  <button
                    v-else
                    @click.stop="downloadFee(fee)"
                    class="text-slate-400 hover:text-indigo-600 p-2">
                    <i class="fa fa-file-pdf-o text-lg"></i>
                  </button>
                </td> -->
              </tr>

              <!-- EXPANDED ROW -->
              <tr v-if="expandedId === fee.id">
                <td colspan="5" class="bg-slate-50/50 dark:bg-slate-800/30 p-0">
                  <div class="px-20 py-8">
                    <div class="bg-white dark:bg-slate-900 rounded-3xl border p-6 max-w-2xl">
                      <h4 class="text-[10px] font-black uppercase mb-6 text-slate-400">
                        Detailed Fee Components
                      </h4>

                      <div class="space-y-4">
                        <div v-for="(item, index) in fee.breakout" :key="index"
                          class="flex justify-between border-b last:border-0 pb-3">
                          <span>{{ item.label }}</span>
                          <span class="font-black">₹{{ item.value.toLocaleString() }}</span>
                        </div>
                      </div>

                      <div class="mt-6 pt-6 border-t flex justify-between">
                        <span class="text-xs font-black uppercase">Total</span>
                        <span class="text-xl font-black text-indigo-600">
                          ₹{{ fee.amount.toLocaleString() }}
                        </span>
                      </div>

                      <p class="mt-4 text-[10px] italic text-slate-400">
                        Note: {{ fee.words }}
                      </p>
                    </div>
                  </div>
                </td>
              </tr>

            </template>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useStudentDashboard } from "~/composables/useStudentDashboard";
import { useToast } from '~/composables/useToast';

const { dashboardData, loading, error, loadDashboard } = useStudentDashboard();
const { addToast } = useToast();

const expandedId = ref(null);
const hasError = ref(false);

/**
 * Load dashboard data
 */
onMounted(async () => {
  try {
    await loadDashboard();
  } catch (err) {
    console.error('Dashboard load error:', err);
    hasError.value = true;
  }
});

/**
 * Transform API fees → UI-friendly structure
 */
const fees = computed(() => {
  const feeData = dashboardData.value?.fees;

  if (!feeData || !feeData.fees || feeData.fees.length === 0) {
    return [];
  }

  return feeData.fees.map((item) => ({
    id: item.name,
    program_name: item.fee_structure || "Fee",
    transactionId: item.name,
    amount: Number(item.grand_total) || 0,
    status: (Number(item.outstanding_amount) || 0) === 0 ? "Paid" : "Unpaid",
    date: item.due_date || item.posting_date || "N/A",
    words: item.remarks || "N/A",
    breakout: [] // No breakdown in API
  }));
});

/**
 * Summary calculations
 */
const totalFees = computed(() =>
  fees.value.reduce((acc, curr) => acc + (Number(curr.amount) || 0), 0)
);

const balanceDue = computed(() =>
  fees.value.reduce((acc, curr) =>
    curr.status === 'Unpaid' ? acc + (Number(curr.amount) || 0) : acc, 0
  )
);

/**
 * UI actions
 */
const toggleExpand = (id) => {
  expandedId.value = expandedId.value === id ? null : id;
};

const downloadFee = (fee) => {
  addToast(`Downloading Receipt for ${fee.transactionId}`, 'success');
};
</script>