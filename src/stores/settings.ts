/**
 * Settings store — manages app settings and API key status.
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/composables/useApi'
import type { Settings, ApiKeyStatus } from '@/types'

const DEFAULT_SETTINGS: Settings = {
  default_source_lang: 'auto',
  default_target_lang: 'ID',
  default_engine: 'google',
  output_dir: '',
  gpu_enabled: false,
  available_source_langs: {},
  available_target_langs: {},
  available_engines: {},
}

export const useSettingsStore = defineStore('settings', () => {
  // State
  const settings = ref<Settings>({ ...DEFAULT_SETTINGS })
  const apiKeys = ref<ApiKeyStatus>({ deepl_set: false, openai_set: false })
  const loading = ref(false)
  const error = ref('')

  // Actions
  async function fetchSettings() {
    loading.value = true
    try {
      const res = await api.get<Settings>('/settings')
      settings.value = res.data
    } catch (e: any) {
      error.value = e.message
    } finally {
      loading.value = false
    }
  }

  async function updateSettings(updates: Partial<Settings>) {
    try {
      await api.put('/settings', updates)
      await fetchSettings()
    } catch (e: any) {
      error.value = e.message
      throw e
    }
  }

  async function resetSettings() {
    try {
      await api.post('/settings/reset')
      await fetchSettings()
    } catch (e: any) {
      error.value = e.message
      throw e
    }
  }

  async function fetchApiKeyStatus() {
    try {
      const res = await api.get<ApiKeyStatus>('/settings/api-keys')
      apiKeys.value = res.data
    } catch (e: any) {
      error.value = e.message
    }
  }

  async function saveApiKey(provider: string, key: string) {
    try {
      await api.put('/settings/api-keys', { provider, key })
      await fetchApiKeyStatus()
    } catch (e: any) {
      error.value = e.message
      throw e
    }
  }

  async function deleteApiKey(provider: string) {
    try {
      await api.delete(`/settings/api-keys/${provider}`)
      await fetchApiKeyStatus()
    } catch (e: any) {
      error.value = e.message
      throw e
    }
  }

  return {
    settings,
    apiKeys,
    loading,
    error,
    fetchSettings,
    updateSettings,
    resetSettings,
    fetchApiKeyStatus,
    saveApiKey,
    deleteApiKey,
  }
})
