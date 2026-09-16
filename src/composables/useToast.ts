/**
 * Reactive toast notification system.
 */
import { reactive } from 'vue'
import type { Toast, ToastType } from '@/types'

const toasts = reactive<Toast[]>([])
let nextId = 0

function showToast(message: string, type: ToastType = 'info', duration = 4000) {
  const id = nextId++
  toasts.push({ id, message, type, duration })

  if (duration > 0) {
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }
}

function removeToast(id: number) {
  const idx = toasts.findIndex((t) => t.id === id)
  if (idx !== -1) toasts.splice(idx, 1)
}

export function useToast() {
  return {
    toasts,
    showToast,
    removeToast,
  }
}
