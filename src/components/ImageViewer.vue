<script setup lang="ts">
import { ref, onMounted } from 'vue'

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
    class="image-viewer-container"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointercancel="onPointerUp"
  >
    <!-- Translated Result (Base) -->
    <img :src="afterSrc" class="viewer-img after-img" alt="Translated Result" draggable="false" />

    <!-- Original (Clipped on top) -->
    <div class="before-clip" :style="{ width: sliderPosition + '%' }">
      <img :src="beforeSrc" class="viewer-img before-img" alt="Original" draggable="false" />
    </div>

    <!-- Slider Divider Line & Handle -->
    <div class="slider-line" :style="{ left: sliderPosition + '%' }">
      <div class="slider-handle">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6" />
        </svg>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </div>
    </div>

    <!-- Frosted Badges -->
    <div class="viewer-label label-before">
      <span class="label-dot dot-original"></span>
      <span>Asli</span>
    </div>
    <div class="viewer-label label-after">
      <span class="label-dot dot-result"></span>
      <span>Hasil AI</span>
    </div>
  </div>
</template>

<style scoped>
.image-viewer-container {
  position: relative;
  width: 100%;
  max-height: 75vh;
  min-height: 380px;
  overflow: hidden;
  border-radius: 16px;
  cursor: col-resize;
  user-select: none;
  touch-action: none;
  background: #08090E;
  border: 1px solid var(--border);
  box-shadow: 0 16px 40px -8px rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.viewer-img {
  display: block;
  width: 100%;
  max-height: 75vh;
  object-fit: contain;
  pointer-events: none;
}

.after-img {
  position: relative;
  z-index: 1;
}

.before-clip {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  overflow: hidden;
  z-index: 2;
  display: flex;
  align-items: center;
}

.before-img {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 100%;
  max-height: 75vh;
  object-fit: contain;
  min-width: 100%;
}

.slider-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 0 12px rgba(99, 102, 241, 0.8);
  transform: translateX(-50%);
  z-index: 10;
  pointer-events: none;
}

.slider-handle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 44px;
  height: 44px;
  background: #1E1B4B;
  border: 2px solid #818CF8;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FFFFFF;
  box-shadow: 0 0 20px rgba(99, 102, 241, 0.6), 0 4px 12px rgba(0, 0, 0, 0.5);
  pointer-events: auto;
  cursor: col-resize;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.image-viewer-container:hover .slider-handle {
  transform: translate(-50%, -50%) scale(1.08);
  box-shadow: 0 0 28px rgba(99, 102, 241, 0.8), 0 6px 16px rgba(0, 0, 0, 0.6);
}

.viewer-label {
  position: absolute;
  top: 16px;
  padding: 6px 12px;
  background: rgba(15, 16, 24, 0.75);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #FFFFFF;
  font-family: var(--font-heading);
  font-size: 12px;
  font-weight: 600;
  border-radius: 8px;
  pointer-events: none;
  z-index: 12;
  display: flex;
  align-items: center;
  gap: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.label-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.dot-original {
  background: #F59E0B;
  box-shadow: 0 0 6px #F59E0B;
}

.dot-result {
  background: #10B981;
  box-shadow: 0 0 6px #10B981;
}

.label-before {
  left: 16px;
}

.label-after {
  right: 16px;
}
</style>
