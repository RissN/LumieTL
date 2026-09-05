import { defineStore } from 'pinia'
import axios from 'axios'
import type { AppSettings, ApiKeysStatus } from '@/types'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    settings: {
      default_source_lang: 'auto',
      default_target_lang: 'ID',
      default_engine: 'google',
      font_size: 14,
      output_dir: '',
      gpu_enabled: false
    } as AppSettings,
    apiKeys: {
      deepl_set: false,
      openai_set: false
    } as ApiKeysStatus,
    loading: false
  }),
  actions: {
    async fetchSettings() {
      try {
        const res = await axios.get('/api/settings')
        this.settings = res.data
        const keysRes = await axios.get('/api/settings/api-keys')
        this.apiKeys = keysRes.data
      } catch (e) {
        console.error('Failed to load settings', e)
      }
    },
    async saveSettings(newSettings: AppSettings) {
      const res = await axios.put('/api/settings', newSettings)
      this.settings = res.data.settings
    },
    async saveApiKey(provider: 'deepl' | 'openai', key: string) {
      await axios.put('/api/settings/api-keys', { provider, key })
      await this.fetchSettings()
    }
  }
})
