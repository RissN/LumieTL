<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useBatchStore } from '@/stores/batch'
import { useSettingsStore } from '@/stores/settings'
import { useToast } from '@/composables/useToast'
import DropZone from '@/components/DropZone.vue'
import BatchTable from '@/components/BatchTable.vue'
import LangSelector from '@/components/LangSelector.vue'

const batch = useBatchStore()
const settingsStore = useSettingsStore()
const { showToast } = useToast()

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

function onFilesSelected(files: FileList) {
  batch.addFiles(files)
}

function selectFolder() {
  folderInput.value?.click()
}

function onFolderChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.length) {
    // Filter to image files only
    const imageFiles = Array.from(input.files).filter((f) =>
      /\.(jpe?g|png|webp|avif)$/i.test(f.name)
    )
    batch.addFiles(imageFiles)
    input.value = ''
  }
}

async function handleStart() {
  try {
    await batch.startBatch()
    showToast('Batch dimulai', 'info')
  } catch {
    showToast(batch.error || 'Gagal memulai batch', 'error')
  }
}

function handleCancel() {
  batch.cancelBatch()
  showToast('Batch dibatalkan', 'warning')
}
</script>

<template>
  <div class="page-batch">
    <div class="page-header">
      <h1 class="page-title">Batch</h1>
    </div>

    <!-- Controls -->
    <div class="controls-row">
      <LangSelector
        v-model="batch.sourceLang"
        :options="settingsStore.settings.available_source_langs"
        label="Bahasa Sumber"
        id="batch-source"
      />
      <LangSelector
        v-model="batch.targetLang"
        :options="settingsStore.settings.available_target_langs"
        label="Bahasa Target"
        id="batch-target"
      />
      <LangSelector
        v-model="batch.engine"
        :options="settingsStore.settings.available_engines"
        label="Engine"
        id="batch-engine"
      />
    </div>

    <!-- File selection -->
    <div v-if="!batch.taskId" class="file-selection">
      <div class="file-actions">
        <DropZone :multiple="true" @files="onFilesSelected" />

        <div class="folder-select">
          <button class="btn btn-secondary" @click="selectFolder">
            📁 Pilih Folder
          </button>
          <input
            ref="folderInput"
            type="file"
            webkitdirectory
            class="hidden-input"
            @change="onFolderChange"
          />
        </div>
      </div>

      <!-- Selected files list -->
      <div v-if="batch.selectedFiles.length > 0" class="selected-files">
        <div class="selected-header">
          <span>{{ batch.selectedFiles.length }} file dipilih</span>
          <button class="btn btn-ghost btn-sm" @click="batch.clearFiles()">
            Hapus Semua
          </button>
        </div>
        <div class="file-list">
          <div
            v-for="(file, i) in batch.selectedFiles"
            :key="i"
            class="file-item"
          >
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ (file.size / 1024).toFixed(0) }} KB</span>
            <button class="btn-remove" @click="batch.removeFile(i)">✕</button>
          </div>
        </div>

        <button
          class="btn btn-primary"
          :disabled="batch.loading"
          @click="handleStart"
        >
          {{ batch.loading ? 'Memulai...' : 'Mulai Batch' }}
        </button>
      </div>
    </div>

    <!-- Active batch -->
    <div v-if="batch.task" class="batch-active">
      <!-- Progress bar -->
      <div class="progress-section">
        <div class="progress-info">
          <span>{{ batch.task.done }} / {{ batch.task.total }} selesai</span>
          <span>{{ batch.progress }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: batch.progress + '%' }"></div>
        </div>
      </div>

      <!-- Batch table -->
      <BatchTable :files="batch.task.files" />

      <!-- Actions -->
      <div class="batch-actions">
        <button
          v-if="!batch.task.is_complete && !batch.task.cancelled"
          class="btn btn-danger"
          @click="handleCancel"
        >
          Batal
        </button>

        <button
          v-if="batch.task.is_complete && batch.task.success > 0"
          class="btn btn-primary"
          @click="batch.downloadAll()"
        >
          ⬇ Download Semua
        </button>

        <button
          v-if="batch.task.is_complete"
          class="btn btn-secondary"
          @click="batch.downloadLog()"
        >
          📄 Export Log
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

    <!-- Error -->
    <div v-if="batch.error" class="error-banner">
      <span>❌</span>
      <span>{{ batch.error }}</span>
    </div>
  </div>
</template>

<style scoped>
.page-batch {
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.file-selection {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 600px;
}

.folder-select {
  display: flex;
  gap: 10px;
}

.hidden-input {
  display: none;
}

.selected-files {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selected-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  color: var(--text-secondary);
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 240px;
  overflow-y: auto;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 4px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 13px;
}

.file-item:hover {
  background: var(--bg-elevated);
}

.file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
}

.file-size {
  color: var(--text-secondary);
  font-size: 12px;
  flex-shrink: 0;
}

.btn-remove {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 14px;
  padding: 2px 4px;
  border-radius: 4px;
  transition: all 0.15s;
}

.btn-remove:hover {
  color: var(--error);
  background: color-mix(in srgb, var(--error) 15%, transparent);
}

.batch-active {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.progress-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--text-secondary);
}

.progress-bar {
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.batch-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
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

/* Buttons */
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

.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-primary { background: var(--accent); color: #fff; }
.btn-primary:hover:not(:disabled) { opacity: 0.85; }

.btn-secondary {
  background: var(--bg-elevated);
  color: var(--text-primary);
  border: 1px solid var(--border);
}
.btn-secondary:hover { border-color: var(--accent); }

.btn-danger {
  background: color-mix(in srgb, var(--error) 15%, transparent);
  color: var(--error);
  border: 1px solid color-mix(in srgb, var(--error) 30%, transparent);
}
.btn-danger:hover { background: color-mix(in srgb, var(--error) 25%, transparent); }

.btn-ghost { background: transparent; color: var(--text-secondary); }
.btn-ghost:hover { color: var(--text-primary); background: var(--bg-elevated); }

.btn-sm { padding: 5px 10px; font-size: 12px; }
</style>
