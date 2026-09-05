<template>
  <div class="flex flex-col h-full bg-[#18181C] border border-[#2A2A30] rounded-xl overflow-hidden">
    <!-- Canvas Area -->
    <div
      ref="containerRef"
      class="relative flex-1 bg-[#0F0F11] overflow-hidden flex items-center justify-center select-none cursor-crosshair min-h-[300px]"
      @mousemove="onMouseMove"
      @mouseup="isDragging = false"
      @mouseleave="isDragging = false"
    >
      <div v-if="!beforeSrc && !afterSrc" class="text-sm text-[#8A8A96]">
        Hasil terjemahan akan tampil di sini
      </div>

      <div
        v-else
        class="relative max-w-full max-h-full transition-transform"
        :style="{ transform: `scale(${zoomScale})` }"
      >
        <!-- After Image (Background/Full) -->
        <img
          v-if="afterSrc"
          :src="afterSrc"
          alt="Hasil Terjemahan"
          class="max-h-[460px] object-contain block pointer-events-none"
        />

        <!-- Before Image (Clipped Left) -->
        <div
          v-if="beforeSrc && afterSrc"
          class="absolute inset-0 overflow-hidden"
          :style="{ width: `${splitPercent}%` }"
        >
          <img
            :src="beforeSrc"
            alt="Asli"
            class="max-h-[460px] object-contain block max-w-none pointer-events-none"
          />
        </div>

        <!-- Single Before Image if After is not yet ready -->
        <img
          v-else-if="beforeSrc && !afterSrc"
          :src="beforeSrc"
          alt="Asli"
          class="max-h-[460px] object-contain block pointer-events-none"
        />

        <!-- Divider Line & Slider Handle -->
        <div
          v-if="beforeSrc && afterSrc"
          class="absolute top-0 bottom-0 w-[2px] bg-[#6C8EF5] cursor-ew-resize"
          :style="{ left: `${splitPercent}%` }"
          @mousedown.prevent="isDragging = true"
        >
          <div
            class="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 w-6 h-6 rounded-full bg-[#6C8EF5] text-white flex items-center justify-center shadow-lg"
          >
            <MoveHorizontal class="w-3.5 h-3.5" />
          </div>
        </div>
      </div>
    </div>

    <!-- Toolbar -->
    <div class="flex items-center justify-between px-4 py-2 bg-[#18181C] border-t border-[#2A2A30]">
      <div class="text-xs text-[#8A8A96]">
        Sebelum | Sesudah (Geser pembatas tengah)
      </div>
      <div class="flex items-center gap-1.5">
        <button
          @click="zoomScale = Math.min(zoomScale * 1.2, 4)"
          title="Perbesar"
          class="p-1.5 bg-[#222228] hover:bg-[#2A2A30] text-[#E8E8ED] rounded border border-[#2A2A30] transition-colors"
        >
          <ZoomIn class="w-3.5 h-3.5" />
        </button>
        <button
          @click="zoomScale = Math.max(zoomScale / 1.2, 0.5)"
          title="Perkecil"
          class="p-1.5 bg-[#222228] hover:bg-[#2A2A30] text-[#E8E8ED] rounded border border-[#2A2A30] transition-colors"
        >
          <ZoomOut class="w-3.5 h-3.5" />
        </button>
        <button
          @click="zoomScale = 1"
          title="Reset Zoom"
          class="px-2.5 py-1 text-xs bg-[#222228] hover:bg-[#2A2A30] text-[#E8E8ED] rounded border border-[#2A2A30] flex items-center gap-1 transition-colors"
        >
          <RotateCcw class="w-3 h-3" />
          <span>Reset</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ZoomIn, ZoomOut, RotateCcw, MoveHorizontal } from 'lucide-vue-next'

defineProps<{
  beforeSrc: string | null
  afterSrc: string | null
}>()

const splitPercent = ref(50)
const zoomScale = ref(1)
const isDragging = ref(false)
const containerRef = ref<HTMLDivElement | null>(null)

function onMouseMove(e: MouseEvent) {
  if (!isDragging.value || !containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const pct = Math.max(2, Math.min(98, (x / rect.width) * 100))
  splitPercent.value = pct
}
</script>
