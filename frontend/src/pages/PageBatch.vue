<template>
  <div class="space-y-4">
    <!-- Header -->
    <div>
      <h1 class="text-xl font-bold text-[#E8E8ED]">Proses Batch</h1>
      <p class="text-sm text-[#8A8A96]">Unggah beberapa berkas sekaligus untuk diterjemahkan secara otomatis</p>
    </div>

    <!-- Controls -->
    <div class="flex flex-wrap items-center gap-3 bg-[#18181C] p-3 rounded-lg border border-[#2A2A30]">
      <input
        ref="multiInput"
        type="file"
        multiple
        accept="image/jpeg,image/png,image/webp,image/avif"
        class="hidden"
        @change="onFilesSelected"
      />
      <button
        @click="multiInput?.click()"
        class="px-3 py-1.5 text-xs bg-[#222228] hover:bg-[#2A2A30] text-[#E8E8ED] rounded border border-[#2A2A30]"
      >
        📁 Pilih Beberapa File
      </button>

      <span class="text-xs text-[#8A8A96]">{{ selectedFiles.length }} file dipilih</span>

      <div class="ml-auto flex items-center gap-3">
        <select
          v-model="engine"
          class="bg-[#222228] border border-[#2A2A30] text-[#E8E8ED] text-xs rounded px-2.5 py-1.5 focus:border-[#6C8EF5] outline-none"
        >
          <option value="google">Google Translate</option>
          <option value="deepl">DeepL</option>
          <option value="openai">OpenAI GPT-4o</option>
        </select>

        <button
          @click="startBatch"
          :disabled="selectedFiles.length === 0 || isRunning"
          class="bg-[#6C8EF5] hover:bg-[#7D9CF8] disabled:bg-[#222228] disabled:text-[#8A8A96] text-white text-xs font-semibold px-4 py-2 rounded-md transition-colors"
        >
          {{ isRunning ? 'Memproses...' : 'Mulai Batch' }}
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-[#18181C] border border-[#2A2A30] rounded-xl overflow-hidden">
      <table class="w-full text-left text-xs">
        <thead class="bg-[#0F0F11] text-[#8A8A96] border-b border-[#2A2A30]">
          <tr>
            <th class="p-3">Nama File</th>
            <th class="p-3">Ukuran</th>
            <th class="p-3">Status</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-[#2A2A30]">
          <tr v-for="(file, idx) in selectedFiles" :key="idx" class="hover:bg-[#222228]/50">
            <td class="p-3 text-[#E8E8ED] font-medium">{{ file.name }}</td>
            <td class="p-3 text-[#8A8A96]">{{ Math.round(file.size / 1024) }} KB</td>
            <td class="p-3">
              <span v-if="taskResults[idx]?.status === 'success'" class="text-[#4CAF82]">✅ Selesai</span>
              <span v-else-if="taskResults[idx]?.status === 'error'" class="text-[#E05C5C]">❌ Gagal</span>
              <span v-else-if="isRunning && currentProgress >= idx" class="text-[#6C8EF5]">⏳ Memproses</span>
              <span v-else class="text-[#8A8A96]">⏸ Menunggu</span>
            </td>
          </tr>
          <tr v-if="selectedFiles.length === 0">
            <td colspan="3" class="p-8 text-center text-[#8A8A96]">
              Belum ada file yang dipilih untuk proses batch.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <Toast ref="toastRef" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import Toast from '@/components/Toast.vue'

const multiInput = ref<HTMLInputElement | null>(null)
const selectedFiles = ref<File[]>([])
const engine = ref('google')
const isRunning = ref(false)
const currentProgress = ref(0)
const taskResults = ref<any[]>([])
const toastRef = ref<InstanceType<typeof Toast> | null>(null)

function onFilesSelected(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files) {
    selectedFiles.value = Array.from(target.files)
    taskResults.value = []
    currentProgress.value = 0
  }
}

async function startBatch() {
  if (selectedFiles.value.length === 0) return

  isRunning.value = true
  const formData = new FormData()
  selectedFiles.value.forEach(f => formData.append('files', f))
  formData.append('source_lang', 'auto')
  formData.append('target_lang', 'ID')
  formData.append('engine', engine.value)

  try {
    const res = await axios.post('/api/translate/batch/start', formData)
    const taskId = res.data.task_id

    // Poll status
    const interval = setInterval(async () => {
      const statusRes = await axios.get(`/api/translate/batch/${taskId}`)
      currentProgress.value = statusRes.data.progress
      taskResults.value = statusRes.data.results

      if (statusRes.data.status === 'finished' || statusRes.data.status === 'cancelled') {
        clearInterval(interval)
        isRunning.value = false
        toastRef.value?.show('Batch translation selesai!')
      }
    }, 2000)
  } catch (err: any) {
    isRunning.value = false
    toastRef.value?.show(err.response?.data?.detail || 'Gagal memulai batch', 'error')
  }
}
</script>
