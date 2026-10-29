const API_BASE = 'http://127.0.0.1:8000/api';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('access_token') || null;
    this.user = JSON.parse(localStorage.getItem('user_info') || 'null');
  }

  setAuth(tokens, user) {
    this.token = tokens.access;
    this.user = user;
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    localStorage.setItem('user_info', JSON.stringify(user));
  }

  clearAuth() {
    this.token = null;
    this.user = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_info');
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
      ...this.getHeaders(),
      ...(options.headers || {})
    };
    if (options.body instanceof FormData) {
      delete headers['Content-Type'];
    }
    const config = {
      ...options,
      headers
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        let msg = data.error || data.detail;
        if (!msg || typeof msg !== 'string' || msg.includes('permission to perform this action') || msg.includes('do not have permission')) {
          if (response.status === 403) {
            msg = 'Bạn không có quyền thực hiện thao tác này (Truy cập bị từ chối).';
          } else if (response.status === 401) {
            msg = 'Phiên làm việc đã hết hạn hoặc chưa đăng nhập.';
          } else if (response.status === 404) {
            msg = 'Không tìm thấy dữ liệu yêu cầu.';
          } else {
            msg = 'Có lỗi xảy ra khi gọi API.';
          }
        } else if (msg === 'Authentication credentials were not provided.') {
          msg = 'Vui lòng đăng nhập để tiếp tục.';
        } else if (typeof msg === 'string' && msg.includes('Given token not valid')) {
          msg = 'Phiên đăng nhập không hợp lệ hoặc đã hết hạn.';
        } else if (msg === 'Not found.') {
          msg = 'Không tìm thấy dữ liệu yêu cầu.';
        }

        const error = new Error(msg);
        error.status = response.status;
        error.data = { ...data, detail: msg, error: msg };
        throw error;
      }

      return data;
    } catch (err) {
      throw err;
    }
  }

  // Auth APIs
  async login(username, password) {
    const res = await this.request('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    });
    this.setAuth(res.tokens, res.user);
    return res;
  }

  async quickSwitch(username) {
    const res = await this.request('/auth/quick-switch/', {
      method: 'POST',
      body: JSON.stringify({ username })
    });
    this.setAuth(res.tokens, res.user);
    return res;
  }

  async getMe() {
    return this.request('/auth/me/');
  }

  // Employee Profile APIs
  async getEmployees(params = {}) {
    const query = new URLSearchParams(params).toString();
    const endpoint = query ? `/employees/?${query}` : '/employees/';
    return this.request(endpoint);
  }

  async getEmployeeById(id) {
    return this.request(`/employees/${id}/`);
  }

  async updateEmployee(id, data) {
    return this.request(`/employees/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }

  async createEmployee(data) {
    return this.request('/employees/', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  async deleteEmployee(id) {
    return this.request(`/employees/${id}/`, {
      method: 'DELETE'
    });
  }

  // Labor Contract APIs
  async getContracts(params = {}) {
    const query = new URLSearchParams(params).toString();
    const endpoint = query ? `/contracts/?${query}` : '/contracts/';
    return this.request(endpoint);
  }

  async getContractById(id) {
    return this.request(`/contracts/${id}/`);
  }

  async createContract(data) {
    const isForm = data instanceof FormData;
    return this.request('/contracts/', {
      method: 'POST',
      body: isForm ? data : JSON.stringify(data)
    });
  }

  async updateContract(id, data) {
    const isForm = data instanceof FormData;
    return this.request(`/contracts/${id}/`, {
      method: 'PATCH',
      body: isForm ? data : JSON.stringify(data)
    });
  }

  async downloadContractFile(contractId, filename = 'hop_dong_lao_dong.pdf') {
    const url = `${API_BASE}/contracts/${contractId}/download/?mode=download`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${this.token}`
      }
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.error || err.detail || 'Không thể tải tệp hợp đồng');
    }
    const blob = await response.blob();
    const contentType = response.headers.get('Content-Type') || 'application/octet-stream';
    const typedBlob = new Blob([blob], { type: contentType });
    const blobUrl = window.URL.createObjectURL(typedBlob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    // Trì hoãn việc giải phóng blob URL để đảm bảo trình duyệt đã hoàn tất ghi file xuống ổ đĩa
    setTimeout(() => {
      window.URL.revokeObjectURL(blobUrl);
    }, 10000);
  }

  getContractViewUrl(contractId) {
    return `${API_BASE}/contracts/${contractId}/download/?mode=view&token=${encodeURIComponent(this.token || '')}`;
  }

  // User Account Management APIs (Admin / HR)
  async getUsers() {
    return this.request('/auth/users/');
  }

  async getUserById(id) {
    return this.request(`/auth/users/${id}/`);
  }

  async updateUser(id, data) {
    return this.request(`/auth/users/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }

  async resetUserPassword(id, newPassword) {
    return this.request(`/auth/users/${id}/reset-password/`, {
      method: 'POST',
      body: JSON.stringify({ new_password: newPassword })
    });
  }

  async toggleUserLock(id) {
    return this.request(`/auth/users/${id}/toggle-lock/`, {
      method: 'POST'
    });
  }

  async resetEmployeePassword(employeeId, newPassword) {
    return this.request(`/employees/${employeeId}/reset-password/`, {
      method: 'POST',
      body: JSON.stringify({ new_password: newPassword })
    });
  }

  async toggleEmployeeLock(employeeId) {
    return this.request(`/employees/${employeeId}/toggle-lock/`, {
      method: 'POST'
    });
  }

  async updateEmployeeAccount(employeeId, data) {
    return this.request(`/employees/${employeeId}/update-account/`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  }

  // Security & Audit Log APIs
  async getAuditLogs() {
    return this.request('/audit-logs/');
  }

  async getSecurityStats() {
    return this.request('/security/stats/');
  }

  async getTokenForUser(username = 'nv_nam', password = 'Employee@123') {
    try {
      const response = await fetch(`${API_BASE}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await response.json();
      return data.tokens?.access || null;
    } catch (e) {
      return null;
    }
  }

  // Thử nghiệm IDOR: Kiểm tra phân quyền truy cập cấp đối tượng
  async testIdorRequest(targetEmployeeId, customToken = null) {
    const url = `${API_BASE}/employees/${targetEmployeeId}/`;
    const headers = this.getHeaders();
    if (customToken) {
      headers['Authorization'] = `Bearer ${customToken}`;
    }
    const response = await fetch(url, {
      method: 'GET',
      headers
    });
    const status = response.status;
    const data = await response.json().catch(() => ({}));
    return { status, data };
  }

  // Thử nghiệm can thiệp trường lương trái phép
  async testTamperSalary(employeeId, fakeSalary = 99000000, customToken = null) {
    const url = `${API_BASE}/employees/${employeeId}/`;
    const headers = this.getHeaders();
    if (customToken) {
      headers['Authorization'] = `Bearer ${customToken}`;
    }
    const response = await fetch(url, {
      method: 'PATCH',
      headers,
      body: JSON.stringify({ basic_salary: fakeSalary })
    });
    const status = response.status;
    const data = await response.json().catch(() => ({}));
    return { status, data };
  }
}

export const api = new ApiService();
