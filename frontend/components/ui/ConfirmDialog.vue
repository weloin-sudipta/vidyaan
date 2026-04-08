<template>
  <Transition name="fade">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-[110] flex items-center justify-center min-h-screen p-4 sm:p-6 overflow-y-auto"
      role="dialog"
      aria-modal="true"
    >
      <!-- Overlay -->
      <div
        class="absolute inset-0 bg-slate-900/30 backdrop-blur-[3px]"
        @click="onCancel"
      ></div>

      <!-- Dialog Box -->
      <Transition name="zoom" appear>
        <div
          class="relative w-full max-w-md mx-auto flex flex-col overflow-hidden bg-white/95 dark:bg-slate-900/95 backdrop-blur-2xl border border-white/50 dark:border-slate-800/50 rounded-2xl sm:rounded-[2rem] shadow-[0_20px_60px_-15px_rgba(0,0,0,0.25)] dark:shadow-[0_20px_60px_-15px_rgba(0,0,0,0.6)]"
        >
          <!-- Decorative top accent -->
          <div :class="['h-1.5 w-full', styles.accent]"></div>

          <!-- Body -->
          <div class="px-6 sm:px-8 pt-6 sm:pt-8 pb-4 sm:pb-6">
            <div class="flex items-start gap-4">
              <!-- Icon bubble -->
              <div
                :class="[
                  'shrink-0 w-12 h-12 sm:w-14 sm:h-14 rounded-2xl flex items-center justify-center',
                  styles.iconBg,
                ]"
              >
                <i :class="['fa text-xl sm:text-2xl', styles.iconColor, icon || styles.icon]"></i>
              </div>

              <div class="flex-1 min-w-0">
                <h3
                  class="text-base sm:text-lg font-black tracking-tight text-slate-800 dark:text-white uppercase leading-tight"
                >
                  {{ title }}
                </h3>
                <p
                  class="mt-2 text-sm text-slate-600 dark:text-slate-300 leading-relaxed break-words"
                >
                  <slot>{{ message }}</slot>
                </p>
                <p
                  v-if="hint"
                  class="mt-3 text-xs font-semibold uppercase tracking-wide text-slate-400 dark:text-slate-500 flex items-center gap-1.5"
                >
                  <i class="fa fa-info-circle"></i>
                  <span>{{ hint }}</span>
                </p>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div
            class="px-6 sm:px-8 py-4 sm:py-5 bg-slate-50/70 dark:bg-slate-800/60 border-t border-slate-100/60 dark:border-slate-800/60 flex flex-col-reverse sm:flex-row sm:justify-end gap-3 rounded-b-2xl sm:rounded-b-[2rem]"
          >
            <button
              type="button"
              :disabled="loading"
              @click="onCancel"
              class="px-5 py-2.5 rounded-xl text-sm font-bold text-slate-600 dark:text-slate-300 bg-white dark:bg-slate-700 border border-slate-200 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ cancelText }}
            </button>

            <button
              type="button"
              :disabled="loading"
              @click="onConfirm"
              :class="[
                'px-5 py-2.5 rounded-xl text-sm font-bold text-white shadow-lg transition-all disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2',
                styles.button,
              ]"
            >
              <i v-if="loading" class="fa fa-spinner fa-spin"></i>
              <i v-else-if="confirmIcon" :class="['fa', confirmIcon]"></i>
              <span>{{ loading ? loadingText : confirmText }}</span>
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: 'Are you sure?' },
  message: { type: String, default: '' },
  hint: { type: String, default: '' },
  confirmText: { type: String, default: 'Confirm' },
  cancelText: { type: String, default: 'Cancel' },
  loadingText: { type: String, default: 'Working…' },
  confirmIcon: { type: String, default: '' },
  icon: { type: String, default: '' },
  // visual variant — controls accent + icon + button colors
  variant: {
    type: String,
    default: 'info', // 'info' | 'success' | 'warning' | 'danger' | 'publish'
    validator: (v) => ['info', 'success', 'warning', 'danger', 'publish'].includes(v),
  },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const VARIANTS = {
  info: {
    accent: 'bg-gradient-to-r from-indigo-500 to-blue-500',
    iconBg: 'bg-indigo-100 dark:bg-indigo-900/40',
    iconColor: 'text-indigo-600 dark:text-indigo-300',
    icon: 'fa-info-circle',
    button:
      'bg-gradient-to-r from-indigo-600 to-blue-600 hover:shadow-indigo-300 dark:hover:shadow-indigo-900',
  },
  success: {
    accent: 'bg-gradient-to-r from-emerald-500 to-green-500',
    iconBg: 'bg-emerald-100 dark:bg-emerald-900/40',
    iconColor: 'text-emerald-600 dark:text-emerald-300',
    icon: 'fa-check-circle',
    button:
      'bg-gradient-to-r from-emerald-600 to-green-600 hover:shadow-emerald-300 dark:hover:shadow-emerald-900',
  },
  warning: {
    accent: 'bg-gradient-to-r from-amber-500 to-orange-500',
    iconBg: 'bg-amber-100 dark:bg-amber-900/40',
    iconColor: 'text-amber-600 dark:text-amber-300',
    icon: 'fa-exclamation-triangle',
    button:
      'bg-gradient-to-r from-amber-500 to-orange-500 hover:shadow-amber-300 dark:hover:shadow-amber-900',
  },
  danger: {
    accent: 'bg-gradient-to-r from-rose-500 to-red-500',
    iconBg: 'bg-rose-100 dark:bg-rose-900/40',
    iconColor: 'text-rose-600 dark:text-rose-300',
    icon: 'fa-exclamation-circle',
    button:
      'bg-gradient-to-r from-rose-600 to-red-600 hover:shadow-rose-300 dark:hover:shadow-rose-900',
  },
  publish: {
    accent: 'bg-gradient-to-r from-violet-500 via-fuchsia-500 to-pink-500',
    iconBg: 'bg-violet-100 dark:bg-violet-900/40',
    iconColor: 'text-violet-600 dark:text-violet-300',
    icon: 'fa-paper-plane',
    button:
      'bg-gradient-to-r from-violet-600 via-fuchsia-600 to-pink-600 hover:shadow-fuchsia-300 dark:hover:shadow-fuchsia-900',
  },
}

const styles = computed(() => VARIANTS[props.variant] || VARIANTS.info)

const close = () => emit('update:modelValue', false)

const onConfirm = () => {
  if (props.loading) return
  emit('confirm')
}

const onCancel = () => {
  if (props.loading) return
  emit('cancel')
  close()
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.zoom-enter-active {
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.zoom-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}
</style>
