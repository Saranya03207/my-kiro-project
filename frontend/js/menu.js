/**
 * Student Menu Browsing & Filtering
 */

import apiClient from './api.js';
import cartManager from './cart.js';
import { formatPrice, escapeHtml, getCategoryEmoji, showToast } from './utils.js';

export class MenuManager {
  constructor() {
    this.items = [];
    this.categories = new Set(['All']);
    this.currentCategory = 'All';
    this.searchTerm = '';
    this.quantities = {}; // itemId -> selected quantity
  }

  async loadMenu() {
    const grid = document.getElementById('foodGrid');
    const loading = document.getElementById('menuLoading');
    const emptyState = document.getElementById('menuEmptyState');

    if (loading) loading.classList.remove('hidden');
    if (grid) grid.innerHTML = '';
    if (emptyState) emptyState.classList.add('hidden');

    try {
      const items = await apiClient.getMenuItems({
        search: this.searchTerm,
        category: this.currentCategory === 'All' ? null : this.currentCategory
      });

      this.items = items || [];
      
      // Collect categories
      this.items.forEach(item => {
        if (item.category) this.categories.add(item.category);
      });
      this.renderCategoryChips();

      this.renderMenuGrid();
    } catch (err) {
      console.error('Failed to load menu:', err);
      showToast('Failed to load menu items', 'error');
      if (emptyState) {
        emptyState.classList.remove('hidden');
        const desc = emptyState.querySelector('.empty-state-desc');
        if (desc) desc.textContent = 'Could not connect to the menu service. Please refresh.';
      }
    } finally {
      if (loading) loading.classList.add('hidden');
    }
  }

  renderCategoryChips() {
    const container = document.getElementById('categoryChips');
    if (!container) return;

    const list = Array.from(this.categories);
    container.innerHTML = list.map(cat => `
      <button class="filter-chip ${cat === this.currentCategory ? 'active' : ''}" data-category="${escapeHtml(cat)}">
        ${cat === 'All' ? '🍽️ All' : `${getCategoryEmoji(cat)} ${escapeHtml(cat)}`}
      </button>
    `).join('');

    container.querySelectorAll('.filter-chip').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const cat = e.currentTarget.dataset.category;
        this.currentCategory = cat;
        container.querySelectorAll('.filter-chip').forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        this.loadMenu();
      });
    });
  }

  renderMenuGrid() {
    const grid = document.getElementById('foodGrid');
    const emptyState = document.getElementById('menuEmptyState');
    if (!grid) return;

    if (this.items.length === 0) {
      grid.innerHTML = '';
      if (emptyState) emptyState.classList.remove('hidden');
      return;
    }

    if (emptyState) emptyState.classList.add('hidden');

    grid.innerHTML = this.items.map(item => {
      const isOutOfStock = item.stock_quantity <= 0 || !item.is_available;
      const isLowStock = !isOutOfStock && item.stock_quantity <= item.stock_threshold;
      
      let stockBadge = '';
      if (isOutOfStock) {
        stockBadge = '<span class="badge badge-error">Out of Stock</span>';
      } else if (isLowStock) {
        stockBadge = `<span class="badge badge-warning">Low Stock (${item.stock_quantity} left)</span>`;
      } else {
        stockBadge = `<span class="badge badge-success">In Stock (${item.stock_quantity})</span>`;
      }

      const currentQty = this.quantities[item.id] || 1;

      return `
        <div class="food-card ${isOutOfStock ? 'unavailable' : ''}" data-id="${item.id}">
          <div class="food-card-banner">
            ${getCategoryEmoji(item.category)}
            <span class="food-card-category-tag">${escapeHtml(item.category)}</span>
            <div class="food-card-stock-tag">${stockBadge}</div>
          </div>

          <div class="food-card-body">
            <div class="food-card-title-row">
              <h3 class="food-card-title">${escapeHtml(item.name)}</h3>
              <span class="food-card-price">${formatPrice(item.price)}</span>
            </div>
            
            <p class="food-card-desc">${escapeHtml(item.description || 'Freshly prepared daily.')}</p>

            <div class="food-card-footer">
              <div class="qty-selector">
                <button class="qty-btn btn-qty-minus" data-id="${item.id}" ${isOutOfStock || currentQty <= 1 ? 'disabled' : ''}>-</button>
                <input type="number" class="qty-input" value="${currentQty}" min="1" max="${item.stock_quantity}" data-id="${item.id}" readonly>
                <button class="qty-btn btn-qty-plus" data-id="${item.id}" ${isOutOfStock || currentQty >= item.stock_quantity ? 'disabled' : ''}>+</button>
              </div>

              <button class="btn btn-primary btn-add-cart" data-id="${item.id}" ${isOutOfStock ? 'disabled' : ''}>
                ${isOutOfStock ? 'Sold Out' : 'Add to Cart'}
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Attach listeners
    grid.querySelectorAll('.btn-qty-minus').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        const cur = this.quantities[id] || 1;
        if (cur > 1) {
          this.quantities[id] = cur - 1;
          this.updateCardQtyDisplay(id);
        }
      });
    });

    grid.querySelectorAll('.btn-qty-plus').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        const item = this.items.find(i => i.id === id);
        const cur = this.quantities[id] || 1;
        if (item && cur < item.stock_quantity) {
          this.quantities[id] = cur + 1;
          this.updateCardQtyDisplay(id);
        }
      });
    });

    grid.querySelectorAll('.btn-add-cart').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        const item = this.items.find(i => i.id === id);
        const qty = this.quantities[id] || 1;
        if (item) {
          const success = cartManager.addItem(item, qty);
          if (success) {
            this.quantities[id] = 1;
            this.updateCardQtyDisplay(id);
          }
        }
      });
    });
  }

  updateCardQtyDisplay(itemId) {
    const card = document.querySelector(`.food-card[data-id="${itemId}"]`);
    if (!card) return;

    const item = this.items.find(i => i.id === itemId);
    const qty = this.quantities[itemId] || 1;
    const input = card.querySelector('.qty-input');
    const minusBtn = card.querySelector('.btn-qty-minus');
    const plusBtn = card.querySelector('.btn-qty-plus');

    if (input) input.value = qty;
    if (minusBtn) minusBtn.disabled = qty <= 1;
    if (plusBtn && item) plusBtn.disabled = qty >= item.stock_quantity;
  }

  setSearchTerm(term) {
    this.searchTerm = term;
    this.loadMenu();
  }
}

export const menuManager = new MenuManager();
export default menuManager;
