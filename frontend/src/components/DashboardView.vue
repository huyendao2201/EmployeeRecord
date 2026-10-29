<template>
  <div class="dashboard-wrap">
    <!-- 1. Hero Welcome Banner (Clean, Real SaaS Style) -->
    <div class="hero-banner card-uupm">
      <div class="hero-content">
        <h2>Xin chào, <span class="gradient-text">{{ displayName }}</span>!</h2>
        <p class="hero-desc">
          Chào mừng bạn quay trở lại Cổng thông tin Quản lý Nhân sự SecureHR.
        </p>
      </div>
      <div class="hero-badge-box">
        <span class="user-role-chip" :class="'role-' + (currentUser?.role?.toLowerCase() || 'employee')">
          {{ currentUser?.role_display }}
        </span>
        <span class="status-live-chip font-mono">
          <span class="dot-green"></span> Đang hoạt động
        </span>
      </div>
    </div>

    <!-- 2. KPI Overview Cards (Dynamic by User Role) -->
    <div class="kpi-grid">
      <!-- Dành cho Nhân viên thông thường -->
      <template v-if="!isStaffRole">
        <div class="kpi-card card-uupm">
          <div class="kpi-top">
            <span class="kpi-label">HỒ SƠ CÁ NHÂN</span>
            <div class="kpi-icon-box bg-primary-soft">
              <User class="w-5 h-5 text-primary" />
            </div>
          </div>
          <div class="kpi-value-row">
            <span class="kpi-value font-mono">{{ myProfile?.employee_code || 'EMP001' }}</span>
          </div>
          <span class="kpi-subtext">{{ myProfile?.department || 'Phòng Công nghệ & Phần mềm' }}</span>
        </div>

        <div class="kpi-card card-uupm">
          <div class="kpi-top">
            <span class="kpi-label">HỢP ĐỒNG LAO ĐỘNG</span>
            <div class="kpi-icon-box bg-emerald-soft">
              <FileText class="w-5 h-5 text-emerald" />
            </div>
          </div>
          <div class="kpi-value-row">
            <span class="kpi-value font-mono text-emerald">Hiệu lực</span>
          </div>
          <span class="kpi-subtext">{{ myContract?.contract_type_display || 'Hợp đồng chính thức' }}</span>
        </div>

        <div class="kpi-card card-uupm">
          <div class="kpi-top">
            <span class="kpi-label">CHỨC DANH HIỆN TẠI</span>
            <div class="kpi-icon-box bg-blue-soft">
              <Briefcase class="w-5 h-5 text-blue" />
            </div>
          </div>
          <div class="kpi-value-row">
            <span class="kpi-value text-compact">{{ myProfile?.position || 'Nhân viên' }}</span>
          </div>
          <span class="kpi-subtext">Trạng thái: Đang công tác</span>
        </div>

        <div class="kpi-card card-uupm">
          <div class="kpi-top">
            <span class="kpi-label">BẢO MẬT PHÂN QUYỀN</span>
            <div class="kpi-icon-box bg-purple-soft">
              <ShieldCheck class="w-5 h-5 text-purple" />
            </div>
          </div>
          <div class="kpi-value-row">
            <span class="kpi-value font-mono text-purple">Chính chủ</span>
          </div>
          <span class="kpi-subtext">Quyền truy cập tối thiểu (Least Privilege)</span>
        </div>
      </template>

      <!-- Dành cho Quản lý / HR / Kế toán / Admin -->
      <template v-else>
        <div class="kpi-card card-uupm">
          <div class="kpi-top">
            <span class="kpi-label">TỔNG NHÂN SỰ</span>
            <div class="kpi-icon-box bg-primary-soft">
              <Users class="w-5 h-5 text-primary" />
            </div>
          </div>
          <div class="kpi-value-row">
            <span class="kpi-value font-mono">{{ stats.total_employees || 5 }}</span>
            <span class="kpi-badge badge-primary">HỒ SƠ</span>
          </div>
          <span class="kpi-subtext">Nhân sự toàn công ty đang quản lý</span>
        </div>

        <div class="kpi-card card-uupm">
          <div class="kpi-top">
            <span class="kpi-label">HỢP ĐỒNG LAO ĐỘNG</span>
            <div class="kpi-icon-box bg-emerald-soft">
              <FileText class="w-5 h-5 text-emerald" />
            </div>
          </div>
          <div class="kpi-value-row">
            <span class="kpi-value font-mono">{{ stats.total_contracts || 5 }}</span>
            <span class="kpi-badge badge-emerald">HIỆU LỰC</span>
          </div>
          <span class="kpi-subtext">Hợp đồng lao động pháp lý</span>
        </div>

        <div class="kpi-card card-uupm">
          <div class="kpi-top">
            <span class="kpi-label">PHÒNG BAN CHUYÊN MÔN</span>
            <div class="kpi-icon-box bg-blue-soft">
              <Building2 class="w-5 h-5 text-blue" />
            </div>
          </div>
          <div class="kpi-value-row">
            <span class="kpi-value font-mono">4</span>
            <span class="kpi-badge badge-blue">ĐƠN VỊ</span>
          </div>
          <span class="kpi-subtext">Khối công nghệ, kinh doanh, HR, kế toán</span>
        </div>

        <div class="kpi-card card-uupm">
          <div class="kpi-top">
            <span class="kpi-label">GIÁM SÁT HỆ THỐNG</span>
            <div class="kpi-icon-box bg-purple-soft">
              <Activity class="w-5 h-5 text-purple" />
            </div>
          </div>
          <div class="kpi-value-row">
            <span class="kpi-value font-mono text-purple">Ổn định</span>
            <span class="kpi-badge badge-purple">24/7</span>
          </div>
          <span class="kpi-subtext">Ghi vết kiểm toán an toàn thông tin</span>
        </div>
      </template>
    </div>

    <!-- 3. Hai Cột Thông tin Thực tế (Real SaaS Layout) -->
    <div class="dashboard-columns">
      <!-- Cột Trái: Thông tin Công tác / Danh bạ -->
      <div class="column-card card-uupm">
        <div class="card-header-clean">
          <div class="header-title-clean">
            <UserCheck class="w-5 h-5 text-primary" />
            <h3>{{ isStaffRole ? 'Danh bạ Nhân sự (Xem nhanh)' : 'Thông tin Nhân sự & Công tác' }}</h3>
          </div>
          <button @click="$emit('nav-to', 'profile')" class="btn-text-link">
            <span>{{ isStaffRole ? 'Xem tất cả' : 'Xem chi tiết' }}</span>
            <ArrowRight class="w-4 h-4 ml-1" />
          </button>
        </div>

        <!-- Nội dung cho Nhân viên -->
        <div v-if="!isStaffRole" class="profile-info-grid">
          <div class="info-row">
            <span class="info-label">Họ và tên:</span>
            <span class="info-val font-semibold">{{ myProfile?.full_name || currentUser?.first_name }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Mã nhân viên:</span>
            <span class="info-val font-mono code-tag">{{ myProfile?.employee_code || 'EMP001' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Phòng ban:</span>
            <span class="info-val">{{ myProfile?.department || 'Phòng Công nghệ & Phần mềm' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Vị trí / Chức danh:</span>
            <span class="info-val">{{ myProfile?.position || 'Kỹ sư phần mềm' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Email công vụ:</span>
            <span class="info-val font-mono">{{ myProfile?.email || currentUser?.email || 'nam.nguyen@company.vn' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Số điện thoại:</span>
            <span class="info-val font-mono">{{ myProfile?.phone || '0901234567' }}</span>
          </div>
        </div>

        <!-- Nội dung cho Quản lý / HR: Bảng tóm tắt danh bạ -->
        <div v-else class="directory-mini-table">
          <table class="table-compact">
            <thead>
              <tr>
                <th>MÃ NV</th>
                <th>HỌ TÊN</th>
                <th>PHÒNG BAN</th>
                <th>CHỨC VỤ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="emp in quickEmployees" :key="emp.id">
                <td><span class="code-tag font-mono">{{ emp.employee_code }}</span></td>
                <td class="font-medium">{{ emp.full_name }}</td>
                <td>{{ emp.department }}</td>
                <td>{{ emp.position }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Cột Phải: Hợp đồng & Tiện ích -->
      <div class="column-card card-uupm">
        <div class="card-header-clean">
          <div class="header-title-clean">
            <FileText class="w-5 h-5 text-emerald" />
            <h3>Hợp đồng Lao động</h3>
          </div>
          <button @click="$emit('nav-to', 'contracts')" class="btn-text-link">
            <span>Xem hợp đồng</span>
            <ArrowRight class="w-4 h-4 ml-1" />
          </button>
        </div>

        <div v-if="!isStaffRole" class="contract-info-grid">
          <div class="info-row">
            <span class="info-label">Số hợp đồng:</span>
            <span class="info-val font-mono font-semibold">{{ myContract?.contract_number || 'HĐLĐ-2024-001' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Loại hợp đồng:</span>
            <span class="info-val">{{ myContract?.contract_type_display || 'Hợp đồng không xác định thời hạn' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Ngày hiệu lực:</span>
            <span class="info-val font-mono">{{ formatDate(myContract?.start_date) || '15/01/2024' }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Trạng thái:</span>
            <span class="info-val">
              <span class="status-pill-green font-mono">{{ myContract?.status_display || 'Đang hiệu lực' }}</span>
            </span>
          </div>
        </div>

        <div v-else class="directory-mini-table">
          <table class="table-compact">
            <thead>
              <tr>
                <th>SỐ HĐ</th>
                <th>NHÂN VIÊN</th>
                <th>LOẠI HỢP ĐỒNG</th>
                <th>MỨC LƯƠNG</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in quickContracts" :key="c.id">
                <td><span class="code-tag font-mono">{{ c.contract_number }}</span></td>
                <td class="font-medium">{{ c.employee_name }}</td>
                <td>{{ c.contract_type_display }}</td>
                <td class="salary-cell font-mono">{{ formatMoney(c.salary_rate) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Khối Tiện ích Kiểm định An ninh (Tạm thời ẩn theo yêu cầu) -->
        <!--
        <div class="security-diagnostic-tile">
          <div class="tile-icon">
            <ShieldCheck class="w-5 h-5 text-primary" />
          </div>
          <div class="tile-content">
            <h4>Kiểm định An ninh & Phân quyền</h4>
            <p>Kiểm tra tính tuân thủ các quy tắc bảo mật và quyền truy cập API của hệ thống.</p>
          </div>
          <button @click="$emit('nav-to', 'exploit')" class="btn-secondary btn-tile">
            <span>Kiểm tra</span>
            <ChevronRight class="w-4 h-4 ml-1" />
          </button>
        </div>
        -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { api } from '../api';
import {
  User,
  Users,
  UserCheck,
  FileText,
  Briefcase,
  Building2,
  ShieldCheck,
  Activity,
  ArrowRight,
  ChevronRight
} from '@lucide/vue';

const props = defineProps({
  currentUser: Object
});

defineEmits(['nav-to']);

const stats = ref({});
const myProfile = ref(null);
const myContract = ref(null);
const quickEmployees = ref([]);
const quickContracts = ref([]);

const displayName = computed(() => {
  return props.currentUser?.first_name || props.currentUser?.username || 'Nhân viên';
});

const isStaffRole = computed(() => {
  return ['ADMIN', 'HR', 'ACCOUNTANT'].includes(props.currentUser?.role);
});

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  return d.toLocaleDateString('vi-VN');
}

function formatMoney(amount) {
  if (!amount) return '0 ₫';
  return Number(amount).toLocaleString('vi-VN') + ' ₫';
}

async function loadData() {
  try {
    // 1. Tải stats tổng quan
    const statData = await api.getSecurityStats();
    stats.value = statData || {};

    // 2. Tải thông tin cá nhân của người dùng
    if (props.currentUser?.profile_id) {
      try {
        const prof = await api.getEmployeeById(props.currentUser.profile_id);
        myProfile.value = prof;
      } catch (e) {
        // Fallback profile
      }
    }

    // 3. Tải hợp đồng
    try {
      const contracts = await api.getContracts();
      const list = Array.isArray(contracts) ? contracts : (contracts.results || []);
      if (list.length > 0) {
        myContract.value = list[0];
      }
      if (isStaffRole.value) {
        quickContracts.value = list.slice(0, 4);
      }
    } catch (e) {
      // Ignore
    }

    // 4. Nếu là quản lý, tải danh bạ xem nhanh
    if (isStaffRole.value) {
      try {
        const emps = await api.getEmployees();
        const empList = Array.isArray(emps) ? emps : (emps.results || []);
        quickEmployees.value = empList.slice(0, 4);
      } catch (e) {
        // Ignore
      }
    }
  } catch (err) {
    console.error('Lỗi tải dữ liệu dashboard:', err);
  }
}

onMounted(() => {
  loadData();
});

defineExpose({ loadStats: loadData });
</script>

<style scoped>
.dashboard-wrap {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1480px;
  margin: 0 auto;
  padding: 24px;
}

/* 1. Hero Banner */
.hero-banner {
  padding: 28px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  background: #ffffff;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
}

.hero-content h2 {
  font-size: 1.65rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 6px;
  color: var(--text);
}

.hero-desc {
  font-size: 0.92rem;
  color: var(--text-muted);
}

.hero-badge-box {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-role-chip {
  font-size: 0.76rem;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: var(--radius-xs);
}

.role-admin { background: #fee2e2; color: #b91c1c; }
.role-hr { background: #e0e7ff; color: #4338ca; }
.role-accountant { background: #fef3c7; color: #b45309; }
.role-employee { background: #f1f5f9; color: #475569; }

.status-live-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.76rem;
  color: #15803d;
  background: #dcfce7;
  padding: 4px 10px;
  border-radius: var(--radius-xs);
  font-weight: 600;
}

.dot-green {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #16a34a;
}

/* 2. KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}

.kpi-card {
  padding: 20px 22px;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
}

.kpi-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.kpi-label {
  font-size: 0.72rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  color: var(--text-muted);
}

.kpi-icon-box {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
}

.bg-primary-soft { background: var(--primary-light); }
.bg-emerald-soft { background: rgba(16, 185, 129, 0.12); }
.bg-blue-soft { background: rgba(59, 130, 246, 0.12); }
.bg-purple-soft { background: rgba(168, 85, 247, 0.12); }

.text-blue { color: #2563eb; }
.text-purple { color: #9333ea; }

.kpi-value-row {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 6px;
}

.kpi-value {
  font-size: 1.85rem;
  font-weight: 800;
  color: var(--text);
  line-height: 1;
}

.text-compact {
  font-size: 1.25rem;
  letter-spacing: -0.01em;
}

.kpi-badge {
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 7px;
  border-radius: var(--radius-full);
}

.badge-primary { background: var(--primary-light); color: var(--primary); }
.badge-emerald { background: rgba(16, 185, 129, 0.12); color: #10b981; }
.badge-blue { background: rgba(59, 130, 246, 0.12); color: #2563eb; }
.badge-purple { background: rgba(168, 85, 247, 0.12); color: #9333ea; }

.kpi-subtext {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* 3. Columns Layout */
.dashboard-columns {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.column-card {
  padding: 24px;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.card-header-clean {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-light);
}

.header-title-clean {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-title-clean h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text);
}

.btn-text-link {
  display: inline-flex;
  align-items: center;
  background: none;
  border: none;
  color: var(--primary);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-text-link:hover {
  text-decoration: underline;
}

/* Info Rows */
.profile-info-grid,
.contract-info-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.88rem;
  padding: 4px 0;
}

.info-label {
  color: var(--text-muted);
}

.info-val {
  color: var(--text);
}

.code-tag {
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: var(--radius-xs);
  color: #334155;
  font-weight: 600;
}

.status-pill-green {
  font-size: 0.76rem;
  background: #dcfce7;
  color: #15803d;
  padding: 3px 8px;
  border-radius: var(--radius-xs);
  font-weight: 600;
}

/* Mini Table */
.directory-mini-table {
  overflow-x: auto;
}

.table-compact {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.84rem;
}

.table-compact th {
  text-align: left;
  padding: 8px 10px;
  font-size: 0.72rem;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border);
}

.table-compact td {
  padding: 10px;
  border-bottom: 1px solid var(--border-light);
  color: var(--text);
}

/* Security Diagnostic Tile */
.security-diagnostic-tile {
  margin-top: 10px;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.tile-icon {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-sm);
  background: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tile-content {
  flex: 1;
}

.tile-content h4 {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 2px;
}

.tile-content p {
  font-size: 0.78rem;
  color: var(--text-muted);
  line-height: 1.4;
  margin: 0;
}

.btn-tile {
  padding: 6px 12px;
  font-size: 0.78rem;
  flex-shrink: 0;
}

@media (max-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .dashboard-columns {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .kpi-grid {
    grid-template-columns: 1fr;
  }
}
</style>
