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
const showDeepl = ref(false)
const showOpenai = ref(false)
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
    showToast('Pengaturan berhasil disimpan', 'success')
  } catch {
    showToast('Gagal menyimpan pengaturan', 'error')
  }
}

async function resetSettings() {
  if (!confirm('Apakah Anda yakin ingin mereset semua pengaturan ke nilai bawaan?')) return
  try {
    await store.resetSettings()
    showToast('Pengaturan telah direset ke bawaan', 'success')
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
    showToast(`API key ${provider.toUpperCase()} berhasil disimpan & dienkripsi`, 'success')
  } catch {
    showToast(`Gagal menyimpan API key ${provider}`, 'error')
  } finally {
    savingKey.value = null
  }
}

async function removeApiKey(provider: string) {
  if (!confirm(`Hapus API key ${provider.toUpperCase()}?`)) return
  try {
    await store.deleteApiKey(provider)
    showToast(`API key ${provider.toUpperCase()} dihapus`, 'success')
  } catch {
    showToast(`Gagal menghapus API key ${provider}`, 'error')
  }
}
</script>

<template>
  <div class="page-settings">
    <!-- Header -->
    <header class="page-header">
      <div class="header-titles">
        <h1 class="page-title">Pengaturan Sistem</h1>
        <p class="page-subtitle">
          Sesuaikan konfigurasi penerjemahan bawaan, akselerasi GPU, dan kunci API eksternal.
        </p>
      </div>

      <div class="header-actions">
        <button class="btn btn-ghost btn-sm" @click="resetSettings">
          Reset Default
        </button>
        <button class="btn btn-primary" @click="saveSettings">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
            <polyline points="17 21 17 13 7 13 7 21"/>
            <polyline points="7 3 7 8 15 8"/>
          </svg>
          Simpan Pengaturan
        </button>
      </div>
    </header>

    <div class="settings-content-grid">
      <!-- Section 1: General Preferences -->
      <section class="settings-card glass-card">
        <div class="card-title-row">
          <div class="card-icon-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
          </div>
          <div>
            <h2 class="card-title">Preferensi Penerjemahan</h2>
            <p class="card-subtitle">Pilihan bawaan yang akan otomatis terpilih saat membuka aplikasi.</p>
          </div>
        </div>

        <div class="selectors-grid">
          <LangSelector
            v-model="store.settings.default_source_lang"
            :options="store.settings.available_source_langs"
            label="Bahasa Sumber Bawaan"
            id="settings-source"
          />

          <LangSelector
            v-model="store.settings.default_target_lang"
            :options="store.settings.available_target_langs"
            label="Bahasa Target Bawaan"
            id="settings-target"
          />

          <LangSelector
            v-model="store.settings.default_engine"
            :options="store.settings.available_engines"
            label="Mesin AI Bawaan"
            id="settings-engine"
          />
        </div>

        <!-- GPU Acceleration Row -->
        <div class="toggle-card glass-panel">
          <div class="toggle-info">
            <div class="toggle-header-row">
              <span class="toggle-title">Akselerasi GPU (NVIDIA CUDA)</span>
              <span class="cuda-status-badge" :class="{ active: store.settings.gpu_enabled }">
                {{ store.settings.gpu_enabled ? 'Aktif' : 'Non-aktif' }}
              </span>
            </div>
            <p class="toggle-desc">
              Aktifkan jika perangkat Anda memiliki kartu grafis NVIDIA dan driver CUDA terpasang. Memberikan peningkatan kecepatan deteksi & inpainting hingga 5x lipat.
            </p>
          </div>

          <label class="switch" for="gpu-toggle">
            <input
              id="gpu-toggle"
              type="checkbox"
              v-model="store.settings.gpu_enabled"
            />
            <span class="switch-slider"></span>
          </label>
        </div>
      </section>

      <!-- Section 2: API Keys -->
      <section class="settings-card glass-card">
        <div class="card-title-row">
          <div class="card-icon-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>
            </svg>
          </div>
          <div>
            <h2 class="card-title">Kunci API Terenkripsi</h2>
            <p class="card-subtitle">
              Disimpan aman menggunakan enkripsi Fernet pada disk lokal Anda. Kunci tidak pernah dibagikan ke pihak ketiga.
            </p>
          </div>
        </div>

        <div class="api-keys-list">
          <!-- DeepL Card -->
          <div class="api-key-item glass-panel">
            <div class="key-header">
              <div class="key-brand">
                <span class="key-name">DeepL API</span>
                <span class="key-tag">Translate Engine</span>
              </div>
              <span :class="['key-status-badge', store.apiKeys.deepl_set ? 'is-set' : 'is-unset']">
                <span class="status-dot"></span>
                {{ store.apiKeys.deepl_set ? 'Kunci Tersimpan' : 'Belum Dikonfigurasi' }}
              </span>
            </div>

            <div class="key-input-row">
              <div class="input-with-icon">
                <input
                  v-model="deeplKey"
                  :type="showDeepl ? 'text' : 'password'"
                  placeholder="Masukkan Auth Key DeepL (contoh: xxxxxxxx-xxxx-...:fx)"
                  class="styled-input"
                />
                <button
                  type="button"
                  class="btn-eye"
                  @click="showDeepl = !showDeepl"
                  title="Lihat / Sembunyikan"
                >
                  <svg v-if="!showDeepl" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                    <line x1="1" y1="1" x2="23" y2="23" />
                  </svg>
                </button>
              </div>

              <div class="key-actions-group">
                <button
                  class="btn btn-primary btn-sm"
                  :disabled="savingKey === 'deepl'"
                  @click="saveApiKey('deepl')"
                >
                  Simpan Kunci
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
          </div>

          <!-- OpenAI Card -->
          <div class="api-key-item glass-panel">
            <div class="key-header">
              <div class="key-brand">
                <span class="key-name">OpenAI API (GPT-4o)</span>
                <span class="key-tag">Translate Engine</span>
              </div>
              <span :class="['key-status-badge', store.apiKeys.openai_set ? 'is-set' : 'is-unset']">
                <span class="status-dot"></span>
                {{ store.apiKeys.openai_set ? 'Kunci Tersimpan' : 'Belum Dikonfigurasi' }}
              </span>
            </div>

            <div class="key-input-row">
              <div class="input-with-icon">
                <input
                  v-model="openaiKey"
                  :type="showOpenai ? 'text' : 'password'"
                  placeholder="Masukkan OpenAI Secret Key (sk-...)"
                  class="styled-input"
                />
                <button
                  type="button"
                  class="btn-eye"
                  @click="showOpenai = !showOpenai"
                  title="Lihat / Sembunyikan"
                >
                  <svg v-if="!showOpenai" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                  <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                    <line x1="1" y1="1" x2="23" y2="23" />
                  </svg>
                </button>
              </div>

              <div class="key-actions-group">
                <button
                  class="btn btn-primary btn-sm"
                  :disabled="savingKey === 'openai'"
                  @click="saveApiKey('openai')"
                >
                  Simpan Kunci
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
          </div>
        </div>
      </section>

      <!-- Section 3: Offline AI Models -->
      <section class="settings-card glass-card">
        <div class="card-title-row">
          <div class="card-icon-box">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
              <line x1="12" y1="22.08" x2="12" y2="12"/>
            </svg>
          </div>
          <div>
            <h2 class="card-title">Model Deep Learning Offline</h2>
            <p class="card-subtitle">
              Model deteksi balon, OCR teks manga, dan inpainting latar gambar.
            </p>
          </div>
        </div>

        <ModelStatus />
      </section>
    </div>
  </div>
</template>

<style scoped>
.page-settings {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.page-title {
  font-size: 26px;
  font-weight: 700;
  color: #FFFFFF;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 13.5px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.settings-content-grid {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.settings-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-title-row {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.card-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.15);
  color: #818CF8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-title {
  font-family: var(--font-heading);
  font-size: 17px;
  font-weight: 700;
  color: #FFFFFF;
}

.card-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.selectors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
}

/* GPU Toggle Card */
.toggle-card {
  padding: 16px 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.toggle-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.toggle-header-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toggle-title {
  font-family: var(--font-heading);
  font-size: 14.5px;
  font-weight: 600;
  color: #FFFFFF;
}

.cuda-status-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-secondary);
}

.cuda-status-badge.active {
  background: rgba(16, 185, 129, 0.15);
  color: #34D399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.toggle-desc {
  font-size: 12.5px;
  color: var(--text-secondary);
  max-width: 650px;
}

/* Switch */
.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 26px;
  flex-shrink: 0;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background: rgba(255, 255, 255, 0.15);
  transition: 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  border-radius: 14px;
}

.switch-slider:before {
  position: absolute;
  content: '';
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background: white;
  transition: 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
}

.switch input:checked + .switch-slider {
  background: var(--accent);
}

.switch input:checked + .switch-slider:before {
  transform: translateX(22px);
}

/* API Keys */
.api-keys-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.api-key-item {
  padding: 16px 20px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.key-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.key-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.key-name {
  font-family: var(--font-heading);
  font-size: 14.5px;
  font-weight: 600;
  color: #FFFFFF;
}

.key-tag {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-muted);
}

.key-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 9px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.key-status-badge.is-set {
  background: rgba(16, 185, 129, 0.15);
  color: #34D399;
}
.key-status-badge.is-set .status-dot {
  background: #10B981;
}

.key-status-badge.is-unset {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-muted);
}
.key-status-badge.is-unset .status-dot {
  background: var(--text-muted);
}

.key-input-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.input-with-icon {
  position: relative;
  flex: 1;
  min-width: 280px;
}

.styled-input {
  width: 100%;
  background: rgba(13, 14, 21, 0.8);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 42px 10px 14px;
  color: var(--text-primary);
  font-family: monospace;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s ease;
}

.styled-input:focus {
  border-color: var(--accent);
}

.styled-input::placeholder {
  color: var(--text-muted);
}

.btn-eye {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
}

.btn-eye:hover {
  color: var(--text-primary);
}

.key-actions-group {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
