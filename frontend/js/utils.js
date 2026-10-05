/**
 * UI Utilities for Smart Canteen Manager
 * Helper functions for formatting, modals, badges, food image mapping, and order timelines
 */

export function formatPrice(amount) {
  const num = typeof amount === 'number' ? amount : parseFloat(amount || 0);
  return `$${num.toFixed(2)}`;
}

export function formatDateTime(isoString) {
  if (!isoString) return '-';
  try {
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return isoString;
    return date.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return isoString;
  }
}

export function getTimeGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

export function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function debounce(fn, delay = 300) {
  let timer = null;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

// Centralized SVG icon library for consistent professional UI icons
export const SVG_ICONS = {
  utensils: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><path d="M18 2v20"></path><path d="M21 15V2a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"></path><path d="M6 2v20"></path><path d="M3 2v7c0 1.1.9 2 2 2h2a2 2 0 0 0 2-2V2"></path></svg>`,
  cart: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>`,
  receipt: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1-2-1Z"></path><path d="M16 8H8"></path><path d="M16 12H8"></path><path d="M13 16H8"></path></svg>`,
  grid: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><rect x="3" y="3" width="7" height="7" rx="1"></rect><rect x="14" y="3" width="7" height="7" rx="1"></rect><rect x="14" y="14" width="7" height="7" rx="1"></rect><rect x="3" y="14" width="7" height="7" rx="1"></rect></svg>`,
  bowl: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><path d="M4 11a8 8 0 0 0 16 0H4Z"></path><path d="M6 19h12"></path><path d="M9 7c0-1.5.5-3 1.5-3s1.5 1.5 1.5 3"></path><path d="M13 7c0-1.5.5-3 1.5-3s1.5 1.5 1.5 3"></path></svg>`,
  coffee: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg>`,
  cake: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><path d="M20 21v-8a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8"></path><path d="M4 16s2-1 4-1 4 1 4 1 2-1 4-1 4 1 4 1"></path><path d="M2 21h20"></path><path d="M12 7v4"></path><path d="M12 3a1 1 0 0 1 1 1c0 .5-.4 1-1 1s-1-.5-1-1a1 1 0 0 1 1-1Z"></path></svg>`,
  flame: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path></svg>`,
  clock: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`,
  dollar: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>`,
  chart: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>`,
  package: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>`,
  chef: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><path d="M6 13.84V6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v7.84"></path><path d="M3 10h18"></path><path d="M12 18v4"></path><path d="M8 22h8"></path></svg>`,
  bell: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>`,
  check: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><polyline points="20 6 9 17 4 12"></polyline></svg>`,
  checkCircle: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
  x: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`,
  xCircle: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`,
  alertTriangle: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
  info: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`,
  user: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`,
  shield: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>`,
  zap: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>`,
  search: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>`,
  refresh: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>`,
  trash: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>`,
  celebration: (size, cls) => `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"${cls}><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3Z"></path></svg>`
};

export function getSvgIcon(name, size = 18, className = '') {
  const factory = SVG_ICONS[name];
  const clsAttr = className ? ` class="${escapeHtml(className)}"` : '';
  if (factory) {
    return factory(size, clsAttr);
  }
  return '';
}

export function showToast(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  const iconSvg = type === 'success' ? getSvgIcon('checkCircle', 18) :
                  type === 'error' ? getSvgIcon('xCircle', 18) :
                  type === 'warning' ? getSvgIcon('alertTriangle', 18) :
                  getSvgIcon('info', 18);

  toast.innerHTML = `<span class="toast-icon">${iconSvg}</span> <span class="toast-text">${escapeHtml(message)}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

export function showModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('hidden');
    const firstInput = modal.querySelector('input:not([type=hidden]), select, textarea, button.btn-primary');
    if (firstInput) firstInput.focus();
  }
}

export function hideModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('hidden');
  }
}

export function getStatusBadge(status) {
  const s = (status || '').toLowerCase();
  switch (s) {
    case 'pending':
      return `<span class="badge badge-warning"><span class="badge-dot"></span> Pending</span>`;
    case 'preparing':
      return `<span class="badge badge-info"><span class="badge-dot pulse"></span> Preparing</span>`;
    case 'ready':
      return `<span class="badge badge-success"><span class="badge-dot pulse"></span> Ready for Pickup</span>`;
    case 'completed':
      return `<span class="badge badge-neutral"><span class="badge-dot"></span> Completed</span>`;
    case 'cancelled':
      return `<span class="badge badge-error"><span class="badge-dot"></span> Cancelled</span>`;
    default:
      return `<span class="badge badge-neutral">${escapeHtml(status)}</span>`;
  }
}

/**
 * Maps a menu item to its local photo asset based on name or category
 */
export function getFoodImage(item) {
  if (!item) return 'assets/food/default-food.jpg';

  // Use custom uploaded image if available
  if (item.image_url && typeof item.image_url === 'string' && item.image_url.trim()) {
    return item.image_url.trim();
  }

  const name = (item.name || '').toLowerCase();
  const cat = (item.category || '').toLowerCase();

  // Specific item matching
  if (name.includes('biryani') || name.includes('briyani')) return 'assets/food/biryani.jpg';
  if (name.includes('curd')) return 'assets/food/curd-rice.jpg';
  if (name.includes('lemon')) return 'assets/food/lemon-rice.jpg';
  if (name.includes('cheeseburger') || name.includes('burger')) return 'assets/food/cheeseburger.jpg';
  if (name.includes('wrap') || name.includes('chicken')) return 'assets/food/chicken-wrap.jpg';
  if (name.includes('pizza')) return 'assets/food/pizza.jpg';
  if (name.includes('fries') || name.includes('potato')) return 'assets/food/fries.jpg';
  if (name.includes('nacho') || name.includes('taco')) return 'assets/food/nachos.jpg';
  if (name.includes('latte') || name.includes('coffee') || name.includes('cappuccino')) return 'assets/food/caramel-latte.jpg';
  if (name.includes('smoothie') || name.includes('shake') || name.includes('berry')) return 'assets/food/berry-smoothie.jpg';
  if (name.includes('brownie') || name.includes('cake') || name.includes('chocolate')) return 'assets/food/brownie.jpg';

  // Category based matching
  if (cat.includes('meal')) return 'assets/food/meals.jpg';
  if (cat.includes('snack')) return 'assets/food/snacks.jpg';
  if (cat.includes('bev') || cat.includes('drink')) return 'assets/food/beverages.jpg';
  if (cat.includes('dessert') || cat.includes('sweet')) return 'assets/food/desserts.jpg';

  return 'assets/food/default-food.jpg';
}

export function getCategoryIcon(category, size = 16) {
  const cat = (category || '').toLowerCase();
  if (cat === 'all') return getSvgIcon('grid', size);
  if (cat.includes('meal')) return getSvgIcon('utensils', size);
  if (cat.includes('snack')) return getSvgIcon('bowl', size);
  if (cat.includes('bev') || cat.includes('drink')) return getSvgIcon('coffee', size);
  if (cat.includes('dessert')) return getSvgIcon('cake', size);
  return getSvgIcon('utensils', size);
}

// Backward-compatible alias returning professional SVG icon instead of emoji
export function getCategoryEmoji(category) {
  return getCategoryIcon(category, 16);
}

/**
 * Builds an interactive visual progress timeline for an order
 */
export function getOrderTimelineHtml(status) {
  const s = (status || '').toLowerCase();
  if (s === 'cancelled') {
    return `
      <div class="order-cancelled-banner">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex-shrink: 0;">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="15" y1="9" x2="9" y2="15"></line>
          <line x1="9" y1="9" x2="15" y2="15"></line>
        </svg>
        <div>
          <strong>Order Cancelled</strong>
          <p>This booking was cancelled. Please place a new order if needed.</p>
        </div>
      </div>
    `;
  }

  const checkIcon = `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>`;

  const stages = [
    { 
      key: 'pending', 
      label: 'Order Placed', 
      icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>` 
    },
    { 
      key: 'preparing', 
      label: 'In Kitchen', 
      icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 13.84V6a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v7.84"></path><path d="M3 10h18"></path><path d="M12 18v4"></path><path d="M8 22h8"></path></svg>` 
    },
    { 
      key: 'ready', 
      label: 'Ready for Pickup', 
      icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>` 
    },
    { 
      key: 'completed', 
      label: 'Completed', 
      icon: `<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"></polyline></svg>` 
    }
  ];

  const stageOrder = ['pending', 'preparing', 'ready', 'completed'];
  const currentIndex = stageOrder.indexOf(s);

  const stepsHtml = stages.map((stage, idx) => {
    let stateClass = 'future';
    if (idx < currentIndex) stateClass = 'done';
    else if (idx === currentIndex) stateClass = 'active';

    return `
      <div class="timeline-step ${stateClass}">
        <div class="timeline-marker">
          ${stateClass === 'done' ? checkIcon : stage.icon}
        </div>
        <div class="timeline-label">${stage.label}</div>
      </div>
    `;
  }).join('<div class="timeline-connector"></div>');

  return `<div class="order-timeline">${stepsHtml}</div>`;
}

/**
 * Prominent top-right visual notification when an order becomes ready for pickup
 * Displays clean celebratory SVG icon, order ID, instructions, and View Order button
 */
export function showOrderReadyNotification(order, onViewOrder = null) {
  let container = document.getElementById('orderReadyContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'orderReadyContainer';
    container.className = 'order-ready-container';
    document.body.appendChild(container);
  }

  const notification = document.createElement('div');
  notification.className = 'order-ready-toast';
  notification.setAttribute('role', 'alert');
  notification.setAttribute('aria-live', 'assertive');

  notification.innerHTML = `
    <div class="order-ready-toast-icon">
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
        <circle cx="18" cy="4" r="3" fill="#10b981" stroke="none"></circle>
      </svg>
    </div>
    <div class="order-ready-toast-content">
      <div class="order-ready-toast-title">YOUR ORDER IS READY</div>
      <div class="order-ready-toast-desc">Order #${order.id} is ready for pickup.</div>
      <div class="order-ready-toast-actions">
        <button type="button" class="btn btn-sm btn-primary btn-view-ready-order" data-order-id="${order.id}">
          View Order
        </button>
      </div>
    </div>
    <button type="button" class="order-ready-toast-close" aria-label="Dismiss order ready notification">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  `;

  let dismissTimer = null;

  const dismiss = () => {
    if (dismissTimer) clearTimeout(dismissTimer);
    notification.classList.add('dismissing');
    setTimeout(() => notification.remove(), 250);
  };

  const btnView = notification.querySelector('.btn-view-ready-order');
  if (btnView && typeof onViewOrder === 'function') {
    btnView.addEventListener('click', () => {
      onViewOrder(order.id);
      dismiss();
    });
  }

  const btnClose = notification.querySelector('.order-ready-toast-close');
  if (btnClose) {
    btnClose.addEventListener('click', dismiss);
  }

  container.appendChild(notification);

  // Auto-dismiss after 10 seconds
  dismissTimer = setTimeout(dismiss, 10000);
}
