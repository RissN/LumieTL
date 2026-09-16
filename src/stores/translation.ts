/**
 * Translation store — manages single-image translation state.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/composables/useApi'
import type { TranslationResult } from '@/types'

export const useTranslationStore = defineStore('translation', () => {
  // State
  const sourceFile = ref<File | null>(null)
  const sourcePreview = ref<string>('')
  const sourceLang = ref('auto')
  const targetLang = ref('ID')
  const engine = ref('google')
  const resultBase64 = ref<string>('')
  const duration = ref<number>(0)
  const loading = ref(false)
  const error = ref<string>('')

  // Actions
  function setFile(file: File) {
    sourceFile.value = file
    sourcePreview.value = URL.createObjectURL(file)
    resultBase64.value = ''
    duration.value = 0
    error.value = ''
  }

  function clearFile() {
    if (sourcePreview.value) {
      URL.revokeObjectURL(sourcePreview.value)
    }
    sourceFile.value = null
    sourcePreview.value = ''
    resultBase64.value = ''
    duration.value = 0
    error.value = ''
  }

  async function translate() {
    if (!sourceFile.value) return

    loading.value = true
    error.value = ''
    resultBase64.value = ''

    try {
      const formData = new FormData()
      formData.append('file', sourceFile.value)
      formData.append('source_lang', sourceLang.value)
      formData.append('target_lang', targetLang.value)
      formData.append('engine', engine.value)

      const res = await api.post<TranslationResult>('/translate/single', formData)
      resultBase64.value = res.data.result_image_base64
      duration.value = res.data.duration
    } catch (e: any) {
      error.value = e.message || 'Translation failed'
    } finally {
      loading.value = false
    }
  }

  function downloadResult() {
    if (!resultBase64.value) return

    const link = document.createElement('a')
    link.href = `data:image/png;base64,${resultBase64.value}`
    link.download = `translated_${sourceFile.value?.name || 'image'}.png`
    link.click()
  }

  return {
    sourceFile,
    sourcePreview,
    sourceLang,
    targetLang,
    engine,
    resultBase64,
    duration,
    loading,
    error,
    setFile,
    clearFile,
    translate,
    downloadResult,
  }
})
