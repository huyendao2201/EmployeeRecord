import { ref, reactive } from 'vue';

const toasts = ref([]);
let toastIdCounter = 0;

/**
 * Toast item interface:
 * {
 *   id: number,
 *   type: 'success' | 'error' | 'warning' | 'info',
 *   title: string,
 *   message: string,
 *   duration: number, // ms, 0 means persistent
 *   createdAt: number,
 *   timer: any,
 *   paused: boolean,
 *   remainingTime: number,
 *   startTime: number
 * }
 */

export function useToast() {
  function addToast({
    type = 'info',
    title = '',
    message = '',
    duration = 4000
  }) {
    const id = ++toastIdCounter;
    
    // Default titles based on type
    const defaultTitles = {
      success: 'Thành công',
      error: 'Đã xảy ra lỗi',
      warning: 'Cảnh báo',
      info: 'Thông báo'
    };

    const finalTitle = title || defaultTitles[type] || 'Thông báo';

    const toast = reactive({
      id,
      type,
      title: finalTitle,
      message,
      duration,
      createdAt: Date.now(),
      startTime: Date.now(),
      remainingTime: duration,
      paused: false,
      timer: null
    });

    if (duration > 0) {
      toast.timer = setTimeout(() => {
        removeToast(id);
      }, duration);
    }

    toasts.value.unshift(toast); // Newest at top

    // Keep max 6 toasts visible to avoid cluttering
    if (toasts.value.length > 6) {
      const removed = toasts.value.pop();
      if (removed?.timer) clearTimeout(removed.timer);
    }

    return id;
  }

  function removeToast(id) {
    const index = toasts.value.findIndex(t => t.id === id);
    if (index !== -1) {
      const toast = toasts.value[index];
      if (toast.timer) clearTimeout(toast.timer);
      toasts.value.splice(index, 1);
    }
  }

  function pauseToast(id) {
    const toast = toasts.value.find(t => t.id === id);
    if (toast && toast.duration > 0 && !toast.paused) {
      clearTimeout(toast.timer);
      toast.paused = true;
      const elapsed = Date.now() - toast.startTime;
      toast.remainingTime = Math.max(0, toast.remainingTime - elapsed);
    }
  }

  function resumeToast(id) {
    const toast = toasts.value.find(t => t.id === id);
    if (toast && toast.duration > 0 && toast.paused) {
      toast.paused = false;
      toast.startTime = Date.now();
      toast.timer = setTimeout(() => {
        removeToast(id);
      }, toast.remainingTime);
    }
  }

  function clearAll() {
    toasts.value.forEach(t => {
      if (t.timer) clearTimeout(t.timer);
    });
    toasts.value = [];
  }

  // Shorthand helpers
  const success = (message, title = '', duration = 4000) => 
    addToast({ type: 'success', title, message, duration });

  const error = (message, title = '', duration = 5000) => 
    addToast({ type: 'error', title, message, duration });

  const warning = (message, title = '', duration = 4500) => 
    addToast({ type: 'warning', title, message, duration });

  const info = (message, title = '', duration = 3800) => 
    addToast({ type: 'info', title, message, duration });

  return {
    toasts,
    addToast,
    removeToast,
    pauseToast,
    resumeToast,
    clearAll,
    success,
    error,
    warning,
    info
  };
}
