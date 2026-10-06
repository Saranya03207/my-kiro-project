/**
 * Student Menu Browsing & Filtering
 * Enhanced with local food photography, featured section, and category chips
 */

import apiClient from './api.js';
import cartManager from './cart.js';
import { formatPrice, escapeHtml, getCategoryIcon, getCategoryEmoji, getSvgIcon, getFoodImage, showToast } from './utils.js';

export class MenuManager {
  constructor() {
    this.items = [];
    this.categories = new Set(['All', 'Meals', 'Snacks', 'Beverages', 'Desserts']);
    this.currentCategory = 'All';
    this.searchTerm = '';
    this.quantities = {};
  }

  async loadMenu() {
    const grid = document.getElementById('foodGrid');
    const loading = document.getElementById('menuLoading');
    const emptyState = document.getElementById('menuEmptyState');
    const featuredSection = document.getElementById('featuredSection');

    // Render category chips immediately
    this.renderCategoryChips();

    if (loading) loading.classList.remove('hidden');
    if (grid) {
      grid.setAttribute('aria-busy', 'true');
      grid.innerHTML = '';
    }
    if (emptyState) emptyState.classList.add('hidden');
    if (featuredSection) featuredSection.classList.add('hidden');

    try {
      const items = await apiClient.getMenuItems({
        search: this.searchTerm,
        category: this.currentCategory === 'All' ? null : this.currentCategory
      });

      this.items = items || [];
      
      // Collect any additional categories
      this.items.forEach(item => {
        if (item.category) this.categories.add(item.category);
      });
      this.renderCategoryChips();

      // Render featured popular section if on "All" and no search query
      if (this.currentCategory === 'All' && !this.searchTerm && this.items.length >= 3) {
        this.renderFeaturedSection();
      }

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
      if (grid) grid.removeAttribute('aria-busy');
      if (loading) loading.classList.add('hidden');
    }
  }

  renderCategoryChips() {
    const container = document.getElementById('categoryChips');
    if (!container) return;

    const list = Array.from(this.categories);
    container.innerHTML = list.map(cat => `
      <button class="filter-chip ${cat === this.currentCategory ? 'active' : ''}" data-category="${escapeHtml(cat)}">
        <span style="display: inline-flex; align-items: center;">${getCategoryIcon(cat, 16)}</span>
        <span>${escapeHtml(cat)}</span>
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

  renderFeaturedSection() {
    const featuredSection = document.getElementById('featuredSection');
    const featuredGrid = document.getElementById('featuredGrid');
    if (!featuredSection || !featuredGrid) return;

    // Pick top 3 available items as featured highlights
    const featuredItems = this.items.filter(i => i.is_available && i.stock_quantity > 0).slice(0, 3);
    if (featuredItems.length === 0) return;

    featuredGrid.innerHTML = featuredItems.map(item => this.createFoodCardHtml(item, true)).join('');
    featuredSection.classList.remove('hidden');

    this.attachCardEventListeners(featuredGrid);
  }

  resetFilters() {
    this.searchTerm = '';
    this.currentCategory = 'All';
    const searchInput = document.getElementById('menuSearchInput');
    const searchClearBtn = document.getElementById('btnMenuSearchClear');
    if (searchInput) searchInput.value = '';
    if (searchClearBtn) searchClearBtn.classList.add('hidden');
    this.renderCategoryChips();
    this.loadMenu();
  }

  renderMenuGrid() {
    const grid = document.getElementById('foodGrid');
    const emptyState = document.getElementById('menuEmptyState');
    if (!grid) return;

    if (this.items.length === 0) {
      grid.innerHTML = '';
      if (emptyState) {
        emptyState.classList.remove('hidden');
        const descEl = document.getElementById('menuEmptyStateDesc');
        if (descEl) {
          if (this.searchTerm && this.currentCategory !== 'All') {
            descEl.textContent = `No dishes found matching "${this.searchTerm}" in "${this.currentCategory}". Try clearing your filters.`;
          } else if (this.searchTerm) {
            descEl.textContent = `No dishes found matching "${this.searchTerm}". Check your spelling or try another dish.`;
          } else if (this.currentCategory !== 'All') {
            descEl.textContent = `No food items are currently available in "${this.currentCategory}".`;
          } else {
            descEl.textContent = 'No food items are currently available on the canteen menu.';
          }
        }
        const resetBtn = document.getElementById('btnResetMenuFilters');
        if (resetBtn && !resetBtn._hasListener) {
          resetBtn._hasListener = true;
          resetBtn.addEventListener('click', () => this.resetFilters());
        }
      }
      return;
    }

    if (emptyState) emptyState.classList.add('hidden');

    grid.innerHTML = this.items.map(item => this.createFoodCardHtml(item, false)).join('');
    this.attachCardEventListeners(grid);
  }

  createFoodCardHtml(item, isFeatured = false) {
    const isOutOfStock = item.stock_quantity <= 0 || !item.is_available;
    const isLowStock = !isOutOfStock && item.stock_quantity <= item.stock_threshold;
    
    let stockBadge = '';
    if (isOutOfStock) {
      stockBadge = `<span class="badge badge-error">${getSvgIcon('xCircle', 12)} Out of Stock</span>`;
    } else if (isLowStock) {
      stockBadge = `<span class="badge badge-warning">${getSvgIcon('alertTriangle', 12)} Only ${item.stock_quantity} Left</span>`;
    } else {
      stockBadge = `<span class="badge badge-success">${getSvgIcon('checkCircle', 12)} Available</span>`;
    }

    const currentQty = this.quantities[item.id] || 1;
    const imgSrc = getFoodImage(item);
    const altText = `Freshly prepared ${escapeHtml(item.name)}${item.category ? ` (${escapeHtml(item.category)})` : ''}`;
    const fallbackAltText = `Photo of ${escapeHtml(item.name)}`;

    return `
      <div class="food-card ${isOutOfStock ? 'unavailable' : ''}" data-id="${item.id}">
        <div class="food-card-media">
          <img src="${imgSrc}" alt="${altText}" class="food-card-img" loading="lazy" onerror="this.onerror=null; this.src='assets/food/default-food.jpg'; this.alt='${fallbackAltText}';">
          <span class="food-card-category-pill">${getCategoryIcon(item.category, 14)} ${escapeHtml(item.category)}</span>
          <div class="food-card-stock-pill">${stockBadge}</div>
        </div>

        <div class="food-card-body">
          <div class="food-card-title-row">
            <h3 class="food-card-title">${escapeHtml(item.name)}</h3>
            <span class="food-card-price">${formatPrice(item.price)}</span>
          </div>
          
          <p class="food-card-desc">${escapeHtml(item.description || 'Deliciously prepared with fresh campus ingredients.')}</p>

          <div class="food-card-footer">
            <div class="qty-selector">
              <button class="qty-btn btn-qty-minus" data-id="${item.id}" ${isOutOfStock || currentQty <= 1 ? 'disabled' : ''}>-</button>
              <input type="number" class="qty-input" value="${currentQty}" min="1" max="${item.stock_quantity}" data-id="${item.id}" readonly>
              <button class="qty-btn btn-qty-plus" data-id="${item.id}" ${isOutOfStock || currentQty >= item.stock_quantity ? 'disabled' : ''}>+</button>
            </div>

            <button class="btn btn-primary btn-add-cart" data-id="${item.id}" ${isOutOfStock ? 'disabled' : ''}>
              ${isOutOfStock ? 'Sold Out' : '<span>+ Add</span>'}
            </button>
          </div>
        </div>
      </div>
    `;
  }

  attachCardEventListeners(container) {
    container.querySelectorAll('.btn-qty-minus').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        const cur = this.quantities[id] || 1;
        if (cur > 1) {
          this.quantities[id] = cur - 1;
          this.updateAllCardQtyDisplays(id);
        }
      });
    });

    container.querySelectorAll('.btn-qty-plus').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        const item = this.items.find(i => i.id === id);
        const cur = this.quantities[id] || 1;
        if (item && cur < item.stock_quantity) {
          this.quantities[id] = cur + 1;
          this.updateAllCardQtyDisplays(id);
        }
      });
    });

    container.querySelectorAll('.btn-add-cart').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.dataset.id, 10);
        const item = this.items.find(i => i.id === id);
        const qty = this.quantities[id] || 1;
        if (item) {
          const success = cartManager.addItem(item, qty);
          if (success) {
            this.quantities[id] = 1;
            this.updateAllCardQtyDisplays(id);
          }
        }
      });
    });
  }

  updateAllCardQtyDisplays(itemId) {
    const cards = document.querySelectorAll(`.food-card[data-id="${itemId}"]`);
    const item = this.items.find(i => i.id === itemId);
    const qty = this.quantities[itemId] || 1;

    cards.forEach(card => {
      const input = card.querySelector('.qty-input');
      const minusBtn = card.querySelector('.btn-qty-minus');
      const plusBtn = card.querySelector('.btn-qty-plus');

      if (input) input.value = qty;
      if (minusBtn) minusBtn.disabled = qty <= 1;
      if (plusBtn && item) plusBtn.disabled = qty >= item.stock_quantity;
    });
  }

  setSearchTerm(term) {
    this.searchTerm = term;
    this.loadMenu();
  }
}

export const menuManager = new MenuManager();
export default menuManager;
