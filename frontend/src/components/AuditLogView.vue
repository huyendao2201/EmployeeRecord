<template>
  <div class="audit-wrap">
    <!-- Header -->
    <div class="audit-header card-uupm">
      <div class="header-left">
        <div class="header-icon-box">
          <Activity class="w-6 h-6 text-primary" />
        </div>
        <div>
          <h2>Nhật ký Kiểm toán & Giám sát An ninh (Audit Logs Console)</h2>
          <p class="subtitle">
            Hệ thống giám sát nội bộ ghi vết thời gian thực mọi hành vi truy cập và cảnh báo an ninh.
          </p>
        </div>
      </div>
      <div class="header-actions">
        <button @click="fetchLogs(true)" :disabled="loading" class="btn-secondary">
          <RefreshCw class="w-4 h-4 mr-2" :class="{ spin: loading }" />
          <span>Làm mới Nhật ký</span>
        </button>
      </div>
    </div>


    <!-- Filter Pills Bar -->
    <div class="filters-bar">
      <div class="filter-pills">
        <button
          v-for="tab in filterTabs"
          :key="tab.value"
          @click="activeFilter = tab.value"
          class="filter-pill"
          :class="{
            active: activeFilter === tab.value,
            'pill-alert': tab.alert && countAlerts(tab.value) > 0
          }"
        >
          <span>{{ tab.label }}</span>
          <span class="count-tag font-mono">{{ countAlerts(tab.value) }}</span>
        </button>
      </div>
    </div>

    <!-- Audit Logs Table -->
    <div class="table-container card-uupm">
      <div v-if="loading && filteredLogs.length === 0" class="loading-state">
        <RefreshCw class="w-7 h-7 spin text-primary" />
        <span>Đang phân tích và truy xuất sự kiện kiểm toán...</span>
      </div>

      <div v-else-if="filteredLogs.length === 0" class="empty-state">
        <FileText class="w-10 h-10 text-muted" />
        <p>Không có sự kiện nào trong bộ lọc này.</p>
      </div>

      <div v-else class="table-responsive">
        <table class="soc-table">
          <colgroup>
            <col class="col-w-id" />
            <col class="col-w-time" />
            <col class="col-w-ip" />
            <col class="col-w-user" />
            <col class="col-w-action" />
            <col class="col-w-resource" />
            <col class="col-w-status" />
            <col class="col-w-details" />
          </colgroup>
          <thead>
            <tr>
              <th class="th-id">ID</th>
              <th class="th-time">THỜI GIAN</th>
              <th class="th-ip">IP CLIENT</th>
              <th class="th-user">TÁC TỬ (USER)</th>
              <th class="th-action">HÀNH ĐỘNG</th>
              <th class="th-resource">TÀI NGUYÊN</th>
              <th class="th-status">KẾT QUẢ</th>
              <th class="th-details">CHI TIẾT SỰ KIỆN</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="log in filteredLogs"
              :key="log.id"
              class="clickable-row"
              :class="{
                'row-idor-alert': log.action === 'IDOR_ATTEMPT',
                'row-lock-alert': log.action === 'ACCOUNT_LOCKED'
              }"
              @click="viewLogDetail(log)"
              :title="'Xem chi tiết sự kiện #' + log.id"
            >
              <td class="col-id font-mono">
                <span class="code-pill font-mono id-pill">#{{ log.id }}</span>
              </td>
              <td class="col-time font-mono">{{ formatTime(log.timestamp) }}</td>
              <td class="col-ip">
                <span class="ip-chip font-mono">{{ log.ip_address || '127.0.0.1' }}</span>
              </td>
              <td class="col-user">
                <span class="user-chip-text">{{ log.username || log.username_attempt || 'Anonymous' }}</span>
              </td>
              <td class="col-action">
                <span
                  class="action-tag"
                  :class="'act-' + log.action.toLowerCase()"
                  :title="log.action_display || log.action"
                >
                  <ShieldAlert v-if="log.action === 'IDOR_ATTEMPT'" class="w-3.5 h-3.5 mr-1 flex-shrink-0 text-crimson" />
                  <Lock v-else-if="log.action === 'ACCOUNT_LOCKED'" class="w-3.5 h-3.5 mr-1 flex-shrink-0 text-amber" />
                  <span class="action-tag-text">{{ getActionLabel(log) }}</span>
                </span>
              </td>
              <td class="col-resource">
                <span v-if="log.resource_type" class="resource-pill font-mono">
                  {{ log.resource_type }} #{{ log.resource_id }}
                </span>
                <span v-else class="text-dim">-</span>
              </td>
              <td class="col-status">
                <span class="status-badge-soc font-mono" :class="'stat-' + log.status.toLowerCase()">
                  {{ log.status_display || log.status }}
                </span>
              </td>
              <td class="col-details" :title="log.details">
                {{ log.details }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Audit Log Detail Modal -->
    <div
      v-if="selectedLog"
      class="modal-overlay animate-fade-in"
      @click.self="closeLogDetail"
    >
      <div class="modal-card detail-modal-card card-uupm">
        <div class="modal-header">
          <div class="header-icon-box">
            <Activity class="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3>Chi tiết Bản ghi Kiểm toán</h3>
            <span class="sub-label">Thông tin kiểm toán an ninh & truy vết hệ thống</span>
          </div>
          <div class="header-right-badges">
            <span class="id-badge-banner font-mono">
              <Hash class="w-3.5 h-3.5 mr-1" />
              <span>ID Sự kiện: #{{ selectedLog.id }}</span>
            </span>
            <button @click="closeLogDetail" class="btn-close-modal" title="Đóng">
              <X class="w-5 h-5" />
            </button>
          </div>
        </div>

        <div class="log-detail-body">
          <div class="detail-row-2">
            <div class="form-group-clean">
              <label>ID BẢN GHI (PRIMARY KEY)</label>
              <div class="readonly-pill-box font-mono font-bold text-primary">
                #{{ selectedLog.id }}
              </div>
            </div>
            <div class="form-group-clean">
              <label>THỜI GIAN GHI NHẬN</label>
              <div class="readonly-pill-box font-mono">
                {{ formatTime(selectedLog.timestamp) }}
              </div>
            </div>
          </div>

          <div class="detail-row-2">
            <div class="form-group-clean">
              <label>TÁC TỬ / TÀI KHOẢN (USER)</label>
              <div class="readonly-pill-box font-bold">
                {{ selectedLog.username || selectedLog.username_attempt || 'Anonymous / Khách' }}
              </div>
            </div>
            <div class="form-group-clean">
              <label>ĐỊA CHỈ IP CLIENT</label>
              <div class="readonly-pill-box font-mono">
                {{ selectedLog.ip_address || '127.0.0.1' }}
              </div>
            </div>
          </div>

          <div class="detail-row-2">
            <div class="form-group-clean">
              <label>HÀNH ĐỘNG HỆ THỐNG</label>
              <div class="readonly-pill-box font-mono">
                <span class="action-tag" :class="'act-' + selectedLog.action.toLowerCase()">
                  {{ getActionLabel(selectedLog) }}
                </span>
                <span class="text-xs text-muted ml-2">({{ selectedLog.action }})</span>
              </div>
            </div>
            <div class="form-group-clean">
              <label>KẾT QUẢ XỬ LÝ</label>
              <div>
                <span class="status-badge-soc font-mono" :class="'stat-' + (selectedLog.status || '').toLowerCase()">
                  {{ selectedLog.status_display || selectedLog.status }}
                </span>
              </div>
            </div>
          </div>

          <div class="detail-row-2">
            <div class="form-group-clean">
              <label>LOẠI TÀI NGUYÊN</label>
              <div class="readonly-pill-box font-mono">
                {{ selectedLog.resource_type || 'N/A' }}
              </div>
            </div>
            <div class="form-group-clean">
              <label>ID TÀI NGUYÊN BỊ TÁC ĐỘNG</label>
              <div class="readonly-pill-box font-mono font-bold text-primary">
                {{ selectedLog.resource_id ? '#' + selectedLog.resource_id : 'N/A' }}
              </div>
            </div>
          </div>

          <div class="form-group-clean">
            <label>CHI TIẾT NỘI DUNG SỰ KIỆN</label>
            <div class="readonly-details-box">
              {{ selectedLog.details || 'Không có mô tả bổ sung' }}
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeLogDetail" class="btn-primary">
            <span>Đóng chi tiết</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { api } from '../api';
import {
  Activity,
  RefreshCw,
  ShieldCheck,
  ShieldAlert,
  Lock,
  FileText,
  Hash,
  X
} from '@lucide/vue';
import { useToast } from '../composables/useToast';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const logs = ref([]);
const loading = ref(false);
const activeFilter = ref('ALL');
const selectedLog = ref(null);

const filterTabs = [
  { label: 'Tất cả sự kiện', value: 'ALL', alert: false },
  { label: '🚨 Cảnh báo IDOR', value: 'IDOR_ATTEMPT', alert: true },
  { label: '🔒 Khóa tài khoản', value: 'ACCOUNT_LOCKED', alert: true },
  { label: '🔑 Đăng nhập', value: 'LOGIN', alert: false },
  { label: '👤 Hồ sơ Nhân sự', value: 'PROFILE', alert: false },
  { label: '📄 Hợp đồng Lao động', value: 'CONTRACT', alert: false },
];

function viewLogDetail(log) {
  selectedLog.value = log;
  router.push(`/audit/${log.id}`);
}

function closeLogDetail() {
  selectedLog.value = null;
  router.push('/audit');
}

function syncSelectedFromRoute() {
  if (route.params.id) {
    const targetId = Number(route.params.id);
    const found = logs.value.find(l => l.id === targetId);
    if (found) {
      selectedLog.value = found;
    }
  } else {
    selectedLog.value = null;
  }
}

watch(() => route.params.id, () => {
  syncSelectedFromRoute();
});

async function fetchLogs(manual = false) {
  loading.value = true;
  try {
    const data = await api.getAuditLogs();
    logs.value = Array.isArray(data) ? data : (data.results || []);
    syncSelectedFromRoute();
    if (manual === true) {
      toast.info('Đã đồng bộ và cập nhật danh sách nhật ký kiểm toán mới nhất.', 'Nhật ký hệ thống');
    }
  } catch (err) {
    console.error('Lỗi tải audit logs:', err);
    if (manual === true) {
      toast.error('Không thể kết nối đến dịch vụ Audit Logs.', 'Lỗi tải dữ liệu');
    }
  } finally {
    loading.value = false;
  }
}

function countAlerts(filterKey) {
  if (filterKey === 'ALL') return logs.value.length;
  if (filterKey === 'IDOR_ATTEMPT') return logs.value.filter(l => l.action === 'IDOR_ATTEMPT').length;
  if (filterKey === 'ACCOUNT_LOCKED') return logs.value.filter(l => l.action === 'ACCOUNT_LOCKED').length;
  if (filterKey === 'LOGIN') return logs.value.filter(l => l.action && l.action.startsWith('LOGIN')).length;
  if (filterKey === 'PROFILE') return logs.value.filter(l => l.action && (l.action.includes('PROFILE') || l.action.includes('EMPLOYEE'))).length;
  if (filterKey === 'CONTRACT') return logs.value.filter(l => l.action && (l.action.includes('CONTRACT') || l.action.includes('SALARY'))).length;
  return 0;
}

const filteredLogs = computed(() => {
  if (activeFilter.value === 'ALL') return logs.value;
  if (activeFilter.value === 'IDOR_ATTEMPT') return logs.value.filter(l => l.action === 'IDOR_ATTEMPT');
  if (activeFilter.value === 'ACCOUNT_LOCKED') return logs.value.filter(l => l.action === 'ACCOUNT_LOCKED');
  if (activeFilter.value === 'LOGIN') return logs.value.filter(l => l.action && l.action.startsWith('LOGIN'));
  if (activeFilter.value === 'PROFILE') return logs.value.filter(l => l.action && (l.action.includes('PROFILE') || l.action.includes('EMPLOYEE')));
  if (activeFilter.value === 'CONTRACT') return logs.value.filter(l => l.action && (l.action.includes('CONTRACT') || l.action.includes('SALARY')));
  return logs.value;
});

function formatTime(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  return d.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' ' + d.toLocaleDateString('vi-VN');
}

function getActionLabel(log) {
  if (log.action === 'IDOR_ATTEMPT') return 'Cảnh báo IDOR';
  if (log.action === 'ACCOUNT_LOCKED') return 'Khóa tài khoản';
  return log.action_display || log.action;
}

onMounted(() => {
  fetchLogs();
});

defineExpose({ fetchLogs });
</script>

<style scoped>
.audit-wrap {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.audit-header {
  padding: 28px 34px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  background: #ffffff;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-icon-box {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--primary-light);
  border: 1px solid var(--primary-light-border);
  display: flex;
  align-items: center;
  justify-content: center;
}

.audit-header h2 {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text);
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.88rem;
  margin-top: 3px;
}

/* Immutability Banner */
.immutability-banner {
  background: rgba(34, 197, 94, 0.08);
  border: 1px solid rgba(34, 197, 94, 0.25);
  border-radius: var(--radius-md);
  padding: 16px 22px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.banner-icon {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-sm);
  background: rgba(34, 197, 94, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.banner-text {
  font-size: 0.88rem;
  color: #166534;
  line-height: 1.55;
}

.banner-text strong {
  color: #15803d;
}

/* Filter Pills */
.filters-bar {
  display: flex;
  overflow-x: auto;
}

.filter-pills {
  display: flex;
  gap: 8px;
}

.filter-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #ffffff;
  border: 1px solid var(--border);
  color: var(--text-muted);
  padding: 8px 18px;
  border-radius: var(--radius-full);
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
}

.filter-pill:hover {
  background: #f8fafc;
  color: var(--text);
  border-color: #cbd5e1;
}

.filter-pill.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #ffffff;
  box-shadow: var(--shadow-primary);
}

.pill-alert {
  border-color: rgba(244, 63, 94, 0.3);
}

.count-tag {
  font-size: 0.72rem;
  background: rgba(0, 0, 0, 0.06);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.filter-pill.active .count-tag {
  background: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

/* Table */
.table-container {
  overflow: hidden;
  background: #ffffff;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.table-responsive {
  overflow-x: auto;
  width: 100%;
}

.soc-table {
  width: 100%;
  min-width: 1080px;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.88rem;
  table-layout: fixed;
}

.col-w-id { width: 68px; }
.col-w-time { width: 175px; }
.col-w-ip { width: 120px; }
.col-w-user { width: 135px; }
.col-w-action { width: 220px; }
.col-w-resource { width: 165px; }
.col-w-status { width: 140px; }
.col-w-details { width: auto; }

.th-id {
  width: 68px;
}

.clickable-row {
  cursor: pointer;
  transition: background 0.15s ease;
}

.clickable-row:hover td {
  background: #f1f5f9;
}

.id-pill {
  color: var(--primary);
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.2);
  font-weight: 700;
}

.code-pill {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  color: #334155;
  font-weight: 600;
  font-size: 0.78rem;
}

.soc-table th {
  background: #f8fafc;
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  text-align: left;
  white-space: nowrap;
}

.soc-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
  text-align: left;
  overflow: hidden;
  box-sizing: border-box;
}

.soc-table tbody tr:hover {
  background: #f8fafc;
}

.row-idor-alert {
  background: #fff1f2 !important;
  box-shadow: inset 4px 0 0 var(--accent-crimson);
}

.row-lock-alert {
  background: #fffbeb !important;
  box-shadow: inset 4px 0 0 var(--accent-amber);
}

.col-time {
  font-size: 0.8rem;
  color: var(--text-muted);
  white-space: nowrap;
}

.ip-chip {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  padding: 3px 8px;
  border-radius: var(--radius-xs);
  font-size: 0.78rem;
  color: #475569;
  white-space: nowrap;
  display: inline-block;
}

.user-chip-text {
  font-weight: 700;
  color: var(--text);
  white-space: nowrap;
}

.action-tag {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  padding: 4px 10px;
  border-radius: var(--radius-xs);
  font-size: 0.78rem;
  font-weight: 700;
  font-family: var(--font-mono);
  white-space: nowrap;
  box-sizing: border-box;
}

.action-tag-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.act-idor_attempt {
  background: var(--accent-crimson-light);
  color: var(--accent-crimson);
  border: 1px solid rgba(244, 63, 94, 0.35);
}

.act-account_locked {
  background: var(--accent-amber-light);
  color: #b45309;
  border: 1px solid rgba(245, 158, 11, 0.35);
}

.act-login_success {
  background: var(--secondary-light);
  color: #15803d;
}

.act-login_failed {
  background: var(--accent-crimson-light);
  color: var(--accent-crimson);
}

.act-view_student, .act-view_profile, .act-view_contract {
  background: var(--primary-light);
  color: var(--primary);
}

.act-create_student, .act-update_student, .act-update_profile {
  background: rgba(139, 92, 246, 0.1);
  color: #7c3aed;
}

.act-update_grade {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
}

.act-delete_student {
  background: rgba(244, 63, 94, 0.12);
  color: #f43f5e;
}

.resource-pill {
  font-size: 0.78rem;
  background: #f8fafc;
  padding: 3px 8px;
  border-radius: var(--radius-xs);
  color: var(--text-muted);
  border: 1px solid var(--border);
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}

.status-badge-soc {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: 0.74rem;
  font-weight: 700;
  white-space: nowrap;
}

.stat-success { background: var(--secondary-light); color: #15803d; }
.stat-forbidden { background: var(--accent-crimson-light); color: var(--accent-crimson); border: 1px solid rgba(244, 63, 94, 0.3); font-weight: 800; }
.stat-warning { background: var(--accent-amber-light); color: #b45309; }
.stat-failed { background: #f1f5f9; color: #64748b; }

.col-details {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.85rem;
  color: var(--text-muted);
  display: block;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px;
  gap: 14px;
  color: var(--text-muted);
}

.text-primary { color: var(--primary); }
.text-emerald { color: #16a34a; }
.text-crimson { color: var(--accent-crimson); }
.text-amber { color: var(--accent-amber); }
.text-dim { color: var(--text-dim); }

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 20px;
}

.modal-card {
  width: 100%;
  max-width: 640px;
  background: #ffffff;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-xl);
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 14px;
  position: relative;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text);
}

.sub-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  display: block;
  margin-top: 2px;
}

.header-right-badges {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.id-badge-banner {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  background: rgba(37, 99, 235, 0.1);
  border: 1px solid rgba(37, 99, 235, 0.3);
  border-radius: var(--radius-full);
  color: var(--primary);
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.btn-close-modal {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  border-radius: var(--radius-xs);
  transition: var(--transition-fast);
}

.btn-close-modal:hover {
  background: #f1f5f9;
  color: var(--text);
}

.log-detail-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 6px;
}

.detail-row-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.form-group-clean {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group-clean label {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

.readonly-pill-box {
  padding: 8px 12px;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.88rem;
  color: var(--text);
}

.readonly-details-box {
  padding: 12px;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.86rem;
  color: var(--text);
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid var(--border-light);
}

@media (max-width: 640px) {
  .detail-row-2 {
    grid-template-columns: 1fr;
  }
}
</style>
