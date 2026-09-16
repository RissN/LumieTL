<script setup lang="ts">
import type { BatchFileInfo } from '@/types'

defineProps<{
  files: BatchFileInfo[]
}>()

defineEmits<{
  retry: [filename: string]
}>()

function formatDuration(d: number): string {
  if (d <= 0) return '—'
  return `${d.toFixed(1)}s`
}
</script>

<template>
  <div class="batch-table-wrapper glass-card">
    <table class="batch-table">
      <thead>
        <tr>
          <th>File Manga</th>
          <th>Status Proses</th>
          <th>Durasi</th>
          <th class="text-right">Keterangan</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="file in files" :key="file.filename" class="table-row">
          <td class="cell-filename">
            <div class="file-info-group">
              <div class="file-icon-box">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
              </div>
              <span class="file-name-text" :title="file.filename">{{ file.filename }}</span>
            </div>
          </td>
          <td>
            <!-- Pending -->
            <span v-if="file.status === 'pending'" class="status-badge status-pending">
              <span class="status-dot-pulse"></span>
              Menunggu
            </span>

            <!-- Processing -->
            <span v-else-if="file.status === 'processing'" class="status-badge status-processing">
              <span class="spinner-tiny"></span>
              Memproses AI
            </span>

            <!-- Done -->
            <span v-else-if="file.status === 'done'" class="status-badge status-done">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              Selesai
            </span>

            <!-- Error -->
            <span v-else-if="file.status === 'error'" class="status-badge status-error">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
              Gagal
            </span>

            <!-- Cancelled -->
            <span v-else-if="file.status === 'cancelled'" class="status-badge status-cancelled">
              Dibatalkan
            </span>
          </td>
          <td class="cell-duration">{{ formatDuration(file.duration) }}</td>
          <td class="text-right">
            <button
              v-if="file.status === 'error'"
              class="btn btn-secondary btn-sm"
              @click="$emit('retry', file.filename)"
            >
              Coba Lagi
            </button>
            <span v-else-if="file.error" class="error-msg" :title="file.error">
              {{ file.error }}
            </span>
            <span v-else-if="file.status === 'done'" class="success-msg">
              Siap diunduh
            </span>
            <span v-else class="text-muted">—</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.batch-table-wrapper {
  overflow-x: auto;
  border-radius: 14px;
}

.batch-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.batch-table thead {
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid var(--border);
}

.batch-table th {
  padding: 12px 16px;
  text-align: left;
  color: var(--text-secondary);
  font-family: var(--font-heading);
  font-weight: 600;
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

.text-right {
  text-align: right !important;
}

.table-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: background 0.15s ease;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.03);
}

.batch-table td {
  padding: 12px 16px;
  color: var(--text-primary);
  vertical-align: middle;
}

.file-info-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon-box {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(99, 102, 241, 0.1);
  color: #818CF8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-name-text {
  max-width: 320px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
  color: var(--text-primary);
}

.cell-duration {
  font-family: monospace;
  font-size: 12px;
  color: var(--text-secondary);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 11.5px;
  font-weight: 600;
  letter-spacing: 0.2px;
}

.status-pending {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-secondary);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.status-dot-pulse {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
}

.status-processing {
  background: rgba(99, 102, 241, 0.15);
  color: #A5B4FC;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.spinner-tiny {
  width: 12px;
  height: 12px;
  border: 2px solid rgba(165, 180, 252, 0.3);
  border-top-color: #A5B4FC;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.status-done {
  background: rgba(16, 185, 129, 0.12);
  color: #34D399;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.status-error {
  background: rgba(244, 63, 94, 0.12);
  color: #FB7185;
  border: 1px solid rgba(244, 63, 94, 0.25);
}

.status-cancelled {
  background: rgba(245, 158, 11, 0.12);
  color: #FBBF24;
}

.error-msg {
  font-size: 11.5px;
  color: var(--error);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

.success-msg {
  font-size: 12px;
  color: #34D399;
  font-weight: 500;
}

.text-muted {
  color: var(--text-muted);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
