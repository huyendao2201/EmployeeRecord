<template>
  <div class="contracts-wrap">
    <!-- Header -->
    <div class="contracts-header card-uupm">
      <div class="header-left">
        <div class="header-icon-box">
          <FileText class="w-6 h-6 text-emerald" />
        </div>
        <div>
          <h2>Danh sách Hợp đồng Lao động</h2>
          <p class="subtitle">
            Quản lý và tra cứu thông tin hợp đồng lao động của nhân sự.
          </p>
        </div>
      </div>
      <div class="header-actions">
        <button
          v-if="isHRorAdmin"
          @click="openAddModal"
          class="btn-primary"
        >
          <Plus class="w-4 h-4 mr-1.5" />
          <span>Thêm Hợp đồng mới</span>
        </button>
        <button @click="loadContracts" :disabled="loading" class="btn-secondary">
          <RefreshCw class="w-4 h-4 mr-2" :class="{ spin: loading }" />
          <span>Làm mới Danh sách</span>
        </button>
      </div>
    </div>

    <!-- Search & Filter Bar -->
    <div class="search-filter-bar card-uupm">
      <div class="search-box">
        <Search class="w-4 h-4 text-muted input-icon" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Tìm theo Số HĐ, Tên nhân viên, Mã NV..."
          class="search-input"
        />
      </div>

      <div class="filter-controls">
        <select v-model="filterType" class="select-control">
          <option value="">Tất cả loại hợp đồng</option>
          <option value="PROBATION">Thử việc (2 tháng)</option>
          <option value="ONE_YEAR">Xác định thời hạn (1 năm)</option>
          <option value="THREE_YEAR">Xác định thời hạn (3 năm)</option>
          <option value="INDEFINITE">Không xác định thời hạn</option>
        </select>

        <select v-model="filterStatus" class="select-control">
          <option value="">Tất cả trạng thái</option>
          <option value="ACTIVE">Hiệu lực</option>
          <option value="EXPIRED">Hết hạn</option>
          <option value="TERMINATED">Đã chấm dứt</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && contractsList.length === 0" class="loading-state">
      <RefreshCw class="w-8 h-8 spin text-primary" />
      <span>Đang tải dữ liệu hợp đồng...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredContracts.length === 0" class="empty-state card-uupm">
      <FileText class="w-12 h-12 text-muted" />
      <h3>Không tìm thấy Hợp đồng Lao động</h3>
      <p>Không có bản ghi hợp đồng nào phù hợp với bộ lọc hiện tại.</p>
    </div>

    <!-- Table -->
    <div v-else class="table-container card-uupm">
      <div class="table-responsive">
        <table class="soc-table">
          <thead>
            <tr>
              <th class="th-id">ID</th>
              <th>SỐ HỢP ĐỒNG</th>
              <th>NHÂN VIÊN KÝ KẾT</th>
              <th>MÃ NHÂN VIÊN</th>
              <th>LOẠI HỢP ĐỒNG</th>
              <th>NGÀY HIỆU LỰC</th>
              <th>NGÀY HẾT HẠN</th>
              <th>MỨC LƯƠNG CƠ SỞ</th>
              <th>TRẠNG THÁI</th>
              <th>TỆP ĐÍNH KÈM</th>
              <th>THAO TÁC</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in filteredContracts" :key="c.id">
              <td>
                <span class="code-pill font-mono id-pill">#{{ c.id }}</span>
              </td>
              <td>
                <span class="contract-code-pill font-mono">{{ c.contract_number }}</span>
              </td>
              <td class="name-cell font-medium">{{ c.employee_name }}</td>
              <td><span class="code-pill font-mono">{{ c.employee_code }}</span></td>
              <td><span class="type-tag">{{ c.contract_type_display }}</span></td>
              <td class="font-mono">{{ formatDate(c.start_date) }}</td>
              <td class="font-mono">{{ c.end_date ? formatDate(c.end_date) : 'Vô thời hạn' }}</td>
              <td class="salary-cell font-mono">{{ formatMoney(c.salary_rate) }}</td>
              <td>
                <span class="status-badge-contract font-mono" :class="'stat-' + c.status.toLowerCase()">
                  <CheckCircle2 class="w-3.5 h-3.5 mr-1" />
                  {{ c.status_display }}
                </span>
              </td>
              <td>
                <div v-if="c.contract_file" class="file-pill-group">
                  <button
                    @click="handleViewFile(c)"
                    class="btn-file-pill font-mono"
                    :title="'Xem trực tiếp tệp: ' + (c.contract_file_name || 'Hợp đồng')"
                  >
                    <Eye class="w-3.5 h-3.5 mr-1 text-primary flex-shrink-0" />
                    <span class="file-name-truncate">{{ c.contract_file_name || 'Xem tệp' }}</span>
                  </button>
                  <button
                    @click="handleDownloadFile(c)"
                    class="btn-icon-download"
                    :title="'Tải về máy: ' + (c.contract_file_name || 'Hợp đồng')"
                  >
                    <Download class="w-3.5 h-3.5" />
                  </button>
                </div>
                <span v-else class="no-file-tag">Chưa có tệp</span>
              </td>
              <td>
                <button
                  @click="viewContractDetail(c)"
                  class="btn-table-action"
                  :title="'Xem chi tiết hợp đồng #' + c.id"
                >
                  <Eye class="w-3.5 h-3.5 mr-1" />
                  <span>Chi tiết</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Contract Detail Modal -->
    <div
      v-if="selectedContract"
      class="modal-overlay animate-fade-in"
      @click.self="closeContractDetail"
    >
      <div class="modal-card detail-modal-card card-uupm">
        <div class="modal-header">
          <div class="header-icon-box">
            <FileText class="w-5 h-5 text-emerald" />
          </div>
          <div>
            <h3>Chi tiết Hợp đồng Lao động</h3>
            <span class="sub-label">Thông tin hợp đồng và hồ sơ pháp lý nhân sự</span>
          </div>
          <div class="header-right-badges">
            <span class="id-badge-banner font-mono">
              <Hash class="w-3.5 h-3.5 mr-1" />
              <span>ID Hợp đồng: #{{ selectedContract.id }}</span>
            </span>
            <button @click="closeContractDetail" class="btn-close-modal" title="Đóng">
              <X class="w-5 h-5" />
            </button>
          </div>
        </div>

        <div class="contract-detail-body">
          <div class="detail-row-2">
            <div class="form-group-clean">
              <label>ID HỆ THỐNG (PRIMARY KEY)</label>
              <div class="readonly-pill-box font-mono font-bold text-primary">
                #{{ selectedContract.id }}
              </div>
            </div>
            <div class="form-group-clean">
              <label>SỐ HỢP ĐỒNG</label>
              <div class="readonly-pill-box font-mono font-semibold">
                {{ selectedContract.contract_number }}
              </div>
            </div>
          </div>

          <div class="detail-row-2">
            <div class="form-group-clean">
              <label>NHÂN VIÊN KÝ KẾT</label>
              <div class="readonly-pill-box font-medium">
                {{ selectedContract.employee_name }}
              </div>
            </div>
            <div class="form-group-clean">
              <label>MÃ NHÂN VIÊN</label>
              <div class="readonly-pill-box font-mono">
                {{ selectedContract.employee_code }}
              </div>
            </div>
          </div>

          <div class="detail-row-2">
            <div class="form-group-clean">
              <label>LOẠI HỢP ĐỒNG</label>
              <div class="readonly-pill-box">
                {{ selectedContract.contract_type_display }}
              </div>
            </div>
            <div class="form-group-clean">
              <label>MỨC LƯƠNG CƠ SỞ</label>
              <div class="readonly-pill-box salary-cell font-mono">
                {{ formatMoney(selectedContract.salary_rate) }}
              </div>
            </div>
          </div>

          <div class="detail-row-2">
            <div class="form-group-clean">
              <label>NGÀY CÓ HIỆU LỰC</label>
              <div class="readonly-pill-box font-mono">
                {{ formatDate(selectedContract.start_date) }}
              </div>
            </div>
            <div class="form-group-clean">
              <label>NGÀY HẾT HẠN</label>
              <div class="readonly-pill-box font-mono">
                {{ selectedContract.end_date ? formatDate(selectedContract.end_date) : 'Không xác định thời hạn' }}
              </div>
            </div>
          </div>

          <div class="form-group-clean">
            <label>TRẠNG THÁI HIỆU LỰC</label>
            <div>
              <span class="status-badge-contract font-mono" :class="'stat-' + (selectedContract.status || '').toLowerCase()">
                <CheckCircle2 class="w-3.5 h-3.5 mr-1" />
                {{ selectedContract.status_display || selectedContract.status }}
              </span>
            </div>
          </div>

          <!-- Tệp đính kèm hợp đồng -->
          <div class="form-group-clean">
            <label>TỆP VĂN BẢN HỢP ĐỒNG ĐÍNH KÈM</label>
            <div v-if="selectedContract.contract_file" class="file-attachment-card">
              <div class="file-icon-box">
                <FileText class="w-6 h-6 text-emerald" />
              </div>
              <div class="file-info-box">
                <div class="file-name font-mono font-semibold">{{ selectedContract.contract_file_name || 'Tệp hợp đồng đã lưu' }}</div>
                <div class="file-meta text-xs text-muted">Định dạng hỗ trợ: PDF / Word / Ảnh | Đã lưu trữ an toàn</div>
              </div>
              <div class="file-actions">
                <button type="button" @click="handleViewFile(selectedContract)" class="btn-primary btn-sm">
                  <Eye class="w-4 h-4 mr-1.5" />
                  <span>Xem trực tiếp</span>
                </button>
                <button type="button" @click="handleDownloadFile(selectedContract)" class="btn-secondary btn-sm">
                  <Download class="w-4 h-4 mr-1.5" />
                  <span>Tải về máy</span>
                </button>
                <button v-if="isHRorAdmin" type="button" @click="triggerEditFileUpload" class="btn-secondary btn-sm" title="Thay đổi tệp đính kèm">
                  <Upload class="w-4 h-4 mr-1.5" />
                  <span>Thay tệp</span>
                </button>
                <input
                  v-if="isHRorAdmin"
                  ref="editFileInput"
                  type="file"
                  accept=".pdf,.doc,.docx,.png,.jpg,.jpeg"
                  class="hidden-file-input"
                  @change="handleEditFileSelected"
                />
              </div>
            </div>
            <div v-else class="no-file-card">
              <div class="no-file-info">
                <Paperclip class="w-5 h-5 text-muted mr-2" />
                <span class="text-sm text-muted">Hợp đồng này hiện chưa có tệp văn bản đính kèm.</span>
              </div>
              <button v-if="isHRorAdmin" type="button" @click="triggerEditFileUpload" class="btn-secondary btn-sm">
                <Upload class="w-4 h-4 mr-1.5" />
                <span>Tải tệp lên</span>
              </button>
              <input
                v-if="isHRorAdmin"
                ref="editFileInput"
                type="file"
                accept=".pdf,.doc,.docx,.png,.jpg,.jpeg"
                class="hidden-file-input"
                @change="handleEditFileSelected"
              />
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="closeContractDetail" class="btn-primary">
            <span>Đóng chi tiết</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Add Contract Modal (Admin / HR) -->
    <div v-if="showAddModal" class="modal-overlay animate-fade-in" @click.self="showAddModal = false">
      <div class="modal-card card-uupm">
        <div class="modal-header">
          <div class="header-icon-box">
            <FilePlus class="w-5 h-5 text-emerald" />
          </div>
          <div>
            <h3>Tạo Hợp đồng Lao động Mới</h3>
            <span class="sub-label">Ký kết và lưu trữ hồ sơ hợp đồng lao động điện tử</span>
          </div>
          <button @click="showAddModal = false" class="btn-close-modal" title="Đóng">
            <X class="w-5 h-5" />
          </button>
        </div>

        <div v-if="addError" class="modal-error-banner">
          <AlertCircle class="w-4 h-4 mr-2 flex-shrink-0" />
          <span>{{ addError }}</span>
        </div>

        <form @submit.prevent="handleCreateContract" class="modal-form">
          <div class="modal-form-grid">
            <div class="form-group-clean">
              <label>NHÂN VIÊN KÝ KẾT (*)</label>
              <select v-model="addForm.employee" required class="select-control">
                <option value="" disabled>-- Chọn nhân viên --</option>
                <option v-for="emp in employeesList" :key="emp.id" :value="emp.id">
                  {{ emp.employee_code }} - {{ emp.full_name }} ({{ emp.department }})
                </option>
              </select>
            </div>

            <div class="form-group-clean">
              <label>SỐ HỢP ĐỒNG (*)</label>
              <input
                v-model="addForm.contract_number"
                type="text"
                required
                class="input-uupm font-mono"
                placeholder="Ví dụ: HDLD-2024-006"
              />
            </div>

            <div class="form-group-clean">
              <label>LOẠI HỢP ĐỒNG</label>
              <select v-model="addForm.contract_type" class="select-control">
                <option value="PROBATION">Thử việc (2 tháng)</option>
                <option value="ONE_YEAR">Xác định thời hạn (1 năm)</option>
                <option value="THREE_YEAR">Xác định thời hạn (3 năm)</option>
                <option value="INDEFINITE">Không xác định thời hạn</option>
              </select>
            </div>

            <div class="form-group-clean">
              <label>MỨC LƯƠNG CƠ SỞ (VNĐ) (*)</label>
              <input
                v-model.number="addForm.salary_rate"
                type="number"
                step="500000"
                required
                class="input-uupm font-mono"
              />
            </div>

            <div class="form-group-clean">
              <label>NGÀY HIỆU LỰC (*)</label>
              <input
                v-model="addForm.start_date"
                type="date"
                required
                class="input-uupm font-mono"
              />
            </div>

            <div class="form-group-clean">
              <label>NGÀY HẾT HẠN</label>
              <input
                v-model="addForm.end_date"
                type="date"
                class="input-uupm font-mono"
              />
            </div>

            <!-- Trường tải lên tệp hợp đồng -->
            <div class="form-group-clean col-span-2">
              <label>TỆP ĐÍNH KÈM HỢP ĐỒNG (PDF, DOCX, ẢNH)</label>
              <div class="file-upload-dropzone" :class="{ 'has-file': !!addFile }">
                <input
                  type="file"
                  id="contract-file-input"
                  ref="addFileInputRef"
                  accept=".pdf,.doc,.docx,.png,.jpg,.jpeg"
                  class="hidden-file-input"
                  @change="onAddFileChanged"
                />
                <label for="contract-file-input" class="dropzone-label">
                  <div class="dropzone-icon">
                    <Upload v-if="!addFile" class="w-6 h-6 text-primary" />
                    <FileCheck v-else class="w-6 h-6 text-emerald" />
                  </div>
                  <div class="dropzone-text" v-if="!addFile">
                    <span class="dropzone-title">Nhấp để chọn tệp hoặc kéo thả tệp hợp đồng</span>
                    <span class="dropzone-sub">Chấp nhận .pdf, .doc, .docx, .png, .jpg (Tối đa 10MB)</span>
                  </div>
                  <div class="dropzone-text" v-else>
                    <span class="dropzone-title font-mono font-medium">{{ addFile.name }} ({{ formatFileSize(addFile.size) }})</span>
                    <span class="dropzone-sub text-emerald">Tệp hợp lệ sẵn sàng tải lên</span>
                  </div>
                </label>
                <button
                  v-if="addFile"
                  type="button"
                  @click="removeAddFile"
                  class="btn-remove-file"
                  title="Xóa tệp đã chọn"
                >
                  <X class="w-4 h-4 text-crimson" />
                </button>
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showAddModal = false" class="btn-secondary">Hủy bỏ</button>
            <button type="submit" :disabled="addLoading" class="btn-primary">
              <RefreshCw v-if="addLoading" class="w-4 h-4 mr-2 spin" />
              <FilePlus v-else class="w-4 h-4 mr-2" />
              <span>{{ addLoading ? 'Đang tạo hợp đồng...' : 'Ký & Lưu hợp đồng' }}</span>
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
  FileText,
  RefreshCw,
  CheckCircle2,
  Search,
  Plus,
  FilePlus,
  X,
  AlertCircle,
  Hash,
  Eye,
  Paperclip,
  Download,
  Upload,
  FileCheck
} from '@lucide/vue';
import { useToast } from '../composables/useToast';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const props = defineProps({
  currentUser: Object
});

const loading = ref(false);
const contractsList = ref([]);
const employeesList = ref([]);
const searchQuery = ref('');
const filterType = ref('');
const filterStatus = ref('');
const selectedContract = ref(null);

// File management states
const addFile = ref(null);
const addFileInputRef = ref(null);
const editFileInput = ref(null);

// Add Modal State
const showAddModal = ref(false);
const addLoading = ref(false);
const addError = ref('');
const addForm = ref({
  employee: '',
  contract_number: '',
  contract_type: 'ONE_YEAR',
  salary_rate: 18000000,
  start_date: new Date().toISOString().split('T')[0],
  end_date: ''
});

const isHRorAdmin = computed(() => {
  return ['ADMIN', 'HR'].includes(props.currentUser?.role);
});

const filteredContracts = computed(() => {
  let list = contractsList.value;
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(c =>
      (c.contract_number && c.contract_number.toLowerCase().includes(q)) ||
      (c.employee_name && c.employee_name.toLowerCase().includes(q)) ||
      (c.employee_code && c.employee_code.toLowerCase().includes(q))
    );
  }
  if (filterType.value) {
    list = list.filter(c => c.contract_type === filterType.value);
  }
  if (filterStatus.value) {
    list = list.filter(c => c.status === filterStatus.value);
  }
  return list;
});

async function loadContracts() {
  loading.value = true;
  try {
    const data = await api.getContracts();
    contractsList.value = Array.isArray(data) ? data : (data.results || []);

    if (isHRorAdmin.value) {
      try {
        const emps = await api.getEmployees();
        employeesList.value = Array.isArray(emps) ? emps : (emps.results || []);
      } catch (e) {
        // Ignore
      }
    }
    await syncSelectedFromRoute();
  } catch (err) {
    console.error('Lỗi tải hợp đồng:', err);
  } finally {
    loading.value = false;
  }
}

function viewContractDetail(c) {
  selectedContract.value = c;
  router.push(`/contracts/${c.id}`);
}

function closeContractDetail() {
  selectedContract.value = null;
  router.push('/contracts');
}

async function syncSelectedFromRoute() {
  if (route.params.id) {
    const targetId = Number(route.params.id);
    const found = contractsList.value.find(c => c.id === targetId);
    if (found) {
      selectedContract.value = found;
    } else {
      try {
        const data = await api.getContractById(targetId);
        selectedContract.value = data;
      } catch (err) {
        toast.error(err.data?.error || err.message || `Không tìm thấy hợp đồng #${targetId}`, 'Không tìm thấy');
        router.replace('/contracts');
      }
    }
  } else {
    selectedContract.value = null;
  }
}

watch(() => route.params.id, () => {
  syncSelectedFromRoute();
});

function openAddModal() {
  const nextNum = contractsList.value.length + 1;
  addForm.value = {
    employee: employeesList.value[0]?.id || '',
    contract_number: `HDLD-2024-00${nextNum}`,
    contract_type: 'ONE_YEAR',
    salary_rate: 18000000,
    start_date: new Date().toISOString().split('T')[0],
    end_date: ''
  };
  addFile.value = null;
  if (addFileInputRef.value) addFileInputRef.value.value = '';
  addError.value = '';
  showAddModal.value = true;
}

function onAddFileChanged(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  const validExts = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg'];
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!validExts.includes(ext)) {
    toast.warning('Định dạng tệp không được hỗ trợ. Vui lòng chọn .pdf, .doc, .docx, .png, .jpg', 'Tệp không hợp lệ');
    e.target.value = '';
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    toast.warning('Dung lượng tệp vượt quá giới hạn tối đa 10MB.', 'Tệp quá lớn');
    e.target.value = '';
    return;
  }
  addFile.value = file;
}

function removeAddFile() {
  addFile.value = null;
  if (addFileInputRef.value) addFileInputRef.value.value = '';
}

async function handleCreateContract() {
  if (!addForm.value.employee) {
    addError.value = 'Vui lòng chọn nhân viên ký kết.';
    toast.warning('Vui lòng chọn nhân viên ký kết.', 'Thiếu thông tin');
    return;
  }
  addLoading.value = true;
  addError.value = '';
  try {
    const formData = new FormData();
    formData.append('employee', addForm.value.employee);
    formData.append('contract_number', addForm.value.contract_number);
    formData.append('contract_type', addForm.value.contract_type);
    formData.append('salary_rate', addForm.value.salary_rate);
    formData.append('start_date', addForm.value.start_date);
    if (addForm.value.end_date) {
      formData.append('end_date', addForm.value.end_date);
    }
    if (addFile.value) {
      formData.append('contract_file', addFile.value);
    }

    await api.createContract(formData);
    showAddModal.value = false;
    addFile.value = null;
    await loadContracts();
    toast.success('Tạo hợp đồng lao động và lưu trữ tệp thành công!', 'Hợp đồng lao động');
  } catch (err) {
    const msg = err.data?.error || err.data?.detail || err.message || 'Lỗi khi tạo hợp đồng';
    addError.value = msg;
    toast.error(msg, 'Tạo hợp đồng thất bại');
  } finally {
    addLoading.value = false;
  }
}

function handleViewFile(contract) {
  if (!contract || !contract.id) return;
  const viewUrl = api.getContractViewUrl(contract.id);
  window.open(viewUrl, '_blank');
}

async function handleDownloadFile(contract) {
  if (!contract || !contract.id) return;
  try {
    const fname = contract.contract_file_name || `HDLD_${contract.contract_number}.pdf`;
    await api.downloadContractFile(contract.id, fname);
    toast.success(`Đang tải xuống tệp: ${fname}`, 'Tải tệp thành công');
  } catch (err) {
    toast.error(err.message || 'Không thể tải tệp đính kèm.', 'Lỗi tải tệp');
  }
}

function triggerEditFileUpload() {
  editFileInput.value?.click();
}

async function handleEditFileSelected(e) {
  const file = e.target.files?.[0];
  if (!file || !selectedContract.value) return;
  const validExts = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg'];
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!validExts.includes(ext)) {
    toast.warning('Định dạng tệp không được hỗ trợ. Vui lòng chọn .pdf, .doc, .docx, .png, .jpg', 'Tệp không hợp lệ');
    e.target.value = '';
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    toast.warning('Dung lượng tệp vượt quá giới hạn tối đa 10MB.', 'Tệp quá lớn');
    e.target.value = '';
    return;
  }
  try {
    const formData = new FormData();
    formData.append('contract_file', file);
    const updated = await api.updateContract(selectedContract.value.id, formData);
    selectedContract.value = updated;
    await loadContracts();
    toast.success('Đã tải lên và lưu trữ tệp hợp đồng mới thành công!', 'Cập nhật tệp đính kèm');
  } catch (err) {
    toast.error(err.message || 'Không thể tải lên tệp.', 'Lỗi cập nhật tệp');
  } finally {
    e.target.value = '';
  }
}

function formatFileSize(bytes) {
  if (!bytes) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function formatDate(dStr) {
  if (!dStr) return '-';
  const d = new Date(dStr);
  return d.toLocaleDateString('vi-VN');
}

function formatMoney(amount) {
  if (!amount) return '0 ₫';
  return Number(amount).toLocaleString('vi-VN') + ' ₫';
}

onMounted(() => {
  loadContracts();
});

defineExpose({ loadContracts });
</script>

<style scoped>
.contracts-wrap {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1480px;
  margin: 0 auto;
  padding: 24px;
}

.contracts-header {
  padding: 24px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  background: #ffffff;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
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
  background: rgba(16, 185, 129, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
}

.contracts-header h2 {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text);
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.86rem;
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

.filter-controls {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
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
  text-align: left;
  font-size: 0.86rem;
}

.soc-table th {
  background: #f8fafc;
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
}

.soc-table td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-light);
  color: var(--text);
  vertical-align: middle;
}

.contract-code-pill {
  background: #f1f5f9;
  padding: 3px 8px;
  border-radius: var(--radius-xs);
  font-weight: 600;
  color: #1e293b;
}

.code-pill {
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: var(--radius-xs);
  color: #334155;
  font-weight: 600;
  font-size: 0.78rem;
}

.type-tag {
  font-size: 0.82rem;
  color: var(--text);
}

.salary-cell {
  font-weight: 700;
  color: #059669;
}

.status-badge-contract {
  display: inline-flex;
  align-items: center;
  font-size: 0.76rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: var(--radius-xs);
}

.stat-active {
  background: #dcfce7;
  color: #15803d;
}

.stat-expired {
  background: #fee2e2;
  color: #b91c1c;
}

.stat-terminated {
  background: #f1f5f9;
  color: #475569;
}

.empty-state {
  padding: 48px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  background: #ffffff;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
}

.empty-state h3 {
  font-size: 1.15rem;
  color: var(--text);
}

.empty-state p {
  font-size: 0.88rem;
  color: var(--text-muted);
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

.th-id {
  width: 65px;
}

.id-pill {
  color: var(--primary);
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.2);
  font-weight: 700;
}

.btn-table-action {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: #f1f5f9;
  border: 1px solid var(--border);
  border-radius: var(--radius-xs);
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text);
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-table-action:hover {
  background: #e2e8f0;
  color: var(--primary);
  border-color: var(--primary);
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
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: var(--radius-full);
  color: #059669;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.contract-detail-body {
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

.readonly-pill-box {
  padding: 8px 12px;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 0.88rem;
  color: var(--text);
}

.detail-modal-card {
  max-width: 640px;
}

/* Tệp đính kèm Table & Modal */
.btn-file-pill {
  display: inline-flex;
  align-items: center;
  max-width: 140px;
  padding: 4px 8px;
  background: rgba(37, 99, 235, 0.06);
  border: 1px solid rgba(37, 99, 235, 0.2);
  border-radius: var(--radius-xs);
  font-size: 0.74rem;
  color: var(--primary);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-file-pill:hover {
  background: rgba(37, 99, 235, 0.12);
  border-color: var(--primary);
}

.file-name-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-file-tag {
  font-size: 0.75rem;
  color: var(--text-dim);
  font-style: italic;
}

.file-attachment-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  background: #f8fafc;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
}

.file-icon-box {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-sm);
  background: rgba(16, 185, 129, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-info-box {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 0.88rem;
  color: var(--text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  margin-top: 2px;
}

.file-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.78rem;
}

.no-file-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #fcfcfd;
  border: 1px dashed var(--border);
  border-radius: var(--radius-md);
  gap: 12px;
}

.no-file-info {
  display: flex;
  align-items: center;
}

.hidden-file-input {
  display: none;
}

/* Dropzone Upload */
.col-span-2 {
  grid-column: span 2 / span 2;
}

.file-upload-dropzone {
  position: relative;
  border: 2px dashed #cbd5e1;
  border-radius: var(--radius-md);
  padding: 16px;
  background: #fafafa;
  transition: var(--transition-fast);
  cursor: pointer;
}

.file-upload-dropzone:hover {
  border-color: var(--primary);
  background: #f8faff;
}

.file-upload-dropzone.has-file {
  border-color: var(--emerald);
  background: rgba(16, 185, 129, 0.04);
}

.dropzone-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  gap: 4px;
}

.dropzone-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.dropzone-icon {
  margin-bottom: 4px;
}

.dropzone-title {
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--text);
}

.dropzone-sub {
  font-size: 0.76rem;
  color: var(--text-muted);
}

.btn-remove-file {
  position: absolute;
  top: 10px;
  right: 10px;
  background: #fee2e2;
  border: none;
  border-radius: var(--radius-xs);
  padding: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition-fast);
}

.btn-remove-file:hover {
  background: #fecdd3;
}

.file-pill-group {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-file-pill {
  display: inline-flex;
  align-items: center;
  padding: 5px 12px;
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.2);
  border-radius: var(--radius-full);
  color: var(--primary);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition-fast);
  max-width: 170px;
}

.btn-file-pill:hover {
  background: rgba(37, 99, 235, 0.16);
  border-color: var(--primary);
}

.btn-icon-download {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: #ffffff;
  color: var(--text-dim);
  cursor: pointer;
  transition: var(--transition-fast);
}

.btn-icon-download:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: #f8faff;
}

@media (max-width: 640px) {
  .modal-form-grid,
  .detail-row-2 {
    grid-template-columns: 1fr;
  }
  .col-span-2 {
    grid-column: span 1;
  }
  .file-attachment-card {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
