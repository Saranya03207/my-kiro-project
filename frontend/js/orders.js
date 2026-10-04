/**
 * Student Order Management & Status Tracking
 * Enhanced with visual order timeline, item resolution,
 * and Ready-for-Pickup sound/visual notifications.
 */

import apiClient from './api.js';
import { 
  formatPrice, 
  formatDateTime, 
  getStatusBadge, 
  getOrderTimelineHtml, 
  escapeHtml, 
  getFoodImage, 
  showToast,
  showOrderReadyNotification
} from './utils.js';
import { playOrderReadySound } from './audio.js';

export class OrderManager {
  constructor() {
    this.orders = [];
    this.menuMap = {}; // menu_item_id -> { name, price, category }
    this.pollTimer = null;
    this.currentFilter = 'all';
    this.knownOrderStatuses = new Map(); // orderId -> last seen status
    this.isInitialLoad = true; // Guard against notifications on page load/refresh
  }

  async initMenuMap() {
    try {
      const items = await apiClient.getMenuItems();
      if (Array.isArray(items)) {
        items.forEach(item => {
          this.menuMap[item.id] = { name: item.name, price: item.price, category: item.category };
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
      this.detectStatusTransitions(this.orders);
      this.renderOrders();

      // Check if auto-refresh is needed for active orders
      const hasActive = this.orders.some(o => ['pending', 'preparing', 'ready'].includes((o.status || '').toLowerCase()));
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
    }, 5000);
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
      this.detectStatusTransitions(this.orders);
      this.renderOrders();

      const hasActive = this.orders.some(o => ['pending', 'preparing', 'ready'].includes((o.status || '').toLowerCase()));
      if (!hasActive) {
        this.stopPolling();
      }
    } catch {
      // Ignore background refresh errors
    }
  }

  /**
   * Status transition detector strictly enforcing:
   * previousStatus !== "ready" AND currentStatus === "ready"
   * - Does NOT trigger on initial page load / refresh
   * - Does NOT trigger repeatedly on consecutive polls of ready orders
   * - Tracks each order independently by order ID
   */
  detectStatusTransitions(newOrders) {
    if (this.isInitialLoad) {
      // Record initial baseline status for all existing orders without notifying
      newOrders.forEach(o => {
        this.knownOrderStatuses.set(o.id, (o.status || '').toLowerCase());
      });
      this.isInitialLoad = false;
      return;
    }

    newOrders.forEach(order => {
      const currentStatus = (order.status || '').toLowerCase();
      const prevStatus = this.knownOrderStatuses.get(order.id);

      // Trigger condition strictly on transition INTO "ready"
      if (prevStatus && prevStatus !== 'ready' && currentStatus === 'ready') {
        this.handleOrderBecameReady(order);
      }

      this.knownOrderStatuses.set(order.id, currentStatus);
    });
  }

  /**
   * Handles an observed transition into ready state
   * Plays chime and renders prominent visual notification
   */
  handleOrderBecameReady(order) {
    // 1. Play pleasant local chime notification (with Web Audio fallback and autoplay safety)
    playOrderReadySound();

    // 2. Display prominent top-right notification banner (always shown, even if sound is off/blocked)
    showOrderReadyNotification(order, (orderId) => {
      this.navigateToOrder(orderId);
    });
  }

  /**
   * Switch to My Orders tab and smoothly focus on the targeted ready order
   */
  navigateToOrder(orderId) {
    const tabOrdersBtn = document.querySelector('[data-tab="tabOrders"]');
    if (tabOrdersBtn) {
      tabOrdersBtn.click();
    }

    setTimeout(() => {
      const card = document.querySelector(`[data-order-id="${orderId}"]`);
      if (card) {
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        card.classList.add('order-card-target-focus');
        setTimeout(() => card.classList.remove('order-card-target-focus'), 2500);
      }
    }, 120);
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
      filtered = this.orders.filter(o => ['pending', 'preparing', 'ready'].includes((o.status || '').toLowerCase()));
    } else if (this.currentFilter === 'completed') {
      filtered = this.orders.filter(o => (o.status || '').toLowerCase() === 'completed');
    } else if (this.currentFilter === 'cancelled') {
      filtered = this.orders.filter(o => (o.status || '').toLowerCase() === 'cancelled');
    }

    if (filtered.length === 0) {
      listEl.innerHTML = '';
      if (emptyEl) emptyEl.classList.remove('hidden');
      return;
    }

    if (emptyEl) emptyEl.classList.add('hidden');

    listEl.innerHTML = filtered.map(order => {
      const statusLower = (order.status || '').toLowerCase();
      const isReady = statusLower === 'ready';
      const timelineHtml = getOrderTimelineHtml(order.status);

      const itemsHtml = (order.items || []).map(item => {
        const itemInfo = this.menuMap[item.menu_item_id] || { name: `Food Item #${item.menu_item_id}` };
        const unitPrice = parseFloat(item.price_at_order_time || 0);
        const subtotal = unitPrice * item.quantity;
        const imgSrc = getFoodImage(itemInfo);

        return `
          <tr>
            <td style="display: flex; align-items: center; gap: 10px;">
              <img src="${imgSrc}" alt="${escapeHtml(itemInfo.name)}" style="width: 38px; height: 38px; border-radius: var(--radius-xs); object-fit: cover;" onerror="this.src='assets/food/default-food.jpg'">
              <div>
                <strong>${escapeHtml(itemInfo.name)}</strong>
              </div>
            </td>
            <td>× ${item.quantity}</td>
            <td class="numeric">${formatPrice(unitPrice)}</td>
            <td class="numeric"><strong>${formatPrice(subtotal)}</strong></td>
          </tr>
        `;
      }).join('');

      // Prominent ready-for-pickup banner displayed inside ready order cards
      const readyBannerHtml = isReady ? `
        <div class="ready-pickup-banner">
          <div class="ready-pickup-icon">
            <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
          </div>
          <div class="ready-pickup-text">
            <strong>READY FOR PICKUP</strong>
            <span>Your order is ready! Please collect it from the canteen counter.</span>
          </div>
        </div>
      ` : '';

      return `
        <div class="order-card ${isReady ? 'order-ready-highlight' : ''}" data-order-id="${order.id}">
          <div class="order-header ${isReady ? 'order-header-ready' : ''}">
            <div class="order-meta">
              <span class="order-id">Order #${order.id}</span>
              <span class="order-date">Placed: ${formatDateTime(order.created_at)}</span>
            </div>
            <div>
              ${getStatusBadge(order.status)}
            </div>
          </div>

          ${readyBannerHtml}

          <div class="order-body">
            <!-- Visual Order Timeline -->
            ${timelineHtml}

            <!-- Items Table -->
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
            <span class="text-muted" style="font-size: var(--font-size-sm)">Total Amount Paid / Booked</span>
            <span class="order-total-amount">${formatPrice(order.total_price)}</span>
          </div>
        </div>
      `;
    }).join('');
  }
}

export const orderManager = new OrderManager();
export default orderManager;
