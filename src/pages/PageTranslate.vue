<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTranslationStore } from '@/stores/translation'
import { useSettingsStore } from '@/stores/settings'
import { useToast } from '@/composables/useToast'
import DropZone from '@/components/DropZone.vue'
import ImageViewer from '@/components/ImageViewer.vue'
import LangSelector from '@/components/LangSelector.vue'

const store = useTranslationStore()
const settingsStore = useSettingsStore()
const { showToast } = useToast()

const viewMode = ref<'slider' | 'side' | 'result'>('slider')

onMounted(async () => {
  await settingsStore.fetchSettings()
  if (settingsStore.settings.default_source_lang) {
    store.sourceLang = settingsStore.settings.default_source_lang
  }
  if (settingsStore.settings.default_target_lang) {
    store.targetLang = settingsStore.settings.default_target_lang
  }
  if (settingsStore.settings.default_engine) {
    store.engine = settingsStore.settings.default_engine
  }
})

function onFilesSelected(files: FileList | File[]) {
  if (files.length > 0) {
    store.setFile(files[0])
    viewMode.value = 'slider'
  }
}

function swapLanguages() {
  if (store.sourceLang === 'auto') {
    showToast('Tidak bisa menukar bahasa saat sumber adalah Auto-detect', 'warning')
    return
  }
  const temp = store.sourceLang
  store.sourceLang = store.targetLang
  store.targetLang = temp
  showToast('Bahasa berhasil ditukar', 'info')
}

async function handleTranslate() {
  try {
    await store.translate()
    if (store.resultBase64) {
      showToast(`Terjemahan selesai dalam ${store.duration}s`, 'success')
    }
  } catch {
    showToast(store.error || 'Terjemahan gagal', 'error')
  }
}

async function copyResultToClipboard() {
  if (!store.resultBase64) return
  try {
    const res = await fetch(`data:image/png;base64,${store.resultBase64}`)
    const blob = await res.blob()
    await navigator.clipboard.write([
      new ClipboardItem({ 'image/png': blob }),
    ])
    showToast('Gambar berhasil disalin ke clipboard!', 'success')
  } catch {
    showToast('Gagal menyalin gambar ke clipboard', 'error')
  }
}
</script>

<template>
  <div class="page-translate">
    <!-- Header -->
    <header class="page-header">
      <div class="header-titles">
        <h1 class="page-title">Terjemahkan Manga</h1>
        <p class="page-subtitle">
          Deteksi teks otomatis, OCR, penghapusan balon (inpainting), dan terjemahan AI instan.
        </p>
      </div>
    </header>

    <!-- Sleek Glassmorphic Control Bar -->
    <div class="control-bar glass-card">
      <div class="lang-controls">
        <LangSelector
          v-model="store.sourceLang"
          :options="settingsStore.settings.available_source_langs"
          label="Bahasa Sumber"
          id="source-lang"
        />

        <button
          type="button"
          class="btn-swap"
          title="Tukar Bahasa"
          @click="swapLanguages"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="17 1 21 5 17 9" />
            <path d="M3 11V9a4 4 0 014-4h14" />
            <polyline points="7 23 3 19 7 15" />
            <path d="M21 13v2a4 4 0 01-4 4H3" />
          </svg>
        </button>

        <LangSelector
          v-model="store.targetLang"
          :options="settingsStore.settings.available_target_langs"
          label="Bahasa Target"
          id="target-lang"
        />
      </div>

      <div class="divider-v"></div>

      <div class="engine-control">
        <LangSelector
          v-model="store.engine"
          :options="settingsStore.settings.available_engines"
          label="Mesin AI"
          id="engine-select"
        />
      </div>
    </div>

    <!-- Main Translation Workspace -->
    <div class="workspace-area">
      <!-- Empty State: DropZone -->
      <div v-if="!store.sourcePreview" class="empty-drop-wrapper">
        <DropZone @files="onFilesSelected" />
      </div>

      <!-- Loaded Image State -->
      <div v-else class="preview-workspace">
        <!-- Top Toolbar for Loaded Image -->
        <div class="preview-toolbar glass-panel">
          <div class="file-meta">
            <span class="file-name-tag">{{ store.sourceFile?.name }}</span>
            <span v-if="store.sourceFile" class="file-size-tag">
              {{ (store.sourceFile.size / 1024 / 1024).toFixed(2) }} MB
            </span>
          </div>

          <!-- View mode toggle if result exists -->
          <div v-if="store.resultBase64" class="view-mode-tabs">
            <button
              :class="['tab-btn', { active: viewMode === 'slider' }]"
              @click="viewMode = 'slider'"
            >
              Slider Komparasi
            </button>
            <button
              :class="['tab-btn', { active: viewMode === 'side' }]"
              @click="viewMode = 'side'"
            >
              Side by Side
            </button>
            <button
              :class="['tab-btn', { active: viewMode === 'result' }]"
              @click="viewMode = 'result'"
            >
              Hasil Saja
            </button>
          </div>

          <div class="toolbar-actions">
            <button class="btn btn-ghost btn-sm" @click="store.clearFile()">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6" />
                <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
              </svg>
              Ganti Gambar
            </button>
          </div>
        </div>

        <!-- Viewer Section -->
        <div class="viewer-wrapper">
          <!-- Slider Mode -->
          <div v-if="store.resultBase64 && viewMode === 'slider'" class="viewer-container">
            <ImageViewer
              :before-src="store.sourcePreview"
              :after-src="`data:image/png;base64,${store.resultBase64}`"
            />
          </div>

          <!-- Side-by-Side Mode -->
          <div v-else-if="store.resultBase64 && viewMode === 'side'" class="side-by-side-grid">
            <div class="side-panel glass-panel">
              <div class="panel-badge">Asli</div>
              <img :src="store.sourcePreview" class="side-img" alt="Asli" />
            </div>
            <div class="side-panel glass-panel">
              <div class="panel-badge badge-success">Hasil Terjemahan</div>
              <img :src="`data:image/png;base64,${store.resultBase64}`" class="side-img" alt="Hasil" />
            </div>
          </div>

          <!-- Result Only Mode -->
          <div v-else-if="store.resultBase64 && viewMode === 'result'" class="single-panel glass-panel">
            <img :src="`data:image/png;base64,${store.resultBase64}`" class="single-img" alt="Hasil Terjemahan" />
          </div>

          <!-- Untranslated Source Image -->
          <div v-else class="untranslated-container glass-panel">
            <img :src="store.sourcePreview" class="untranslated-img" alt="Source Manga" />

            <!-- Translation Overlay Spinner -->
            <div v-if="store.loading" class="loading-overlay">
              <div class="glow-spinner"></div>
              <div class="loading-text-group">
                <p class="loading-title">Menerjemahkan Teks...</p>
                <p class="loading-desc">Mendeteksi balon percakapan, inpainting, dan terjemahan AI</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Error Banner -->
        <div v-if="store.error" class="error-banner">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="error-icon">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <div class="error-content">
            <span class="error-title">Gagal Menerjemahkan</span>
            <span class="error-detail">{{ store.error }}</span>
          </div>
        </div>

        <!-- Bottom Action Bar -->
        <div class="action-footer glass-card">
          <div class="primary-action-group">
            <button
              class="btn btn-primary btn-lg"
              :disabled="store.loading"
              @click="handleTranslate"
            >
              <svg v-if="!store.loading" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
              </svg>
              <span v-else class="btn-spinner"></span>
              {{ store.loading ? 'Memproses Terjemahan...' : (store.resultBase64 ? 'Terjemahkan Ulang' : 'Mulai Terjemahkan') }}
            </button>

            <!-- Result Action Buttons -->
            <template v-if="store.resultBase64">
              <button class="btn btn-secondary" @click="store.downloadResult()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                  <polyline points="7 10 12 15 17 10" />
                  <line x1="12" y1="15" x2="12" y2="3" />
                </svg>
                Download Gambar
              </button>

              <button class="btn btn-secondary" @click="copyResultToClipboard">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                  <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
                </svg>
                Salin ke Clipboard
              </button>
            </template>
          </div>

          <!-- Metadata Tag -->
          <div v-if="store.duration > 0" class="meta-duration">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            <span>Waktu proses: <strong>{{ store.duration }} detik</strong></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-translate {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
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

/* Control Bar */
.control-bar {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.lang-controls {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  flex: 1;
  min-width: 320px;
}

.btn-swap {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  margin-bottom: 2px;
  flex-shrink: 0;
}

.btn-swap:hover {
  background: var(--bg-surface-hover);
  color: #818CF8;
  border-color: var(--border-hover);
  transform: rotate(180deg);
}

.divider-v {
  width: 1px;
  height: 42px;
  background: var(--border);
}

.engine-control {
  min-width: 200px;
}

/* Workspace */
.workspace-area {
  width: 100%;
}

.empty-drop-wrapper {
  max-width: 860px;
  margin: 20px auto 0 auto;
}

.preview-workspace {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.preview-toolbar {
  padding: 10px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.file-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-name-tag {
  font-family: var(--font-heading);
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-primary);
}

.file-size-tag {
  font-size: 11.5px;
  padding: 2px 7px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 5px;
  color: var(--text-muted);
}

.view-mode-tabs {
  display: flex;
  background: rgba(13, 14, 21, 0.8);
  padding: 3px;
  border-radius: 8px;
  border: 1px solid var(--border);
}

.tab-btn {
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn.active {
  background: var(--accent);
  color: #FFFFFF;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
}

.viewer-wrapper {
  width: 100%;
  display: flex;
  justify-content: center;
}

.viewer-container {
  width: 100%;
}

/* Side by Side Mode */
.side-by-side-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  width: 100%;
}

.side-panel {
  position: relative;
  overflow: hidden;
  border-radius: 14px;
  background: #08090E;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.side-img, .single-img {
  width: 100%;
  max-height: 75vh;
  object-fit: contain;
}

.single-panel {
  position: relative;
  overflow: hidden;
  border-radius: 14px;
  background: #08090E;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 450px;
}

.panel-badge {
  position: absolute;
  top: 14px;
  left: 14px;
  padding: 4px 10px;
  border-radius: 6px;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  color: #FFFFFF;
  font-size: 12px;
  font-weight: 600;
  z-index: 5;
}

.panel-badge.badge-success {
  background: rgba(16, 185, 129, 0.2);
  color: #34D399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

/* Untranslated Preview */
.untranslated-container {
  position: relative;
  width: 100%;
  max-height: 75vh;
  min-height: 400px;
  background: #08090E;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.untranslated-img {
  width: 100%;
  max-height: 75vh;
  object-fit: contain;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(9, 10, 15, 0.85);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
  z-index: 10;
}

.glow-spinner {
  width: 48px;
  height: 48px;
  border: 3.5px solid rgba(99, 102, 241, 0.2);
  border-top-color: #818CF8;
  border-radius: 50%;
  animation: spin 0.8s cubic-bezier(0.5, 0.1, 0.5, 0.9) infinite;
  box-shadow: 0 0 24px rgba(99, 102, 241, 0.4);
}

.loading-text-group {
  text-align: center;
}

.loading-title {
  font-family: var(--font-heading);
  font-size: 16px;
  font-weight: 600;
  color: #FFFFFF;
}

.loading-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 2px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  background: rgba(244, 63, 94, 0.1);
  border: 1px solid rgba(244, 63, 94, 0.25);
  border-radius: 12px;
  color: #FDA4AF;
}

.error-icon {
  color: #F43F5E;
  flex-shrink: 0;
}

.error-content {
  display: flex;
  flex-direction: column;
}

.error-title {
  font-weight: 600;
  font-size: 13.5px;
  color: #FECDD3;
}

.error-detail {
  font-size: 12.5px;
}

/* Action Footer */
.action-footer {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}

.primary-action-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-duration {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.04);
  padding: 6px 12px;
  border-radius: 8px;
}

.meta-duration strong {
  color: #A5B4FC;
}

.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2.5px solid rgba(255, 255, 255, 0.3);
  border-top-color: #FFFFFF;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@media (max-width: 900px) {
  .side-by-side-grid {
    grid-template-columns: 1fr;
  }
}
</style>
