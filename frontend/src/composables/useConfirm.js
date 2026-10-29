import { ref } from 'vue';

const state = ref({
  isOpen: false,
  title: 'Xác nhận hành động',
  message: '',
  detail: '',
  confirmText: 'Xác nhận',
  cancelText: 'Hủy bỏ',
  type: 'danger', // 'danger' | 'warning' | 'info'
  resolve: null
});

export function useConfirm() {
  function confirm({
    title = 'Xác nhận hành động',
    message = '',
    detail = '',
    confirmText = 'Xác nhận',
    cancelText = 'Hủy bỏ',
    type = 'danger'
  } = {}) {
    return new Promise((resolve) => {
      state.value = {
        isOpen: true,
        title,
        message,
        detail,
        confirmText,
        cancelText,
        type,
        resolve
      };
    });
  }

  function handleConfirm() {
    if (state.value.resolve) {
      state.value.resolve(true);
    }
    state.value.isOpen = false;
  }

  function handleCancel() {
    if (state.value.resolve) {
      state.value.resolve(false);
    }
    state.value.isOpen = false;
  }

  return {
    state,
    confirm,
    handleConfirm,
    handleCancel
  };
}
