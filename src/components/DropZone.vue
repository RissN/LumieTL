<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  accept?: string
  multiple?: boolean
}>()

const emit = defineEmits<{
  files: [files: FileList]
}>()

const isDragging = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

function onDragOver(e: DragEvent) {
  e.preventDefault()
  isDragging.value = true
}

function onDragLeave() {
  isDragging.value = false
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  isDragging.value = false
  if (e.dataTransfer?.files?.length) {
    emit('files', e.dataTransfer.files)
  }
}

function onClick() {
  fileInput.value?.click()
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files?.length) {
    emit('files', input.files)
    input.value = '' // reset for re-selection
  }
}
</script>

<template>
  <div
    :class="['dropzone', { dragging: isDragging }]"
    @dragover="onDragOver"
    @dragleave="onDragLeave"
    @drop="onDrop"
    @click="onClick"
  >
    <input
      ref="fileInput"
      type="file"
      :accept="accept || 'image/jpeg,image/png,image/webp,image/avif'"
      :multiple="multiple || false"
      class="file-input"
      @change="onFileChange"
    />

    <div class="dropzone-content">
      <div class="dropzone-icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
          <polyline points="17,8 12,3 7,8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
      </div>
      <p class="dropzone-text">Seret gambar ke sini, atau klik untuk pilih file</p>
      <p class="dropzone-hint">JPG · PNG · WebP · AVIF</p>
    </div>
  </div>
</template>

<style scoped>
.dropzone {
  border: 2px dashed var(--border);
  border-radius: 12px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--bg-base);
}

.dropzone:hover {
  border-color: var(--accent);
  background: color-mix(in srgb, var(--accent) 5%, var(--bg-base));
}

.dropzone.dragging {
  border-color: var(--accent);
  background: color-mix(in srgb, var(--accent) 10%, var(--bg-base));
  transform: scale(1.01);
}

.file-input {
  display: none;
}

.dropzone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.dropzone-icon {
  color: var(--text-secondary);
  opacity: 0.5;
}

.dropzone.dragging .dropzone-icon,
.dropzone:hover .dropzone-icon {
  color: var(--accent);
  opacity: 1;
}

.dropzone-text {
  color: var(--text-secondary);
  font-size: 14px;
}

.dropzone-hint {
  color: var(--text-secondary);
  font-size: 12px;
  opacity: 0.6;
}
</style>
