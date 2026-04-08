<template>
  <div class="flex flex-col gap-1.5">
    <label
      v-if="label"
      :for="selectId"
      class="text-[11px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400"
    >
      {{ label }}<span v-if="required" class="text-rose-500 ml-0.5">*</span>
    </label>

    <div class="relative">
      <select
        :id="selectId"
        v-bind="$attrs"
        :value="modelValue"
        :disabled="disabled"
        :class="[
          'w-full appearance-none bg-slate-50 dark:bg-slate-700/60 border rounded-2xl py-3.5 px-6 pr-10 font-bold text-sm text-slate-800 dark:text-slate-100 transition-all duration-200',
          'focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:focus:ring-indigo-500 focus:border-transparent',
          error
            ? 'border-rose-400 dark:border-rose-500 bg-rose-50 dark:bg-rose-900/20'
            : 'border-slate-200 dark:border-slate-600 hover:border-indigo-300 dark:hover:border-indigo-600',
          disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
        ]"
        @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
      >
        <option v-if="placeholder" value="" disabled :selected="!modelValue">{{ placeholder }}</option>
        <slot>
          <option
            v-for="opt in options"
            :key="opt.value"
            :value="opt.value"
          >
            {{ opt.label }}
          </option>
        </slot>
      </select>

      <span class="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500">
        <i class="fa-solid fa-chevron-down text-xs"></i>
      </span>
    </div>

    <p v-if="error" class="text-xs text-rose-500 dark:text-rose-400 font-semibold px-1">
      <i class="fa-solid fa-circle-exclamation mr-1"></i>{{ error }}
    </p>
    <p v-else-if="hint" class="text-xs text-slate-400 dark:text-slate-500 px-1">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

export interface SelectOption {
  value: string | number
  label: string
}

const props = withDefaults(defineProps<{
  modelValue?: string | number
  options?: SelectOption[]
  label?: string
  placeholder?: string
  hint?: string
  error?: string
  disabled?: boolean
  required?: boolean
  id?: string
}>(), {
  options: () => [],
  disabled: false,
  required: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const selectId = computed(() => props.id ?? `ui-select-${Math.random().toString(36).slice(2, 7)}`)
</script>
