<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/composables/useApi'
import type { ModelStatus, ModelDownloadProgress } from '@/types'

const status = ref<ModelStatus | null>(null)
const downloadProgress = ref<ModelDownloadProgress | null>(null)
const downloading = ref(false)
const error = ref('')

let pollTimer: ReturnType<typeof setInterval> | null = null

async function fetchStatus() {
  try {
    const res = await api.get<ModelStatus>('/models/status')
    status.value = res.data
  } catch (e: any) {
    error.value = e.message
  }
}

async function startDownload() {
  downloading.value = true
  error.value = ''
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
          await fetchStatus()
        } else if (prog.data.status === 'error') {
          stopPolling()
          downloading.value = false
          error.value = prog.data.error || 'Download failed'
        }
      } catch {
        // ignore polling errors
      }
    }, 1000)
  } catch (e: any) {
    error.value = e.message
    downloading.value = false
  }
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function formatProgress(downloaded: number, total: number): string {
  if (total === 0) return '0%'
  return `${Math.round((downloaded / total) * 100)}%`
}

function formatSize(mb: number): string {
  return `${mb} MB`
}

onMounted(fetchStatus)
</script>

<template>
  <div class="model-status-wrapper">
    <!-- Status Banner -->
    <div v-if="status && status.ready" class="status-banner ready glass-panel">
      <div class="banner-icon-box success">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </div>
      <div class="banner-text-group">
        <span class="banner-title">Seluruh Model Siap Digunakan</span>
        <span class="banner-desc">Detektor balon manga, OCR, dan Inpainting telah terpasang di disk lokal.</span>
      </div>
    </div>

    <div v-else-if="status && !status.ready" class="status-banner not-ready glass-panel">
      <div class="banner-icon-box warning">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
      </div>
      <div class="banner-text-group">
        <span class="banner-title">Beberapa Model Belum Terunduh</span>
        <span class="banner-desc">Unduh model offline untuk menjalankan pipeline deteksi dan inpainting secara optimal.</span>
      </div>
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

    <!-- Download progress -->
    <div v-if="downloading && downloadProgress" class="download-progress-card glass-panel">
      <div class="progress-meta">
        <span class="progress-label">
          Mengunduh model: <strong>{{ downloadProgress.current_model }}</strong>
        </span>
        <span class="progress-pct">
          {{ formatProgress(downloadProgress.progress, downloadProgress.total) }}
        </span>
      </div>
      <div class="progress-track">
        <div
          class="progress-fill"
          :style="{ width: formatProgress(downloadProgress.progress, downloadProgress.total) }"
        ></div>
      </div>
    </div>

    <!-- Model List -->
    <div v-if="status" class="model-cards-list">
      <div
        v-for="model in status.models"
        :key="model.name"
        class="model-item-card glass-panel"
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
          </div>
        </div>

        <span :class="['model-status-chip', model.downloaded ? 'chip-downloaded' : 'chip-missing']">
          <span class="status-dot"></span>
          {{ model.downloaded ? 'Tersedia di Disk' : 'Belum Ada' }}
        </span>
      </div>
    </div>

    <p v-if="error" class="error-msg-text">{{ error }}</p>
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
  gap: 14px;
  padding: 16px 20px;
  border-radius: 12px;
  flex-wrap: wrap;
}

.banner-icon-box {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.banner-icon-box.success {
  background: rgba(16, 185, 129, 0.15);
  color: #34D399;
}

.banner-icon-box.warning {
  background: rgba(245, 158, 11, 0.15);
  color: #FBBF24;
}

.banner-text-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 200px;
}

.banner-title {
  font-family: var(--font-heading);
  font-size: 14.5px;
  font-weight: 700;
  color: #FFFFFF;
}

.banner-desc {
  font-size: 12.5px;
  color: var(--text-secondary);
}

.btn-download-all {
  margin-left: auto;
}

.download-progress-card {
  padding: 16px 20px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.progress-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.progress-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.progress-label strong {
  color: #FFFFFF;
}

.progress-pct {
  font-family: monospace;
  font-size: 13px;
  font-weight: 700;
  color: #818CF8;
}

.progress-track {
  height: 8px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent-gradient);
  box-shadow: 0 0 14px rgba(99, 102, 241, 0.6);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.model-cards-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.model-item-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  border-radius: 10px;
  transition: background 0.15s ease;
}

.model-item-card:hover {
  background: rgba(255, 255, 255, 0.03);
}

.model-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-icon-badge {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.1);
  color: #818CF8;
  display: flex;
  align-items: center;
  justify-content: center;
}

.model-names {
  display: flex;
  align-items: center;
  gap: 8px;
}

.model-name {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-primary);
}

.model-size-badge {
  font-size: 11px;
  font-family: monospace;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
}

.model-status-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.chip-downloaded {
  background: rgba(16, 185, 129, 0.12);
  color: #34D399;
}
.chip-downloaded .status-dot {
  background: #10B981;
}

.chip-missing {
  background: rgba(244, 63, 94, 0.12);
  color: #FB7185;
}
.chip-missing .status-dot {
  background: #F43F5E;
}

.error-msg-text {
  color: var(--error);
  font-size: 13px;
}
</style>
