import { ref, type Ref } from 'vue'

export type ToastType = 'success' | 'error' | 'info' | 'warning' | string

export interface Toast {
  id: string
  message: string
  type: ToastType
  timeout?: number
}

export interface UseToastReturn {
  toasts: Ref<Toast[]>
  addToast: (message: string, type?: ToastType, duration?: number) => void
  removeToast: (id: string) => void
}

const toasts: Ref<Toast[]> = ref([])

export const useToast = (): UseToastReturn => {
  const addToast = (
    message: string,
    type: ToastType = 'success',
    duration: number = 4000
  ): void => {
    const id = Date.now() + Math.random().toString(36).substr(2, 9)
    toasts.value.push({ id, message, type })
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
  }

  const removeToast = (id: string): void => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }

  return { toasts, addToast, removeToast }
}
