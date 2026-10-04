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
  
  const icon = type === 'success' ? '✓' :
               type === 'error' ? '✕' :
               type === 'warning' ? '⚠' : 'ℹ';

  toast.innerHTML = `<span class="toast-icon">${icon}</span> <span class="toast-text">${escapeHtml(message)}</span>`;
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
  const name = (item.name || '').toLowerCase();
  const cat = (item.category || '').toLowerCase();

  // Specific item matching
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

export function getCategoryEmoji(category) {
  const cat = (category || '').toLowerCase();
  if (cat.includes('meal')) return '🍛';
  if (cat.includes('snack')) return '🍟';
  if (cat.includes('bev') || cat.includes('drink')) return '🥤';
  if (cat.includes('dessert')) return '🍰';
  return '🍽️';
}

/**
 * Builds an interactive visual progress timeline for an order
 */
export function getOrderTimelineHtml(status) {
  const s = (status || '').toLowerCase();
  if (s === 'cancelled') {
    return `
      <div class="order-cancelled-banner">
        <span class="cancel-icon">✕</span>
        <div>
          <strong>Order Cancelled</strong>
          <p>This booking was cancelled. Please place a new order if needed.</p>
        </div>
      </div>
    `;
  }

  const stages = [
    { key: 'pending', label: 'Order Placed', icon: '📝' },
    { key: 'preparing', label: 'In Kitchen', icon: '🍳' },
    { key: 'ready', label: 'Ready for Pickup', icon: '🔔' },
    { key: 'completed', label: 'Completed', icon: '✨' }
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
          ${stateClass === 'done' ? '✓' : stage.icon}
        </div>
        <div class="timeline-label">${stage.label}</div>
      </div>
    `;
  }).join('<div class="timeline-connector"></div>');

  return `<div class="order-timeline">${stepsHtml}</div>`;
}
