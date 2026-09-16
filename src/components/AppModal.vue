<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useModal } from '@/composables/useModal'

const { isOpen, modalConfig, handleConfirm, handleCancel } = useModal()

function onKeydown(e: KeyboardEvent) {
  if (!isOpen.value) return
  if (e.key === 'Escape') {
    handleCancel()
  } else if (e.key === 'Enter') {
    handleConfirm()
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="isOpen" class="modal-backdrop" @click.self="handleCancel">
        <div class="modal-card glass-card" role="dialog" aria-modal="true">
          <!-- Close button in top-right -->
          <button class="btn-close-modal" @click="handleCancel" title="Tutup">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>

          <!-- Icon Header Badge -->
          <div class="modal-icon-row">
            <!-- Warning Icon -->
            <div v-if="modalConfig.type === 'warning'" class="modal-badge-circle badge-warning">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
            </div>

            <!-- Error Icon -->
            <div v-else-if="modalConfig.type === 'error'" class="modal-badge-circle badge-error">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="15" y1="9" x2="9" y2="15" />
                <line x1="9" y1="9" x2="15" y2="15" />
              </svg>
            </div>

            <!-- Confirm Icon -->
            <div v-else-if="modalConfig.type === 'confirm'" class="modal-badge-circle" :class="modalConfig.danger ? 'badge-danger' : 'badge-confirm'">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>

            <!-- Info Icon -->
            <div v-else class="modal-badge-circle badge-info">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="16" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12.01" y2="8"/>
              </svg>
            </div>
          </div>

          <!-- Body Content -->
          <div class="modal-content-group">
            <h2 class="modal-title">{{ modalConfig.title }}</h2>
            <p class="modal-message">{{ modalConfig.message }}</p>

            <!-- Optional Technical Details Block -->
            <div v-if="modalConfig.detail" class="detail-box">
              <span class="detail-label">Detail Teknis:</span>
              <pre class="detail-code">{{ modalConfig.detail }}</pre>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="modal-actions-row">
            <button
              v-if="modalConfig.type === 'confirm' || modalConfig.cancelText"
              class="btn btn-secondary btn-cancel"
              @click="handleCancel"
            >
              {{ modalConfig.cancelText || 'Batal' }}
            </button>

            <button
              :class="[
                'btn',
                modalConfig.danger ? 'btn-danger' : 'btn-primary',
                'btn-confirm'
              ]"
              @click="handleConfirm"
            >
              {{ modalConfig.confirmText || 'Lanjutkan' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(5, 6, 10, 0.75);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999;
  padding: 20px;
}

.modal-card {
  position: relative;
  width: 100%;
  max-width: 460px;
  background: rgba(18, 19, 28, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 32px 28px 24px 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  box-shadow: 0 24px 60px -12px rgba(0, 0, 0, 0.8), 0 0 40px rgba(99, 102, 241, 0.15);
  transform: translateY(0);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-close-modal {
  position: absolute;
  top: 18px;
  right: 18px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.btn-close-modal:hover {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-primary);
}

/* Badge circles */
.modal-icon-row {
  margin-bottom: 18px;
}

.modal-badge-circle {
  width: 60px;
  height: 60px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.4);
}

.badge-warning {
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.35);
  color: #FBBF24;
  box-shadow: 0 0 28px rgba(245, 158, 11, 0.25);
}

.badge-error {
  background: rgba(244, 63, 94, 0.15);
  border: 1px solid rgba(244, 63, 94, 0.35);
  color: #FB7185;
  box-shadow: 0 0 28px rgba(244, 63, 94, 0.25);
}

.badge-danger {
  background: rgba(244, 63, 94, 0.15);
  border: 1px solid rgba(244, 63, 94, 0.35);
  color: #FB7185;
  box-shadow: 0 0 28px rgba(244, 63, 94, 0.25);
}

.badge-confirm {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.35);
  color: #818CF8;
  box-shadow: 0 0 28px rgba(99, 102, 241, 0.25);
}

.badge-info {
  background: rgba(6, 182, 212, 0.15);
  border: 1px solid rgba(6, 182, 212, 0.35);
  color: #38BDF8;
}

/* Content */
.modal-content-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.modal-title {
  font-family: var(--font-heading);
  font-size: 19px;
  font-weight: 700;
  color: #FFFFFF;
  letter-spacing: -0.3px;
}

.modal-message {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.55;
  max-width: 380px;
  margin: 0 auto;
}

.detail-box {
  margin-top: 14px;
  background: rgba(10, 11, 16, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 10px 14px;
  text-align: left;
  max-height: 120px;
  overflow-y: auto;
}

.detail-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-code {
  font-family: monospace;
  font-size: 12px;
  color: #FB7185;
  white-space: pre-wrap;
  word-break: break-all;
  margin-top: 4px;
}

/* Actions */
.modal-actions-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
  width: 100%;
}

.btn-cancel {
  flex: 1;
  padding: 11px 18px;
}

.btn-confirm {
  flex: 1;
  padding: 11px 18px;
}

/* Transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-active .modal-card,
.modal-fade-leave-active .modal-card {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .modal-card {
  opacity: 0;
  transform: scale(0.92) translateY(12px);
}

.modal-fade-leave-to .modal-card {
  opacity: 0;
  transform: scale(0.95);
}
</style>
