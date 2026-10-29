<template>
  <div class="login-page-wrap">
    <div class="login-card-container">
      <!-- Top Brand Header -->
      <div class="brand-header">
        <div class="brand-logo-badge">
          <Shield class="w-7 h-7 text-white" />
        </div>
        <div class="brand-title-wrap">
          <h1>SecureHR</h1>
        </div>
        <p class="brand-tagline">
          Hệ thống Quản lý Hồ sơ & Thông tin Nhân sự Doanh nghiệp
        </p>
      </div>

      <!-- Main Login Card -->
      <div class="login-card card-uupm animate-fade-in">
        <div class="card-title-row">
          <h3>Đăng nhập</h3>
          <span class="sub-label">Vui lòng nhập tài khoản để truy cập hệ thống</span>
        </div>

        <!-- Error / Lockout Banner -->
        <div v-if="errorMessage" class="error-banner" :class="{ 'lockout-alert': isLocked }">
          <AlertTriangle class="w-5 h-5 flex-shrink-0" />
          <div class="error-text">
            <strong>{{ isLocked ? 'TÀI KHOẢN TẠM KHÓA (HTTP 429)' : 'ĐĂNG NHẬP THẤT BẠI' }}</strong>
            <p>{{ errorMessage }}</p>
          </div>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-item">
            <label>TÊN ĐĂNG NHẬP</label>
            <div class="input-wrap">
              <User class="w-4 h-4 input-icon text-muted" />
              <input
                v-model="username"
                type="text"
                required
                class="input-uupm with-icon"
                placeholder="Nhập tên đăng nhập (ví dụ: nv_nam)"
              />
            </div>
          </div>

          <div class="form-item">
            <label>MẬT KHẨU</label>
            <div class="input-wrap">
              <Key class="w-4 h-4 input-icon text-muted" />
              <input
                v-model="password"
                type="password"
                required
                class="input-uupm with-icon"
                placeholder="Nhập mật khẩu"
              />
            </div>
          </div>

          <button type="submit" :disabled="loading" class="btn-primary btn-submit-full">
            <RefreshCw v-if="loading" class="w-4 h-4 mr-2 spin" />
            <Lock v-else class="w-4 h-4 mr-2" />
            {{ loading ? 'Đang xác thực...' : 'Đăng nhập' }}
          </button>
        </form>

        <!-- Subtle Demo Account Switcher (Minimalist & Professional) -->
        <div class="demo-accounts-bar">
          <span class="demo-accounts-label">Tài khoản demo:</span>
          <div class="demo-chips">
            <button
              type="button"
              @click="fillForm('nv_nam', 'Employee@123')"
              class="demo-chip"
              :class="{ 'chip-active': username === 'nv_nam' }"
            >
              Nhân viên Nam
            </button>
            <button
              type="button"
              @click="fillForm('hr_linh', 'Hr@123')"
              class="demo-chip"
              :class="{ 'chip-active': username === 'hr_linh' }"
            >
              HR Linh
            </button>
            <button
              type="button"
              @click="fillForm('ketoan_hoa', 'Ketoan@123')"
              class="demo-chip"
              :class="{ 'chip-active': username === 'ketoan_hoa' }"
            >
              Kế toán Hoa
            </button>
            <button
              type="button"
              @click="fillForm('admin', 'Admin@123')"
              class="demo-chip"
              :class="{ 'chip-active': username === 'admin' }"
            >
              Admin
            </button>
          </div>
        </div>
      </div>

      <!-- Footer Info -->
      <footer class="login-footer">
        <span>© 2024 SecureHR Management System • Phiên bản 2.1</span>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { api } from '../api';
import {
  Shield,
  Lock,
  User,
  Key,
  AlertTriangle,
  RefreshCw
} from '@lucide/vue';
import { useToast } from '../composables/useToast';

const toast = useToast();

const emit = defineEmits(['login-success']);

const username = ref('nv_nam');
const password = ref('Employee@123');
const loading = ref(false);
const errorMessage = ref('');
const isLocked = ref(false);

function fillForm(u, p) {
  username.value = u;
  password.value = p;
  errorMessage.value = '';
  isLocked.value = false;
  toast.info(`Đã điền thông tin tài khoản: ${u}`, 'Tài khoản mẫu');
}

async function handleLogin() {
  loading.value = true;
  errorMessage.value = '';
  isLocked.value = false;

  try {
    const res = await api.login(username.value, password.value);
    emit('login-success', res.user);
  } catch (err) {
    const msg = err.data?.error || err.data?.detail || err.message;
    errorMessage.value = msg;
    if (err.data?.is_locked || err.status === 429) {
      isLocked.value = true;
      toast.error(msg || 'Tài khoản đã bị tạm khóa 5 phút do vượt quá giới hạn thử sai!', 'Bảo vệ Brute-Force');
    } else {
      toast.error(msg || 'Tên đăng nhập hoặc mật khẩu không chính xác', 'Đăng nhập thất bại');
    }
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  padding: 40px 20px;
}

.login-card-container {
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.brand-header {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.brand-logo-badge {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(91, 99, 211, 0.28);
  margin-bottom: 4px;
}

.brand-title-wrap h1 {
  font-size: 1.85rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.025em;
}

.brand-tagline {
  font-size: 0.88rem;
  color: var(--text-muted);
  max-width: 360px;
  line-height: 1.5;
}

/* Login Card */
.login-card {
  width: 100%;
  background: #ffffff;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 36px 32px;
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.05), 0 2px 6px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-title-row h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text);
}

.sub-label {
  font-size: 0.82rem;
  color: var(--text-muted);
  display: block;
  margin-top: 4px;
}

.error-banner {
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: #e11d48;
  font-size: 0.84rem;
}

.error-text strong {
  display: block;
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  margin-bottom: 2px;
}

.error-text p {
  line-height: 1.45;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-item label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.02em;
}

.input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  pointer-events: none;
}

.input-uupm.with-icon {
  padding-left: 38px;
}

.input-uupm {
  width: 100%;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 11px 14px;
  color: var(--text);
  font-size: 0.92rem;
  transition: var(--transition-fast);
}

.input-uupm:focus {
  border-color: var(--primary);
  outline: none;
  box-shadow: 0 0 0 3px rgba(91, 99, 211, 0.12);
}

.btn-submit-full {
  width: 100%;
  padding: 12px 18px;
  font-size: 0.92rem;
  font-weight: 600;
  margin-top: 4px;
}

/* Discreet Demo Switcher */
.demo-accounts-bar {
  padding-top: 14px;
  border-top: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.demo-accounts-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.demo-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.demo-chip {
  padding: 5px 10px;
  border-radius: var(--radius-xs);
  border: 1px solid var(--border);
  background: #ffffff;
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition-fast);
}

.demo-chip:hover {
  background: #f1f5f9;
  color: var(--text);
  border-color: #cbd5e1;
}

.demo-chip.chip-active {
  background: var(--primary-light);
  color: var(--primary);
  border-color: rgba(91, 99, 211, 0.3);
  font-weight: 600;
}

/* Footer */
.login-footer {
  font-size: 0.78rem;
  color: var(--text-dim);
  text-align: center;
}
</style>
