/**
 * Cart Manager for Student Interface
 * Enhanced with food thumbnails and reassuring checkout UI
 */

import apiClient from './api.js';
import AuthService from './auth.js';
import { formatPrice, showToast, escapeHtml, getFoodImage, getSvgIcon } from './utils.js';
import { playOrderConfirmedSound } from './audio.js';

export class CartManager {
  constructor() {
    this.items = [];
    this.loadFromStorage();
  }

  getStorageKey() {
    const user = AuthService.getUser();
    return `canteen_cart_${user.userId || 'guest'}`;
  }

  loadFromStorage() {
    try {
      const data = localStorage.getItem(this.getStorageKey());
      this.items = data ? JSON.parse(data) : [];
    } catch {
      this.items = [];
    }
  }

  saveToStorage() {
    try {
      localStorage.setItem(this.getStorageKey(), JSON.stringify(this.items));
    } catch (e) {
      console.warn('Storage save failed:', e);
    }
    this.updateCartBadge();
  }

  addItem(item, quantity = 1) {
    if (!item || !item.id || quantity <= 0) return false;
    
    const existing = this.items.find(i => i.id === item.id);
    const currentQty = existing ? existing.quantity : 0;
    const requestedQty = currentQty + quantity;

    if (requestedQty > item.stock_quantity) {
      showToast(`Cannot add more than available stock (${item.stock_quantity} available)`, 'warning');
      return false;
    }

    if (existing) {
      existing.quantity = requestedQty;
      existing.stock_quantity = item.stock_quantity;
    } else {
      this.items.push({
        id: item.id,
        name: item.name,
        category: item.category,
        price: parseFloat(item.price),
        quantity: quantity,
        stock_quantity: item.stock_quantity
      });
    }

    this.saveToStorage();
    showToast(`Added ${quantity} × ${item.name} to cart`, 'success');
    return true;
  }

  updateQuantity(itemId, newQty) {
    const item = this.items.find(i => i.id === itemId);
    if (!item) return;

    const parsedQty = parseInt(newQty, 10);
    if (isNaN(parsedQty)) return;

    if (parsedQty <= 0) {
      this.removeItem(itemId);
      return;
    }

    if (parsedQty > item.stock_quantity) {
      showToast(`Maximum available stock for "${item.name}" is ${item.stock_quantity}`, 'warning');
      item.quantity = Math.max(1, item.stock_quantity);
    } else {
      item.quantity = parsedQty;
    }

    this.saveToStorage();
    this.renderCartUI();
  }

  removeItem(itemId) {
    this.items = this.items.filter(i => i.id !== itemId);
    this.saveToStorage();
    this.renderCartUI();
    showToast('Item removed from cart', 'info');
  }

  clear() {
    this.items = [];
    this.saveToStorage();
    this.renderCartUI();
  }

  getTotal() {
    return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  }

  getItemCount() {
    return this.items.reduce((sum, item) => sum + item.quantity, 0);
  }

  updateCartBadge() {
    const badges = document.querySelectorAll('.cart-badge-count');
    const count = this.getItemCount();
    badges.forEach(b => {
      b.textContent = count;
      b.classList.toggle('hidden', count === 0);
    });
  }

  renderCartUI() {
    this.updateCartBadge();

    const container = document.getElementById('cartItemsList');
    const emptyState = document.getElementById('cartEmptyState');
    const summaryCard = document.getElementById('cartSummaryCard');
    const subtotalEl = document.getElementById('cartSubtotal');
    const totalEl = document.getElementById('cartTotal');
    const countEl = document.getElementById('cartItemCount');
    const placeBtn = document.getElementById('btnPlaceOrder');

    if (!container) return;

    if (this.items.length === 0) {
      container.innerHTML = '';
      if (emptyState) emptyState.classList.remove('hidden');
      if (summaryCard) summaryCard.classList.add('hidden');
      if (placeBtn) placeBtn.disabled = true;
      return;
    }

    if (emptyState) emptyState.classList.add('hidden');
    if (summaryCard) summaryCard.classList.remove('hidden');
    if (placeBtn) placeBtn.disabled = false;

    container.innerHTML = this.items.map(item => {
      const imgSrc = getFoodImage(item);
      return `
        <div class="cart-item" data-id="${item.id}">
          <div class="cart-item-media">
            <img 
              src="${imgSrc}" 
              alt="${escapeHtml(item.name)}" 
              class="cart-item-img"
              onerror="this.onerror=null; this.src='assets/food/default-food.jpg';"
            >
          </div>

          <div class="cart-item-info">
            <div class="cart-item-name">${escapeHtml(item.name)}</div>
            <div class="cart-item-unit-price">${formatPrice(item.price)} each • Max ${item.stock_quantity}</div>
          </div>

          <div class="qty-selector" role="group" aria-label="Quantity for ${escapeHtml(item.name)}">
            <button type="button" class="qty-btn btn-decrease" data-id="${item.id}" aria-label="Decrease quantity for ${escapeHtml(item.name)}" title="Decrease quantity">-</button>
            <input type="number" class="qty-input" value="${item.quantity}" min="1" max="${item.stock_quantity}" data-id="${item.id}" readonly aria-label="Current quantity of ${escapeHtml(item.name)}" aria-valuenow="${item.quantity}" aria-valuemin="1" aria-valuemax="${item.stock_quantity}">
            <button type="button" class="qty-btn btn-increase" data-id="${item.id}" aria-label="Increase quantity for ${escapeHtml(item.name)}" title="${item.quantity >= item.stock_quantity ? 'Maximum stock reached' : 'Increase quantity'}" ${item.quantity >= item.stock_quantity ? 'disabled' : ''}>+</button>
          </div>

          <div class="cart-item-total">
            ${formatPrice(item.price * item.quantity)}
          </div>

          <button class="btn btn-sm btn-outline-danger btn-remove" data-id="${item.id}" title="Remove item" aria-label="Remove ${escapeHtml(item.name)} from cart">
            ${getSvgIcon('trash', 14)}
          </button>
        </div>
      `;
    }).join('');

    const total = this.getTotal();
    const itemCount = this.getItemCount();
    if (subtotalEl) subtotalEl.textContent = formatPrice(total);
    if (totalEl) totalEl.textContent = formatPrice(total);
    if (countEl) countEl.textContent = `${itemCount} item${itemCount !== 1 ? 's' : ''}`;

    // Attach listeners
    container.querySelectorAll('.btn-decrease').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        const item = this.items.find(i => i.id === id);
        if (item) this.updateQuantity(id, item.quantity - 1);
      });
    });

    container.querySelectorAll('.btn-increase').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        const item = this.items.find(i => i.id === id);
        if (item && item.quantity < item.stock_quantity) {
          this.updateQuantity(id, item.quantity + 1);
        }
      });
    });

    container.querySelectorAll('.btn-remove').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        this.removeItem(id);
      });
    });
  }

  async placeOrder() {
    if (this.items.length === 0) {
      showToast('Your cart is empty', 'warning');
      return null;
    }

    const orderData = {
      items: this.items.map(item => ({
        menu_item_id: item.id,
        quantity: item.quantity
      }))
    };

    const placeBtn = document.getElementById('btnPlaceOrder');
    if (placeBtn) {
      placeBtn.disabled = true;
      placeBtn.innerHTML = '<span class="spinner"></span> Confirming Booking...';
    }

    try {
      const createdOrder = await apiClient.createOrder(orderData);
      
      this.clear();
      showToast(`Order #${createdOrder.id} placed successfully!`, 'success');
      sessionStorage.setItem('canteen_latest_order_id', createdOrder.id);

      // Play pleasant confirmation chime for confirmed order
      playOrderConfirmedSound();

      return createdOrder;
    } catch (err) {
      console.error('Order placement failed:', err);
      showToast(err.message || 'Failed to place booking', 'error');
      return null;
    } finally {
      if (placeBtn) {
        placeBtn.disabled = false;
        placeBtn.innerHTML = 'Place Food Booking';
      }
    }
  }
}

export const cartManager = new CartManager();
export default cartManager;
