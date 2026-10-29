<template>
  <div class="app-layout">
    <!-- Hệ thống Flash Message (Toasts) và Hộp thoại Xác nhận (Confirm Modal) toàn cục -->
    <FlashMessageContainer />
    <ConfirmModal />

    <!-- 1. Khi ở trang Login (hoặc chưa đăng nhập) -->
    <router-view
      v-if="isLoginPage || !currentUser"
      :currentUser="currentUser"
      @login-success="onLoginSuccess"
    />

    <!-- 2. Khi ĐÃ đăng nhập thành công: Hiển thị Không gian làm việc đầy đủ với URL theo từng trang -->
    <template v-else>
      <!-- Frosted Glass Navbar -->
      <header class="top-navbar">
        <div class="nav-container">
          <div class="nav-brand">
            <div class="brand-badge-icon">
              <Shield class="w-5 h-5 text-white" />
            </div>
            <div class="brand-info">
              <div class="brand-title-row">
                <h1>SecureHR</h1>
              </div>
              <span class="sub-brand">Hệ thống Quản lý Nhân sự</span>
            </div>
          </div>

          <div class="nav-right">
            <!-- Logged User Profile -->
            <div class="user-chip-panel">
              <div class="avatar-glow">
                {{ currentUser.first_name?.charAt(0) || currentUser.username.charAt(0).toUpperCase() }}
              </div>
              <div class="user-meta">
                <span class="user-name">{{ currentUser.first_name || currentUser.username }}</span>
                <span class="role-tag" :class="'role-' + currentUser.role.toLowerCase()">
                  {{ currentUser.role_display }}
                </span>
              </div>
            </div>

            <button @click="handleLogout" class="btn-logout-sleek" title="Đăng xuất">
              <LogOut class="w-4 h-4 mr-1.5" />
              <span>Đăng xuất</span>
            </button>
          </div>
        </div>
      </header>

      <!-- Modern Segmented Tab Bar có URL riêng cho từng trang -->
      <nav class="tabs-nav-bar">
        <div class="tabs-container">
          <router-link
            to="/dashboard"
            class="tab-pill"
            :class="{ active: currentTab === 'dashboard' }"
          >
            <LayoutDashboard class="w-4 h-4 mr-2" />
            <span>Tổng quan</span>
          </router-link>

          <router-link
            :to="profileNavPath"
            class="tab-pill"
            :class="{ active: currentTab === 'profile' }"
          >
            <User class="w-4 h-4 mr-2" />
            <span>{{ isStaffRole ? 'Hồ sơ Nhân viên' : 'Hồ sơ Cá nhân' }}</span>
          </router-link>

          <router-link
            to="/contracts"
            class="tab-pill"
            :class="{ active: currentTab === 'contracts' }"
          >
            <FileText class="w-4 h-4 mr-2" />
            <span>Hợp đồng Lao động</span>
          </router-link>

          <!-- Tab Kiểm định An ninh (Tạm thời ẩn theo yêu cầu) -->
          <!--
          <router-link
            to="/exploit"
            class="tab-pill"
            :class="{ active: currentTab === 'exploit' }"
          >
            <ShieldCheck class="w-4 h-4 mr-2 text-primary" />
            <span>Kiểm định An ninh</span>
          </router-link>
          -->

          <router-link
            v-if="isAdminOrHR"
            to="/audit"
            class="tab-pill"
            :class="{ active: currentTab === 'audit' }"
          >
            <Activity class="w-4 h-4 mr-2" />
            <span>Nhật ký Hệ thống</span>
          </router-link>
        </div>
      </nav>

      <!-- Main Body Content tải view theo URL tương ứng -->
      <main class="main-body animate-fade-in">
        <router-view
          v-slot="{ Component }"
        >
          <component
            :is="Component"
            :currentUser="currentUser"
            @event-triggered="onSecurityEventTriggered"
            @profile-updated="onProfileUpdated"
            @open-exploit-lab="router.push('/exploit')"
            @nav-to="(tab) => router.push('/' + tab)"
          />
        </router-view>
      </main>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { api } from './api';
import {
  Shield,
  ShieldCheck,
  LogOut,
  User,
  FileText,
  Activity,
  LayoutDashboard
} from '@lucide/vue';

import FlashMessageContainer from './components/FlashMessageContainer.vue';
import ConfirmModal from './components/ConfirmModal.vue';
import { useToast } from './composables/useToast';
import { useConfirm } from './composables/useConfirm';

const route = useRoute();
const router = useRouter();
const toast = useToast();
const { confirm } = useConfirm();

// Khởi tạo thông tin người dùng từ localStorage để giao diện tải mượt mà không bị giật
const currentUser = ref(api.user);

const isLoginPage = computed(() => {
  return route.name === 'Login' || route.path === '/login';
});

const currentTab = computed(() => {
  const p = route.path;
  if (p.startsWith('/profile') || p.startsWith('/employees')) return 'profile';
  if (p.startsWith('/contracts')) return 'contracts';
  if (p.startsWith('/exploit') || p.startsWith('/security')) return 'exploit';
  if (p.startsWith('/audit')) return 'audit';
  return 'dashboard';
});

const isStaffRole = computed(() => {
  return ['ADMIN', 'HR', 'ACCOUNTANT'].includes(currentUser.value?.role);
});

const isAdminOrHR = computed(() => {
  return ['ADMIN', 'HR'].includes(currentUser.value?.role);
});

const profileNavPath = computed(() => {
  if (isStaffRole.value) {
    return '/profile';
  }
  if (currentUser.value?.profile_id) {
    return `/profile/${currentUser.value.profile_id}`;
  }
  return '/profile';
});

async function checkAuth() {
  if (api.token) {
    try {
      const me = await api.getMe();
      currentUser.value = me;
    } catch (e) {
      api.clearAuth();
      currentUser.value = null;
      toast.warning('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.', 'Phiên làm việc');
      router.push('/login');
    }
  } else {
    currentUser.value = null;
    if (!isLoginPage.value) {
      router.push({ path: '/login', query: { redirect: route.fullPath } });
    }
  }
}

function onLoginSuccess(user) {
  currentUser.value = user;
  toast.success(`Chào mừng ${user.first_name || user.username} (${user.role_display}) đăng nhập thành công!`, 'Đăng nhập thành công');
  const redirect = route.query.redirect || '/dashboard';
  router.push(redirect);
}

async function handleLogout() {
  const confirmed = await confirm({
    title: 'Đăng xuất tài khoản',
    message: 'Bạn có chắc chắn muốn kết thúc phiên làm việc hiện tại không?',
    confirmText: 'Đăng xuất',
    cancelText: 'Ở lại',
    type: 'warning'
  });
  if (!confirmed) return;

  const name = currentUser.value?.first_name || currentUser.value?.username || '';
  api.clearAuth();
  currentUser.value = null;
  toast.info(`Tài khoản ${name} đã đăng xuất an toàn khỏi hệ thống.`, 'Đã đăng xuất');
  router.push('/login');
}

function onSecurityEventTriggered() {
  // Sự kiện an ninh đã kích hoạt
}

function onProfileUpdated() {
  // Cập nhật hồ sơ thành công
}

onMounted(() => {
  checkAuth();
});
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}

/* Top Navbar */
.top-navbar {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-light);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.nav-container {
  max-width: 1480px;
  margin: 0 auto;
  padding: 14px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-badge-icon {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-primary);
}

.brand-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-title-row h1 {
  font-size: 1.45rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  background: var(--gradient-text);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.version-chip {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  font-weight: 700;
  background: var(--primary-light);
  color: var(--primary);
  border: 1px solid var(--primary-light-border);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  letter-spacing: 0.05em;
}

.sub-brand {
  font-size: 0.78rem;
  color: var(--text-muted);
  display: block;
  font-weight: 500;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 14px;
}

.telemetry-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--secondary-light);
  border: 1px solid rgba(34, 197, 94, 0.2);
  padding: 6px 14px;
  border-radius: var(--radius-full);
}

.telemetry-pulse {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  background: var(--secondary);
  box-shadow: 0 0 10px rgba(34, 197, 94, 0.5);
  animation: pulseGlow 1.8s infinite;
}

@keyframes pulseGlow {
  0% { transform: scale(0.95); opacity: 0.7; }
  50% { transform: scale(1.15); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.7; }
}

.telemetry-text {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 700;
  color: #15803d;
  letter-spacing: 0.04em;
}

.user-chip-panel {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #ffffff;
  border: 1px solid var(--border);
  padding: 4px 14px 4px 6px;
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-sm);
}

.avatar-glow {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: var(--gradient-primary);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  box-shadow: 0 2px 8px rgba(91, 99, 211, 0.3);
}

.user-meta {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--text);
  line-height: 1.1;
}

.role-tag {
  font-family: var(--font-mono);
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
}

.role-admin { color: #e11d48; }
.role-registrar { color: #5b63d3; }
.role-teacher { color: #d97706; }
.role-student { color: #16a34a; }

.btn-logout-sleek {
  display: inline-flex;
  align-items: center;
  color: var(--text-muted);
  font-size: 0.82rem;
  font-weight: 600;
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  background: #ffffff;
  border: 1px solid var(--border);
  transition: var(--transition-fast);
  cursor: pointer;
}

.btn-logout-sleek:hover {
  background: var(--accent-crimson-light);
  color: var(--accent-crimson);
  border-color: rgba(244, 63, 94, 0.3);
}

/* Tabs Navigation */
.tabs-nav-bar {
  background: #ffffff;
  border-bottom: 1px solid var(--border);
  padding: 6px 28px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.tabs-container {
  max-width: 1480px;
  margin: 0 auto;
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 4px 0;
}

.tab-pill {
  display: inline-flex;
  align-items: center;
  padding: 10px 20px;
  border-radius: var(--radius-md);
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-muted);
  text-decoration: none;
  background: transparent;
  border: 1px solid transparent;
  cursor: pointer;
  transition: var(--transition-normal);
  white-space: nowrap;
}

.tab-pill:hover {
  color: var(--primary);
  background: var(--surface-hover);
}

.tab-pill.active {
  color: var(--primary);
  background: var(--primary-light);
  border-color: var(--primary-light-border);
  box-shadow: var(--shadow-sm);
}

.tab-pill-exploit {
  position: relative;
}

.tab-pill-exploit.active {
  color: var(--accent-crimson);
  background: var(--accent-crimson-light);
  border-color: rgba(244, 63, 94, 0.25);
}

.hot-badge {
  font-family: var(--font-mono);
  font-size: 0.62rem;
  font-weight: 700;
  background: var(--accent-crimson);
  color: #ffffff;
  padding: 2px 6px;
  border-radius: var(--radius-full);
  margin-left: 8px;
  text-transform: uppercase;
}

/* Main Body */
.main-body {
  flex: 1;
  padding-bottom: 60px;
}

@media (max-width: 900px) {
  .nav-container {
    flex-direction: column;
    align-items: flex-start;
  }
  .nav-right {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
