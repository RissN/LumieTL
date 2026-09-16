<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import { useModal } from '@/composables/useModal'
import type { HistoryEntry, HistoryResponse } from '@/types'

const { showToast } = useToast()
const { showConfirm, showError } = useModal()

const entries = ref<HistoryEntry[]>([])
const total = ref(0)
const page = ref(0)
const limit = 30

// Filters
const filterEngine = ref('')
const filterStatus = ref('')
const searchQuery = ref('')

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
    showError('Gagal Mengambil Riwayat', e.message)
  } finally {
    loading.value = false
  }
}

async function deleteEntry(id: number) {
  const confirmed = await showConfirm({
    title: 'Hapus Catatan Riwayat?',
    message: 'Catatan ini akan dihapus secara permanen dari basis data riwayat.',
    confirmText: 'Hapus',
    cancelText: 'Batal',
    danger: true,
  })
  if (!confirmed) return

  try {
    await api.delete(`/history/${id}`)
    showToast('Riwayat berhasil dihapus', 'success')
    await fetchHistory()
  } catch (e: any) {
    showError('Gagal Menghapus Riwayat', e.message)
  }
}

async function clearAll() {
  const confirmed = await showConfirm({
    title: 'Hapus Seluruh Riwayat?',
    message: 'Apakah Anda yakin ingin menghapus seluruh riwayat terjemahan? Tindakan ini tidak dapat dibatalkan.',
    confirmText: 'Bersihkan Semua',
    cancelText: 'Batal',
    danger: true,
  })
  if (!confirmed) return

  try {
    await api.delete('/history/all')
    showToast('Seluruh riwayat berhasil dibersihkan', 'success')
    entries.value = []
    total.value = 0
    page.value = 0
  } catch (e: any) {
    showError('Gagal Membersihkan Riwayat', e.message)
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
  google: 'Google Translate',
  deepl: 'DeepL',
  openai: 'OpenAI GPT-4o',
}

// Client-side quick search
const filteredEntries = computed(() => {
  if (!searchQuery.value.trim()) return entries.value
  const q = searchQuery.value.toLowerCase()
  return entries.value.filter(
    (e) =>
      e.input_filename.toLowerCase().includes(q) ||
      e.source_lang.toLowerCase().includes(q) ||
      e.target_lang.toLowerCase().includes(q)
  )
})

// Calculate basic stats from visible entries
const successRate = computed(() => {
  if (entries.value.length === 0) return 100
  const successCount = entries.value.filter((e) => e.success).length
  return Math.round((successCount / entries.value.length) * 100)
})

const avgDuration = computed(() => {
  if (entries.value.length === 0) return 0
  const totalDuration = entries.value.reduce((acc, e) => acc + e.duration, 0)
  return (totalDuration / entries.value.length).toFixed(1)
})

onMounted(fetchHistory)
</script>

<template>
  <div class="page-history">
    <!-- Header -->
    <header class="page-header">
      <div class="header-titles">
        <h1 class="page-title">Riwayat Terjemahan</h1>
        <p class="page-subtitle">
          Arsip seluruh aktivitas terjemahan manga beserta metadata performa dan status.
        </p>
      </div>

      <button
        v-if="entries.length > 0"
        class="btn btn-danger-ghost btn-sm"
        @click="clearAll"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="3 6 5 6 21 6"/>
          <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
        </svg>
        Bersihkan Semua
      </button>
    </header>

    <!-- Stat Summary Cards -->
    <div class="stats-grid">
      <div class="stat-card glass-card">
        <div class="stat-icon-wrap">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-label">Total Aktivitas</span>
          <span class="stat-value">{{ total }} <small>halaman</small></span>
        </div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon-wrap stat-success">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-label">Tingkat Keberhasilan</span>
          <span class="stat-value">{{ successRate }}%</span>
        </div>
      </div>

      <div class="stat-card glass-card">
        <div class="stat-icon-wrap stat-amber">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-label">Rata-rata Waktu Proses</span>
          <span class="stat-value">{{ avgDuration }} <small>detik</small></span>
        </div>
      </div>
    </div>

    <!-- Filter & Search Toolbar -->
    <div class="toolbar-card glass-card">
      <div class="search-wrap">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-icon">
          <circle cx="11" cy="11" r="8"/>
          <line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Cari berdasarkan nama file atau bahasa..."
          class="search-input"
        />
      </div>

      <div class="filter-controls">
        <div class="select-box">
          <select v-model="filterEngine" class="filter-select" @change="applyFilter">
            <option value="">Semua Mesin</option>
            <option value="google">Google Translate</option>
            <option value="deepl">DeepL</option>
            <option value="openai">OpenAI GPT-4o</option>
          </select>
        </div>

        <div class="select-box">
          <select v-model="filterStatus" class="filter-select" @change="applyFilter">
            <option value="">Semua Status</option>
            <option value="success">Berhasil</option>
            <option value="error">Gagal</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Main Table -->
    <div class="table-wrapper glass-card">
      <table class="custom-table">
        <thead>
          <tr>
            <th>Waktu & Tanggal</th>
            <th>Nama Berkas</th>
            <th>Pasangan Bahasa</th>
            <th>Mesin AI</th>
            <th>Durasi</th>
            <th>Status</th>
            <th class="text-right">Aksi</th>
          </tr>
        </thead>
        <tbody>
          <!-- Loading State -->
          <tr v-if="loading">
            <td colspan="7" class="cell-empty">
              <div class="table-loader">
                <div class="spinner-inline"></div>
                <span>Memuat data riwayat...</span>
              </div>
            </td>
          </tr>

          <!-- Empty State -->
          <tr v-else-if="filteredEntries.length === 0">
            <td colspan="7" class="cell-empty">
              <div class="empty-illustration">
                <div class="empty-icon-circle">
                  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <circle cx="12" cy="12" r="10"/>
                    <polyline points="12 6 12 12 16 14"/>
                  </svg>
                </div>
                <span class="empty-title">Belum ada data riwayat</span>
                <span class="empty-desc">Terjemahan gambar tunggal atau batch akan otomatis tercatat di sini.</span>
              </div>
            </td>
          </tr>

          <!-- Rows -->
          <tr v-for="entry in filteredEntries" :key="entry.id" class="data-row">
            <td class="cell-date">
              <span class="date-text">{{ formatDate(entry.timestamp) }}</span>
            </td>
            <td class="cell-filename" :title="entry.input_filename">
              <div class="filename-wrap">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="file-icon">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
                <span class="file-text">{{ entry.input_filename }}</span>
              </div>
            </td>
            <td class="cell-lang">
              <span class="lang-tag">{{ entry.source_lang }}</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="arrow-icon">
                <polyline points="9 18 15 12 9 6" />
              </svg>
              <span class="lang-tag target">{{ entry.target_lang }}</span>
            </td>
            <td>
              <span class="engine-pill">{{ engineNames[entry.engine] || entry.engine }}</span>
            </td>
            <td class="cell-duration">
              {{ entry.duration.toFixed(1) }}s
            </td>
            <td>
              <span :class="['status-chip', entry.success ? 'chip-success' : 'chip-error']">
                <span class="status-dot"></span>
                {{ entry.success ? 'Berhasil' : 'Gagal' }}
              </span>
            </td>
            <td class="text-right">
              <button class="btn-delete-row" title="Hapus catatan riwayat" @click="deleteEntry(entry.id)">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="total > limit" class="pagination-bar glass-card">
      <button class="btn btn-ghost btn-sm" :disabled="page === 0" @click="prevPage">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        Halaman Sebelumnya
      </button>
      <span class="page-info">
        Menampilkan <strong>{{ page * limit + 1 }}–{{ Math.min((page + 1) * limit, total) }}</strong> dari <strong>{{ total }}</strong>
      </span>
      <button
        class="btn btn-ghost btn-sm"
        :disabled="(page + 1) * limit >= total"
        @click="nextPage"
      >
        Halaman Selanjutnya
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<style scoped>
.page-history {
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

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-card {
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon-wrap {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: rgba(99, 102, 241, 0.15);
  color: #818CF8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-wrap.stat-success {
  background: rgba(16, 185, 129, 0.15);
  color: #34D399;
}

.stat-icon-wrap.stat-amber {
  background: rgba(245, 158, 11, 0.15);
  color: #FBBF24;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-value {
  font-family: var(--font-heading);
  font-size: 22px;
  font-weight: 800;
  color: #FFFFFF;
}

.stat-value small {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-muted);
}

/* Toolbar */
.toolbar-card {
  padding: 12px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.search-wrap {
  position: relative;
  flex: 1;
  min-width: 260px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  background: rgba(13, 14, 21, 0.6);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 9px 14px 9px 36px;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  border-color: var(--accent);
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-select {
  appearance: none;
  background: rgba(13, 14, 21, 0.6);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 9px 28px 9px 14px;
  color: var(--text-primary);
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  outline: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%239CA3AF' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
}

.filter-select:focus {
  border-color: var(--accent);
}

/* Table */
.table-wrapper {
  overflow-x: auto;
  border-radius: 14px;
}

.custom-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.custom-table thead {
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid var(--border);
}

.custom-table th {
  padding: 12px 18px;
  text-align: left;
  font-family: var(--font-heading);
  font-size: 11.5px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.6px;
}

.text-right {
  text-align: right !important;
}

.data-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: background 0.15s ease;
}

.data-row:last-child {
  border-bottom: none;
}

.data-row:hover {
  background: rgba(255, 255, 255, 0.03);
}

.custom-table td {
  padding: 12px 18px;
  vertical-align: middle;
}

.cell-date {
  white-space: nowrap;
  font-size: 12px;
  color: var(--text-muted);
}

.filename-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  max-width: 240px;
}

.file-icon {
  color: #818CF8;
  flex-shrink: 0;
}

.file-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
  font-weight: 500;
}

.cell-lang {
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.lang-tag {
  font-family: monospace;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-secondary);
}

.lang-tag.target {
  background: rgba(99, 102, 241, 0.15);
  color: #A5B4FC;
}

.arrow-icon {
  color: var(--text-muted);
}

.engine-pill {
  font-size: 11.5px;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.cell-duration {
  font-family: monospace;
  color: var(--text-secondary);
}

.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 9px;
  border-radius: 6px;
  font-size: 11.5px;
  font-weight: 600;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.chip-success {
  background: rgba(16, 185, 129, 0.12);
  color: #34D399;
}
.chip-success .status-dot {
  background: #10B981;
}

.chip-error {
  background: rgba(244, 63, 94, 0.12);
  color: #FB7185;
}
.chip-error .status-dot {
  background: #F43F5E;
}

.btn-delete-row {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  transition: all 0.15s ease;
}

.btn-delete-row:hover {
  color: var(--error);
  background: var(--error-bg);
}

/* Empty & Loading */
.cell-empty {
  padding: 48px 20px !important;
  text-align: center;
}

.table-loader {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: var(--text-secondary);
}

.spinner-inline {
  width: 18px;
  height: 18px;
  border: 2.5px solid rgba(99, 102, 241, 0.2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.empty-illustration {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.empty-icon-circle {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.04);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.empty-title {
  font-family: var(--font-heading);
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-desc {
  font-size: 13px;
  color: var(--text-secondary);
  max-width: 320px;
}

/* Pagination */
.pagination-bar {
  padding: 12px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.page-info {
  font-size: 12.5px;
  color: var(--text-secondary);
}

.page-info strong {
  color: var(--text-primary);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 800px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
