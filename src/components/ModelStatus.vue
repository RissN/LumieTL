<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import api from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import { useModal } from '@/composables/useModal'
import type { ModelStatus, ModelDownloadProgress } from '@/types'

const status = ref<ModelStatus | null>(null)
const downloadProgress = ref<ModelDownloadProgress | null>(null)
const downloading = ref(false)
const openingFolder = ref(false)

const { showToast } = useToast()
const { showError } = useModal()

let pollTimer: ReturnType<typeof setInterval> | null = null

async function fetchStatus() {
  try {
    const res = await api.get<ModelStatus>('/models/status')
    status.value = res.data
  } catch (e: any) {
    console.error('Failed to fetch model status:', e)
  }
}

async function startDownload() {
  downloading.value = true
  downloadProgress.value = {
    status: 'downloading',
    current_model: 'Menyiapkan koneksi...',
    progress: 0,
    total: 100,
    percent: 0,
    overall_percent: 0,
    error: null,
  }

  try {
    const res = await api.post<{ task_id: string }>('/models/download')
    const taskId = res.data.task_id

    pollTimer = setInterval(async () => {
      try {
        const prog = await api.get<ModelDownloadProgress>(`/models/download/${taskId}`)
        downloadProgress.value = prog.data

        if (prog.data.status === 'done') {
          stopPolling()
          downloading.value = false
          showToast('Seluruh model deep learning offline berhasil diunduh!', 'success')
          await fetchStatus()
        } else if (prog.data.status === 'error') {
          stopPolling()
          downloading.value = false
          const errMsg = prog.data.error || 'Pengunduhan model terputus.'
          showError(
            'Gagal Mengunduh Model',
            'Koneksi ke server model terputus atau gagal mengunduh asset release dari GitHub.',
            errMsg
          )
          await fetchStatus()
        }
      } catch {
        // Continue polling on transient errors
      }
    }, 800)
  } catch (e: any) {
    downloading.value = false
    downloadProgress.value = null
    const errText = e.response?.data?.detail || e.message || 'Terjadi kesalahan koneksi.'
    showError(
      'Gagal Memulai Pengunduhan',
      'Tidak dapat memulai proses pengunduhan model offline.',
      errText
    )
  }
}

async function openModelsFolder() {
  openingFolder.value = true
  try {
    await api.post('/models/open-folder')
    showToast('Folder model berhasil dibuka di file manager', 'info')
  } catch (e: any) {
    showToast('Gagal membuka folder model', 'error')
  } finally {
    openingFolder.value = false
  }
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function formatBytes(bytes: number): string {
  if (!bytes || bytes <= 0) return '0 MB'
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(1)} MB`
}

function formatSize(mb: number): string {
  return `${mb} MB`
}

onMounted(fetchStatus)
onUnmounted(stopPolling)
</script>

<template>
  <div class="model-status-wrapper">
    <!-- Status Banner -->
    <div v-if="status && status.ready" class="status-banner ready glass-panel">
      <div class="banner-icon-box success">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </div>
      <div class="banner-text-group">
        <span class="banner-title">Seluruh Model Siap Digunakan</span>
        <span class="banner-desc">Detektor balon manga, OCR, dan Inpainting telah terpasang di disk lokal.</span>
      </div>
      <button
        class="btn btn-secondary btn-sm"
        :disabled="openingFolder"
        @click="openModelsFolder"
        title="Buka lokasi folder penyimpanan model"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
        </svg>
        Buka Folder Model
      </button>
    </div>

    <div v-else-if="status && !status.ready" class="status-banner not-ready glass-panel">
      <div class="banner-icon-box warning">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
      </div>
      <div class="banner-text-group">
        <span class="banner-title">Beberapa Model Belum Terunduh</span>
        <span class="banner-desc">Unduh model offline untuk menjalankan pipeline deteksi dan inpainting secara optimal.</span>
      </div>
      <div class="banner-action-group">
        <button
          class="btn btn-secondary btn-sm"
          :disabled="openingFolder"
          @click="openModelsFolder"
          title="Buka lokasi folder model di File Explorer"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>
          </svg>
          Buka Folder
        </button>
        <button
          v-if="!downloading"
          class="btn btn-primary btn-sm btn-download-all"
          @click="startDownload"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Unduh Semua Model
        </button>
      </div>
    </div>

    <!-- Active Download Progress Card -->
    <div v-if="downloading && downloadProgress" class="download-progress-card glass-panel">
      <div class="progress-meta">
        <div class="progress-title-col">
          <span class="progress-badge-live">
            <span class="pulse-dot"></span>
            Sedang Mengunduh
          </span>
          <span class="progress-label">
            Model: <strong>{{ downloadProgress.current_model }}</strong>
          </span>
        </div>
        <div class="progress-numbers">
          <span class="progress-bytes">
            {{ formatBytes(downloadProgress.progress) }} / {{ formatBytes(downloadProgress.total) }}
          </span>
          <span class="progress-pct">
            {{ downloadProgress.percent || 0 }}%
          </span>
        </div>
      </div>

      <!-- Current model progress track -->
      <div class="progress-track">
        <div
          class="progress-fill"
          :style="{ width: `${downloadProgress.percent || 0}%` }"
        ></div>
      </div>

      <!-- Overall progress meta if multiple models -->
      <div v-if="downloadProgress.overall_percent !== undefined" class="overall-progress-row">
        <span class="overall-label">
          Total Progres ({{ downloadProgress.completed_count || 0 }}/{{ downloadProgress.total_models || 3 }} Selesai)
        </span>
        <span class="overall-pct">{{ downloadProgress.overall_percent }}%</span>
      </div>
      <div v-if="downloadProgress.overall_percent !== undefined" class="overall-progress-track">
        <div
          class="overall-progress-fill"
          :style="{ width: `${downloadProgress.overall_percent}%` }"
        ></div>
      </div>
    </div>

    <!-- Model List -->
    <div v-if="status" class="model-cards-list">
      <div
        v-for="model in status.models"
        :key="model.name"
        :class="[
          'model-item-card',
          'glass-panel',
          downloading && downloadProgress?.current_model === model.name ? 'is-downloading' : ''
        ]"
      >
        <div class="model-info">
          <div class="model-icon-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 2 7 12 12 22 7 12 2"/>
              <polyline points="2 17 12 22 22 17"/>
              <polyline points="2 12 12 17 22 12"/>
            </svg>
          </div>
          <div class="model-names">
            <span class="model-name">{{ model.name }}</span>
            <span class="model-size-badge">{{ formatSize(model.size_mb) }}</span>
            <span class="model-filename-badge">{{ model.filename }}</span>
          </div>
        </div>

        <div class="model-action-cell">
          <!-- Active downloading state -->
          <span
            v-if="downloading && downloadProgress?.current_model === model.name"
            class="model-status-chip chip-active"
          >
            <span class="status-dot active-dot"></span>
            Mengunduh {{ downloadProgress.percent || 0 }}%
          </span>

          <!-- Ready state -->
          <span
            v-else
            :class="['model-status-chip', model.downloaded ? 'chip-downloaded' : 'chip-missing']"
          >
            <span class="status-dot"></span>
            {{ model.downloaded ? 'Tersedia di Disk' : 'Belum Ada' }}
          </span>

          <!-- Direct Download Link from GitHub -->
          <a
            v-if="model.url && !model.downloaded"
            :href="model.url"
            target="_blank"
            rel="noopener noreferrer"
            class="btn-direct-link"
            title="Unduh manual via browser / download manager"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
            Link Manual
          </a>
        </div>
      </div>
    </div>

    <!-- Models Directory Path Footer Note -->
    <div v-if="status?.model_dir" class="model-path-note">
      <span class="path-note-label">Direktori Model:</span>
      <code class="path-note-code">{{ status.model_dir }}</code>
    </div>
  </div>
</template>

<style scoped>
.model-status-wrapper {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 14px;
  flex-wrap: wrap;
}

.banner-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.banner-icon-box.success {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #34D399;
}

.banner-icon-box.warning {
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #FBBF24;
}

.banner-text-group {
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
  min-width: 220px;
}

.banner-title {
  font-family: var(--font-heading);
  font-size: 15px;
  font-weight: 700;
  color: #FFFFFF;
}

.banner-desc {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.45;
}

.banner-action-group {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
  flex-wrap: wrap;
}

.download-progress-card {
  padding: 18px 22px;
  border-radius: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(99, 102, 241, 0.05);
  border: 1px solid rgba(99, 102, 241, 0.25);
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.12);
}

.progress-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.progress-title-col {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-badge-live {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(99, 102, 241, 0.2);
  color: #A5B4FC;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #6366F1;
  box-shadow: 0 0 10px #6366F1;
  animation: pulse-glow 1.5s infinite;
}

@keyframes pulse-glow {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.5; }
}

.progress-label {
  font-size: 13.5px;
  color: var(--text-secondary);
}

.progress-label strong {
  color: #FFFFFF;
}

.progress-numbers {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bytes {
  font-family: monospace;
  font-size: 12.5px;
  color: var(--text-muted);
}

.progress-pct {
  font-family: monospace;
  font-size: 14px;
  font-weight: 700;
  color: #818CF8;
}

.progress-track {
  height: 9px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 5px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366F1 0%, #A855F7 100%);
  box-shadow: 0 0 16px rgba(168, 85, 247, 0.7);
  border-radius: 5px;
  transition: width 0.2s ease;
}

.overall-progress-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 4px;
}

.overall-label {
  font-size: 12px;
  color: var(--text-muted);
}

.overall-pct {
  font-family: monospace;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
}

.overall-progress-track {
  height: 4px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 2px;
  overflow: hidden;
}

.overall-progress-fill {
  height: 100%;
  background: rgba(129, 140, 248, 0.5);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.model-cards-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.model-item-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.model-item-card.is-downloading {
  border-color: rgba(99, 102, 241, 0.4);
  background: rgba(99, 102, 241, 0.05);
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.15);
}

.model-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.model-icon-badge {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.2);
  color: #818CF8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.model-names {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.model-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.model-size-badge {
  font-size: 11px;
  font-family: monospace;
  padding: 2px 7px;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-muted);
}

.model-filename-badge {
  font-size: 11px;
  font-family: monospace;
  padding: 2px 7px;
  border-radius: 5px;
  background: rgba(99, 102, 241, 0.08);
  color: #A5B4FC;
}

.model-action-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.model-status-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 8px;
  font-size: 12.5px;
  font-weight: 600;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}

.chip-downloaded {
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.25);
  color: #34D399;
}
.chip-downloaded .status-dot {
  background: #10B981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
}

.chip-missing {
  background: rgba(244, 63, 94, 0.12);
  border: 1px solid rgba(244, 63, 94, 0.25);
  color: #FB7185;
}
.chip-missing .status-dot {
  background: #F43F5E;
}

.chip-active {
  background: rgba(99, 102, 241, 0.18);
  border: 1px solid rgba(99, 102, 241, 0.4);
  color: #A5B4FC;
}
.active-dot {
  background: #818CF8;
  box-shadow: 0 0 10px #818CF8;
  animation: pulse-glow 1.2s infinite;
}

.btn-direct-link {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 8px;
  font-size: 11.5px;
  font-weight: 500;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  text-decoration: none;
  transition: all 0.15s ease;
}

.btn-direct-link:hover {
  color: #FFFFFF;
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.model-path-note {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.04);
  font-size: 12px;
  color: var(--text-muted);
  flex-wrap: wrap;
}

.path-note-label {
  font-weight: 600;
  color: var(--text-secondary);
}

.path-note-code {
  font-family: monospace;
  color: #A5B4FC;
  word-break: break-all;
}
</style>
