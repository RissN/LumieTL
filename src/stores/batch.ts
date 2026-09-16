/**
 * Batch processing store — manages batch task state and polling.
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/composables/useApi'
import type { BatchTask } from '@/types'

export const useBatchStore = defineStore('batch', () => {
  // State
  const taskId = ref<string>('')
  const task = ref<BatchTask | null>(null)
  const sourceLang = ref('auto')
  const targetLang = ref('ID')
  const engine = ref('google')
  const loading = ref(false)
  const error = ref('')
  const selectedFiles = ref<File[]>([])

  // Polling
  let pollInterval: ReturnType<typeof setInterval> | null = null

  // Computed
  const progress = computed(() => {
    if (!task.value || task.value.total === 0) return 0
    return Math.round((task.value.done / task.value.total) * 100)
  })

  // Actions
  function addFiles(files: FileList | File[]) {
    const arr = Array.from(files)
    selectedFiles.value.push(...arr)
  }

  function removeFile(index: number) {
    selectedFiles.value.splice(index, 1)
  }

  function clearFiles() {
    selectedFiles.value = []
  }

  async function startBatch() {
    if (selectedFiles.value.length === 0) return

    loading.value = true
    error.value = ''
    task.value = null

    try {
      const formData = new FormData()
      for (const file of selectedFiles.value) {
        formData.append('files', file)
      }
      formData.append('source_lang', sourceLang.value)
      formData.append('target_lang', targetLang.value)
      formData.append('engine', engine.value)

      const res = await api.post<{ task_id: string }>('/translate/batch/start', formData)
      taskId.value = res.data.task_id
      startPolling()
    } catch (e: any) {
      error.value = e.message || 'Failed to start batch'
    } finally {
      loading.value = false
    }
  }

  function startPolling() {
    stopPolling()
    // Immediately fetch once
    fetchStatus()
    pollInterval = setInterval(fetchStatus, 1500)
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
  }

  async function fetchStatus() {
    if (!taskId.value) return
    try {
      const res = await api.get<BatchTask>(`/translate/batch/${taskId.value}`)
      task.value = res.data
      if (res.data.is_complete) {
        stopPolling()
      }
    } catch {
      // Silently ignore polling errors
    }
  }

  async function cancelBatch() {
    if (!taskId.value) return
    try {
      await api.delete(`/translate/batch/${taskId.value}`)
      stopPolling()
      await fetchStatus()
    } catch (e: any) {
      error.value = e.message || 'Failed to cancel batch'
    }
  }

  function downloadAll() {
    if (!taskId.value) return
    const url = `/api/translate/batch/${taskId.value}/download`
    const link = document.createElement('a')
    link.href = url
    link.download = `LumieTL_batch_${taskId.value}.zip`
    link.click()
  }

  function downloadLog() {
    if (!taskId.value) return
    const url = `/api/translate/batch/${taskId.value}/log`
    const link = document.createElement('a')
    link.href = url
    link.download = `LumieTL_batch_${taskId.value}.txt`
    link.click()
  }

  function reset() {
    stopPolling()
    taskId.value = ''
    task.value = null
    selectedFiles.value = []
    error.value = ''
    loading.value = false
  }

  return {
    taskId,
    task,
    sourceLang,
    targetLang,
    engine,
    loading,
    error,
    selectedFiles,
    progress,
    addFiles,
    removeFile,
    clearFiles,
    startBatch,
    cancelBatch,
    downloadAll,
    downloadLog,
    reset,
  }
})
