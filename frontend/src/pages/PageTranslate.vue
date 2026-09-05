<template>
  <div class="space-y-4">
    <!-- Header -->
    <div>
      <h1 class="text-xl font-bold text-[#E8E8ED]">Terjemahkan Gambar</h1>
      <p class="text-sm text-[#8A8A96]">Unggah halaman manga atau manhwa untuk diterjemahkan secara otomatis</p>
    </div>

    <!-- Controls Toolbar -->
    <div class="flex flex-wrap items-center gap-3 bg-[#18181C] p-3 rounded-lg border border-[#2A2A30]">
      <div class="flex items-center gap-2">
        <label class="text-xs text-[#8A8A96]">Sumber:</label>
        <select
          v-model="sourceLang"
          class="bg-[#222228] border border-[#2A2A30] text-[#E8E8ED] text-xs rounded px-2.5 py-1.5 focus:border-[#6C8EF5] outline-none"
        >
          <option value="auto">Auto-detect</option>
          <option value="JPN">Jepang</option>
          <option value="KOR">Korea</option>
          <option value="CHS">Mandarin (Simplified)</option>
          <option value="CHT">Mandarin (Traditional)</option>
        </select>
      </div>

      <div class="flex items-center gap-2">
        <label class="text-xs text-[#8A8A96]">Target:</label>
        <select
          v-model="targetLang"
          class="bg-[#222228] border border-[#2A2A30] text-[#E8E8ED] text-xs rounded px-2.5 py-1.5 focus:border-[#6C8EF5] outline-none"
        >
          <option value="ID">Indonesia</option>
          <option value="EN">Inggris</option>
          <option value="VI">Vietnam</option>
          <option value="TH">Thailand</option>
        </select>
      </div>

      <div class="flex items-center gap-2">
        <label class="text-xs text-[#8A8A96]">Engine:</label>
        <select
          v-model="engine"
          class="bg-[#222228] border border-[#2A2A30] text-[#E8E8ED] text-xs rounded px-2.5 py-1.5 focus:border-[#6C8EF5] outline-none"
        >
          <option value="google">Google Translate</option>
          <option value="deepl">DeepL</option>
          <option value="openai">OpenAI GPT-4o</option>
        </select>
      </div>

      <div class="ml-auto">
        <button
          @click="startTranslation"
          :disabled="!selectedFile || isProcessing"
          class="bg-[#6C8EF5] hover:bg-[#7D9CF8] disabled:bg-[#222228] disabled:text-[#8A8A96] text-white text-xs font-semibold px-4 py-2 rounded-md transition-colors"
        >
          {{ isProcessing ? 'Menerjemahkan...' : 'Terjemahkan' }}
        </button>
      </div>
    </div>

    <!-- Main Workspace -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <DropZone @file-selected="onFileSelected" />
      <ImageViewer :before-src="beforePreview" :after-src="afterPreview" />
    </div>

    <!-- Actions Bar -->
    <div class="flex items-center justify-between pt-2">
      <div class="text-xs text-[#8A8A96]">
        <span v-if="duration">Selesai dalam {{ duration }} detik</span>
      </div>
      <div class="flex gap-2">
        <button
          @click="downloadResult"
          :disabled="!afterPreview"
          class="px-3 py-1.5 text-xs bg-[#222228] hover:bg-[#2A2A30] disabled:opacity-50 text-[#E8E8ED] rounded border border-[#2A2A30]"
        >
          💾 Unduh Hasil
        </button>
      </div>
    </div>

    <Toast ref="toastRef" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import DropZone from '@/components/DropZone.vue'
import ImageViewer from '@/components/ImageViewer.vue'
import Toast from '@/components/Toast.vue'

const sourceLang = ref('auto')
const targetLang = ref('ID')
const engine = ref('google')

const selectedFile = ref<File | null>(null)
const beforePreview = ref<string | null>(null)
const afterPreview = ref<string | null>(null)
const isProcessing = ref(false)
const duration = ref<number | null>(null)
const toastRef = ref<InstanceType<typeof Toast> | null>(null)

function onFileSelected(file: File) {
  selectedFile.value = file
  beforePreview.value = URL.createObjectURL(file)
  afterPreview.value = null
  duration.value = null
}

async function startTranslation() {
  if (!selectedFile.value) return

  isProcessing.value = true
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('source_lang', sourceLang.value)
  formData.append('target_lang', targetLang.value)
  formData.append('engine', engine.value)

  try {
    const res = await axios.post('/api/translate/single', formData)
    afterPreview.value = `data:image/png;base64,${res.data.result_image_base64}`
    duration.value = res.data.duration
    toastRef.value?.show('Terjemahan berhasil selesai!')
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Terjadi kesalahan saat menerjemahkan.'
    toastRef.value?.show(msg, 'error')
  } finally {
    isProcessing.value = false
  }
}

function downloadResult() {
  if (!afterPreview.value) return
  const a = document.createElement('a')
  a.href = afterPreview.value
  a.download = `translated_${selectedFile.value?.name || 'manga.png'}`
  a.click()
}
</script>
