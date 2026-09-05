<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-[#E8E8ED]">Riwayat Terjemahan</h1>
        <p class="text-sm text-[#8A8A96]">Catatan berkas yang pernah diterjemahkan pada server ini</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="loadHistory"
          class="px-3 py-1.5 text-xs bg-[#222228] hover:bg-[#2A2A30] text-[#E8E8ED] rounded border border-[#2A2A30] flex items-center gap-1.5 transition-colors"
        >
          <RefreshCw class="w-3.5 h-3.5 text-[#6C8EF5]" />
          <span>Segarkan</span>
        </button>
        <button
          @click="clearAll"
          class="px-3 py-1.5 text-xs bg-[#222228] hover:bg-[#2A2A30] text-[#E05C5C] rounded border border-[#2A2A30] flex items-center gap-1.5 transition-colors"
        >
          <Trash2 class="w-3.5 h-3.5 text-[#E05C5C]" />
          <span>Hapus Semua</span>
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-[#18181C] border border-[#2A2A30] rounded-xl overflow-hidden">
      <table class="w-full text-left text-xs">
        <thead class="bg-[#0F0F11] text-[#8A8A96] border-b border-[#2A2A30]">
          <tr>
            <th class="p-3">Tanggal</th>
            <th class="p-3">File Sumber</th>
            <th class="p-3">Bahasa</th>
            <th class="p-3">Engine</th>
            <th class="p-3">Durasi</th>
            <th class="p-3">Status</th>
            <th class="p-3 text-right">Aksi</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#2A2A30]">
          <tr v-for="item in items" :key="item.id" class="hover:bg-[#222228]/50">
            <td class="p-3 text-[#8A8A96] whitespace-nowrap">{{ item.timestamp }}</td>
            <td class="p-3 text-[#E8E8ED] font-medium">{{ item.input_path.split(/[\\/]/).pop() }}</td>
            <td class="p-3 text-[#8A8A96] flex items-center gap-1">
              <span>{{ item.source_lang }}</span>
              <ArrowRight class="w-3 h-3 text-[#8A8A96]" />
              <span>{{ item.target_lang }}</span>
            </td>
            <td class="p-3 text-[#E8E8ED]">{{ item.engine }}</td>
            <td class="p-3 text-[#8A8A96]">{{ item.duration ? item.duration.toFixed(2) + 's' : '—' }}</td>
            <td class="p-3">
              <span v-if="item.success" class="text-[#4CAF82] flex items-center gap-1.5">
                <CheckCircle2 class="w-3.5 h-3.5" />
                <span>Selesai</span>
              </span>
              <span v-else class="text-[#E05C5C] flex items-center gap-1.5">
                <XCircle class="w-3.5 h-3.5" />
                <span>Gagal</span>
              </span>
            </td>
            <td class="p-3 text-right">
              <button
                @click="deleteItem(item.id)"
                class="p-1 hover:bg-[#2A2A30] rounded text-[#8A8A96] hover:text-[#E05C5C] transition-colors"
                title="Hapus"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </td>
          </tr>
          <tr v-if="items.length === 0">
            <td colspan="7" class="p-8 text-center text-[#8A8A96]">
              Belum ada riwayat terjemahan.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Toast ref="toastRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { RefreshCw, Trash2, ArrowRight, CheckCircle2, XCircle } from 'lucide-vue-next'
import type { HistoryItem } from '@/types'
import Toast from '@/components/Toast.vue'

const items = ref<HistoryItem[]>([])
const toastRef = ref<InstanceType<typeof Toast> | null>(null)

async function loadHistory() {
  try {
    const res = await axios.get('/api/history')
    items.value = res.data.items
  } catch (e) {
    console.error('Failed to load history', e)
  }
}

async function deleteItem(id: number) {
  try {
    await axios.delete(`/api/history/${id}`)
    items.value = items.value.filter(i => i.id !== id)
    toastRef.value?.show('Item riwayat dihapus')
  } catch (e) {
    toastRef.value?.show('Gagal menghapus item', 'error')
  }
}

async function clearAll() {
  if (!confirm('Hapus seluruh riwayat terjemahan?')) return
  try {
    await axios.delete('/api/history/all')
    items.value = []
    toastRef.value?.show('Riwayat berhasil dibersihkan!')
  } catch (e) {
    toastRef.value?.show('Gagal membersihkan riwayat', 'error')
  }
}

onMounted(() => {
  loadHistory()
})
</script>
