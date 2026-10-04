/**
 * UI Utilities for Smart Canteen Manager
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
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return isoString;
  }
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

  toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
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
      return `<span class="badge badge-warning">⏳ Pending</span>`;
    case 'preparing':
      return `<span class="badge badge-info">🍳 Preparing</span>`;
    case 'ready':
      return `<span class="badge badge-success">✓ Ready for Pickup</span>`;
    case 'completed':
      return `<span class="badge badge-neutral">✓ Completed</span>`;
    case 'cancelled':
      return `<span class="badge badge-error">✕ Cancelled</span>`;
    default:
      return `<span class="badge badge-neutral">${escapeHtml(status)}</span>`;
  }
}

export function getCategoryEmoji(category) {
  const cat = (category || '').toLowerCase();
  if (cat.includes('meal') || cat.includes('burger') || cat.includes('pizza') || cat.includes('lunch')) return '🍔';
  if (cat.includes('snack') || cat.includes('fries') || cat.includes('chips')) return '🍟';
  if (cat.includes('bev') || cat.includes('drink') || cat.includes('coffee') || cat.includes('tea') || cat.includes('soda')) return '🥤';
  if (cat.includes('dessert') || cat.includes('sweet') || cat.includes('cake') || cat.includes('ice')) return '🍰';
  return '🍽️';
}
