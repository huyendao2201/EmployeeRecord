<template>
  <div class="toast-viewport" aria-live="polite" aria-atomic="true">
    <!-- Nút xóa tất cả nếu có nhiều hơn 2 thông báo -->
    <transition name="fade">
      <div v-if="toasts.length > 2" class="toast-actions-bar">
        <button @click="clearAll" class="btn-clear-all" title="Xóa tất cả thông báo">
          <span>Xóa tất cả ({{ toasts.length }})</span>
        </button>
      </div>
    </transition>

    <transition-group name="toast-list" tag="div" class="toast-stack">
      <div
        v-for="item in toasts"
        :key="item.id"
        class="toast-item"
        :class="'toast-' + item.type"
        role="alert"
        @mouseenter="pauseToast(item.id)"
        @mouseleave="resumeToast(item.id)"
      >
        <!-- Icon nhận diện theo loại -->
        <div class="toast-icon-wrap">
          <CheckCircle2 v-if="item.type === 'success'" class="w-5 h-5 text-emerald" />
          <AlertCircle v-else-if="item.type === 'error'" class="w-5 h-5 text-crimson" />
          <AlertTriangle v-else-if="item.type === 'warning'" class="w-5 h-5 text-amber" />
          <Info v-else class="w-5 h-5 text-primary" />
        </div>

        <!-- Nội dung thông báo -->
        <div class="toast-body">
          <div class="toast-title-row">
            <h4 class="toast-title">{{ item.title }}</h4>
            <span class="toast-type-pill">{{ getTypeLabel(item.type) }}</span>
          </div>
          <p class="toast-message">{{ item.message }}</p>
        </div>

        <!-- Nút đóng thủ công -->
        <button
          @click="removeToast(item.id)"
          class="toast-close-btn"
          aria-label="Đóng thông báo"
          title="Đóng"
        >
          <X class="w-4 h-4" />
        </button>

        <!-- Thanh đếm ngược tiến trình (Progress Bar) -->
        <div
          v-if="item.duration > 0"
          class="toast-progress-bar"
          :class="{ paused: item.paused }"
          :style="{
            animationDuration: item.duration + 'ms',
            animationPlayState: item.paused ? 'paused' : 'running'
          }"
        ></div>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useToast } from '../composables/useToast';
import {
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Info,
  X
} from '@lucide/vue';

const {
  toasts,
  removeToast,
  pauseToast,
  resumeToast,
  clearAll
} = useToast();

function getTypeLabel(type) {
  switch (type) {
    case 'success': return 'Thành công';
    case 'error': return 'Lỗi';
    case 'warning': return 'Cảnh báo';
    case 'info': return 'Hệ thống';
    default: return 'Thông báo';
  }
}
</script>

<style scoped>
.toast-viewport {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 99999;
  width: 100%;
  max-width: 420px;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toast-actions-bar {
  display: flex;
  justify-content: flex-end;
  pointer-events: auto;
  margin-bottom: 2px;
}

.btn-clear-all {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid var(--border-light);
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: var(--transition-fast);
}

.btn-clear-all:hover {
  background: #ffffff;
  color: var(--accent-crimson);
  border-color: rgba(244, 63, 94, 0.3);
  transform: translateY(-1px);
}

.toast-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toast-item {
  pointer-events: auto;
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px 18px 18px 16px;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: var(--radius-md);
  box-shadow: 0 10px 30px -4px rgba(15, 23, 42, 0.12),
              0 4px 12px -2px rgba(15, 23, 42, 0.06);
  overflow: hidden;
  border: 1px solid transparent;
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1),
              box-shadow 0.25s ease,
              border-color 0.25s ease;
}

.toast-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 36px -4px rgba(15, 23, 42, 0.16),
              0 6px 16px -2px rgba(15, 23, 42, 0.08);
}

/* Biến thể theo loại */
.toast-success {
  border-color: rgba(34, 197, 94, 0.28);
  border-left: 4px solid var(--secondary);
}

.toast-error {
  border-color: rgba(244, 63, 94, 0.28);
  border-left: 4px solid var(--accent-crimson);
}

.toast-warning {
  border-color: rgba(245, 158, 11, 0.28);
  border-left: 4px solid var(--accent-amber);
}

.toast-info {
  border-color: rgba(91, 99, 211, 0.28);
  border-left: 4px solid var(--primary);
}

/* Icon wrap */
.toast-icon-wrap {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
}

.toast-success .toast-icon-wrap {
  background: rgba(34, 197, 94, 0.12);
}

.toast-error .toast-icon-wrap {
  background: rgba(244, 63, 94, 0.12);
}

.toast-warning .toast-icon-wrap {
  background: rgba(245, 158, 11, 0.12);
}

.toast-info .toast-icon-wrap {
  background: rgba(91, 99, 211, 0.12);
}

.text-emerald {
  color: #16a34a;
}

.text-crimson {
  color: #e11d48;
}

.text-amber {
  color: #d97706;
}

.text-primary {
  color: var(--primary);
}

/* Body */
.toast-body {
  flex: 1;
  min-width: 0;
}

.toast-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.toast-title {
  font-family: var(--font-heading);
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.3;
  margin: 0;
}

.toast-type-pill {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.toast-success .toast-type-pill {
  background: rgba(34, 197, 94, 0.14);
  color: #15803d;
}

.toast-error .toast-type-pill {
  background: rgba(244, 63, 94, 0.14);
  color: #be123c;
}

.toast-warning .toast-type-pill {
  background: rgba(245, 158, 11, 0.14);
  color: #b45309;
}

.toast-info .toast-type-pill {
  background: rgba(91, 99, 211, 0.14);
  color: var(--primary-dark);
}

.toast-message {
  font-family: var(--font-sans);
  font-size: 0.88rem;
  line-height: 1.45;
  color: #334155;
  margin: 0;
  word-break: break-word;
}

/* Nút close */
.toast-close-btn {
  flex-shrink: 0;
  background: transparent;
  border: none;
  color: var(--text-dim);
  width: 28px;
  height: 28px;
  border-radius: var(--radius-xs);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition-fast);
  margin-top: -2px;
  margin-right: -4px;
}

.toast-close-btn:hover {
  background: rgba(15, 23, 42, 0.06);
  color: var(--text);
}

/* Progress bar */
.toast-progress-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  width: 100%;
  transform-origin: left;
  animation: toast-timer linear forwards;
}

.toast-success .toast-progress-bar {
  background: #22c55e;
}

.toast-error .toast-progress-bar {
  background: #f43f5e;
}

.toast-warning .toast-progress-bar {
  background: #f59e0b;
}

.toast-info .toast-progress-bar {
  background: var(--primary);
}

@keyframes toast-timer {
  from {
    transform: scaleX(1);
  }
  to {
    transform: scaleX(0);
  }
}

/* Vue Transitions */
.toast-list-enter-active {
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-list-leave-active {
  transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  position: absolute;
  width: 100%;
}

.toast-list-enter-from {
  opacity: 0;
  transform: translateX(100px) scale(0.92);
}

.toast-list-leave-to {
  opacity: 0;
  transform: translateX(80px) scale(0.9);
}

.toast-list-move {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile responsive */
@media (max-width: 640px) {
  .toast-viewport {
    top: 14px;
    right: 14px;
    left: 14px;
    max-width: calc(100% - 28px);
  }
}
</style>
