<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import type { HistoryEntry, HistoryResponse } from '@/types'

const { showToast } = useToast()

const entries = ref<HistoryEntry[]>([])
const total = ref(0)
const page = ref(0)
const limit = 30

// Filters
const filterEngine = ref('')
const filterStatus = ref('')

const loading = ref(false)

async function fetchHistory() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      limit,
      offset: page.value * limit,
    }
    if (filterEngine.value) params.engine = filterEngine.value
    if (filterStatus.value) params.status = filterStatus.value

    const res = await api.get<HistoryResponse>('/history', { params })
    entries.value = res.data.items
    total.value = res.data.total
  } catch (e: any) {
    showToast(e.message, 'error')
  } finally {
    loading.value = false
  }
}

async function deleteEntry(id: number) {
  try {
    await api.delete(`/history/${id}`)
    showToast('Riwayat dihapus', 'success')
    await fetchHistory()
  } catch (e: any) {
    showToast(e.message, 'error')
  }
}

async function clearAll() {
  if (!confirm('Hapus semua riwayat?')) return
  try {
    await api.delete('/history/all')
    showToast('Semua riwayat dihapus', 'success')
    entries.value = []
    total.value = 0
    page.value = 0
  } catch (e: any) {
    showToast(e.message, 'error')
  }
}

function nextPage() {
  if ((page.value + 1) * limit < total.value) {
    page.value++
    fetchHistory()
  }
}

function prevPage() {
  if (page.value > 0) {
    page.value--
    fetchHistory()
  }
}

function applyFilter() {
  page.value = 0
  fetchHistory()
}

function formatDate(ts: string): string {
  try {
    const d = new Date(ts)
    return d.toLocaleString('id-ID', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  } catch {
    return ts
  }
}

const engineNames: Record<string, string> = {
  google: 'Google',
  deepl: 'DeepL',
  openai: 'OpenAI',
}

onMounted(fetchHistory)
</script>

<template>
  <div class="page-history">
    <div class="page-header">
      <h1 class="page-title">Riwayat</h1>
      <button
        v-if="entries.length > 0"
        class="btn btn-danger-ghost"
        @click="clearAll"
      >
        Hapus Semua
      </button>
    </div>

    <!-- Filters -->
    <div class="filters-row">
      <select v-model="filterEngine" class="filter-select" @change="applyFilter">
        <option value="">Semua Engine</option>
        <option value="google">Google</option>
        <option value="deepl">DeepL</option>
        <option value="openai">OpenAI</option>
      </select>

      <select v-model="filterStatus" class="filter-select" @change="applyFilter">
        <option value="">Semua Status</option>
        <option value="success">Berhasil</option>
        <option value="error">Gagal</option>
      </select>
    </div>

    <!-- Table -->
    <div class="history-table-wrapper">
      <table class="history-table">
        <thead>
          <tr>
            <th>Tanggal</th>
            <th>File</th>
            <th>Bahasa</th>
            <th>Engine</th>
            <th>Durasi</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="cell-empty">Memuat...</td>
          </tr>
          <tr v-else-if="entries.length === 0">
            <td colspan="7" class="cell-empty">Belum ada riwayat</td>
          </tr>
          <tr v-for="entry in entries" :key="entry.id">
            <td class="cell-date">{{ formatDate(entry.timestamp) }}</td>
            <td class="cell-filename" :title="entry.input_filename">
              {{ entry.input_filename }}
            </td>
            <td class="cell-lang">
              {{ entry.source_lang }} → {{ entry.target_lang }}
            </td>
            <td>
              <span class="engine-badge">{{ engineNames[entry.engine] || entry.engine }}</span>
            </td>
            <td class="cell-duration">{{ entry.duration.toFixed(1) }}s</td>
            <td>
              <span :class="['status-dot', entry.success ? 'dot-success' : 'dot-error']">
                {{ entry.success ? '✅' : '❌' }}
              </span>
            </td>
            <td>
              <button class="btn-delete" @click="deleteEntry(entry.id)" title="Hapus">
                🗑
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="total > limit" class="pagination">
      <button class="btn btn-ghost btn-sm" :disabled="page === 0" @click="prevPage">
        ← Sebelumnya
      </button>
      <span class="page-info">
        {{ page * limit + 1 }}–{{ Math.min((page + 1) * limit, total) }} dari {{ total }}
      </span>
      <button
        class="btn btn-ghost btn-sm"
        :disabled="(page + 1) * limit >= total"
        @click="nextPage"
      >
        Selanjutnya →
      </button>
    </div>
  </div>
</template>

<style scoped>
.page-history {
  display: flex;
  flex-direction: column;
  gap: 16px;
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

.filters-row {
  display: flex;
  gap: 10px;
}

.filter-select {
  appearance: none;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 12px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  outline: none;
}

.filter-select:focus {
  border-color: var(--accent);
}

.filter-select option {
  background: var(--bg-surface);
}

.history-table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--border);
  border-radius: 10px;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.history-table thead {
  background: var(--bg-elevated);
}

.history-table th {
  padding: 10px 14px;
  text-align: left;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 1px solid var(--border);
}

.history-table td {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  color: var(--text-primary);
}

.history-table tr:last-child td {
  border-bottom: none;
}

.history-table tr:hover td {
  background: color-mix(in srgb, var(--bg-elevated) 50%, transparent);
}

.cell-empty {
  text-align: center;
  color: var(--text-secondary);
  padding: 32px !important;
}

.cell-date {
  white-space: nowrap;
  color: var(--text-secondary);
  font-size: 12px;
}

.cell-filename {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-lang {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.cell-duration {
  font-variant-numeric: tabular-nums;
  color: var(--text-secondary);
}

.engine-badge {
  padding: 2px 7px;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 500;
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  color: var(--accent);
}

.status-dot {
  font-size: 14px;
}

.btn-delete {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  padding: 4px;
  border-radius: 4px;
  opacity: 0.5;
  transition: all 0.15s;
}

.btn-delete:hover {
  opacity: 1;
  background: color-mix(in srgb, var(--error) 15%, transparent);
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.page-info {
  font-size: 13px;
  color: var(--text-secondary);
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
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-ghost { background: transparent; color: var(--text-secondary); }
.btn-ghost:hover:not(:disabled) { color: var(--text-primary); background: var(--bg-elevated); }

.btn-sm { padding: 5px 10px; font-size: 12px; }

.btn-danger-ghost {
  background: transparent;
  color: var(--error);
  border: 1px solid color-mix(in srgb, var(--error) 30%, transparent);
}
.btn-danger-ghost:hover {
  background: color-mix(in srgb, var(--error) 10%, transparent);
}
</style>
