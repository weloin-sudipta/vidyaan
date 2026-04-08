<template>
  <div class="flex flex-col gap-1.5">
    <label
      v-if="label"
      :for="inputId"
      class="text-[11px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400"
    >
      {{ label }}<span v-if="required" class="text-rose-500 ml-0.5">*</span>
    </label>

    <input
      :id="inputId"
      v-bind="$attrs"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="[
        'w-full bg-slate-50 dark:bg-slate-700/60 border rounded-2xl py-3.5 px-6 font-bold text-sm text-slate-800 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500 transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-indigo-400 dark:focus:ring-indigo-500 focus:border-transparent',
        error
          ? 'border-rose-400 dark:border-rose-500 bg-rose-50 dark:bg-rose-900/20'
          : 'border-slate-200 dark:border-slate-600 hover:border-indigo-300 dark:hover:border-indigo-600',
        disabled ? 'opacity-50 cursor-not-allowed' : '',
      ]"
      @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />

    <p v-if="error" class="text-xs text-rose-500 dark:text-rose-400 font-semibold px-1">
      <i class="fa-solid fa-circle-exclamation mr-1"></i>{{ error }}
    </p>
    <p v-else-if="hint" class="text-xs text-slate-400 dark:text-slate-500 px-1">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  modelValue?: string | number
  label?: string
  placeholder?: string
  hint?: string
  error?: string
  type?: string
  disabled?: boolean
  required?: boolean
  id?: string
}>(), {
  type: 'text',
  disabled: false,
  required: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const inputId = computed(() => props.id ?? `ui-input-${Math.random().toString(36).slice(2, 7)}`)
</script>
