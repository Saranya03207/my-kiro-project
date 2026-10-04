/**
 * API Client for Smart Canteen Manager
 * Handles all HTTP communication with the FastAPI backend
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  constructor(message, status = 0, code = null, details = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }

  isAuthError() {
    return this.status === 401;
  }

  isPermissionError() {
    return this.status === 403;
  }

  isNotFoundError() {
    return this.status === 404;
  }

  isValidationError() {
    return this.status === 400;
  }

  isServerError() {
    return this.status >= 500;
  }
}

class ApiClient {
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  getAuthHeaders() {
    const token = sessionStorage.getItem('canteen_session_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      ...this.getAuthHeaders(),
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, { ...options, headers });
      
      // Handle 204 No Content
      if (response.status === 204) {
        return null;
      }

      // Safely parse JSON or text
      const text = await response.text();
      let data = null;
      if (text) {
        try {
          data = JSON.parse(text);
        } catch {
          data = text;
        }
      }

      if (!response.ok) {
        let errorMsg = 'Request failed';
        let errorCode = 'REQUEST_FAILED';
        let errorDetails = null;

        if (data && typeof data === 'object') {
          if (data.detail && typeof data.detail === 'object' && data.detail.error) {
            errorMsg = data.detail.error.message || errorMsg;
            errorCode = data.detail.error.code || errorCode;
            errorDetails = data.detail.error.details || null;
          } else if (typeof data.detail === 'string') {
            errorMsg = data.detail;
          } else if (data.message) {
            errorMsg = data.message;
          }
        }

        throw new ApiError(errorMsg, response.status, errorCode, errorDetails);
      }

      return data;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError('Unable to connect to backend server', 0, 'NETWORK_ERROR');
    }
  }

  // --- Authentication ---
  async login(userId, role) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId, role })
    });
  }

  async logout() {
    return this.request('/auth/logout', {
      method: 'POST'
    });
  }

  // --- Menu (Student) ---
  async getMenuItems(filters = {}) {
    const params = new URLSearchParams();
    if (filters.search && filters.search.trim()) params.append('search', filters.search.trim());
    if (filters.category && filters.category.trim()) params.append('category', filters.category.trim());
    const query = params.toString();
    return this.request(`/menu/items${query ? `?${query}` : ''}`);
  }

  async getMenuItem(id) {
    return this.request(`/menu/items/${id}`);
  }

  // --- Orders (Student) ---
  async createOrder(orderData) {
    return this.request('/orders/', {
      method: 'POST',
      body: JSON.stringify(orderData)
    });
  }

  async getOrder(id) {
    return this.request(`/orders/${id}`);
  }

  async getOrderHistory(status = null) {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    const query = params.toString();
    return this.request(`/orders/history${query ? `?${query}` : ''}`);
  }

  // --- Admin Menu ---
  async createMenuItem(itemData) {
    return this.request('/admin/menu/items', {
      method: 'POST',
      body: JSON.stringify(itemData)
    });
  }

  async updateMenuItem(id, itemData) {
    return this.request(`/admin/menu/items/${id}`, {
      method: 'PUT',
      body: JSON.stringify(itemData)
    });
  }

  async toggleMenuItemAvailability(id) {
    return this.request(`/admin/menu/items/${id}/availability`, {
      method: 'PATCH'
    });
  }

  async deleteMenuItem(id) {
    return this.request(`/admin/menu/items/${id}`, {
      method: 'DELETE'
    });
  }

  // --- Admin Inventory ---
  async getInventory() {
    return this.request('/admin/inventory');
  }

  async updateStock(id, quantity) {
    return this.request(`/admin/inventory/${id}?quantity=${encodeURIComponent(quantity)}`, {
      method: 'PUT'
    });
  }

  async getLowStockItems() {
    return this.request('/admin/inventory/low-stock');
  }

  async updateStockThreshold(id, threshold) {
    return this.request(`/admin/inventory/${id}/threshold?threshold=${encodeURIComponent(threshold)}`, {
      method: 'PUT'
    });
  }

  // --- Admin Orders ---
  async getAllOrders(status = null) {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    const query = params.toString();
    return this.request(`/admin/orders${query ? `?${query}` : ''}`);
  }

  async updateOrderStatus(id, newStatus) {
    return this.request(`/admin/orders/${id}/status?new_status=${encodeURIComponent(newStatus)}`, {
      method: 'PATCH'
    });
  }

  // --- Admin Analytics ---
  async getDailySales(targetDate = null) {
    const params = new URLSearchParams();
    if (targetDate) params.append('target_date', targetDate);
    const query = params.toString();
    return this.request(`/admin/analytics/sales/daily${query ? `?${query}` : ''}`);
  }

  async getSalesByDateRange(startDate, endDate) {
    return this.request(`/admin/analytics/sales/range?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`);
  }

  async getPopularItems(days = 7, limit = 10) {
    return this.request(`/admin/analytics/popular-items?days=${encodeURIComponent(days)}&limit=${encodeURIComponent(limit)}`);
  }
}

export const apiClient = new ApiClient();
export default apiClient;
