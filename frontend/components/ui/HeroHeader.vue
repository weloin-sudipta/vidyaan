<template>
  <header
    class="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 
           p-8 flex flex-col lg:flex-row justify-between items-center gap-6 transition-colors"
  >

    <!-- LEFT SECTION -->
    <div class="flex items-center gap-4">

      <!-- Optional Icon -->
      <div v-if="icon"
           class="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center 
                  justify-center text-white shadow-xl shadow-indigo-100 dark:shadow-none transition-colors">
        <i :class="icon + ' text-2xl'"></i>
      </div>

      <div>
        <h1 class="text-3xl font-black tracking-tight text-slate-800 dark:text-slate-100 transition-colors">
          {{ title }}
        </h1>

        <p v-if="subtitle"
           class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase 
                  tracking-[0.2em] mt-1 transition-colors">
          {{ subtitle }}
        </p>
      </div>

    </div>

    <!-- RIGHT SECTION -->
    <div class="flex items-center gap-4 w-full lg:w-auto">

      <!-- Optional Search -->
      <div v-if="searchable"
           class="w-full lg:w-96 relative">
        <i class="fa fa-search absolute left-4 top-1/2 -translate-y-1/2 text-slate-300 dark:text-slate-500 transition-colors"></i>

        <input
          v-model="internalSearch"
          @input="$emit('update:search', internalSearch)"
          type="text"
          :placeholder="searchPlaceholder"
          class="w-full bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800/50 rounded-2xl 
                 pl-12 pr-4 py-3 text-xs font-bold text-slate-700 dark:text-slate-300
                 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-all"
        />
      </div>

      <!-- Action Buttons Slot -->
      <div class="flex gap-3">
        <slot />
      </div>

    </div>

  </header>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  title: String,
  subtitle: String,
  icon: String,
  searchable: {
    type: Boolean,
    default: false
  },
  search: String,
  searchPlaceholder: {
    type: String,
    default: 'Search...'
  }
})

const emit = defineEmits(['update:search'])

const internalSearch = ref(props.search || '')

watch(() => props.search, (val) => {
  internalSearch.value = val
})
</script>