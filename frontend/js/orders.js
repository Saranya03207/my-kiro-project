/**
 * Student Order Management & Status Tracking
 */

import apiClient from './api.js';
import { formatPrice, formatDateTime, getStatusBadge, escapeHtml, showToast } from './utils.js';

export class OrderManager {
  constructor() {
    this.orders = [];
    this.menuMap = {}; // menu_item_id -> { name, price }
    this.pollTimer = null;
    this.currentFilter = 'all';
  }

  async initMenuMap() {
    try {
      const items = await apiClient.getMenuItems();
      if (Array.isArray(items)) {
        items.forEach(item => {
          this.menuMap[item.id] = { name: item.name, price: item.price };
        });
      }
    } catch (err) {
      console.warn('Could not populate menu map for order names:', err);
    }
  }

  async loadOrders() {
    const listEl = document.getElementById('ordersList');
    const loadingEl = document.getElementById('ordersLoading');
    const emptyEl = document.getElementById('ordersEmptyState');

    if (loadingEl) loadingEl.classList.remove('hidden');
    if (emptyEl) emptyEl.classList.add('hidden');

    try {
      if (Object.keys(this.menuMap).length === 0) {
        await this.initMenuMap();
      }

      const orders = await apiClient.getOrderHistory();
      this.orders = orders || [];
      this.renderOrders();

      // Check if auto-refresh is needed for active orders
      const hasActive = this.orders.some(o => ['pending', 'preparing', 'ready'].includes(o.status.toLowerCase()));
      if (hasActive) {
        this.startPolling();
      } else {
        this.stopPolling();
      }
    } catch (err) {
      console.error('Failed to load orders:', err);
      showToast('Could not load orders', 'error');
      if (emptyEl) emptyEl.classList.remove('hidden');
    } finally {
      if (loadingEl) loadingEl.classList.add('hidden');
    }
  }

  startPolling() {
    if (this.pollTimer) return;
    this.pollTimer = setInterval(() => {
      this.silentRefresh();
    }, 8000);
  }

  stopPolling() {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  }

  async silentRefresh() {
    try {
      const orders = await apiClient.getOrderHistory();
      this.orders = orders || [];
      this.renderOrders();
      const hasActive = this.orders.some(o => ['pending', 'preparing', 'ready'].includes(o.status.toLowerCase()));
      if (!hasActive) {
        this.stopPolling();
      }
    } catch {
      // Ignore background refresh errors
    }
  }

  setFilter(filter) {
    this.currentFilter = filter;
    this.renderOrders();
  }

  renderOrders() {
    const listEl = document.getElementById('ordersList');
    const emptyEl = document.getElementById('ordersEmptyState');
    if (!listEl) return;

    let filtered = this.orders;
    if (this.currentFilter === 'active') {
      filtered = this.orders.filter(o => ['pending', 'preparing', 'ready'].includes(o.status.toLowerCase()));
    } else if (this.currentFilter === 'completed') {
      filtered = this.orders.filter(o => o.status.toLowerCase() === 'completed');
    } else if (this.currentFilter === 'cancelled') {
      filtered = this.orders.filter(o => o.status.toLowerCase() === 'cancelled');
    }

    if (filtered.length === 0) {
      listEl.innerHTML = '';
      if (emptyEl) emptyEl.classList.remove('hidden');
      return;
    }

    if (emptyEl) emptyEl.classList.add('hidden');

    listEl.innerHTML = filtered.map(order => {
      const itemsHtml = (order.items || []).map(item => {
        const itemInfo = this.menuMap[item.menu_item_id];
        const name = itemInfo ? itemInfo.name : `Food Item #${item.menu_item_id}`;
        const unitPrice = parseFloat(item.price_at_order_time || 0);
        const subtotal = unitPrice * item.quantity;

        return `
          <tr>
            <td><strong>${escapeHtml(name)}</strong></td>
            <td>× ${item.quantity}</td>
            <td class="numeric">${formatPrice(unitPrice)}</td>
            <td class="numeric"><strong>${formatPrice(subtotal)}</strong></td>
          </tr>
        `;
      }).join('');

      return `
        <div class="order-card" data-order-id="${order.id}">
          <div class="order-header">
            <div class="order-meta">
              <span class="order-id">Order #${order.id}</span>
              <span class="order-date">Placed: ${formatDateTime(order.created_at)}</span>
            </div>
            <div>
              ${getStatusBadge(order.status)}
            </div>
          </div>

          <div class="order-body">
            <table class="order-items-table">
              <thead>
                <tr>
                  <th>Item</th>
                  <th>Quantity</th>
                  <th class="numeric">Price</th>
                  <th class="numeric">Total</th>
                </tr>
              </thead>
              <tbody>
                ${itemsHtml}
              </tbody>
            </table>
          </div>

          <div class="order-footer">
            <span class="text-muted">Total Amount</span>
            <span class="order-total-amount">${formatPrice(order.total_price)}</span>
          </div>
        </div>
      `;
    }).join('');
  }
}

export const orderManager = new OrderManager();
export default orderManager;
