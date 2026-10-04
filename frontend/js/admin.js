/**
 * Admin Dashboard, Menu, Inventory, and Orders Management
 * Enhanced with food thumbnails, stock capacity progress bars, and kitchen order workflows
 */

import apiClient from './api.js';
import { 
  formatPrice, 
  formatDateTime, 
  getStatusBadge, 
  escapeHtml, 
  getFoodImage, 
  showToast, 
  showModal, 
  hideModal,
  getSvgIcon
} from './utils.js';

export class AdminManager {
  constructor() {
    this.menuItems = [];
    this.inventory = [];
    this.orders = [];
    this.menuMap = {};
    this.itemToDelete = null;
    this.itemToEdit = null;
    this.activeTab = 'dashboard';
    this.ordersFilter = 'all';
    this.inventoryFilter = 'all';
  }

  async init() {
    await this.loadDashboardData();
  }

  // --- DASHBOARD TAB ---
  async loadDashboardData() {
    try {
      const [dailySales, lowStock, orders, popular] = await Promise.all([
        apiClient.getDailySales().catch(() => null),
        apiClient.getLowStockItems().catch(() => []),
        apiClient.getAllOrders().catch(() => []),
        apiClient.getPopularItems(7, 5).catch(() => [])
      ]);

      this.orders = orders || [];
      const pendingCount = this.orders.filter(o => o.status === 'pending').length;

      // Stats Cards
      const todayRevEl = document.getElementById('statTodayRevenue');
      const todayOrdersEl = document.getElementById('statTodayOrders');
      const pendingOrdersEl = document.getElementById('statPendingOrders');
      const lowStockEl = document.getElementById('statLowStock');

      if (todayRevEl) todayRevEl.textContent = formatPrice(dailySales?.total_revenue || 0);
      if (todayOrdersEl) todayOrdersEl.textContent = dailySales?.total_orders || 0;
      if (pendingOrdersEl) pendingOrdersEl.textContent = pendingCount;
      if (lowStockEl) lowStockEl.textContent = lowStock?.length || 0;

      // Render Popular Items Table
      this.renderPopularItems(popular || []);

      // Render Recent Orders in Dashboard
      this.renderRecentOrders(this.orders.slice(0, 5));

      // Render Low Stock Alert Banner/List
      this.renderLowStockAlerts(lowStock || []);

    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      showToast('Error refreshing dashboard metrics', 'error');
    }
  }

  renderPopularItems(items) {
    const tbody = document.getElementById('popularItemsBody');
    if (!tbody) return;

    if (items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted" style="padding: 24px;">No sales data recorded yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = items.map(item => {
      const imgSrc = getFoodImage(item);
      return `
        <tr>
          <td style="display: flex; align-items: center; gap: 10px;">
            <img src="${imgSrc}" alt="${escapeHtml(item.item_name)}" class="table-thumb" onerror="this.src='assets/food/default-food.jpg'">
            <strong>${escapeHtml(item.item_name || `Item #${item.menu_item_id}`)}</strong>
          </td>
          <td><span class="badge badge-neutral">${escapeHtml(item.category || 'General')}</span></td>
          <td><strong>${item.total_quantity_sold || 0}</strong> orders</td>
          <td><strong style="color: var(--accent);">${formatPrice(item.total_revenue || 0)}</strong></td>
        </tr>
      `;
    }).join('');
  }

  renderRecentOrders(orders) {
    const listEl = document.getElementById('recentOrdersList');
    if (!listEl) return;

    if (orders.length === 0) {
      listEl.innerHTML = `<div class="empty-state" style="padding: 24px;"><span class="empty-state-desc">No orders placed today yet.</span></div>`;
      return;
    }

    listEl.innerHTML = `
      <table class="data-table">
        <thead>
          <tr>
            <th>Order ID</th>
            <th>Student</th>
            <th>Total</th>
            <th>Status</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          ${orders.map(o => `
            <tr>
              <td><strong>#${o.id}</strong></td>
              <td>${escapeHtml(o.student_id)}</td>
              <td><strong>${formatPrice(o.total_price)}</strong></td>
              <td>${getStatusBadge(o.status)}</td>
              <td>${formatDateTime(o.created_at)}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  }

  renderLowStockAlerts(items) {
    const container = document.getElementById('lowStockAlertsList');
    if (!container) return;

    if (items.length === 0) {
      container.innerHTML = `<div class="alert alert-success"><span style="display: inline-flex; align-items: center;">${getSvgIcon('checkCircle', 18)}</span> <div><strong>All Stocks Healthy:</strong> All canteen inventory items are stocked above their shortage threshold.</div></div>`;
      return;
    }

    container.innerHTML = `
      <div class="alert alert-warning">
        <span style="display: inline-flex; align-items: center;">${getSvgIcon('alertTriangle', 18)}</span>
        <div>
          <strong>${items.length} item(s) running low on inventory stock:</strong>
          <ul style="margin-top: 4px; padding-left: 20px;">
            ${items.map(i => `<li>${escapeHtml(i.name)}: <strong>${i.stock_quantity} left</strong> (alert threshold: ${i.stock_threshold})</li>`).join('')}
          </ul>
        </div>
      </div>
    `;
  }

  // --- MENU MANAGEMENT TAB ---
  async loadMenuManagement() {
    const tbody = document.getElementById('adminMenuTableBody');
    if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="loading-block"><span class="spinner"></span> Loading menu items...</td></tr>`;

    try {
      const items = await apiClient.getInventory();
      this.menuItems = items || [];
      this.renderMenuTable();
    } catch (err) {
      console.error('Failed to load menu for admin:', err);
      showToast('Could not load menu items', 'error');
    }
  }

  renderMenuTable() {
    const tbody = document.getElementById('adminMenuTableBody');
    if (!tbody) return;

    if (this.menuItems.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted" style="padding: 32px;">No menu items found. Click "+ Add Food Item" to create one.</td></tr>`;
      return;
    }

    tbody.innerHTML = this.menuItems.map(item => {
      const imgSrc = getFoodImage(item);
      return `
        <tr data-item-id="${item.id}">
          <td><strong>#${item.id}</strong></td>
          <td style="display: flex; align-items: center; gap: 12px;">
            <img src="${imgSrc}" alt="${escapeHtml(item.name)}" class="table-thumb" onerror="this.src='assets/food/default-food.jpg'">
            <div>
              <div style="font-weight: 700; color: var(--text-primary);">${escapeHtml(item.name)}</div>
            </div>
          </td>
          <td><span class="badge badge-neutral">${escapeHtml(item.category)}</span></td>
          <td><strong>${item.stock_quantity}</strong></td>
          <td>
            <button class="btn btn-sm ${item.is_available ? 'btn-success' : 'btn-secondary'} btn-toggle-avail" data-id="${item.id}">
              ${item.is_available ? `${getSvgIcon('check', 14)} Available` : `${getSvgIcon('x', 14)} Disabled`}
            </button>
          </td>
          <td class="actions">
            <div style="display: inline-flex; gap: 6px;">
              <button class="btn btn-sm btn-secondary btn-edit-item" data-id="${item.id}">Edit</button>
              <button class="btn btn-sm btn-outline-danger btn-delete-item" data-id="${item.id}">Delete</button>
            </div>
          </td>
        </tr>
      `;
    }).join('');

    tbody.querySelectorAll('.btn-toggle-avail').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        await this.toggleItemAvailability(id);
      });
    });

    tbody.querySelectorAll('.btn-edit-item').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        this.openEditModal(id);
      });
    });

    tbody.querySelectorAll('.btn-delete-item').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        this.openDeleteModal(id);
      });
    });
  }

  async toggleItemAvailability(id) {
    try {
      const updated = await apiClient.toggleMenuItemAvailability(id);
      showToast(`Toggled availability for "${updated.name}"`, 'success');
      await this.loadMenuManagement();
    } catch (err) {
      showToast(err.message || 'Failed to toggle availability', 'error');
    }
  }

  openAddModal() {
    this.itemToEdit = null;
    const title = document.getElementById('menuItemModalTitle');
    const form = document.getElementById('menuItemForm');
    if (title) title.textContent = 'Add New Food Item';
    if (form) form.reset();
    document.getElementById('menuItemId').value = '';
    showModal('menuItemModal');
  }

  async openEditModal(id) {
    const item = this.menuItems.find(i => i.id === id);
    if (!item) return;

    this.itemToEdit = item;
    const title = document.getElementById('menuItemModalTitle');
    if (title) title.textContent = `Edit Food Item: ${item.name}`;

    try {
      const fullItem = await apiClient.getMenuItem(id).catch(() => item);
      document.getElementById('menuItemId').value = fullItem.id;
      document.getElementById('menuItemName').value = fullItem.name;
      document.getElementById('menuItemCategory').value = fullItem.category;
      document.getElementById('menuItemPrice').value = fullItem.price || '';
      document.getElementById('menuItemDesc').value = fullItem.description || '';
      document.getElementById('menuItemStock').value = fullItem.stock_quantity;
      document.getElementById('menuItemThreshold').value = fullItem.stock_threshold || 5;

      showModal('menuItemModal');
    } catch (err) {
      showToast('Could not load item details for edit', 'error');
    }
  }

  async saveMenuItem(formData) {
    const id = formData.id;
    const isEdit = !!id;

    const payload = {
      name: formData.name.trim(),
      category: formData.category.trim(),
      price: parseFloat(formData.price),
      description: formData.description.trim() || 'Freshly prepared item',
      stock_quantity: parseInt(formData.stock_quantity, 10),
      stock_threshold: parseInt(formData.stock_threshold, 10) || 5
    };

    try {
      if (isEdit) {
        await apiClient.updateMenuItem(id, payload);
        showToast('Menu item updated successfully!', 'success');
      } else {
        await apiClient.createMenuItem(payload);
        showToast('New menu item created!', 'success');
      }
      hideModal('menuItemModal');
      await this.loadMenuManagement();
      await this.loadDashboardData();
    } catch (err) {
      console.error('Save failed:', err);
      showToast(err.message || 'Failed to save menu item', 'error');
    }
  }

  openDeleteModal(id) {
    const item = this.menuItems.find(i => i.id === id);
    if (!item) return;
    this.itemToDelete = item;
    const nameEl = document.getElementById('deleteItemName');
    if (nameEl) nameEl.textContent = item.name;
    showModal('confirmDeleteModal');
  }

  async confirmDelete() {
    if (!this.itemToDelete) return;
    try {
      await apiClient.deleteMenuItem(this.itemToDelete.id);
      showToast(`"${this.itemToDelete.name}" deleted`, 'success');
      hideModal('confirmDeleteModal');
      this.itemToDelete = null;
      await this.loadMenuManagement();
      await this.loadDashboardData();
    } catch (err) {
      showToast(err.message || 'Failed to delete item', 'error');
    }
  }

  // --- INVENTORY TAB ---
  async loadInventory() {
    const tbody = document.getElementById('inventoryTableBody');
    if (tbody) tbody.innerHTML = `<tr><td colspan="7" class="loading-block"><span class="spinner"></span> Loading inventory...</td></tr>`;

    try {
      const inventory = await apiClient.getInventory();
      this.inventory = inventory || [];
      this.renderInventoryTable();
    } catch (err) {
      console.error('Failed to load inventory:', err);
      showToast('Could not load inventory', 'error');
    }
  }

  renderInventoryTable() {
    const tbody = document.getElementById('inventoryTableBody');
    if (!tbody) return;

    let items = this.inventory;
    if (this.inventoryFilter === 'low') {
      items = items.filter(i => i.is_low_stock || i.stock_quantity <= i.stock_threshold);
    }

    if (items.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted" style="padding: 32px;">No inventory records found.</td></tr>`;
      return;
    }

    tbody.innerHTML = items.map(item => {
      const isLow = item.stock_quantity <= item.stock_threshold;
      const isOut = item.stock_quantity <= 0;
      let statusTag = '<span class="badge badge-success">Healthy</span>';
      let fillClass = 'healthy';
      if (isOut) {
        statusTag = '<span class="badge badge-error">Out of Stock</span>';
        fillClass = 'out';
      } else if (isLow) {
        statusTag = `<span class="badge badge-warning">Low Stock</span>`;
        fillClass = 'low';
      }

      // Calculate bar percentage (capped at 100%)
      const maxVisual = Math.max(item.stock_threshold * 3, 30);
      const percent = Math.min(Math.round((item.stock_quantity / maxVisual) * 100), 100);
      const imgSrc = getFoodImage(item);

      return `
        <tr data-id="${item.id}">
          <td><strong>#${item.id}</strong></td>
          <td style="display: flex; align-items: center; gap: 10px;">
            <img src="${imgSrc}" alt="${escapeHtml(item.name)}" class="table-thumb" onerror="this.src='assets/food/default-food.jpg'">
            <div>
              <strong>${escapeHtml(item.name)}</strong>
            </div>
          </td>
          <td><span class="badge badge-neutral">${escapeHtml(item.category)}</span></td>
          <td>
            <div class="stock-bar-wrapper">
              <div class="stock-bar-text">
                <span>${item.stock_quantity} in stock</span>
                <span class="text-muted">Threshold: ${item.stock_threshold}</span>
              </div>
              <div class="stock-bar">
                <div class="stock-bar-fill ${fillClass}" style="width: ${percent}%;"></div>
              </div>
            </div>
          </td>
          <td>${statusTag}</td>
          <td class="actions">
            <div style="display: inline-flex; gap: 6px;">
              <button class="btn btn-sm btn-secondary btn-update-stock" data-id="${item.id}" data-stock="${item.stock_quantity}">
                Update Stock
              </button>
              <button class="btn btn-sm btn-secondary btn-update-thresh" data-id="${item.id}" data-thresh="${item.stock_threshold}">
                Threshold
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');

    tbody.querySelectorAll('.btn-update-stock').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        const curStock = e.currentTarget.dataset.stock;
        this.openStockModal(id, curStock);
      });
    });

    tbody.querySelectorAll('.btn-update-thresh').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        const curThresh = e.currentTarget.dataset.thresh;
        this.openThresholdModal(id, curThresh);
      });
    });
  }

  openStockModal(id, currentStock) {
    const item = this.inventory.find(i => i.id === id);
    document.getElementById('stockItemId').value = id;
    document.getElementById('stockItemName').textContent = item ? item.name : `#${id}`;
    document.getElementById('stockQuantityInput').value = currentStock;
    showModal('updateStockModal');
  }

  async saveStock(id, newQuantity) {
    try {
      await apiClient.updateStock(id, newQuantity);
      showToast('Stock quantity updated successfully', 'success');
      hideModal('updateStockModal');
      await this.loadInventory();
      await this.loadDashboardData();
    } catch (err) {
      showToast(err.message || 'Failed to update stock', 'error');
    }
  }

  openThresholdModal(id, currentThreshold) {
    const item = this.inventory.find(i => i.id === id);
    document.getElementById('thresholdItemId').value = id;
    document.getElementById('thresholdItemName').textContent = item ? item.name : `#${id}`;
    document.getElementById('thresholdInput').value = currentThreshold;
    showModal('updateThresholdModal');
  }

  async saveThreshold(id, newThreshold) {
    try {
      await apiClient.updateStockThreshold(id, newThreshold);
      showToast('Stock threshold updated successfully', 'success');
      hideModal('updateThresholdModal');
      await this.loadInventory();
    } catch (err) {
      showToast(err.message || 'Failed to update threshold', 'error');
    }
  }

  // --- ORDERS TAB (Kitchen Workflow) ---
  async loadOrders() {
    const container = document.getElementById('adminOrdersList');
    if (container) container.innerHTML = `<div class="loading-block"><span class="spinner"></span> Loading orders...</div>`;

    try {
      if (this.menuItems.length === 0) {
        const inv = await apiClient.getInventory();
        this.menuItems = inv || [];
      }
      this.menuItems.forEach(i => { this.menuMap[i.id] = i.name; });

      const orders = await apiClient.getAllOrders(this.ordersFilter === 'all' ? null : this.ordersFilter);
      this.orders = orders || [];
      this.renderOrdersList();
    } catch (err) {
      console.error('Failed to load admin orders:', err);
      showToast('Could not load orders', 'error');
    }
  }

  renderOrdersList() {
    const container = document.getElementById('adminOrdersList');
    if (!container) return;

    if (this.orders.length === 0) {
      container.innerHTML = `<div class="empty-state"><span class="empty-state-icon" style="color: var(--text-muted);">${getSvgIcon('receipt', 48)}</span><h3 class="empty-state-title">No orders found</h3><p class="empty-state-desc">There are no kitchen orders matching the selected filter.</p></div>`;
      return;
    }

    container.innerHTML = this.orders.map(order => {
      const status = (order.status || '').toLowerCase();
      
      let actionButtons = '';
      if (status === 'pending') {
        actionButtons = `
          <button class="btn btn-sm btn-accent btn-advance-order" data-id="${order.id}" data-next="preparing">${getSvgIcon('chef', 16)} Start Preparing</button>
          <button class="btn btn-sm btn-outline-danger btn-advance-order" data-id="${order.id}" data-next="cancelled">${getSvgIcon('xCircle', 14)} Cancel</button>
        `;
      } else if (status === 'preparing') {
        actionButtons = `
          <button class="btn btn-sm btn-success btn-advance-order" data-id="${order.id}" data-next="ready">${getSvgIcon('bell', 16)} Mark Ready</button>
          <button class="btn btn-sm btn-outline-danger btn-advance-order" data-id="${order.id}" data-next="cancelled">${getSvgIcon('xCircle', 14)} Cancel</button>
        `;
      } else if (status === 'ready') {
        actionButtons = `
          <button class="btn btn-sm btn-primary btn-advance-order" data-id="${order.id}" data-next="completed">${getSvgIcon('checkCircle', 16)} Mark Completed</button>
          <button class="btn btn-sm btn-outline-danger btn-advance-order" data-id="${order.id}" data-next="cancelled">${getSvgIcon('xCircle', 14)} Cancel</button>
        `;
      } else {
        actionButtons = `<span class="badge badge-neutral">Completed Workflow</span>`;
      }

      const itemsSummary = (order.items || []).map(i => {
        const name = this.menuMap[i.menu_item_id] || `Item #${i.menu_item_id}`;
        return `<div><strong>${i.quantity}×</strong> ${escapeHtml(name)} <span class="text-muted">(${formatPrice(i.price_at_order_time)})</span></div>`;
      }).join('');

      return `
        <div class="order-card" data-order-id="${order.id}">
          <div class="order-header">
            <div class="order-meta">
              <span class="order-id">Order #${order.id}</span>
              <span class="badge badge-info">Student: ${escapeHtml(order.student_id)}</span>
              <span class="order-date">${formatDateTime(order.created_at)}</span>
            </div>
            <div>
              ${getStatusBadge(order.status)}
            </div>
          </div>

          <div class="order-body" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: var(--spacing-md)">
            <div style="font-size: var(--font-size-sm); color: var(--text-secondary); line-height: 1.6;">
              ${itemsSummary}
            </div>

            <div style="display: flex; align-items: center; gap: var(--spacing-xl);">
              <div style="text-align: right">
                <div style="font-size: var(--font-size-xs); color: var(--text-muted); text-transform: uppercase; font-weight: 700;">Total</div>
                <div style="font-size: 1.35rem; font-weight: 800; color: var(--accent);">${formatPrice(order.total_price)}</div>
              </div>

              <div style="display: flex; gap: 8px;">
                ${actionButtons}
              </div>
            </div>
          </div>
        </div>
      `;
    }).join('');

    container.querySelectorAll('.btn-advance-order').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        const nextStatus = e.currentTarget.dataset.next;
        await this.changeOrderStatus(id, nextStatus);
      });
    });
  }

  async changeOrderStatus(id, newStatus) {
    try {
      await apiClient.updateOrderStatus(id, newStatus);
      showToast(`Order #${id} updated to "${newStatus}"`, 'success');
      await this.loadOrders();
      await this.loadDashboardData();
    } catch (err) {
      showToast(err.message || 'Failed to update order status', 'error');
    }
  }
}

export const adminManager = new AdminManager();
export default adminManager;
