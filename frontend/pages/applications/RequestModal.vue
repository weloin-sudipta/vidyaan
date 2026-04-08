<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>

    <div class="relative w-full max-w-lg bg-white dark:bg-slate-900 rounded-[2rem] shadow-2xl dark:shadow-none border border-slate-200 dark:border-slate-800 overflow-hidden transition-colors">

      <!-- Header -->
      <div class="p-6 border-b border-slate-100 dark:border-slate-800 transition-colors">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-black text-slate-800 dark:text-slate-100 transition-colors">New Request</h2>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Submit to administration</p>
          </div>
          <button @click="$emit('close')" class="w-8 h-8 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
            <i class="fa fa-times"></i>
          </button>
        </div>
      </div>

      <!-- Form -->
      <div class="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">Category *</label>
            <select v-model="form.category" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors">
              <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>
          <div>
            <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">Priority</label>
            <select v-model="form.priority" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors">
              <option v-for="p in ['Low', 'Medium', 'High', 'Urgent']" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>
        </div>

        <div>
          <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">Subject *</label>
          <input v-model="form.subject" type="text" placeholder="Brief title for your request"
            class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-colors" />
        </div>

        <div>
          <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 block">Description *</label>
          <textarea v-model="form.description" rows="4" placeholder="Describe your request in detail..."
            class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm font-bold text-slate-700 dark:text-slate-200 outline-none focus:ring-4 focus:ring-indigo-500/10 resize-none transition-colors"></textarea>
        </div>
      </div>

      <!-- Footer -->
      <div class="p-6 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-3 transition-colors">
        <button @click="$emit('close')"
          class="px-6 py-2.5 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded-xl text-xs font-black uppercase tracking-wider hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors">
          Cancel
        </button>
        <button @click="submit" :disabled="submitting || !isValid"
          class="px-6 py-2.5 bg-indigo-600 text-white rounded-xl text-xs font-black uppercase tracking-wider hover:bg-indigo-700 transition-all disabled:opacity-50">
          {{ submitting ? 'Submitting...' : 'Submit Request' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { call } from '~/composables/api/useFrappeFetch'
import { useToast } from '~/composables/ui/useToast'

const emit = defineEmits(['close', 'submitted'])
const { addToast } = useToast()

const submitting = ref(false)
const categories = ["General", "Academic", "Administrative", "Facility", "Complaint", "Permission", "Other"]

const form = ref({
  category: 'General',
  priority: 'Medium',
  subject: '',
  description: '',
})

const isValid = computed(() => form.value.subject.trim() && form.value.description.trim())

const submit = async () => {
  submitting.value = true
  try {
    await call('vidyaan.api_folder.applications.submit_request', {
      subject: form.value.subject,
      description: form.value.description,
      category: form.value.category,
      priority: form.value.priority,
    })
    addToast('Request submitted successfully!', 'success')
    emit('submitted')
  } catch (err) {
    let msg = 'Failed to submit request.'
    if (err instanceof Error && err.message) {
      msg = err.message
    } else if (err?.data?._server_messages) {
      try {
        msg = JSON.parse(JSON.parse(err.data._server_messages)[0]).message
      } catch {}
    }
    addToast(msg, 'error')
  } finally {
    submitting.value = false
  }
}
</script>
