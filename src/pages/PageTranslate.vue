<script setup lang="ts">
import { onMounted } from 'vue'
import { useTranslationStore } from '@/stores/translation'
import { useSettingsStore } from '@/stores/settings'
import { useToast } from '@/composables/useToast'
import DropZone from '@/components/DropZone.vue'
import ImageViewer from '@/components/ImageViewer.vue'
import LangSelector from '@/components/LangSelector.vue'

const store = useTranslationStore()
const settingsStore = useSettingsStore()
const { showToast } = useToast()

onMounted(async () => {
  await settingsStore.fetchSettings()
  // Apply defaults from settings
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

function onFilesSelected(files: FileList) {
  if (files.length > 0) {
    store.setFile(files[0])
  }
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
</script>

<template>
  <div class="page-translate">
    <div class="page-header">
      <h1 class="page-title">Terjemahkan</h1>
    </div>

    <!-- Controls -->
    <div class="controls-row">
      <LangSelector
        v-model="store.sourceLang"
        :options="settingsStore.settings.available_source_langs"
        label="Bahasa Sumber"
        id="source-lang"
      />
      <LangSelector
        v-model="store.targetLang"
        :options="settingsStore.settings.available_target_langs"
        label="Bahasa Target"
        id="target-lang"
      />
      <LangSelector
        v-model="store.engine"
        :options="settingsStore.settings.available_engines"
        label="Engine"
        id="engine"
      />
    </div>

    <!-- Main content area -->
    <div class="translate-content">
      <!-- When no file is selected -->
      <div v-if="!store.sourcePreview" class="upload-area">
        <DropZone @files="onFilesSelected" />
      </div>

      <!-- When file is selected -->
      <div v-else class="preview-area">
        <!-- Before/After Viewer or split view -->
        <div v-if="store.resultBase64" class="viewer-section">
          <ImageViewer
            :before-src="store.sourcePreview"
            :after-src="`data:image/png;base64,${store.resultBase64}`"
          />
        </div>

        <!-- Source only (before translation) -->
        <div v-else class="source-preview">
          <div class="preview-panel">
            <img :src="store.sourcePreview" class="preview-image" alt="Source" />
            <div v-if="store.loading" class="loading-overlay">
              <div class="spinner"></div>
              <p>Menerjemahkan...</p>
            </div>
          </div>
        </div>

        <!-- Error -->
        <div v-if="store.error" class="error-banner">
          <span class="error-icon">❌</span>
          <span>{{ store.error }}</span>
        </div>

        <!-- Action buttons -->
        <div class="action-row">
          <button
            class="btn btn-primary"
            :disabled="store.loading"
            @click="handleTranslate"
          >
            <span v-if="store.loading" class="btn-spinner"></span>
            {{ store.loading ? 'Menerjemahkan...' : 'Terjemahkan' }}
          </button>

          <button
            v-if="store.resultBase64"
            class="btn btn-secondary"
            @click="store.downloadResult()"
          >
            ⬇ Download
          </button>

          <button class="btn btn-ghost" @click="store.clearFile()">
            Hapus
          </button>

          <span v-if="store.duration > 0" class="duration-label">
            {{ store.duration }}s
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-translate {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-title {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
}

.controls-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.translate-content {
  flex: 1;
}

.upload-area {
  max-width: 600px;
}

.preview-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.viewer-section {
  max-width: 900px;
}

.source-preview {
  max-width: 900px;
}

.preview-panel {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-base);
  border: 1px solid var(--border);
}

.preview-image {
  display: block;
  width: 100%;
  max-height: 600px;
  object-fit: contain;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(15, 15, 17, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-secondary);
  font-size: 14px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: color-mix(in srgb, var(--error) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--error) 30%, transparent);
  border-radius: 8px;
  color: var(--error);
  font-size: 13px;
}

.action-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.duration-label {
  margin-left: auto;
  font-size: 13px;
  color: var(--text-secondary);
  font-variant-numeric: tabular-nums;
}

/* Button styles */
.btn {
  padding: 9px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: none;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--accent);
  color: #fff;
}
.btn-primary:hover:not(:disabled) {
  opacity: 0.85;
}

.btn-secondary {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border);
}
.btn-secondary:hover {
  border-color: var(--accent);
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
}
.btn-ghost:hover {
  color: var(--text-primary);
  background: var(--bg-elevated);
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
</style>
