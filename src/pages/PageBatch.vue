<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useBatchStore } from '@/stores/batch'
import { useSettingsStore } from '@/stores/settings'
import { useToast } from '@/composables/useToast'
import { useModal } from '@/composables/useModal'
import DropZone from '@/components/DropZone.vue'
import BatchTable from '@/components/BatchTable.vue'
import LangSelector from '@/components/LangSelector.vue'

const batch = useBatchStore()
const settingsStore = useSettingsStore()
const { showToast } = useToast()
const { showWarning, showError, showConfirm } = useModal()

const folderInput = ref<HTMLInputElement | null>(null)

onMounted(async () => {
  await settingsStore.fetchSettings()
  if (settingsStore.settings.default_source_lang) {
    batch.sourceLang = settingsStore.settings.default_source_lang
  }
  if (settingsStore.settings.default_target_lang) {
    batch.targetLang = settingsStore.settings.default_target_lang
  }
  if (settingsStore.settings.default_engine) {
    batch.engine = settingsStore.settings.default_engine
  }
})

function onFilesSelected(files: FileList | File[]) {
  batch.addFiles(files)
  showToast(`${files.length} file ditambahkan ke antrean`, 'info')
}

function selectFolder() {
  folderInput.value?.click()
}

function onFolderChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.length) {
    const imageFiles = Array.from(input.files).filter((f) =>
      /\.(jpe?g|png|webp|avif)$/i.test(f.name)
    )
    if (imageFiles.length > 0) {
      batch.addFiles(imageFiles)
      showToast(`${imageFiles.length} file manga dari folder dimasukkan ke antrean`, 'success')
    } else {
      showWarning(
        'Tidak Ada Gambar Valid',
        'Folder yang Anda pilih tidak berisi berkas gambar yang didukung (JPG, PNG, WebP, AVIF).'
      )
    }
    input.value = ''
  }
}

const totalSelectedSize = computed(() => {
  const bytes = batch.selectedFiles.reduce((acc, f) => acc + f.size, 0)
  return (bytes / 1024 / 1024).toFixed(1)
})

async function handleStart() {
  try {
    await batch.startBatch()
    showToast('Batch processing dimulai!', 'info')
  } catch {
    showError(
      'Gagal Memulai Batch',
      batch.error || 'Terjadi kesalahan saat menginisialisasi antrean batch.'
    )
  }
}

async function handleCancel() {
  const confirmed = await showConfirm({
    title: 'Hentikan Proses Batch?',
    message: 'Proses penerjemahan seluruh gambar yang tersisa dalam antrean akan dibatalkan.',
    confirmText: 'Ya, Hentikan',
    cancelText: 'Lanjutkan Proses',
    danger: true,
  })
  if (!confirmed) return
  batch.cancelBatch()
  showToast('Batch berhasil dibatalkan', 'info')
}
</script>

<template>
  <div class="page-batch">
    <!-- Header -->
    <header class="page-header">
      <div class="header-titles">
        <h1 class="page-title">Batch Processing</h1>
        <p class="page-subtitle">
          Terjemahkan banyak halaman atau seluruh chapter manga sekaligus dalam satu antrean otomatis.
        </p>
      </div>
    </header>

    <!-- Language & Engine Control Bar -->
    <div class="control-bar glass-card">
      <div class="controls-inner">
        <LangSelector
          v-model="batch.sourceLang"
          :options="settingsStore.settings.available_source_langs"
          label="Bahasa Sumber"
          id="batch-source"
        />

        <div class="arrow-indicator">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </div>

        <LangSelector
          v-model="batch.targetLang"
          :options="settingsStore.settings.available_target_langs"
          label="Bahasa Target"
          id="batch-target"
        />

        <div class="divider-v"></div>

        <LangSelector
          v-model="batch.engine"
          :options="settingsStore.settings.available_engines"
          label="Mesin Terjemahan"
          id="batch-engine"
        />
      </div>
    </div>

    <!-- Mode 1: File Selection & Queue Configuration (before task started) -->
    <div v-if="!batch.taskId" class="queue-setup-section">
      <!-- Dual Upload Hub -->
      <div class="upload-hub-grid">
        <!-- Option A: Multi-files Dropzone -->
        <div class="upload-card glass-card">
          <div class="card-badge">Pilihan 1</div>
          <h2 class="card-heading">Pilih Banyak File Gambar</h2>
          <p class="card-desc">Tarik dan lepas banyak gambar manga sekaligus</p>
          <div class="card-drop-area">
            <DropZone :multiple="true" :compact="true" @files="onFilesSelected" />
          </div>
        </div>

        <!-- Option B: Chapter Folder Selection -->
        <div class="upload-card glass-card">
          <div class="card-badge">Pilihan 2</div>
          <h2 class="card-heading">Pilih Folder Chapter</h2>
          <p class="card-desc">Pilih seluruh folder chapter, LumieTL akan memindai semua gambarnya</p>

          <div class="folder-action-zone" @click="selectFolder">
            <div class="folder-icon-circle">
              <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z" />
                <line x1="12" y1="11" x2="12" y2="17" />
                <line x1="9" y1="14" x2="15" y2="14" />
              </svg>
            </div>
            <span class="folder-btn-text">Klik untuk Memilih Folder Chapter</span>
            <span class="folder-hint">Mendukung folder berisikan JPG, PNG, WebP, AVIF</span>
            <input
              ref="folderInput"
              type="file"
              webkitdirectory
              class="hidden-input"
              @change="onFolderChange"
            />
          </div>
        </div>
      </div>

      <!-- Queue Preview Card (if files selected) -->
      <div v-if="batch.selectedFiles.length > 0" class="selected-queue-card glass-card">
        <div class="queue-header">
          <div class="queue-stats">
            <span class="queue-count">{{ batch.selectedFiles.length }} File Manga Siap Diproses</span>
            <span class="queue-size">Estimasi Total: {{ totalSelectedSize }} MB</span>
          </div>

          <div class="queue-actions">
            <button class="btn btn-ghost btn-sm" @click="batch.clearFiles()">
              Kosongkan Antrean
            </button>
            <button
              class="btn btn-primary btn-lg"
              :disabled="batch.loading"
              @click="handleStart"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"/>
              </svg>
              {{ batch.loading ? 'Menyiapkan...' : 'Mulai Proses Batch' }}
            </button>
          </div>
        </div>

        <!-- Files Chip Grid -->
        <div class="files-preview-list">
          <div
            v-for="(file, i) in batch.selectedFiles"
            :key="i"
            class="file-chip glass-panel"
          >
            <div class="chip-icon">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
            </div>
            <span class="chip-name" :title="file.name">{{ file.name }}</span>
            <span class="chip-size">{{ (file.size / 1024).toFixed(0) }} KB</span>
            <button class="chip-btn-remove" title="Hapus dari antrean" @click="batch.removeFile(i)">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mode 2: Active Batch Progress & Table -->
    <div v-if="batch.task" class="batch-running-section">
      <!-- Progress Banner -->
      <div class="progress-hero-card glass-card">
        <div class="progress-top-row">
          <div class="progress-status-group">
            <span class="progress-title">Status Pemrosesan Batch</span>
            <span class="progress-sub">
              {{ batch.task.done }} dari {{ batch.task.total }} file selesai
              <span v-if="batch.task.errors > 0" class="failed-tag">({{ batch.task.errors }} gagal)</span>
            </span>
          </div>
          <div class="progress-pct-badge">{{ batch.progress }}%</div>
        </div>

        <!-- Glowing Progress Bar -->
        <div class="progress-track">
          <div
            class="progress-fill-glow"
            :style="{ width: batch.progress + '%' }"
          ></div>
        </div>
      </div>

      <!-- Detail Table -->
      <BatchTable :files="batch.task.files" />

      <!-- Batch Footer Actions -->
      <div class="batch-footer-actions glass-card">
        <div class="left-actions">
          <button
            v-if="!batch.task.is_complete && !batch.task.cancelled"
            class="btn btn-danger"
            @click="handleCancel"
          >
            Hentikan / Batal
          </button>
        </div>

        <div class="right-actions">
          <button
            v-if="batch.task.is_complete && batch.task.success > 0"
            class="btn btn-primary btn-lg"
            @click="batch.downloadAll()"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            Download Semua (.ZIP)
          </button>

          <button
            v-if="batch.task.is_complete"
            class="btn btn-secondary"
            @click="batch.downloadLog()"
          >
            Export Log
          </button>

          <button
            v-if="batch.task.is_complete"
            class="btn btn-ghost"
            @click="batch.reset()"
          >
            Batch Baru
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-batch {
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
}

.controls-inner {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  flex-wrap: wrap;
}

.arrow-indicator {
  color: var(--text-muted);
  padding-bottom: 10px;
}

.divider-v {
  width: 1px;
  height: 42px;
  background: var(--border);
  margin: 0 4px;
}

/* Upload Hub */
.upload-hub-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.upload-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: relative;
}

.card-badge {
  font-size: 11px;
  font-weight: 700;
  color: #818CF8;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.card-heading {
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
}

.card-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.card-drop-area {
  margin-top: auto;
}

/* Folder Selection Zone */
.folder-action-zone {
  margin-top: auto;
  min-height: 190px;
  border: 2px dashed rgba(139, 92, 246, 0.3);
  border-radius: 16px;
  background: rgba(139, 92, 246, 0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  text-align: center;
}

.folder-action-zone:hover {
  border-color: #8B5CF6;
  background: rgba(139, 92, 246, 0.08);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px -4px rgba(139, 92, 246, 0.2);
}

.folder-icon-circle {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  background: rgba(139, 92, 246, 0.15);
  border: 1px solid rgba(139, 92, 246, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #A78BFA;
  transition: transform 0.25s ease;
}

.folder-action-zone:hover .folder-icon-circle {
  background: #8B5CF6;
  color: #FFFFFF;
  transform: scale(1.06);
}

.folder-btn-text {
  font-family: var(--font-heading);
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.folder-hint {
  font-size: 12px;
  color: var(--text-muted);
}

.hidden-input {
  display: none;
}

/* Selected Queue Card */
.selected-queue-card {
  padding: 20px 24px;
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.queue-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
}

.queue-stats {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.queue-count {
  font-family: var(--font-heading);
  font-size: 16px;
  font-weight: 700;
  color: #FFFFFF;
}

.queue-size {
  font-size: 12.5px;
  color: var(--text-secondary);
}

.queue-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.files-preview-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
  max-height: 280px;
  overflow-y: auto;
  padding-right: 6px;
}

.file-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 10px;
}

.chip-icon {
  color: #818CF8;
  display: flex;
  align-items: center;
}

.chip-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12.5px;
  color: var(--text-primary);
}

.chip-size {
  font-size: 11px;
  color: var(--text-muted);
}

.chip-btn-remove {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: all 0.15s ease;
}

.chip-btn-remove:hover {
  color: var(--error);
  background: var(--error-bg);
}

/* Progress Hero */
.progress-hero-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.progress-status-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.progress-title {
  font-family: var(--font-heading);
  font-size: 17px;
  font-weight: 700;
  color: #FFFFFF;
}

.progress-sub {
  font-size: 13.5px;
  color: var(--text-secondary);
}

.failed-tag {
  color: #FB7185;
}

.progress-pct-badge {
  font-family: var(--font-heading);
  font-size: 28px;
  font-weight: 800;
  color: #818CF8;
}

.progress-track {
  height: 10px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill-glow {
  height: 100%;
  background: var(--accent-gradient);
  box-shadow: 0 0 16px rgba(99, 102, 241, 0.8);
  border-radius: 6px;
  transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Batch Running Section */
.batch-running-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.batch-footer-actions {
  padding: 16px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.right-actions, .left-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  background: rgba(244, 63, 94, 0.1);
  border: 1px solid rgba(244, 63, 94, 0.25);
  border-radius: 12px;
  color: #FDA4AF;
  font-size: 13px;
}

@media (max-width: 900px) {
  .upload-hub-grid {
    grid-template-columns: 1fr;
  }
}
</style>
