<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

defineProps<{
  beforeSrc: string
  afterSrc: string
}>()

const container = ref<HTMLElement | null>(null)
const sliderPosition = ref(50) // percentage
const isDragging = ref(false)

function updatePosition(clientX: number) {
  if (!container.value) return
  const rect = container.value.getBoundingClientRect()
  const x = clientX - rect.left
  const pct = Math.max(0, Math.min(100, (x / rect.width) * 100))
  sliderPosition.value = pct
}

function onPointerDown(e: PointerEvent) {
  isDragging.value = true
  updatePosition(e.clientX)
  ;(e.target as HTMLElement)?.setPointerCapture?.(e.pointerId)
}

function onPointerMove(e: PointerEvent) {
  if (!isDragging.value) return
  updatePosition(e.clientX)
}

function onPointerUp() {
  isDragging.value = false
}
</script>

<template>
  <div
    ref="container"
    class="image-viewer"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointercancel="onPointerUp"
  >
    <!-- After image (full width, behind) -->
    <img :src="afterSrc" class="viewer-img after-img" alt="Translated" draggable="false" />

    <!-- Before image (clipped by slider) -->
    <div class="before-clip" :style="{ width: sliderPosition + '%' }">
      <img :src="beforeSrc" class="viewer-img before-img" alt="Original" draggable="false" />
    </div>

    <!-- Slider line -->
    <div class="slider-line" :style="{ left: sliderPosition + '%' }">
      <div class="slider-handle">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <path d="M8 5l-5 7 5 7V5zm8 0v14l5-7-5-7z" />
        </svg>
      </div>
    </div>

    <!-- Labels -->
    <span class="viewer-label label-before">Asli</span>
    <span class="viewer-label label-after">Hasil</span>
  </div>
</template>

<style scoped>
.image-viewer {
  position: relative;
  width: 100%;
  overflow: hidden;
  border-radius: 10px;
  cursor: col-resize;
  user-select: none;
  touch-action: none;
  background: var(--bg-base);
  aspect-ratio: auto;
}

.viewer-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  pointer-events: none;
}

.after-img {
  position: relative;
}

.before-clip {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  overflow: hidden;
}

.before-img {
  position: absolute;
  top: 0;
  left: 0;
  width: auto;
  min-width: 0;
}

/* Make before image match container width regardless of clip */
.before-clip .before-img {
  width: var(--container-width, 100%);
}

.slider-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background: white;
  transform: translateX(-50%);
  z-index: 2;
  pointer-events: none;
}

.slider-handle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 36px;
  height: 36px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--bg-base);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  pointer-events: auto;
  cursor: col-resize;
}

.viewer-label {
  position: absolute;
  top: 12px;
  padding: 4px 10px;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  color: white;
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
  pointer-events: none;
  z-index: 3;
}

.label-before {
  left: 12px;
}

.label-after {
  right: 12px;
}
</style>
