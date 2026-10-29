<template>
  <div class="profile-wrap">
    <!-- Header -->
    <div class="profile-header card-uupm">
      <div class="header-left">
        <div class="header-icon-box">
          <UserCheck class="w-6 h-6 text-primary" />
        </div>
        <div>
          <h2>{{ isStaffRole ? 'Danh mục Hồ sơ Nhân viên' : 'Hồ sơ Nhân viên Cá nhân' }}</h2>
          <p class="subtitle">
            {{ isStaffRole ? 'Quản lý danh bạ và hồ sơ nhân sự toàn công ty theo quyền hạn vai trò.' : 'Xem và cập nhật thông tin hồ sơ nhân sự cá nhân.' }}
          </p>
        </div>
      </div>
      <div class="header-actions">
        <button
          v-if="isHRorAdmin && !selectedProfile"
          @click="openAddModal"
          class="btn-primary"
        >
          <Plus class="w-4 h-4 mr-1.5" />
          <span>Thêm nhân viên mới</span>
        </button>
        <button @click="loadData" :disabled="loading" class="btn-secondary">
          <RefreshCw class="w-4 h-4 mr-2" :class="{ spin: loading }" />
          <span>Làm mới Dữ liệu</span>
        </button>
      </div>
    </div>

    <!-- Filter & Search Bar for Staff/HR -->
    <div v-if="isStaffRole && !selectedProfile" class="search-filter-bar card-uupm">
      <div class="search-box">
        <Search class="w-4 h-4 text-muted input-icon" />
        <input
          v-model="searchQuery"
          @input="debounceSearch"
          type="text"
          placeholder="Tìm theo Mã NV, Họ tên, Phòng ban, CCCD..."
          class="search-input"
        />
      </div>

      <div class="filter-controls">
        <select v-model="filterDept" @change="loadData" class="select-control">
          <option value="">Tất cả phòng ban</option>
          <option value="Phòng Công nghệ & Phần mềm">Phòng Công nghệ & Phần mềm</option>
          <option value="Phòng Kinh doanh & Tiếp thị">Phòng Kinh doanh & Tiếp thị</option>
          <option value="Phòng Hành chính - Nhân sự">Phòng Hành chính - Nhân sự</option>
          <option value="Phòng Tài chính - Kế toán">Phòng Tài chính - Kế toán</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !selectedProfile && employeesList.length === 0" class="loading-state">
      <RefreshCw class="w-8 h-8 spin text-primary" />
      <span>Đang tải danh sách nhân sự...</span>
    </div>

    <!-- Directory Table for Staff/HR -->
    <div v-else-if="isStaffRole && !selectedProfile" class="table-container card-uupm">
      <div class="table-responsive">
        <table class="soc-table">
          <thead>
            <tr>
              <th class="th-id">ID</th>
              <th>MÃ NV</th>
              <th>HỌ VÀ TÊN</th>
              <th>TÀI KHOẢN ĐĂNG NHẬP</th>
              <th>PHÒNG BAN</th>
              <th>CHỨC VỤ</th>
              <th>SỐ ĐIỆN THOẠI</th>
              <th>CCCD / ĐỊNH DANH</th>
              <th>LƯƠNG CƠ BẢN</th>
              <th>HỆ SỐ</th>
              <th>THAO TÁC</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="emp in filteredEmployees" :key="emp.id">
              <td><span class="code-pill font-mono id-pill">#{{ emp.id }}</span></td>
              <td><span class="code-pill font-mono">{{ emp.employee_code }}</span></td>
              <td class="name-cell">
                <div class="user-avatar-mini">{{ emp.full_name?.charAt(0) }}</div>
                <span class="font-medium">{{ emp.full_name }}</span>
              </td>
              <td>
                <div class="account-cell-info">
                  <div class="account-username font-mono font-medium">
                    <span
                      class="status-dot"
                      :class="emp.user_is_locked || !emp.user_is_active ? 'dot-locked' : 'dot-active'"
                      :title="emp.user_is_locked || !emp.user_is_active ? 'Tài khoản đang bị khóa' : 'Tài khoản đang hoạt động'"
                    ></span>
                    <span>{{ emp.username || 'Chưa gán' }}</span>
                  </div>
                  <div class="account-pwd-preview font-mono">
                    <span class="pwd-preview-label">MK:</span>
                    <span v-if="revealedTablePwds[emp.id]" class="pwd-preview-val font-semibold text-primary">
                      {{ emp.current_password || 'Employee@123' }}
                    </span>
                    <span v-else class="pwd-preview-dots">••••••</span>
                    <button
                      type="button"
                      @click="toggleTablePwd(emp.id)"
                      class="btn-mini-eye"
                      :title="revealedTablePwds[emp.id] ? 'Ẩn mật khẩu' : 'Xem mật khẩu hiện tại'"
                    >
                      <EyeOff v-if="revealedTablePwds[emp.id]" class="w-3 h-3 text-primary" />
                      <Eye v-else class="w-3 h-3 text-muted" />
                    </button>
                  </div>
                  <div class="account-badges">
                    <span class="role-badge font-mono">{{ emp.user_role_display || emp.user_role || 'Nhân viên' }}</span>
                    <span v-if="emp.user_is_locked || !emp.user_is_active" class="lock-mini-badge font-mono">
                      <Lock class="w-2.5 h-2.5 mr-0.5" />
                      <span>Khóa</span>
                    </span>
                  </div>
                </div>
              </td>
              <td><span class="dept-tag font-mono">{{ emp.department }}</span></td>
              <td><span class="pos-tag">{{ emp.position }}</span></td>
              <td class="font-mono">{{ emp.phone }}</td>
              <td class="font-mono">{{ emp.identity_card }}</td>
              <td class="salary-cell font-mono">{{ formatMoney(emp.basic_salary) }}</td>
              <td><span class="rate-badge font-mono">{{ emp.salary_coefficient }}</span></td>
              <td>
                <div class="action-buttons-cell">
                  <button @click="viewDetail(emp)" class="btn-table-action" :title="'Xem chi tiết hồ sơ #' + emp.id">
                    <span>Xem chi tiết</span>
                  </button>
                  <button
                    v-if="isHRorAdmin"
                    @click="openAccountModal(emp)"
                    class="btn-table-action btn-account-action"
                    :title="'Quản lý tài khoản & an ninh: ' + (emp.username || emp.employee_code)"
                  >
                    <Key class="w-3.5 h-3.5 mr-1" />
                    <span>Tài khoản</span>
                  </button>
                  <button
                    v-if="isHRorAdmin"
                    @click="deleteEmployeeDirect(emp)"
                    class="btn-table-action btn-delete-row"
                    title="Xóa nhân viên"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Detailed Profile View (Personal or Selected) -->
    <div v-else-if="selectedProfile" class="detail-card-container">
      <div class="detail-top-nav">
        <button
          v-if="isStaffRole"
          @click="goBackToList"
          class="btn-back"
        >
          ← Quay lại danh sách nhân viên
        </button>
        <div class="top-nav-actions">
          <span class="id-badge-banner font-mono">
            <Hash class="w-3.5 h-3.5 mr-1" />
            <span>ID Hệ thống: #{{ selectedProfile.id }}</span>
          </span>
          <span class="status-indicator-chip font-mono">
            <span class="dot-green"></span> Trạng thái: Đang hoạt động
          </span>
          <button
            v-if="!isEditing && canEditCurrentProfile"
            @click="startEdit"
            class="btn-edit-mode"
          >
            Chỉnh sửa thông tin
          </button>
          <button
            v-if="isHRorAdmin && !isEditing"
            @click="deleteCurrentProfile"
            class="btn-delete-profile"
            title="Xóa nhân viên khỏi hệ thống"
          >
            <Trash2 class="w-4 h-4 mr-1.5" />
            <span>Xóa nhân viên</span>
          </button>
        </div>
      </div>

      <form @submit.prevent="saveProfile" class="profile-cards-grid">
        <!-- Card 1: Định danh & Cá nhân -->
        <div class="profile-card card-uupm">
          <div class="card-head">
            <div class="head-icon"><UserCheck class="w-5 h-5 text-primary" /></div>
            <h3>Thông tin Định danh & Liên lạc</h3>
          </div>

          <div class="detail-row-2">
            <div class="detail-form-group">
              <label>ID HỆ THỐNG (PRIMARY KEY)</label>
              <input
                :value="'#' + selectedProfile.id"
                disabled
                type="text"
                class="input-detail font-mono locked-field font-semibold text-primary"
              />
            </div>
            <div class="detail-form-group">
              <label>MÃ NHÂN VIÊN</label>
              <input
                :value="editForm.employee_code"
                disabled
                type="text"
                class="input-detail font-mono locked-field"
              />
            </div>
          </div>

          <div class="detail-form-group">
            <label>HỌ VÀ TÊN</label>
            <input
              v-model="editForm.full_name"
              :disabled="!isEditing || isEmployeeRole"
              type="text"
              required
              class="input-detail"
              :class="{ 'locked-field': isEmployeeRole }"
            />
          </div>

          <div class="detail-row-2">
            <div class="detail-form-group">
              <label>NGÀY SINH</label>
              <input
                v-model="editForm.dob"
                :disabled="!isEditing || isEmployeeRole"
                type="date"
                class="input-detail font-mono"
                :class="{ 'locked-field': isEmployeeRole }"
              />
            </div>
            <div class="detail-form-group">
              <label>SỐ CCCD / CMND</label>
              <input
                v-model="editForm.identity_card"
                :disabled="!isEditing || isEmployeeRole"
                type="text"
                required
                class="input-detail font-mono"
                :class="{ 'locked-field': isEmployeeRole }"
              />
            </div>
          </div>

          <div class="detail-row-2">
            <div class="detail-form-group">
              <label>SỐ ĐIỆN THOẠI</label>
              <input
                v-model="editForm.phone"
                :disabled="!isEditing"
                type="text"
                required
                class="input-detail font-mono"
              />
            </div>
            <div class="detail-form-group">
              <label>EMAIL CÔNG VỤ</label>
              <input
                v-model="editForm.email"
                :disabled="!isEditing || isEmployeeRole"
                type="email"
                class="input-detail font-mono"
                :class="{ 'locked-field': isEmployeeRole }"
              />
            </div>
          </div>

          <div class="detail-form-group">
            <label>ĐỊA CHỈ THƯỜNG TRÚ</label>
            <textarea
              v-model="editForm.address"
              :disabled="!isEditing"
              rows="3"
              class="input-detail textarea-detail"
            ></textarea>
          </div>
        </div>

        <!-- Card 2: Vị trí & Chế độ Lương thưởng -->
        <div class="profile-card card-uupm">
          <div class="card-head">
            <div class="head-icon"><Building class="w-5 h-5 text-emerald" /></div>
            <h3>Vị trí Công tác & Chế độ Lương thưởng</h3>
          </div>

          <div class="detail-form-group">
            <label>PHÒNG BAN TRỰC THUỘC</label>
            <input
              v-model="editForm.department"
              :disabled="!isEditing || !isHRorAdmin"
              type="text"
              class="input-detail"
              :class="{ 'locked-field': !isHRorAdmin }"
            />
          </div>

          <div class="detail-form-group">
            <label>VỊ TRÍ / CHỨC DANH</label>
            <input
              v-model="editForm.position"
              :disabled="!isEditing || !isHRorAdmin"
              type="text"
              class="input-detail"
              :class="{ 'locked-field': !isHRorAdmin }"
            />
          </div>

          <div class="detail-row-2">
            <div class="detail-form-group">
              <div class="label-with-guard">
                <label>HỆ SỐ LƯƠNG</label>
                <span v-if="isEmployeeRole" class="guard-pill font-mono">CHỈ ĐỌC</span>
              </div>
              <input
                v-model.number="editForm.salary_coefficient"
                :disabled="!isEditing || !isHRorAdmin"
                type="number"
                step="0.1"
                class="input-detail font-mono"
                :class="{ 'locked-field': !isHRorAdmin }"
              />
            </div>
            <div class="detail-form-group">
              <div class="label-with-guard">
                <label>LƯƠNG CƠ BẢN (VNĐ)</label>
                <span v-if="isEmployeeRole" class="guard-pill font-mono">CHỈ ĐỌC</span>
              </div>
              <input
                v-model.number="editForm.basic_salary"
                :disabled="!isEditing || !isHRorAdmin"
                type="number"
                step="500000"
                class="input-detail font-mono"
                :class="{ 'locked-field': !isHRorAdmin }"
              />
            </div>
          </div>

          <div class="detail-row-2">
            <div class="detail-form-group">
              <label>SỐ TÀI KHOẢN NGÂN HÀNG</label>
              <input
                v-model="editForm.bank_account"
                :disabled="!isEditing"
                type="text"
                class="input-detail font-mono"
              />
            </div>
            <div class="detail-form-group">
              <label>TÊN NGÂN HÀNG</label>
              <input
                v-model="editForm.bank_name"
                :disabled="!isEditing"
                type="text"
                class="input-detail"
              />
            </div>
          </div>

          <!-- Action buttons when editing -->
          <div v-if="isEditing" class="edit-actions-bar">
            <button type="button" @click="cancelEdit" class="btn-secondary">Hủy bỏ</button>
            <button type="submit" :disabled="saving" class="btn-primary">
              <Save class="w-4 h-4 mr-2" />
              {{ saving ? 'Đang lưu thay đổi...' : 'Lưu thay đổi' }}
            </button>
          </div>
        </div>
      </form>

      <!-- Card 3: Tài khoản Đăng nhập & An ninh Hệ thống -->
      <div class="profile-card card-uupm account-mgmt-card">
        <div class="card-head">
          <div class="head-icon head-icon-shield">
            <ShieldCheck v-if="selectedProfile.user_is_active && !selectedProfile.user_is_locked" class="w-5 h-5 text-emerald" />
            <ShieldAlert v-else class="w-5 h-5 text-rose" />
          </div>
          <div class="card-head-title">
            <h3>Tài khoản Đăng nhập & An ninh Hệ thống</h3>
            <p class="card-sub-hint">Thông tin tài khoản đăng nhập, quyền hạn truy cập dữ liệu và giám sát an ninh Zero-Trust</p>
          </div>
          <div class="card-head-badge">
            <span
              class="security-status-badge font-mono"
              :class="selectedProfile.user_is_locked || !selectedProfile.user_is_active ? 'badge-locked' : 'badge-active'"
            >
              <Lock v-if="selectedProfile.user_is_locked || !selectedProfile.user_is_active" class="w-3.5 h-3.5 mr-1" />
              <ShieldCheck v-else class="w-3.5 h-3.5 mr-1" />
              <span>{{ selectedProfile.user_is_locked || !selectedProfile.user_is_active ? 'Tài khoản đang bị khóa' : 'Đang hoạt động an toàn' }}</span>
            </span>
          </div>
        </div>

        <div class="account-details-grid">
          <div class="account-detail-item">
            <span class="detail-label">TÊN ĐĂNG NHẬP (USERNAME)</span>
            <div class="detail-value font-mono flex items-center">
              <Key class="w-4 h-4 text-primary mr-1.5 flex-shrink-0" />
              <strong class="text-primary">{{ selectedProfile.username || 'Chưa liên kết' }}</strong>
            </div>
          </div>

          <div class="account-detail-item">
            <div class="label-with-action">
              <span class="detail-label">MẬT KHẨU HIỆN TẠI</span>
              <button
                type="button"
                @click="showCurrentPasswordInDetail = !showCurrentPasswordInDetail"
                class="btn-reveal-pwd"
                :title="showCurrentPasswordInDetail ? 'Ẩn mật khẩu' : 'Xem mật khẩu hiện tại'"
              >
                <EyeOff v-if="showCurrentPasswordInDetail" class="w-3.5 h-3.5 text-primary mr-1" />
                <Eye v-else class="w-3.5 h-3.5 text-muted mr-1" />
                <span>{{ showCurrentPasswordInDetail ? 'Ẩn' : 'Xem' }}</span>
              </button>
            </div>
            <div class="detail-value font-mono flex items-center">
              <span v-if="showCurrentPasswordInDetail" class="pwd-revealed-badge font-semibold">
                {{ selectedProfile.current_password || 'Employee@123' }}
              </span>
              <span v-else class="pwd-masked-text">
                ••••••••••••
              </span>
            </div>
          </div>

          <div class="account-detail-item">
            <span class="detail-label">VAI TRÒ TRUY CẬP (ROLE)</span>
            <div class="detail-value font-mono">
              <span class="role-pill">{{ selectedProfile.user_role_display || selectedProfile.user_role || 'Nhân viên' }}</span>
            </div>
          </div>

          <div class="account-detail-item">
            <span class="detail-label">TRẠNG THÁI HOẠT ĐỘNG</span>
            <div class="detail-value font-mono">
              <span :class="selectedProfile.user_is_active ? 'text-success font-semibold' : 'text-danger font-semibold'">
                {{ selectedProfile.user_is_active ? '● Đang kích hoạt' : '● Vô hiệu hóa' }}
              </span>
            </div>
          </div>

          <div class="account-detail-item">
            <span class="detail-label">BẢO VỆ CHỐNG BRUTE-FORCE</span>
            <div class="detail-value font-mono">
              <span v-if="selectedProfile.user_is_locked" class="text-danger font-semibold">
                ⚠️ Đang khóa (Thất bại: {{ selectedProfile.user_failed_attempts || 0 }} lần)
              </span>
              <span v-else class="text-success font-semibold">
                ✓ An toàn (Thất bại: {{ selectedProfile.user_failed_attempts || 0 }}/5)
              </span>
            </div>
          </div>

          <div class="account-detail-item">
            <span class="detail-label">LẦN ĐĂNG NHẬP GẦN NHẤT</span>
            <div class="detail-value font-mono text-muted">
              {{ formatDateTime(selectedProfile.user_last_login) }}
            </div>
          </div>

          <div class="account-detail-item">
            <span class="detail-label">NGÀY TẠO TÀI KHOẢN</span>
            <div class="detail-value font-mono text-muted">
              {{ formatDateTime(selectedProfile.user_date_joined) }}
            </div>
          </div>
        </div>

        <!-- HR / Admin Quick Actions for Account -->
        <div v-if="isHRorAdmin" class="account-actions-toolbar">
          <button
            type="button"
            @click="openResetPasswordModal(selectedProfile)"
            class="btn-account-action-primary"
          >
            <Key class="w-4 h-4 mr-1.5" />
            <span>Đặt lại mật khẩu</span>
          </button>
          <button
            type="button"
            @click="handleToggleLock(selectedProfile)"
            :class="selectedProfile.user_is_locked || !selectedProfile.user_is_active ? 'btn-account-action-unlock' : 'btn-account-action-lock'"
            :disabled="lockLoading"
          >
            <Unlock v-if="selectedProfile.user_is_locked || !selectedProfile.user_is_active" class="w-4 h-4 mr-1.5" />
            <Lock v-else class="w-4 h-4 mr-1.5" />
            <span>{{ selectedProfile.user_is_locked || !selectedProfile.user_is_active ? 'Mở khóa tài khoản' : 'Khóa tài khoản' }}</span>
          </button>
          <button
            type="button"
            @click="openAccountModal(selectedProfile)"
            class="btn-account-action-secondary"
          >
            <Settings class="w-4 h-4 mr-1.5" />
            <span>Phân quyền & Tên đăng nhập</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal Thêm Nhân viên Mới (Admin / HR) -->
    <div v-if="showAddModal" class="modal-overlay animate-fade-in" @click.self="showAddModal = false">
      <div class="modal-card card-uupm">
        <div class="modal-header">
          <div class="header-icon-box">
            <UserPlus class="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3>Thêm Nhân viên Mới</h3>
            <span class="sub-label">Tạo hồ sơ nhân sự, hợp đồng ban đầu và kích hoạt tài khoản đăng nhập</span>
          </div>
          <button @click="showAddModal = false" class="btn-close-modal" title="Đóng">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div v-if="addError" class="modal-error-banner">
          <AlertCircle class="w-4 h-4 mr-2 flex-shrink-0" />
          <span>{{ addError }}</span>
        </div>

        <form @submit.prevent="handleCreateEmployee" class="modal-form">
          <div class="modal-form-grid">
            <div class="form-group-clean">
              <label>MÃ NHÂN VIÊN (*)</label>
              <input
                v-model="addForm.employee_code"
                type="text"
                required
                class="input-uupm font-mono"
                placeholder="Ví dụ: EMP005"
              />
            </div>

            <div class="form-group-clean">
              <label>HỌ VÀ TÊN (*)</label>
              <input
                v-model="addForm.full_name"
                type="text"
                required
                class="input-uupm"
                placeholder="Nguyễn Văn A"
              />
            </div>

            <div class="form-group-clean">
              <label>PHÒNG BAN</label>
              <select v-model="addForm.department" class="select-control">
                <option value="Phòng Công nghệ & Phần mềm">Phòng Công nghệ & Phần mềm</option>
                <option value="Phòng Kinh doanh & Tiếp thị">Phòng Kinh doanh & Tiếp thị</option>
                <option value="Phòng Hành chính - Nhân sự">Phòng Hành chính - Nhân sự</option>
                <option value="Phòng Tài chính - Kế toán">Phòng Tài chính - Kế toán</option>
              </select>
            </div>

            <div class="form-group-clean">
              <label>VỊ TRÍ / CHỨC DANH</label>
              <input
                v-model="addForm.position"
                type="text"
                required
                class="input-uupm"
                placeholder="Ví dụ: Kỹ sư Phần mềm"
              />
            </div>

            <div class="form-group-clean">
              <label>SỐ ĐIỆN THOẠI (*)</label>
              <input
                v-model="addForm.phone"
                type="text"
                required
                class="input-uupm font-mono"
                placeholder="0912345678"
              />
            </div>

            <div class="form-group-clean">
              <label>CCCD / ĐỊNH DANH (*)</label>
              <input
                v-model="addForm.identity_card"
                type="text"
                required
                class="input-uupm font-mono"
                placeholder="001198000123"
              />
            </div>

            <div class="form-group-clean">
              <label>EMAIL CÔNG VỤ</label>
              <input
                v-model="addForm.email"
                type="email"
                class="input-uupm font-mono"
                placeholder="email@company.vn"
              />
            </div>

            <div class="form-group-clean">
              <label>LƯƠNG CƠ BẢN (VNĐ)</label>
              <input
                v-model.number="addForm.basic_salary"
                type="number"
                step="500000"
                class="input-uupm font-mono"
              />
            </div>

            <div class="form-group-clean">
              <label>HỆ SỐ LƯƠNG</label>
              <input
                v-model.number="addForm.salary_coefficient"
                type="number"
                step="0.1"
                class="input-uupm font-mono"
              />
            </div>

            <div class="form-group-clean">
              <label>MẬT KHẨU TÀI KHOẢN</label>
              <input
                v-model="addForm.password"
                type="text"
                class="input-uupm font-mono"
                placeholder="Mặc định: Employee@123"
              />
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showAddModal = false" class="btn-secondary">Hủy bỏ</button>
            <button type="submit" :disabled="addLoading" class="btn-primary">
              <RefreshCw v-if="addLoading" class="w-4 h-4 mr-2 spin" />
              <UserPlus v-else class="w-4 h-4 mr-2" />
              <span>{{ addLoading ? 'Đang tạo nhân sự...' : 'Tạo hồ sơ nhân viên' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Đặt lại Mật khẩu Đăng nhập -->
    <div v-if="showResetModal" class="modal-overlay animate-fade-in" @click.self="showResetModal = false">
      <div class="modal-card modal-card-sm card-uupm">
        <div class="modal-header">
          <div class="header-icon-box header-icon-key">
            <Key class="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3>Đặt lại Mật khẩu Đăng nhập</h3>
            <span class="sub-label">Cấp lại mật khẩu mới cho tài khoản nhân viên</span>
          </div>
          <button @click="showResetModal = false" class="btn-close-modal" title="Đóng">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div v-if="resetError" class="modal-error-banner">
          <AlertCircle class="w-4 h-4 mr-2 flex-shrink-0" />
          <span>{{ resetError }}</span>
        </div>

        <div class="account-modal-target-box">
          <div class="target-name font-medium">{{ resetTarget?.full_name }}</div>
          <div class="target-meta font-mono">
            <span>Mã NV: {{ resetTarget?.employee_code }}</span> • 
            <span>Username: <strong>{{ resetTarget?.username || 'Chưa gán' }}</strong></span>
          </div>
          <div class="current-pwd-box font-mono">
            <span class="curr-pwd-title">MẬT KHẨU HIỆN TẠI:</span>
            <span v-if="showCurrentPasswordInModal" class="curr-pwd-text font-semibold text-primary">
              {{ resetTarget?.current_password || 'Employee@123' }}
            </span>
            <span v-else class="curr-pwd-masked">••••••••••••</span>
            <button
              type="button"
              @click="showCurrentPasswordInModal = !showCurrentPasswordInModal"
              class="btn-reveal-pwd-mini"
              :title="showCurrentPasswordInModal ? 'Ẩn mật khẩu hiện tại' : 'Xem mật khẩu hiện tại'"
            >
              <EyeOff v-if="showCurrentPasswordInModal" class="w-3.5 h-3.5 text-primary" />
              <Eye v-else class="w-3.5 h-3.5 text-muted" />
              <span>{{ showCurrentPasswordInModal ? 'Ẩn' : 'Xem' }}</span>
            </button>
          </div>
        </div>

        <form @submit.prevent="handleConfirmResetPassword" class="modal-form">
          <div class="form-group-clean">
            <label>MẬT KHẨU MỚI (*)</label>
            <div class="password-input-wrap">
              <input
                v-model="resetPassword"
                :type="showPasswordText ? 'text' : 'password'"
                required
                minlength="6"
                class="input-uupm font-mono"
                placeholder="Nhập mật khẩu mới (tối thiểu 6 ký tự)"
              />
              <button
                type="button"
                @click="showPasswordText = !showPasswordText"
                class="btn-toggle-eye"
                tabindex="-1"
                title="Ẩn/Hiện mật khẩu"
              >
                <EyeOff v-if="showPasswordText" class="w-4 h-4" />
                <Eye v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div class="security-reset-notice">
            <ShieldCheck class="w-4 h-4 text-primary flex-shrink-0 mr-2 mt-0.5" />
            <div class="notice-text">
              Sau khi đặt lại mật khẩu, hệ thống sẽ tự động kích hoạt tài khoản và mở khóa nếu tài khoản đang bị hạn chế do brute-force.
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showResetModal = false" class="btn-secondary">
              Hủy bỏ
            </button>
            <button type="submit" :disabled="resetLoading" class="btn-primary">
              <Key class="w-4 h-4 mr-1.5" />
              <span>{{ resetLoading ? 'Đang cập nhật...' : 'Xác nhận đổi mật khẩu' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Quản lý Tài khoản & Phân quyền -->
    <div v-if="showAccountModal" class="modal-overlay animate-fade-in" @click.self="showAccountModal = false">
      <div class="modal-card modal-card-sm card-uupm">
        <div class="modal-header">
          <div class="header-icon-box header-icon-settings">
            <Settings class="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3>Quản lý Tài khoản & Phân quyền</h3>
            <span class="sub-label">Cập nhật tên đăng nhập, vai trò hệ thống và trạng thái</span>
          </div>
          <button @click="showAccountModal = false" class="btn-close-modal" title="Đóng">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div v-if="accountError" class="modal-error-banner">
          <AlertCircle class="w-4 h-4 mr-2 flex-shrink-0" />
          <span>{{ accountError }}</span>
        </div>

        <div class="account-modal-target-box">
          <div class="target-name font-medium">{{ accountTarget?.full_name }}</div>
          <div class="target-meta font-mono">
            <span>Mã NV: {{ accountTarget?.employee_code }}</span> • 
            <span>Phòng ban: {{ accountTarget?.department }}</span>
          </div>
          <div class="current-pwd-box font-mono">
            <span class="curr-pwd-title">MẬT KHẨU HIỆN TẠI:</span>
            <span v-if="showCurrentPasswordInAccModal" class="curr-pwd-text font-semibold text-primary">
              {{ accountTarget?.current_password || 'Employee@123' }}
            </span>
            <span v-else class="curr-pwd-masked">••••••••••••</span>
            <button
              type="button"
              @click="showCurrentPasswordInAccModal = !showCurrentPasswordInAccModal"
              class="btn-reveal-pwd-mini"
              :title="showCurrentPasswordInAccModal ? 'Ẩn mật khẩu hiện tại' : 'Xem mật khẩu hiện tại'"
            >
              <EyeOff v-if="showCurrentPasswordInAccModal" class="w-3.5 h-3.5 text-primary" />
              <Eye v-else class="w-3.5 h-3.5 text-muted" />
              <span>{{ showCurrentPasswordInAccModal ? 'Ẩn' : 'Xem' }}</span>
            </button>
          </div>
        </div>

        <form @submit.prevent="handleSaveAccountModal" class="modal-form">
          <div class="form-group-clean">
            <label>TÊN ĐĂNG NHẬP (USERNAME) (*)</label>
            <input
              v-model="accountForm.username"
              type="text"
              required
              class="input-uupm font-mono"
              placeholder="ví dụ: hoanganh"
            />
            <span class="field-hint">Dùng để đăng nhập vào cổng thông tin nội bộ</span>
          </div>

          <div class="form-group-clean">
            <label>VAI TRÒ PHÂN QUYỀN HỆ THỐNG (*)</label>
            <select v-model="accountForm.role" class="select-uupm" required>
              <option value="EMPLOYEE">Nhân viên thông thường (Chỉ xem hồ sơ cá nhân)</option>
              <option value="HR">Chuyên viên Nhân sự (HR - Quản lý hồ sơ nhân viên)</option>
              <option value="ACCOUNTANT">Kế toán viên (Quản lý lương & hợp đồng)</option>
              <option value="ADMIN">Quản trị viên Hệ thống (Toàn quyền quản trị)</option>
            </select>
            <span class="field-hint">Quyết định quyền truy cập dữ liệu theo chính sách RBAC</span>
          </div>

          <div class="account-modal-status-box">
            <div class="status-box-info">
              <span class="status-box-title">Trạng thái khóa tài khoản:</span>
              <span class="status-box-desc font-mono" :class="accountTarget?.user_is_locked || !accountTarget?.user_is_active ? 'text-danger' : 'text-success'">
                {{ accountTarget?.user_is_locked || !accountTarget?.user_is_active ? '● Tài khoản đang bị khóa' : '● Đang hoạt động bình thường' }}
              </span>
            </div>
            <button
              type="button"
              @click="handleToggleLockInModal"
              :class="accountTarget?.user_is_locked || !accountTarget?.user_is_active ? 'btn-toggle-unlock' : 'btn-toggle-lock'"
              :disabled="lockLoading"
            >
              <Unlock v-if="accountTarget?.user_is_locked || !accountTarget?.user_is_active" class="w-3.5 h-3.5 mr-1" />
              <Lock v-else class="w-3.5 h-3.5 mr-1" />
              <span>{{ accountTarget?.user_is_locked || !accountTarget?.user_is_active ? 'Mở khóa ngay' : 'Khóa tài khoản' }}</span>
            </button>
          </div>

          <div class="modal-actions">
            <button
              type="button"
              @click="openResetPasswordModal(accountTarget); showAccountModal = false;"
              class="btn-secondary mr-auto"
            >
              <Key class="w-3.5 h-3.5 mr-1" />
              <span>Đặt lại mật khẩu...</span>
            </button>
            <button type="button" @click="showAccountModal = false" class="btn-secondary">
              Hủy
            </button>
            <button type="submit" :disabled="accountLoading" class="btn-primary">
              <Save class="w-4 h-4 mr-1.5" />
              <span>{{ accountLoading ? 'Đang lưu...' : 'Lưu thông tin' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { api } from '../api';
import {
  UserCheck,
  RefreshCw,
  Plus,
  Search,
  Lock,
  Unlock,
  Key,
  ShieldCheck,
  ShieldAlert,
  Settings,
  Eye,
  EyeOff,
  Save,
  Building,
  UserPlus,
  X,
  AlertCircle,
  Trash2,
  Hash
} from '@lucide/vue';
import { useToast } from '../composables/useToast';
import { useConfirm } from '../composables/useConfirm';

const route = useRoute();
const router = useRouter();

const toast = useToast();
const { confirm } = useConfirm();

const props = defineProps({
  currentUser: Object
});

const emit = defineEmits(['profile-updated']);

const loading = ref(false);
const saving = ref(false);
const employeesList = ref([]);
const selectedProfile = ref(null);
const isEditing = ref(false);
const editForm = ref({});
const searchQuery = ref('');
const filterDept = ref('');

// Add Modal State
const showAddModal = ref(false);
const addLoading = ref(false);
const addError = ref('');
const addForm = ref({
  employee_code: '',
  full_name: '',
  department: 'Phòng Công nghệ & Phần mềm',
  position: 'Chuyên viên Kỹ thuật',
  phone: '0912345678',
  email: '',
  identity_card: '001198000999',
  basic_salary: 16000000,
  salary_coefficient: 1.8,
  password: 'Employee@123'
});

// Account & Security Management State
const showResetModal = ref(false);
const resetTarget = ref(null);
const resetPassword = ref('');
const showPasswordText = ref(false);
const resetLoading = ref(false);
const resetError = ref('');

// Password Visibility States
const showCurrentPasswordInDetail = ref(false);
const showCurrentPasswordInModal = ref(false);
const showCurrentPasswordInAccModal = ref(false);
const revealedTablePwds = ref({});

function toggleTablePwd(empId) {
  revealedTablePwds.value[empId] = !revealedTablePwds.value[empId];
}

const showAccountModal = ref(false);
const accountTarget = ref(null);
const accountForm = ref({
  username: '',
  role: 'EMPLOYEE'
});
const accountLoading = ref(false);
const accountError = ref('');
const lockLoading = ref(false);

const isStaffRole = computed(() => {
  return ['ADMIN', 'HR', 'ACCOUNTANT'].includes(props.currentUser?.role);
});

const isHRorAdmin = computed(() => {
  return ['ADMIN', 'HR'].includes(props.currentUser?.role);
});

const isEmployeeRole = computed(() => {
  return props.currentUser?.role === 'EMPLOYEE';
});

const canEditCurrentProfile = computed(() => {
  if (isHRorAdmin.value) return true;
  if (isEmployeeRole.value) return true;
  return false;
});

const filteredEmployees = computed(() => {
  let list = employeesList.value;
  if (filterDept.value) {
    list = list.filter(e => e.department === filterDept.value);
  }
  return list;
});

let debounceTimer = null;
function debounceSearch() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    loadData();
  }, 350);
}

async function loadData() {
  loading.value = true;
  try {
    const params = {};
    if (searchQuery.value) params.search = searchQuery.value;

    const data = await api.getEmployees(params);
    const list = Array.isArray(data) ? data : (data.results || []);

    if (isStaffRole.value) {
      employeesList.value = list;
      if (route.params.id) {
        const targetId = Number(route.params.id);
        const found = list.find(e => e.id === targetId);
        if (found) {
          selectedProfile.value = found;
          initEditForm(found);
        } else {
          try {
            const single = await api.getEmployeeById(targetId);
            selectedProfile.value = single;
            initEditForm(single);
          } catch (e) {
            toast.error(e.data?.error || e.message || `Không tìm thấy hồ sơ nhân sự #${targetId}`, 'Không tìm thấy');
            router.replace('/profile');
          }
        }
      } else {
        selectedProfile.value = null;
      }
    } else {
      // Vai trò EMPLOYEE (Chỉ xem và sửa hồ sơ của chính mình)
      const ownProfile = list.length > 0 ? list[0] : null;
      if (route.params.id) {
        const targetId = Number(route.params.id);
        if (ownProfile && targetId === ownProfile.id) {
          selectedProfile.value = ownProfile;
          initEditForm(ownProfile);
        } else {
          try {
            const single = await api.getEmployeeById(targetId);
            selectedProfile.value = single;
            initEditForm(single);
          } catch (err) {
            toast.error(err.data?.error || err.message || `Từ chối truy cập hồ sơ #${targetId} (403 Forbidden)`, 'Cảnh báo an ninh IDOR');
            if (ownProfile) {
              selectedProfile.value = ownProfile;
              initEditForm(ownProfile);
              router.replace(`/profile/${ownProfile.id}`);
            }
          }
        }
      } else {
        // Chưa có ID trên URL, tự động cập nhật URL thành /profile/:id
        if (ownProfile) {
          selectedProfile.value = ownProfile;
          initEditForm(ownProfile);
          router.replace(`/profile/${ownProfile.id}`);
        }
      }
    }
  } catch (err) {
    console.error('Lỗi tải hồ sơ nhân viên:', err);
  } finally {
    loading.value = false;
  }
}

function viewDetail(emp) {
  router.push(`/profile/${emp.id}`);
}

function goBackToList() {
  selectedProfile.value = null;
  isEditing.value = false;
  router.push('/profile');
}

watch(() => route.params.id, async (newId) => {
  if (isStaffRole.value) {
    if (!newId) {
      selectedProfile.value = null;
      isEditing.value = false;
    } else {
      const targetId = Number(newId);
      const found = employeesList.value.find(e => e.id === targetId);
      if (found) {
        selectedProfile.value = found;
        initEditForm(found);
        isEditing.value = false;
      } else {
        try {
          const single = await api.getEmployeeById(targetId);
          selectedProfile.value = single;
          initEditForm(single);
          isEditing.value = false;
        } catch (err) {
          toast.error(err.data?.error || err.message || `Không thể xem hồ sơ #${targetId}`, 'Từ chối truy cập (403)');
          router.replace('/profile');
        }
      }
    }
  } else {
    // Vai trò EMPLOYEE
    if (!newId) {
      if (selectedProfile.value?.id) {
        router.replace(`/profile/${selectedProfile.value.id}`);
      }
    } else {
      const targetId = Number(newId);
      if (selectedProfile.value?.id === targetId) {
        // Đã đúng profile hiện tại
      } else {
        try {
          const single = await api.getEmployeeById(targetId);
          selectedProfile.value = single;
          initEditForm(single);
          isEditing.value = false;
        } catch (err) {
          toast.error(err.data?.error || err.message || `Từ chối truy cập hồ sơ #${targetId} (403 Forbidden)`, 'Cảnh báo an ninh IDOR');
          if (selectedProfile.value?.id) {
            router.replace(`/profile/${selectedProfile.value.id}`);
          }
        }
      }
    }
  }
});

function initEditForm(data) {
  editForm.value = { ...data };
}

function startEdit() {
  initEditForm(selectedProfile.value);
  isEditing.value = true;
  if (selectedProfile.value?.id && route.params.id !== String(selectedProfile.value.id)) {
    router.replace(`/profile/${selectedProfile.value.id}`);
  }
}

function cancelEdit() {
  initEditForm(selectedProfile.value);
  isEditing.value = false;
  if (selectedProfile.value?.id && route.params.id !== String(selectedProfile.value.id)) {
    router.replace(`/profile/${selectedProfile.value.id}`);
  }
}

async function saveProfile() {
  saving.value = true;
  try {
    const payload = {};
    if (isHRorAdmin.value) {
      Object.assign(payload, editForm.value);
    } else {
      payload.phone = editForm.value.phone;
      payload.address = editForm.value.address;
      payload.bank_account = editForm.value.bank_account;
      payload.bank_name = editForm.value.bank_name;
    }

    const updated = await api.updateEmployee(selectedProfile.value.id, payload);
    selectedProfile.value = updated;
    isEditing.value = false;
    emit('profile-updated');
    await loadData();
    toast.success('Cập nhật hồ sơ thành công! Sự kiện đã được ghi nhận vào Audit Log.', 'Hồ sơ nhân viên');
  } catch (err) {
    toast.error(err.data?.error || err.message || 'Lỗi khi cập nhật hồ sơ', 'Cập nhật thất bại');
  } finally {
    saving.value = false;
  }
}

function openAddModal() {
  const nextNum = employeesList.value.length + 1;
  addForm.value = {
    employee_code: `EMP00${nextNum}`,
    full_name: '',
    department: 'Phòng Công nghệ & Phần mềm',
    position: 'Chuyên viên Kỹ thuật',
    phone: '0912345678',
    email: '',
    identity_card: `001198000${nextNum}${nextNum}${nextNum}`,
    basic_salary: 16000000,
    salary_coefficient: 1.8,
    password: 'Employee@123'
  };
  addError.value = '';
  showAddModal.value = true;
}

async function handleCreateEmployee() {
  addLoading.value = true;
  addError.value = '';
  try {
    const res = await api.createEmployee(addForm.value);
    showAddModal.value = false;
    emit('profile-updated');
    await loadData();
    if (res && res.id) {
      router.push(`/profile/${res.id}`);
    }
    toast.success(`Đã thêm thành công nhân viên ${addForm.value.full_name} (${addForm.value.employee_code})!`, 'Tạo nhân viên mới');
  } catch (err) {
    const msg = err.data?.error || err.data?.detail || err.message || 'Không thể tạo nhân sự mới';
    addError.value = msg;
    toast.error(msg, 'Tạo nhân sự thất bại');
  } finally {
    addLoading.value = false;
  }
}

async function deleteCurrentProfile() {
  if (!selectedProfile.value) return;
  const target = selectedProfile.value;
  const confirmed = await confirm({
    title: 'Xóa hồ sơ nhân viên',
    message: `Bạn có chắc chắn muốn xóa hồ sơ nhân viên "${target.full_name}" (${target.employee_code}) khỏi hệ thống?`,
    detail: 'Toàn bộ dữ liệu hồ sơ, hợp đồng và lịch sử liên quan sẽ bị xóa vĩnh viễn. Hành động này không thể hoàn tác.',
    confirmText: 'Xác nhận xóa',
    cancelText: 'Hủy bỏ',
    type: 'danger'
  });
  if (!confirmed) return;

  try {
    await api.deleteEmployee(target.id);
    selectedProfile.value = null;
    isEditing.value = false;
    emit('profile-updated');
    router.push('/profile');
    await loadData();
    toast.success(`Đã xóa thành công nhân viên ${target.full_name} khỏi hệ thống.`, 'Đã xóa hồ sơ');
  } catch (err) {
    toast.error(err.data?.error || err.message || 'Lỗi khi xóa nhân viên', 'Xóa thất bại');
  }
}

async function deleteEmployeeDirect(emp) {
  const confirmed = await confirm({
    title: 'Xóa hồ sơ nhân viên',
    message: `Bạn có chắc chắn muốn xóa hồ sơ nhân viên "${emp.full_name}" (${emp.employee_code})?`,
    detail: 'Dữ liệu nhân sự sẽ bị gỡ bỏ khỏi hệ thống và lưu vết vi phạm/thao tác vào Audit Log.',
    confirmText: 'Xác nhận xóa',
    cancelText: 'Hủy bỏ',
    type: 'danger'
  });
  if (!confirmed) return;

  try {
    await api.deleteEmployee(emp.id);
    if (selectedProfile.value?.id === emp.id) {
      selectedProfile.value = null;
      router.push('/profile');
    }
    emit('profile-updated');
    await loadData();
    toast.success(`Đã xóa nhân viên ${emp.full_name} (${emp.employee_code}) thành công.`, 'Đã xóa nhân viên');
  } catch (err) {
    toast.error(err.data?.error || err.message || 'Lỗi khi xóa nhân viên', 'Xóa thất bại');
  }
}

function formatDateTime(val) {
  if (!val) return 'Chưa có thông tin';
  const d = new Date(val);
  return d.toLocaleString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function openResetPasswordModal(emp) {
  resetTarget.value = emp;
  resetPassword.value = '';
  resetError.value = '';
  showPasswordText.value = false;
  showCurrentPasswordInModal.value = false;
  showResetModal.value = true;
}

async function handleConfirmResetPassword() {
  if (!resetTarget.value) return;
  if (!resetPassword.value || resetPassword.value.length < 6) {
    resetError.value = 'Mật khẩu phải có độ dài tối thiểu 6 ký tự.';
    return;
  }
  resetLoading.value = true;
  resetError.value = '';
  try {
    const res = await api.resetEmployeePassword(resetTarget.value.id, resetPassword.value);
    toast.success(res.message || 'Đặt lại mật khẩu thành công!', 'Bảo mật tài khoản');
    showResetModal.value = false;
    await loadData();
    if (selectedProfile.value?.id === resetTarget.value.id) {
      const refreshed = await api.getEmployeeById(resetTarget.value.id);
      selectedProfile.value = refreshed;
    }
  } catch (err) {
    const msg = err.data?.error || err.data?.detail || err.message || 'Lỗi đặt lại mật khẩu';
    resetError.value = msg;
    toast.error(msg, 'Thao tác thất bại');
  } finally {
    resetLoading.value = false;
  }
}

function openAccountModal(emp) {
  accountTarget.value = emp;
  accountForm.value = {
    username: emp.username || '',
    role: emp.user_role || 'EMPLOYEE'
  };
  accountError.value = '';
  showCurrentPasswordInAccModal.value = false;
  showAccountModal.value = true;
}

async function handleSaveAccountModal() {
  if (!accountTarget.value) return;
  if (!accountForm.value.username.trim()) {
    accountError.value = 'Tên đăng nhập không được để trống.';
    return;
  }
  accountLoading.value = true;
  accountError.value = '';
  try {
    await api.updateEmployeeAccount(accountTarget.value.id, {
      username: accountForm.value.username.trim(),
      role: accountForm.value.role
    });
    toast.success('Cập nhật thông tin tài khoản thành công!', 'Quản lý tài khoản');
    showAccountModal.value = false;
    await loadData();
    if (selectedProfile.value?.id === accountTarget.value.id) {
      const refreshed = await api.getEmployeeById(accountTarget.value.id);
      selectedProfile.value = refreshed;
    }
  } catch (err) {
    const msg = err.data?.error || err.data?.detail || err.message || 'Lỗi cập nhật tài khoản';
    accountError.value = msg;
    toast.error(msg, 'Thao tác thất bại');
  } finally {
    accountLoading.value = false;
  }
}

async function handleToggleLock(emp) {
  if (!emp) return;
  const isCurrentlyLocked = emp.user_is_locked || !emp.user_is_active;
  const actionName = isCurrentlyLocked ? 'mở khóa' : 'khóa';
  const confirmed = await confirm({
    title: `${isCurrentlyLocked ? 'Mở khóa' : 'Khóa'} tài khoản nhân viên`,
    message: `Bạn có chắc chắn muốn ${actionName} tài khoản đăng nhập của "${emp.full_name}" (${emp.username || emp.employee_code})?`,
    detail: isCurrentlyLocked
      ? 'Sau khi mở khóa, tài khoản được kích hoạt lại và nhân viên có thể đăng nhập bình thường.'
      : 'Tài khoản sẽ bị tạm khóa và nhân viên không thể đăng nhập cho đến khi được mở khóa.',
    confirmText: isCurrentlyLocked ? 'Mở khóa ngay' : 'Khóa tài khoản',
    cancelText: 'Hủy bỏ',
    type: isCurrentlyLocked ? 'primary' : 'danger'
  });
  if (!confirmed) return;

  lockLoading.value = true;
  try {
    const res = await api.toggleEmployeeLock(emp.id);
    toast.success(res.message || `Đã ${actionName} tài khoản thành công!`, 'Trạng thái tài khoản');
    await loadData();
    if (selectedProfile.value?.id === emp.id) {
      const refreshed = await api.getEmployeeById(emp.id);
      selectedProfile.value = refreshed;
    }
    if (accountTarget.value?.id === emp.id) {
      const refreshed = await api.getEmployeeById(emp.id);
      accountTarget.value = refreshed;
    }
  } catch (err) {
    const msg = err.data?.error || err.data?.detail || err.message || `Lỗi khi ${actionName} tài khoản`;
    toast.error(msg, 'Thao tác thất bại');
  } finally {
    lockLoading.value = false;
  }
}

async function handleToggleLockInModal() {
  if (!accountTarget.value) return;
  await handleToggleLock(accountTarget.value);
}

function formatMoney(amount) {
  if (!amount) return '0 ₫';
  return Number(amount).toLocaleString('vi-VN') + ' ₫';
}

onMounted(() => {
  loadData();
});

defineExpose({ loadData });
</script>

<style scoped>
.profile-wrap {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1480px;
  margin: 0 auto;
  padding: 24px;
}

/* Header */
.profile-header {
  padding: 24px 28px;
  background: #ffffff;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-icon-box {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-md);
  background: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-header h2 {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text);
}

.subtitle {
  font-size: 0.86rem;
  color: var(--text-muted);
  margin-top: 2px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

/* Search Bar */
.search-filter-bar {
  padding: 14px 20px;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  flex: 1;
  min-width: 260px;
  display: flex;
  align-items: center;
}

.search-box .input-icon {
  position: absolute;
  left: 12px;
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 8px 12px 8px 36px;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.88rem;
  color: var(--text);
  outline: none;
  transition: var(--transition-fast);
}

.search-input:focus {
  background: #ffffff;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(91, 99, 211, 0.12);
}

.select-control {
  padding: 8px 14px;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.86rem;
  color: var(--text);
  outline: none;
}

/* Table */
.table-container {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.table-responsive {
  overflow-x: auto;
}

.soc-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.86rem;
}

.soc-table th {
  text-align: left;
  padding: 12px 16px;
  background: #f8fafc;
  border-bottom: 1px solid var(--border);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.soc-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-light);
  color: var(--text);
  vertical-align: middle;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar-mini {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-xs);
  background: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.78rem;
}

.code-pill {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  color: #334155;
  font-weight: 600;
  font-size: 0.78rem;
}

.dept-tag {
  font-size: 0.78rem;
  color: var(--text-muted);
}

.pos-tag {
  font-size: 0.82rem;
  font-weight: 500;
}

.salary-cell {
  font-weight: 700;
  color: #059669;
}

.rate-badge {
  background: #f0fdf4;
  color: #16a34a;
  border: 1px solid #bbf7d0;
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  font-size: 0.75rem;
  font-weight: 600;
}

.action-buttons-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-table-action {
  padding: 5px 10px;
  font-size: 0.76rem;
  font-weight: 600;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-xs);
  cursor: pointer;
  color: var(--primary);
  transition: var(--transition-fast);
}

.btn-table-action:hover {
  background: var(--primary-light);
  border-color: var(--primary);
}

.btn-delete-row {
  color: #dc2626;
  padding: 5px 8px;
}

.btn-delete-row:hover {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #b91c1c;
}

/* Detail View */
.detail-card-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.btn-back {
  background: none;
  border: none;
  color: var(--primary);
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  padding: 4px 0;
}

.btn-back:hover {
  text-decoration: underline;
}

.top-nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-indicator-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.76rem;
  padding: 4px 10px;
  background: #dcfce7;
  color: #15803d;
  border-radius: var(--radius-xs);
  font-weight: 600;
}

.dot-green {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #16a34a;
}

.btn-edit-mode {
  padding: 6px 14px;
  font-size: 0.82rem;
  font-weight: 600;
  background: var(--primary);
  color: #ffffff;
  border: none;
  border-radius: var(--radius-xs);
  cursor: pointer;
}

.btn-delete-profile {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  font-size: 0.82rem;
  font-weight: 600;
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fecdd3;
  border-radius: var(--radius-xs);
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-delete-profile:hover {
  background: #fecdd3;
}

.profile-cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.profile-card {
  padding: 24px;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.card-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-light);
}

.card-head h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text);
}

.detail-form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.detail-form-group label {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

.detail-row-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.input-detail {
  width: 100%;
  padding: 9px 12px;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.88rem;
  color: var(--text);
  outline: none;
  transition: var(--transition-fast);
}

.input-detail:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(91, 99, 211, 0.12);
}

.locked-field {
  background: #f8fafc;
  color: var(--text-muted);
  cursor: not-allowed;
}

.textarea-detail {
  resize: vertical;
}

.label-with-guard {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.guard-pill {
  font-size: 0.68rem;
  padding: 1px 6px;
  background: #f1f5f9;
  color: var(--text-muted);
  border-radius: var(--radius-xs);
  font-weight: 600;
}

.edit-actions-bar {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
  padding-top: 14px;
  border-top: 1px solid var(--border-light);
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
  max-width: 680px;
  background: #ffffff;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-xl);
  padding: 28px 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
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

.btn-close-modal {
  margin-left: auto;
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

.modal-error-banner {
  background: #fff1f2;
  border: 1px solid #fecdd3;
  color: #e11d48;
  font-size: 0.84rem;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
}

.modal-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px 20px;
  width: 100%;
  box-sizing: border-box;
}

.form-group-clean {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  width: 100%;
  box-sizing: border-box;
}

.form-group-clean label {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-dim);
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid var(--border-light);
}

.id-badge-banner {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.25);
  border-radius: var(--radius-full);
  color: var(--primary);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.id-pill {
  color: var(--primary);
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.2);
  font-weight: 700;
}

.th-id {
  width: 70px;
}

/* Account Info in Table */
.account-cell-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.account-username {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.84rem;
  color: var(--text);
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-active {
  background: #10b981;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.5);
}

.dot-locked {
  background: #ef4444;
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.5);
}

.account-badges {
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
}

.role-badge {
  font-size: 0.7rem;
  background: #f1f5f9;
  color: #475569;
  padding: 1px 6px;
  border-radius: var(--radius-xs);
  font-weight: 600;
  border: 1px solid #e2e8f0;
}

.lock-mini-badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.68rem;
  background: #fee2e2;
  color: #b91c1c;
  padding: 1px 5px;
  border-radius: var(--radius-xs);
  font-weight: 700;
  border: 1px solid #fca5a5;
}

.btn-account-action {
  color: #2563eb;
  background: #eff6ff;
  border-color: #bfdbfe;
  display: inline-flex;
  align-items: center;
}

.btn-account-action:hover {
  background: #dbeafe;
  border-color: #2563eb;
}

/* Card 3: Account & Security Management */
.account-mgmt-card {
  margin-top: 6px;
  border-top: 2px solid var(--primary);
  background: #ffffff;
}

.head-icon-shield {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
}

.head-icon-key {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
}

.head-icon-settings {
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
}

.card-head-title {
  flex: 1;
}

.card-sub-hint {
  font-size: 0.78rem;
  color: var(--text-muted), #64748b;
  margin-top: 2px;
}

.card-head-badge {
  margin-left: auto;
}

.security-status-badge {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  border-radius: var(--radius-full);
  font-size: 0.76rem;
  font-weight: 700;
}

.badge-active {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.badge-locked {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.account-details-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px 20px;
  padding: 16px 20px;
  background: #f8fafc;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
}

.account-detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

.detail-value {
  font-size: 0.88rem;
  color: var(--text);
}

.role-pill {
  display: inline-block;
  background: #e0e7ff;
  color: #3730a3;
  padding: 2px 8px;
  border-radius: var(--radius-xs);
  font-weight: 700;
  font-size: 0.8rem;
  border: 1px solid #c7d2fe;
}

.text-success {
  color: #059669;
}

.text-danger {
  color: #dc2626;
}

.account-actions-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  padding-top: 14px;
  border-top: 1px solid var(--border-light);
}

.btn-account-action-primary {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: var(--primary);
  color: #ffffff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-account-action-primary:hover {
  background: #1d4ed8;
}

.btn-account-action-lock {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
  border-radius: var(--radius-sm);
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-account-action-lock:hover:not(:disabled) {
  background: #fecdd3;
}

.btn-account-action-unlock {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #86efac;
  border-radius: var(--radius-sm);
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-account-action-unlock:hover:not(:disabled) {
  background: #bbf7d0;
}

.btn-account-action-secondary {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background: #ffffff;
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-account-action-secondary:hover {
  background: #f8fafc;
  border-color: var(--text-muted);
}

/* Modals */
.modal-card-sm {
  max-width: 520px;
}

.account-modal-target-box {
  padding: 12px 16px;
  background: #f1f5f9;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-light);
}

.target-name {
  font-size: 0.96rem;
  font-weight: 700;
  color: var(--text);
}

.target-meta {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin-top: 3px;
}

.label-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-text-link {
  display: inline-flex;
  align-items: center;
  background: none;
  border: none;
  color: var(--primary);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}

.btn-text-link:hover {
  text-decoration: underline;
}

.password-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrap input {
  padding-right: 40px;
}

.btn-toggle-eye {
  position: absolute;
  right: 10px;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-toggle-eye:hover {
  color: var(--text);
}

.security-reset-notice {
  display: flex;
  align-items: flex-start;
  padding: 10px 14px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: var(--radius-sm);
  font-size: 0.78rem;
  color: #1e40af;
  line-height: 1.45;
}

.field-hint {
  font-size: 0.74rem;
  color: var(--text-muted);
  margin-top: 2px;
}

.account-modal-status-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  gap: 12px;
}

.status-box-title {
  font-size: 0.74rem;
  font-weight: 700;
  color: var(--text-muted);
  display: block;
}

.status-box-desc {
  font-size: 0.82rem;
  font-weight: 700;
  display: block;
  margin-top: 2px;
}

.btn-toggle-lock {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
  border-radius: var(--radius-xs);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-toggle-lock:hover:not(:disabled) {
  background: #fecdd3;
}

.btn-toggle-unlock {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  background: #dcfce7;
  color: #15803d;
  border: 1px solid #86efac;
  border-radius: var(--radius-xs);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-toggle-unlock:hover:not(:disabled) {
  background: #bbf7d0;
}

.select-uupm {
  width: 100%;
  padding: 9px 12px;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.88rem;
  color: var(--text);
  outline: none;
}

.select-uupm:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(91, 99, 211, 0.12);
}

/* Password Preview in Table */
.account-pwd-preview {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.74rem;
  color: var(--text-muted);
}

.pwd-preview-label {
  font-weight: 700;
  color: var(--text-muted);
  font-size: 0.68rem;
}

.pwd-preview-val {
  padding: 1px 5px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: var(--radius-xs);
  color: var(--primary);
  font-weight: 600;
}

.pwd-preview-dots {
  letter-spacing: 2px;
  color: var(--text-muted);
}

.btn-mini-eye {
  background: none;
  border: none;
  cursor: pointer;
  padding: 1px 3px;
  display: inline-flex;
  align-items: center;
  border-radius: var(--radius-xs);
  transition: var(--transition-fast);
}

.btn-mini-eye:hover {
  background: #f1f5f9;
}

/* Password View in Detail Card */
.btn-reveal-pwd {
  display: inline-flex;
  align-items: center;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: var(--radius-xs);
  padding: 2px 7px;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text);
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-reveal-pwd:hover {
  background: #e2e8f0;
  color: var(--primary);
}

.pwd-revealed-badge {
  padding: 3px 8px;
  background: #ecfdf5;
  color: #065f46;
  border: 1px solid #a7f3d0;
  border-radius: var(--radius-xs);
  font-size: 0.86rem;
  letter-spacing: 0.02em;
}

.pwd-masked-text {
  letter-spacing: 3px;
  color: var(--text-muted);
  font-size: 0.95rem;
}

/* Current Password Box in Modals */
.current-pwd-box {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px dashed var(--border);
  font-size: 0.76rem;
}

.curr-pwd-title {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.04em;
}

.curr-pwd-text {
  padding: 2px 6px;
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  border-radius: var(--radius-xs);
  font-weight: 700;
  color: var(--primary);
}

.curr-pwd-masked {
  letter-spacing: 2px;
  color: var(--text-muted);
}

.btn-reveal-pwd-mini {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: var(--radius-xs);
  padding: 2px 6px;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  margin-left: auto;
}

.btn-reveal-pwd-mini:hover {
  background: #f8fafc;
  color: var(--primary);
  border-color: var(--primary);
}

@media (max-width: 900px) {
  .account-details-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1024px) {
  .profile-cards-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .modal-form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
