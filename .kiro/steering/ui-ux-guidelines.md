# UI/UX Guidelines

## Design Principles

### Simplicity
- Clean, uncluttered interface focused on core tasks
- No unnecessary decorations or animations
- Clear information hierarchy
- Obvious calls-to-action

### Accessibility
- WCAG 2.1 Level AA compliance
- Keyboard navigation support
- Screen reader friendly
- Sufficient color contrast
- Touch-friendly tap targets (minimum 44x44px)

### Responsiveness
- Mobile-first design approach
- Works on all screen sizes (320px to 1920px+)
- Touch-optimized for mobile devices
- Desktop-optimized for productivity

### Performance
- Fast page loads (under 2 seconds)
- Instant feedback for user actions
- No blocking operations in UI
- Smooth scrolling and transitions

## Color Palette

### Primary Colors
```css
:root {
  /* Brand colors */
  --primary: #2563eb;        /* Blue - primary actions */
  --primary-hover: #1d4ed8;  /* Darker blue - hover states */
  --primary-light: #dbeafe;  /* Light blue - backgrounds */
  
  /* Status colors */
  --success: #10b981;        /* Green - success messages */
  --warning: #f59e0b;        /* Orange - warnings */
  --error: #ef4444;          /* Red - errors */
  --info: #3b82f6;           /* Blue - information */
  
  /* Neutral colors */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
  
  /* Semantic colors */
  --background: #ffffff;
  --surface: #f9fafb;
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --border: #e5e7eb;
}
```

### Color Usage
- **Primary blue**: Buttons, links, active states
- **Green**: Order ready, success confirmations, positive actions
- **Orange**: Low stock alerts, pending states, warnings
- **Red**: Errors, delete actions, critical alerts
- **Gray**: Text, borders, backgrounds, disabled states

## Typography

### Font Stack
```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 
               Roboto, 'Helvetica Neue', Arial, sans-serif;
}
```

### Type Scale
```css
:root {
  --font-size-xs: 0.75rem;    /* 12px - labels, captions */
  --font-size-sm: 0.875rem;   /* 14px - secondary text */
  --font-size-base: 1rem;     /* 16px - body text */
  --font-size-lg: 1.125rem;   /* 18px - emphasized text */
  --font-size-xl: 1.25rem;    /* 20px - subheadings */
  --font-size-2xl: 1.5rem;    /* 24px - headings */
  --font-size-3xl: 1.875rem;  /* 30px - page titles */
}
```

### Font Weights
- **400 (Regular)**: Body text
- **500 (Medium)**: Emphasized text
- **600 (Semibold)**: Subheadings
- **700 (Bold)**: Headings, buttons

## Layout

### Spacing System
```css
:root {
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 48px;
}
```

### Container Widths
- **Mobile**: 100% width with 16px padding
- **Tablet**: 100% width with 24px padding
- **Desktop**: 1200px max-width, centered

### Grid System
```css
.grid {
  display: grid;
  gap: var(--spacing-md);
}

/* Mobile: 1 column */
.grid-menu {
  grid-template-columns: 1fr;
}

/* Tablet: 2 columns */
@media (min-width: 768px) {
  .grid-menu {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop: 3 columns */
@media (min-width: 1024px) {
  .grid-menu {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

## Components

### Buttons

```html
<!-- Primary button -->
<button class="btn btn-primary">Place Order</button>

<!-- Secondary button -->
<button class="btn btn-secondary">Cancel</button>

<!-- Danger button -->
<button class="btn btn-danger">Delete Item</button>

<!-- Icon button -->
<button class="btn btn-icon" aria-label="Add to cart">
  <span aria-hidden="true">+</span>
</button>
```

```css
.btn {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: 6px;
  border: none;
  font-weight: 500;
  font-size: var(--font-size-base);
  cursor: pointer;
  transition: background-color 0.2s;
  min-height: 44px; /* Touch target size */
}

.btn-primary {
  background-color: var(--primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-primary:disabled {
  background-color: var(--gray-300);
  cursor: not-allowed;
}
```

### Cards

```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Burger</h3>
    <span class="card-badge">$9.99</span>
  </div>
  <div class="card-body">
    <p class="card-description">Delicious beef burger with fresh vegetables</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-primary">Add to Cart</button>
  </div>
</div>
```

```css
.card {
  background: var(--background);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: var(--spacing-md);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
}

.card-body {
  padding: var(--spacing-md);
}

.card-footer {
  padding: var(--spacing-md);
  background: var(--surface);
  border-top: 1px solid var(--border);
}
```

### Forms

```html
<form class="form">
  <div class="form-group">
    <label for="item-name" class="form-label">Item Name</label>
    <input 
      type="text" 
      id="item-name" 
      class="form-input" 
      placeholder="Enter item name"
      required
    >
    <span class="form-error" id="item-name-error"></span>
  </div>
  
  <div class="form-group">
    <label for="category" class="form-label">Category</label>
    <select id="category" class="form-select">
      <option value="">Select category</option>
      <option value="meals">Meals</option>
      <option value="snacks">Snacks</option>
      <option value="beverages">Beverages</option>
    </select>
  </div>
  
  <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

```css
.form-group {
  margin-bottom: var(--spacing-md);
}

.form-label {
  display: block;
  font-weight: 500;
  margin-bottom: var(--spacing-xs);
  color: var(--text-primary);
}

.form-input,
.form-select {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: var(--font-size-base);
  min-height: 44px; /* Touch target size */
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--primary-light);
}

.form-input.error {
  border-color: var(--error);
}

.form-error {
  display: block;
  color: var(--error);
  font-size: var(--font-size-sm);
  margin-top: var(--spacing-xs);
}
```

### Alerts

```html
<div class="alert alert-success">
  <span class="alert-icon">✓</span>
  <span class="alert-message">Order placed successfully!</span>
</div>

<div class="alert alert-error">
  <span class="alert-icon">✕</span>
  <span class="alert-message">Failed to update inventory</span>
</div>

<div class="alert alert-warning">
  <span class="alert-icon">⚠</span>
  <span class="alert-message">Low stock: Only 3 items remaining</span>
</div>
```

```css
.alert {
  padding: var(--spacing-md);
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.alert-success {
  background-color: #d1fae5;
  color: #065f46;
  border: 1px solid #10b981;
}

.alert-error {
  background-color: #fee2e2;
  color: #991b1b;
  border: 1px solid #ef4444;
}

.alert-warning {
  background-color: #fef3c7;
  color: #92400e;
  border: 1px solid #f59e0b;
}
```

### Badges

```html
<span class="badge badge-success">Available</span>
<span class="badge badge-warning">Low Stock</span>
<span class="badge badge-error">Out of Stock</span>
<span class="badge badge-info">Pending</span>
```

```css
.badge {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: 12px;
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.badge-success {
  background-color: #d1fae5;
  color: #065f46;
}

.badge-warning {
  background-color: #fef3c7;
  color: #92400e;
}

.badge-error {
  background-color: #fee2e2;
  color: #991b1b;
}

.badge-info {
  background-color: #dbeafe;
  color: #1e40af;
}
```

## Page Layouts

### Student Interface

**Structure:**
1. **Header**: Logo, user info, logout button
2. **Main Content**:
   - Menu section with search and filters
   - Cart sidebar (desktop) or bottom sheet (mobile)
3. **Order Status**: Current order tracking
4. **Order History**: Past orders list
5. **AI Assistant**: Floating chat button

**Mobile Layout**: Single column, stacked sections
**Desktop Layout**: Two-column (main content + cart sidebar)

### Admin Interface

**Structure:**
1. **Header**: Logo, admin badge, logout button
2. **Navigation**: Sidebar (desktop) or hamburger menu (mobile)
   - Orders
   - Menu Management
   - Inventory
   - Analytics
3. **Main Content**: Selected section
4. **Alerts Panel**: Low stock notifications

**Mobile Layout**: Tabbed navigation, full-width content
**Desktop Layout**: Fixed sidebar, main content area

## Interaction Patterns

### Loading States

```html
<!-- Button loading state -->
<button class="btn btn-primary" disabled>
  <span class="spinner"></span>
  Processing...
</button>

<!-- Content loading state -->
<div class="skeleton">
  <div class="skeleton-line"></div>
  <div class="skeleton-line short"></div>
</div>
```

### Empty States

```html
<div class="empty-state">
  <span class="empty-state-icon">🍽️</span>
  <h3 class="empty-state-title">No menu items available</h3>
  <p class="empty-state-description">Check back later for today's menu</p>
</div>
```

### Confirmation Dialogs

```html
<div class="modal" role="dialog" aria-labelledby="modal-title">
  <div class="modal-content">
    <h2 id="modal-title">Delete Menu Item?</h2>
    <p>This action cannot be undone.</p>
    <div class="modal-actions">
      <button class="btn btn-secondary">Cancel</button>
      <button class="btn btn-danger">Delete</button>
    </div>
  </div>
</div>
```

### Toast Notifications

```javascript
// Show toast notification
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  
  setTimeout(() => toast.classList.add('toast-show'), 10);
  setTimeout(() => {
    toast.classList.remove('toast-show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}
```

## Order Status Indicators

### Visual States
- **Pending**: Gray badge, clock icon
- **Preparing**: Blue badge, cooking icon
- **Ready**: Green badge, checkmark icon (pulsing)
- **Completed**: Gray badge, completed icon
- **Cancelled**: Red badge, X icon

### Example
```html
<div class="order-status order-status-ready">
  <span class="status-icon">✓</span>
  <span class="status-text">Ready for Pickup</span>
  <span class="status-pulse"></span>
</div>
```

## Responsive Breakpoints

```css
/* Mobile: 320px - 767px */
@media (max-width: 767px) {
  /* Single column layouts */
  /* Larger touch targets */
  /* Simplified navigation */
}

/* Tablet: 768px - 1023px */
@media (min-width: 768px) and (max-width: 1023px) {
  /* Two column layouts */
  /* Side-by-side components */
}

/* Desktop: 1024px+ */
@media (min-width: 1024px) {
  /* Multi-column layouts */
  /* Sidebar navigation */
  /* Hover states */
}
```

## Accessibility Checklist

- [ ] All interactive elements have focus states
- [ ] Color contrast ratio meets WCAG AA standards
- [ ] All images have alt text
- [ ] All forms have proper labels
- [ ] Keyboard navigation works throughout
- [ ] ARIA attributes used where needed
- [ ] Screen reader tested
- [ ] Touch targets are at least 44x44px
- [ ] Error messages are clear and helpful
- [ ] Loading states have aria-live announcements

## Performance Guidelines

- **Images**: Use WebP format, lazy loading for below-fold content
- **CSS**: Minify in production, use critical CSS inline
- **JavaScript**: Defer non-critical scripts, use code splitting
- **Fonts**: Use system fonts (no web font loading)
- **Animations**: Use CSS transforms/opacity (GPU-accelerated)
- **Network**: Minimize API calls, implement caching

## Testing Checklist

- [ ] Test on Chrome, Firefox, Safari, Edge
- [ ] Test on iOS Safari and Android Chrome
- [ ] Test at 320px, 768px, 1024px, 1920px widths
- [ ] Test with keyboard only (no mouse)
- [ ] Test with screen reader (NVDA/VoiceOver)
- [ ] Test with high contrast mode
- [ ] Test with reduced motion preference
- [ ] Test offline behavior
