/**
 * Universal Modal Dialog State & Composable.
 */
import { ref } from 'vue'

export type ModalType = 'warning' | 'error' | 'confirm' | 'info'

export interface ModalConfig {
  type: ModalType
  title: string
  message: string
  detail?: string
  confirmText?: string
  cancelText?: string
  danger?: boolean
  resolve?: (value: boolean) => void
}

const isOpen = ref(false)
const modalConfig = ref<ModalConfig>({
  type: 'warning',
  title: '',
  message: '',
})

function showModal(config: Omit<ModalConfig, 'resolve'>): Promise<boolean> {
  return new Promise((resolve) => {
    modalConfig.value = {
      ...config,
      resolve,
    }
    isOpen.value = true
  })
}

function showWarning(title: string, message: string, detail?: string): Promise<boolean> {
  return showModal({
    type: 'warning',
    title,
    message,
    detail,
    confirmText: 'Mengerti',
  })
}

function showError(title: string, message: string, detail?: string): Promise<boolean> {
  return showModal({
    type: 'error',
    title,
    message,
    detail,
    confirmText: 'Tutup',
    danger: true,
  })
}

function showConfirm(options: {
  title: string
  message: string
  detail?: string
  confirmText?: string
  cancelText?: string
  danger?: boolean
}): Promise<boolean> {
  return showModal({
    type: 'confirm',
    title: options.title,
    message: options.message,
    detail: options.detail,
    confirmText: options.confirmText || 'Lanjutkan',
    cancelText: options.cancelText || 'Batal',
    danger: options.danger ?? true,
  })
}

function handleConfirm() {
  if (modalConfig.value.resolve) {
    modalConfig.value.resolve(true)
  }
  isOpen.value = false
}

function handleCancel() {
  if (modalConfig.value.resolve) {
    modalConfig.value.resolve(false)
  }
  isOpen.value = false
}

export function useModal() {
  return {
    isOpen,
    modalConfig,
    showModal,
    showWarning,
    showError,
    showConfirm,
    handleConfirm,
    handleCancel,
  }
}
