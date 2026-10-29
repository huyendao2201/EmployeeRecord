import { createRouter, createWebHistory } from 'vue-router';
import { api } from '../api';

import DashboardView from '../components/DashboardView.vue';
import ProfileView from '../components/ProfileView.vue';
import ContractsView from '../components/ContractsView.vue';
import SecurityExploitLab from '../components/SecurityExploitLab.vue';
import AuditLogView from '../components/AuditLogView.vue';
import LoginView from '../components/LoginView.vue';

const routes = [
  {
    path: '/',
    redirect: () => {
      return api.token ? '/dashboard' : '/login';
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { title: 'Đăng nhập — SecureHR', guestOnly: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { title: 'Tổng quan — SecureHR', requiresAuth: true }
  },
  {
    path: '/profile/:id?',
    alias: ['/employees/:id?'],
    name: 'Profile',
    component: ProfileView,
    meta: { title: 'Hồ sơ Nhân viên — SecureHR', requiresAuth: true }
  },
  {
    path: '/contracts/:id?',
    name: 'Contracts',
    component: ContractsView,
    meta: { title: 'Hợp đồng Lao động — SecureHR', requiresAuth: true }
  },
  {
    path: '/exploit',
    alias: '/security',
    redirect: '/dashboard'
  },
  {
    path: '/audit/:id?',
    alias: ['/audit-logs/:id?'],
    name: 'AuditLogs',
    component: AuditLogView,
    meta: { title: 'Nhật ký Hệ thống — SecureHR', requiresAuth: true, roles: ['ADMIN', 'HR'] }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  }
});

router.beforeEach((to, from, next) => {
  const hasToken = !!api.token;

  if (to.meta.title) {
    document.title = to.meta.title;
  }

  if (to.meta.requiresAuth && !hasToken) {
    next({ path: '/login', query: { redirect: to.fullPath } });
  } else if (to.meta.guestOnly && hasToken) {
    next('/dashboard');
  } else if (to.meta.roles && hasToken) {
    const userRole = api.user?.role;
    if (userRole && !to.meta.roles.includes(userRole)) {
      next('/dashboard');
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
