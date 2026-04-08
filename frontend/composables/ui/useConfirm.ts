import { ref, reactive } from 'vue'

// ─── Types ────────────────────────────────────────────────────────────────────

export interface ConfirmOptions {
  title?: string
  message?: string
  hint?: string
  variant?: 'info' | 'success' | 'warning' | 'danger' | 'publish'
  confirmText?: string
  cancelText?: string
  loadingText?: string
  confirmIcon?: string
  icon?: string
}

// ─── Singleton state (module-level, shared across all callers) ─────────────────

const open = ref(false)
const loading = ref(false)
const opts = reactive<ConfirmOptions & Record<string, unknown>>({
  title: 'Are you sure?',
  message: '',
  hint: '',
  variant: 'info',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  loadingText: 'Working…',
  confirmIcon: '',
  icon: '',
})

let resolver: ((value: boolean) => void) | null = null

// ─── Composable ────────────────────────────────────────────────────────────────

export function useConfirm() {
  /**
   * Open the confirm dialog and return a Promise that resolves to true (user
   * confirmed) or false (user cancelled).
   *
   * Usage:
   *   const ok = await confirm({ title: '...', message: '...', variant: 'danger' })
   *   if (!ok) return
   *   setLoading(true)
   *   try { await action() } finally { setLoading(false) }
   */
  function confirm(options: ConfirmOptions): Promise<boolean> {
    // Merge defaults then overlay caller's options
    Object.assign(opts, {
      title: 'Are you sure?',
      message: '',
      hint: '',
      variant: 'info',
      confirmText: 'Confirm',
      cancelText: 'Cancel',
      loadingText: 'Working…',
      confirmIcon: '',
      icon: '',
      ...options,
    })
    open.value = true
    loading.value = false
    return new Promise<boolean>((res) => {
      resolver = res
    })
  }

  function setLoading(value: boolean) {
    loading.value = value
  }

  /** Called by <ConfirmDialog> @confirm event */
  function _accept() {
    if (loading.value) return // keep open while caller's async action runs
    resolver?.(true)
    resolver = null
    open.value = false
  }

  /** Called by <ConfirmDialog> @cancel event (also on overlay click) */
  function _cancel() {
    if (loading.value) return
    resolver?.(false)
    resolver = null
    open.value = false
  }

  /** Called by <ConfirmDialog> to signal action complete — closes the dialog */
  function _close() {
    loading.value = false
    open.value = false
    if (resolver) {
      resolver(false)
      resolver = null
    }
  }

  return {
    /** Reactive open state — bind to ConfirmDialog v-model */
    open,
    /** Reactive loading state — bind to ConfirmDialog :loading */
    loading,
    /** Reactive options object — spread as ConfirmDialog props */
    opts,
    confirm,
    setLoading,
    _accept,
    _cancel,
    _close,
  }
}
