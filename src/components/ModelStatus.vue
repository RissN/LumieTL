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
  <div class="model-status">
    <div v-if="status && status.ready" class="status-banner ready">
      <span class="status-icon">✅</span>
      <span>Semua model siap digunakan</span>
    </div>

    <div v-else-if="status && !status.ready" class="status-banner not-ready">
      <span class="status-icon">⚠️</span>
      <span>Beberapa model perlu diunduh</span>
      <button
        v-if="!downloading"
        class="btn-download"
        @click="startDownload"
      >
        Unduh Semua
      </button>
    </div>

    <!-- Download progress -->
    <div v-if="downloading && downloadProgress" class="download-progress">
      <p class="progress-label">
        Mengunduh: <strong>{{ downloadProgress.current_model }}</strong>
      </p>
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: formatProgress(downloadProgress.progress, downloadProgress.total) }"
        ></div>
      </div>
      <p class="progress-pct">
        {{ formatProgress(downloadProgress.progress, downloadProgress.total) }}
      </p>
    </div>

    <!-- Model list -->
    <div v-if="status" class="model-list">
      <div
        v-for="model in status.models"
        :key="model.name"
        class="model-card"
      >
        <div class="model-info">
          <span class="model-name">{{ model.name }}</span>
          <span class="model-size">{{ formatSize(model.size_mb) }}</span>
        </div>
        <span :class="['model-badge', model.downloaded ? 'downloaded' : 'missing']">
          {{ model.downloaded ? 'Terunduh' : 'Belum ada' }}
        </span>
      </div>
    </div>

    <p v-if="error" class="error-text">{{ error }}</p>
  </div>
</template>

<style scoped>
.model-status {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-banner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 14px;
}

.status-banner.ready {
  background: color-mix(in srgb, var(--success) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--success) 30%, transparent);
  color: var(--success);
}

.status-banner.not-ready {
  background: color-mix(in srgb, var(--warning) 10%, transparent);
  border: 1px solid color-mix(in srgb, var(--warning) 30%, transparent);
  color: var(--warning);
}

.btn-download {
  margin-left: auto;
  padding: 6px 14px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn-download:hover {
  opacity: 0.85;
}

.download-progress {
  padding: 12px 16px;
  background: var(--bg-elevated);
  border-radius: 10px;
}

.progress-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.progress-bar {
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-pct {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 6px;
  text-align: right;
}

.model-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.model-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: var(--bg-elevated);
  border-radius: 8px;
}

.model-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.model-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.model-size {
  font-size: 12px;
  color: var(--text-secondary);
}

.model-badge {
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 500;
}

.model-badge.downloaded {
  background: color-mix(in srgb, var(--success) 15%, transparent);
  color: var(--success);
}

.model-badge.missing {
  background: color-mix(in srgb, var(--error) 15%, transparent);
  color: var(--error);
}

.error-text {
  color: var(--error);
  font-size: 13px;
}
</style>
