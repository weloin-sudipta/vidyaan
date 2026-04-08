<template>
  <header
    class="bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-sm dark:shadow-none border border-slate-200/60 dark:border-slate-800 p-8 flex flex-col lg:flex-row justify-between items-center gap-6 transition-colors"
  >
    <!-- Left: icon + title + subtitle -->
    <div class="flex items-center gap-4">
      <div
        v-if="icon"
        class="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-indigo-100 dark:shadow-none"
      >
        <i :class="[icon, 'text-2xl']"></i>
      </div>
      <div>
        <h1 class="text-3xl font-black tracking-tight text-slate-800 dark:text-slate-100">
          {{ title }}
        </h1>
        <p
          v-if="subtitle"
          class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mt-1"
        >
          {{ subtitle }}
        </p>
      </div>
    </div>

    <!-- Right: search + filter slot -->
    <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full lg:w-auto">
      <!-- Search -->
      <div class="relative w-full lg:w-80">
        <i class="fa fa-search absolute left-4 top-1/2 -translate-y-1/2 text-slate-300 dark:text-slate-500"></i>
        <input
          :value="modelValue"
          type="text"
          :placeholder="searchPlaceholder"
          class="w-full bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800/50 rounded-2xl pl-12 pr-4 py-3 text-xs font-bold text-slate-700 dark:text-slate-300 outline-none focus:ring-4 focus:ring-indigo-500/10 transition-all"
          @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        />
      </div>

      <!-- Filter selects slot -->
      <slot />
    </div>
  </header>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title?: string
  subtitle?: string
  icon?: string
  modelValue?: string
  searchPlaceholder?: string
}>(), {
  searchPlaceholder: 'Search...',
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()
</script>
