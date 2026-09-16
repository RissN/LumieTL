<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useToast } from '@/composables/useToast'
import LangSelector from '@/components/LangSelector.vue'
import ModelStatus from '@/components/ModelStatus.vue'

const store = useSettingsStore()
const { showToast } = useToast()

// Local form state for API keys
const deeplKey = ref('')
const openaiKey = ref('')
const savingKey = ref<string | null>(null)

onMounted(async () => {
  await store.fetchSettings()
  await store.fetchApiKeyStatus()
})

async function saveSettings() {
  try {
    await store.updateSettings({
      default_source_lang: store.settings.default_source_lang,
      default_target_lang: store.settings.default_target_lang,
      default_engine: store.settings.default_engine,
      gpu_enabled: store.settings.gpu_enabled,
    })
    showToast('Pengaturan disimpan', 'success')
  } catch {
    showToast('Gagal menyimpan pengaturan', 'error')
  }
}

async function resetSettings() {
  if (!confirm('Reset semua pengaturan ke default?')) return
  try {
    await store.resetSettings()
    showToast('Pengaturan direset', 'success')
  } catch {
    showToast('Gagal mereset pengaturan', 'error')
  }
}

async function saveApiKey(provider: string) {
  const key = provider === 'deepl' ? deeplKey.value : openaiKey.value
  if (!key.trim()) {
    showToast('API key tidak boleh kosong', 'warning')
    return
  }
  savingKey.value = provider
  try {
    await store.saveApiKey(provider, key.trim())
    if (provider === 'deepl') deeplKey.value = ''
    else openaiKey.value = ''
    showToast(`API key ${provider} disimpan`, 'success')
  } catch {
    showToast(`Gagal menyimpan API key ${provider}`, 'error')
  } finally {
    savingKey.value = null
  }
}

async function removeApiKey(provider: string) {
  try {
    await store.deleteApiKey(provider)
    showToast(`API key ${provider} dihapus`, 'success')
  } catch {
    showToast(`Gagal menghapus API key ${provider}`, 'error')
  }
}
</script>

<template>
  <div class="page-settings">
    <div class="page-header">
      <h1 class="page-title">Pengaturan</h1>
    </div>

    <!-- General Settings -->
    <section class="settings-section">
      <h2 class="section-title">Umum</h2>

      <div class="settings-grid">
        <LangSelector
          v-model="store.settings.default_source_lang"
          :options="store.settings.available_source_langs"
          label="Bahasa Sumber Default"
          id="settings-source"
        />

        <LangSelector
          v-model="store.settings.default_target_lang"
          :options="store.settings.available_target_langs"
          label="Bahasa Target Default"
          id="settings-target"
        />

        <LangSelector
          v-model="store.settings.default_engine"
          :options="store.settings.available_engines"
          label="Engine Default"
          id="settings-engine"
        />
      </div>

      <div class="toggle-row">
        <label class="toggle-label" for="gpu-toggle">
          <span class="toggle-text">GPU (CUDA)</span>
          <span class="toggle-hint">Aktifkan jika GPU NVIDIA tersedia</span>
        </label>
        <label class="switch">
          <input
            id="gpu-toggle"
            type="checkbox"
            v-model="store.settings.gpu_enabled"
          />
          <span class="switch-slider"></span>
        </label>
      </div>

      <div class="settings-actions">
        <button class="btn btn-primary" @click="saveSettings">
          Simpan
        </button>
        <button class="btn btn-ghost" @click="resetSettings">
          Reset ke Default
        </button>
      </div>
    </section>

    <!-- API Keys -->
    <section class="settings-section">
      <h2 class="section-title">API Keys</h2>
      <p class="section-desc">
        API key disimpan terenkripsi di server. Nilai key tidak pernah ditampilkan kembali.
      </p>

      <!-- DeepL -->
      <div class="key-row">
        <div class="key-info">
          <span class="key-name">DeepL</span>
          <span :class="['key-status', store.apiKeys.deepl_set ? 'set' : 'unset']">
            {{ store.apiKeys.deepl_set ? '✓ Tersimpan' : 'Belum diatur' }}
          </span>
        </div>
        <div class="key-actions">
          <input
            v-model="deeplKey"
            type="password"
            placeholder="Masukkan API key DeepL"
            class="key-input"
          />
          <button
            class="btn btn-primary btn-sm"
            :disabled="savingKey === 'deepl'"
            @click="saveApiKey('deepl')"
          >
            Simpan
          </button>
          <button
            v-if="store.apiKeys.deepl_set"
            class="btn btn-danger-ghost btn-sm"
            @click="removeApiKey('deepl')"
          >
            Hapus
          </button>
        </div>
      </div>

      <!-- OpenAI -->
      <div class="key-row">
        <div class="key-info">
          <span class="key-name">OpenAI</span>
          <span :class="['key-status', store.apiKeys.openai_set ? 'set' : 'unset']">
            {{ store.apiKeys.openai_set ? '✓ Tersimpan' : 'Belum diatur' }}
          </span>
        </div>
        <div class="key-actions">
          <input
            v-model="openaiKey"
            type="password"
            placeholder="Masukkan API key OpenAI"
            class="key-input"
          />
          <button
            class="btn btn-primary btn-sm"
            :disabled="savingKey === 'openai'"
            @click="saveApiKey('openai')"
          >
            Simpan
          </button>
          <button
            v-if="store.apiKeys.openai_set"
            class="btn btn-danger-ghost btn-sm"
            @click="removeApiKey('openai')"
          >
            Hapus
          </button>
        </div>
      </div>
    </section>

    <!-- Model Status -->
    <section class="settings-section">
      <h2 class="section-title">Model</h2>
      <ModelStatus />
    </section>
  </div>
</template>

<style scoped>
.page-settings {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 720px;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: -8px;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}

.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-top: 1px solid var(--border);
}

.toggle-label {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.toggle-text {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.toggle-hint {
  font-size: 12px;
  color: var(--text-secondary);
}

/* Toggle switch */
.switch {
  position: relative;
  display: inline-block;
  width: 42px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--border);
  transition: 0.2s;
  border-radius: 12px;
}

.switch-slider:before {
  position: absolute;
  content: '';
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background: white;
  transition: 0.2s;
  border-radius: 50%;
}

.switch input:checked + .switch-slider {
  background: var(--accent);
}

.switch input:checked + .switch-slider:before {
  transform: translateX(18px);
}

.settings-actions {
  display: flex;
  gap: 10px;
  padding-top: 8px;
  border-top: 1px solid var(--border);
}

/* API Keys */
.key-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: var(--bg-elevated);
  border-radius: 8px;
}

.key-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.key-name {
  font-weight: 500;
  font-size: 14px;
  color: var(--text-primary);
}

.key-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 5px;
}

.key-status.set {
  background: color-mix(in srgb, var(--success) 15%, transparent);
  color: var(--success);
}

.key-status.unset {
  background: color-mix(in srgb, var(--text-secondary) 10%, transparent);
  color: var(--text-secondary);
}

.key-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.key-input {
  flex: 1;
  background: var(--bg-base);
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 7px 12px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
}

.key-input:focus {
  border-color: var(--accent);
}

.key-input::placeholder {
  color: var(--text-secondary);
  opacity: 0.6;
}

/* Buttons */
.btn {
  padding: 9px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-primary { background: var(--accent); color: #fff; }
.btn-primary:hover:not(:disabled) { opacity: 0.85; }

.btn-ghost { background: transparent; color: var(--text-secondary); }
.btn-ghost:hover { color: var(--text-primary); background: var(--bg-elevated); }

.btn-danger-ghost {
  background: transparent;
  color: var(--error);
}
.btn-danger-ghost:hover {
  background: color-mix(in srgb, var(--error) 10%, transparent);
}

.btn-sm { padding: 6px 12px; font-size: 12px; }
</style>
