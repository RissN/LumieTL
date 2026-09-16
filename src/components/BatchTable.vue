<script setup lang="ts">
import type { BatchFileInfo } from '@/types'

defineProps<{
  files: BatchFileInfo[]
}>()

defineEmits<{
  retry: [filename: string]
}>()

const statusMap: Record<string, { icon: string; label: string; cls: string }> = {
  pending:     { icon: '⏸', label: 'Menunggu', cls: 'status-pending' },
  processing:  { icon: '⏳', label: 'Memproses', cls: 'status-processing' },
  done:        { icon: '✅', label: 'Selesai', cls: 'status-done' },
  error:       { icon: '❌', label: 'Gagal', cls: 'status-error' },
  cancelled:   { icon: '⏹', label: 'Dibatalkan', cls: 'status-cancelled' },
}

function getStatus(status: string) {
  return statusMap[status] || statusMap.pending
}

function formatDuration(d: number): string {
  if (d <= 0) return '—'
  return `${d.toFixed(1)}s`
}
</script>

<template>
  <div class="batch-table-wrapper">
    <table class="batch-table">
      <thead>
        <tr>
          <th>Nama File</th>
          <th>Status</th>
          <th>Durasi</th>
          <th>Aksi</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="file in files" :key="file.filename">
          <td class="cell-filename" :title="file.filename">{{ file.filename }}</td>
          <td>
            <span :class="['status-badge', getStatus(file.status).cls]">
              <span class="status-icon">{{ getStatus(file.status).icon }}</span>
              {{ getStatus(file.status).label }}
            </span>
          </td>
          <td class="cell-duration">{{ formatDuration(file.duration) }}</td>
          <td>
            <button
              v-if="file.status === 'error'"
              class="btn-retry"
              @click="$emit('retry', file.filename)"
            >
              Coba Lagi
            </button>
            <span v-else-if="file.error" class="error-msg" :title="file.error">
              {{ file.error }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.batch-table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 10px;
}

.batch-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.batch-table thead {
  background: var(--bg-elevated);
}

.batch-table th {
  padding: 10px 14px;
  text-align: left;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border);
}

.batch-table td {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  color: var(--text-primary);
}

.batch-table tr:last-child td {
  border-bottom: none;
}

.batch-table tr:hover td {
  background: color-mix(in srgb, var(--bg-elevated) 50%, transparent);
}

.cell-filename {
  max-width: 280px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-duration {
  font-variant-numeric: tabular-nums;
  color: var(--text-secondary);
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-icon {
  font-size: 13px;
}

.status-pending {
  background: color-mix(in srgb, var(--text-secondary) 10%, transparent);
  color: var(--text-secondary);
}

.status-processing {
  background: color-mix(in srgb, var(--accent) 15%, transparent);
  color: var(--accent);
  animation: pulse-opacity 1.5s ease-in-out infinite;
}

.status-done {
  background: color-mix(in srgb, var(--success) 15%, transparent);
  color: var(--success);
}

.status-error {
  background: color-mix(in srgb, var(--error) 15%, transparent);
  color: var(--error);
}

.status-cancelled {
  background: color-mix(in srgb, var(--warning) 15%, transparent);
  color: var(--warning);
}

@keyframes pulse-opacity {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.btn-retry {
  padding: 4px 10px;
  background: transparent;
  color: var(--accent);
  border: 1px solid var(--accent);
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-retry:hover {
  background: color-mix(in srgb, var(--accent) 15%, transparent);
}

.error-msg {
  font-size: 12px;
  color: var(--error);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}
</style>
