<template>
  <transition name="modal-fade">
    <div
      v-if="state.isOpen"
      class="confirm-modal-overlay"
      @click.self="handleCancel"
      @keydown.esc="handleCancel"
      tabindex="-1"
    >
      <div class="confirm-modal-card card-uupm" role="dialog" aria-modal="true">
        <!-- Icon nhận diện -->
        <div class="confirm-icon-box" :class="'icon-' + state.type">
          <Trash2 v-if="state.type === 'danger'" class="w-6 h-6 text-crimson" />
          <AlertTriangle v-else-if="state.type === 'warning'" class="w-6 h-6 text-amber" />
          <HelpCircle v-else class="w-6 h-6 text-primary" />
        </div>

        <!-- Nội dung chính -->
        <div class="confirm-content">
          <h3 class="confirm-title">{{ state.title }}</h3>
          <p class="confirm-message">{{ state.message }}</p>

          <div v-if="state.detail" class="confirm-detail-box">
            <ShieldAlert class="w-4 h-4 mr-2 flex-shrink-0 text-amber" />
            <span>{{ state.detail }}</span>
          </div>
        </div>

        <!-- Nút thao tác -->
        <div class="confirm-actions">
          <button
            type="button"
            @click="handleCancel"
            class="btn-cancel"
          >
            {{ state.cancelText || 'Hủy bỏ' }}
          </button>
          
          <button
            type="button"
            @click="handleConfirm"
            class="btn-confirm"
            :class="'btn-confirm-' + state.type"
          >
            <Trash2 v-if="state.type === 'danger'" class="w-4 h-4 mr-1.5" />
            <span>{{ state.confirmText || 'Xác nhận' }}</span>
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';
import { useConfirm } from '../composables/useConfirm';
import {
  Trash2,
  AlertTriangle,
  HelpCircle,
  ShieldAlert
} from '@lucide/vue';

const { state, handleConfirm, handleCancel } = useConfirm();

function handleKeydown(e) {
  if (!state.value.isOpen) return;
  if (e.key === 'Escape') {
    handleCancel();
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
});
</script>

<style scoped>
.confirm-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 99998;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.confirm-modal-card {
  width: 100%;
  max-width: 460px;
  background: #ffffff;
  border-radius: var(--radius-lg);
  padding: 28px;
  box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.25),
              0 0 0 1px rgba(15, 23, 42, 0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transform-origin: center;
}

.confirm-icon-box {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 18px;
  animation: pulse-subtle 2s infinite ease-in-out;
}

.icon-danger {
  background: rgba(244, 63, 94, 0.12);
  border: 1px solid rgba(244, 63, 94, 0.25);
}

.icon-warning {
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.icon-info {
  background: rgba(91, 99, 211, 0.12);
  border: 1px solid rgba(91, 99, 211, 0.25);
}

.confirm-content {
  width: 100%;
  margin-bottom: 24px;
}

.confirm-title {
  font-family: var(--font-heading);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 10px;
}

.confirm-message {
  font-family: var(--font-sans);
  font-size: 0.95rem;
  color: var(--text-muted);
  line-height: 1.55;
  margin-bottom: 14px;
}

.confirm-detail-box {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  text-align: left;
  background: #fffbeb;
  border: 1px solid #fef3c7;
  border-radius: var(--radius-sm);
  padding: 10px 14px;
  font-size: 0.84rem;
  color: #92400e;
  line-height: 1.4;
}

.confirm-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  width: 100%;
}

.btn-cancel {
  flex: 1;
  background: #f1f5f9;
  color: var(--text);
  border: 1px solid var(--border-light);
  padding: 11px 18px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.92rem;
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-cancel:hover {
  background: #e2e8f0;
  color: #0f172a;
}

.btn-confirm {
  flex: 1.2;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  padding: 11px 18px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.92rem;
  cursor: pointer;
  transition: var(--transition-normal);
  color: #ffffff;
}

.btn-confirm-danger {
  background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
  box-shadow: 0 4px 14px rgba(244, 63, 94, 0.35);
}

.btn-confirm-danger:hover {
  background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
  box-shadow: 0 6px 18px rgba(244, 63, 94, 0.45);
  transform: translateY(-1px);
}

.btn-confirm-warning {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35);
}

.btn-confirm-warning:hover {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
  transform: translateY(-1px);
}

.btn-confirm-info {
  background: var(--primary);
  box-shadow: var(--shadow-primary);
}

.btn-confirm-info:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
}

@keyframes pulse-subtle {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

/* Modal transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .confirm-modal-card {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.modal-fade-leave-active .confirm-modal-card {
  transition: transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-fade-enter-from .confirm-modal-card {
  transform: scale(0.92) translateY(12px);
}

.modal-fade-leave-to .confirm-modal-card {
  transform: scale(0.95) translateY(10px);
}
</style>
