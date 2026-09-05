<template>
  <div
    @dragover.prevent="isDragging = true"
    @dragleave.prevent="isDragging = false"
    @drop.prevent="onDrop"
    @click="triggerBrowse"
    :class="[
      'border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-colors duration-200 min-h-[300px]',
      isDragging
        ? 'border-[#6C8EF5] bg-[#222228]'
        : 'border-[#2A2A30] bg-[#18181C] hover:border-[#6C8EF5] hover:bg-[#222228]'
    ]"
  >
    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/png,image/webp,image/avif"
      class="hidden"
      @change="onFileChanged"
    />

    <div class="w-14 h-14 rounded-2xl bg-[#222228] border border-[#2A2A30] flex items-center justify-center text-[#6C8EF5] mb-3 group-hover:scale-105 transition-transform">
      <UploadCloud class="w-7 h-7" />
    </div>
    <div class="text-sm font-medium text-[#E8E8ED] text-center mb-1">
      <span v-if="selectedFile">{{ selectedFile.name }}</span>
      <span v-else>Seret & lepas gambar di sini, atau klik untuk memilih berkas</span>
    </div>
    <div class="text-xs text-[#8A8A96] text-center">
      <span v-if="selectedFile">{{ Math.round(selectedFile.size / 1024) }} KB</span>
      <span v-else>JPG · PNG · WebP · AVIF (Maks. 50MB)</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UploadCloud } from 'lucide-vue-next'

const emit = defineEmits<{
  (e: 'file-selected', file: File): void
}>()

const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

function triggerBrowse() {
  fileInput.value?.click()
}

function onFileChanged(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    handleFile(target.files[0])
  }
}

function onDrop(event: DragEvent) {
  isDragging.value = false
  if (event.dataTransfer && event.dataTransfer.files.length > 0) {
    handleFile(event.dataTransfer.files[0])
  }
}

function handleFile(file: File) {
  selectedFile.value = file
  emit('file-selected', file)
}
</script>
