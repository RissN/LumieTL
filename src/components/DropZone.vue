<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps<{
  accept?: string
  multiple?: boolean
  compact?: boolean
}>()

const emit = defineEmits<{
  files: [files: FileList | File[]]
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

// Global Clipboard Paste (Ctrl+V) listener
function onWindowPaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items
  if (!items) return
  const imageFiles: File[] = []
  for (let i = 0; i < items.length; i++) {
    if (items[i].type.startsWith('image/')) {
      const file = items[i].getAsFile()
      if (file) imageFiles.push(file)
    }
  }
  if (imageFiles.length > 0) {
    emit('files', imageFiles)
  }
}

onMounted(() => {
  window.addEventListener('paste', onWindowPaste)
})

onUnmounted(() => {
  window.removeEventListener('paste', onWindowPaste)
})
</script>

<template>
  <div
    :class="['dropzone-container', { dragging: isDragging, compact: compact }]"
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

    <div class="dropzone-inner">
      <div class="icon-glow-wrap">
        <div class="icon-circle">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" class="upload-svg">
            <path
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </div>
      </div>

      <div class="text-group">
        <h3 class="main-prompt">
          Tarik & Lepas gambar di sini, atau <span class="accent-text">Pilih File</span>
        </h3>
        <p class="sub-prompt">
          Bisa juga gunakan tangkapan layar dengan tekan <kbd>Ctrl + V</kbd>
        </p>
      </div>

      <div class="badges-row">
        <span class="badge">JPG</span>
        <span class="badge">PNG</span>
        <span class="badge">WEBP</span>
        <span class="badge">AVIF</span>
        <span class="badge-subtle">Maksimal 500 MB</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dropzone-container {
  position: relative;
  border: 2px dashed rgba(99, 102, 241, 0.25);
  border-radius: 18px;
  padding: 48px 24px;
  text-align: center;
  cursor: pointer;
  background: rgba(19, 20, 30, 0.4);
  backdrop-filter: blur(12px);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

.dropzone-container::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.06) 0%, transparent 70%);
  pointer-events: none;
  transition: opacity 0.3s ease;
  opacity: 0.7;
}

.dropzone-container:hover {
  border-color: var(--accent);
  background: rgba(19, 20, 30, 0.7);
  box-shadow: 0 8px 32px -4px rgba(99, 102, 241, 0.18);
  transform: translateY(-2px);
}

.dropzone-container.dragging {
  border-color: #8B5CF6;
  background: rgba(99, 102, 241, 0.12);
  box-shadow: 0 0 36px rgba(99, 102, 241, 0.3);
  transform: scale(1.01);
}

.dropzone-container.compact {
  padding: 32px 16px;
}

.file-input {
  display: none;
}

.dropzone-inner {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.icon-glow-wrap {
  position: relative;
}

.icon-circle {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #818CF8;
  transition: all 0.25s ease;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.dropzone-container:hover .icon-circle,
.dropzone-container.dragging .icon-circle {
  background: var(--accent);
  color: #FFFFFF;
  box-shadow: 0 6px 24px rgba(99, 102, 241, 0.5);
  transform: scale(1.06);
}

.upload-svg {
  transition: transform 0.25s ease;
}

.dropzone-container:hover .upload-svg {
  transform: translateY(-2px);
}

.text-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.main-prompt {
  font-family: var(--font-heading);
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.2px;
}

.accent-text {
  color: #818CF8;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.sub-prompt {
  font-size: 13px;
  color: var(--text-secondary);
}

kbd {
  font-family: monospace;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 5px;
  padding: 2px 6px;
  font-size: 11px;
  color: #E0E7FF;
}

.badges-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 4px;
}

.badge {
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--text-muted);
}

.badge-subtle {
  font-size: 11px;
  color: var(--text-muted);
  margin-left: 4px;
}
</style>
