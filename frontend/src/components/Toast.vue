<template>
  <transition
    enter-active-class="transition duration-200 ease-out"
    enter-from-class="opacity-0 translate-y-2"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition duration-150 ease-in"
    leave-from-class="opacity-100 translate-y-0"
    leave-to-class="opacity-0 translate-y-2"
  >
    <div
      v-if="visible"
      :class="[
        'fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-lg border shadow-xl text-xs font-medium flex items-center gap-2 backdrop-blur-sm',
        type === 'error'
          ? 'bg-[#18181C]/95 border-[#E05C5C] text-[#E05C5C]'
          : 'bg-[#18181C]/95 border-[#6C8EF5] text-[#E8E8ED]'
      ]"
    >
      <AlertCircle v-if="type === 'error'" class="w-4 h-4 shrink-0 text-[#E05C5C]" />
      <CheckCircle2 v-else class="w-4 h-4 shrink-0 text-[#4CAF82]" />
      <span>{{ message }}</span>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { AlertCircle, CheckCircle2 } from 'lucide-vue-next'

const visible = ref(false)
const message = ref('')
const type = ref<'info' | 'error'>('info')
let timer: ReturnType<typeof setTimeout> | null = null

function show(msg: string, toastType: 'info' | 'error' = 'info', duration = 3000) {
  message.value = msg
  type.value = toastType
  visible.value = true
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => {
    visible.value = false
  }, duration)
}

defineExpose({ show })
</script>
