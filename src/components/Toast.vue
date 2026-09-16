<script setup lang="ts">
import { useToast } from '@/composables/useToast'

const { toasts, removeToast } = useToast()

const typeStyles: Record<string, string> = {
  success: 'toast-success',
  error: 'toast-error',
  warning: 'toast-warning',
  info: 'toast-info',
}

const typeIcons: Record<string, string> = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
}
</script>

<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="['toast', typeStyles[toast.type]]"
          @click="removeToast(toast.id)"
        >
          <span class="toast-icon">{{ typeIcons[toast.type] }}</span>
          <span class="toast-message">{{ toast.message }}</span>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 450;
  backdrop-filter: blur(12px);
  cursor: pointer;
  pointer-events: auto;
  max-width: 380px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.toast-icon {
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}

.toast-success {
  background: color-mix(in srgb, var(--success) 20%, var(--bg-surface) 80%);
  border: 1px solid color-mix(in srgb, var(--success) 40%, transparent);
  color: var(--success);
}

.toast-error {
  background: color-mix(in srgb, var(--error) 20%, var(--bg-surface) 80%);
  border: 1px solid color-mix(in srgb, var(--error) 40%, transparent);
  color: var(--error);
}

.toast-warning {
  background: color-mix(in srgb, var(--warning) 20%, var(--bg-surface) 80%);
  border: 1px solid color-mix(in srgb, var(--warning) 40%, transparent);
  color: var(--warning);
}

.toast-info {
  background: color-mix(in srgb, var(--accent) 20%, var(--bg-surface) 80%);
  border: 1px solid color-mix(in srgb, var(--accent) 40%, transparent);
  color: var(--accent);
}

/* Transitions */
.toast-enter-active {
  transition: all 0.3s ease;
}
.toast-leave-active {
  transition: all 0.25s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(30px) scale(0.95);
}
</style>
