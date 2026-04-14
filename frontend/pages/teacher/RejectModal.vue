<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>

    <div class="relative w-full max-w-lg bg-white dark:bg-slate-900 rounded-[2rem] shadow-2xl dark:shadow-none border border-slate-200 dark:border-slate-800 overflow-hidden transition-colors">

      <!-- Header -->
      <div class="p-6 border-b border-slate-100 dark:border-slate-800 transition-colors">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-black text-red-600 dark:text-red-400 transition-colors">Reject Application</h2>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Provide rejection details</p>
          </div>
          <button @click="$emit('close')" class="w-8 h-8 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
            <i class="fa fa-times"></i>
          </button>
        </div>
      </div>

      <!-- Form -->
      <div class="p-6 space-y-4">
        <div>
          <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">
            Reason for Rejection <span class="text-slate-300">(Optional)</span>
          </label>
          <textarea 
            v-model="reason" 
            rows="4" 
            placeholder="Enter the reason for rejection (if any)..."
            class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-red-500/10 resize-none transition-colors"
          ></textarea>
        </div>
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-3 transition-colors">
        <button @click="$emit('close')"
          class="px-6 py-2.5 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-xl text-xs font-black uppercase tracking-wider hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
          Cancel
        </button>
        <button @click="confirmReject" :disabled="submitting"
          class="px-6 py-2.5 bg-red-600 text-white rounded-xl text-xs font-black uppercase tracking-wider hover:bg-red-500 transition-all disabled:opacity-50 flex items-center gap-2">
          <i v-if="submitting" class="fa fa-circle-notch animate-spin"></i>
          {{ submitting ? 'Rejecting...' : 'Confirm Reject' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['close', 'confirm'])
const props = defineProps({
  submitting: {
    type: Boolean,
    default: false
  }
})

const reason = ref('')

const confirmReject = () => {
  emit('confirm', reason.value.trim() || null)
}
</script>