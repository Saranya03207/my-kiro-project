# Frontend Patterns - Smart Canteen Development

## Frontend Architecture

The frontend is built purely with **Vanilla HTML5, CSS3, and ES6+ JavaScript modules**. There are **no external frontend frameworks** (no React, Vue, Angular), **no CSS utilities** (no Tailwind, Bootstrap), and **no bundlers/package managers** (no npm, Webpack, Vite). All scripts run natively in modern web browsers as ES modules (`<script type="module">`).

```
frontend/
├── index.html                  # Split-screen food hero login page
├── student.html                # Student ordering portal (menu, cart drawer, order tracking)
├── admin.html                  # Admin management portal (orders, menu CRUD, inventory, analytics)
├── css/
│   ├── main.css               # Design tokens, CSS variables, typography, layout foundation
│   ├── components.css         # Buttons, cards, modals, tables, badges, toast notifications, timelines
│   └── responsive.css         # Breakpoint rules for tablets and mobile viewports
├── js/
│   ├── api.js                 # Centralized Fetch HTTP client and ApiError class
│   ├── auth.js                # AuthService: session storage, route guards, login, logout
│   ├── menu.js                # MenuManager: menu fetching, category filtering, debounced search
│   ├── cart.js                # CartManager: client-side cart operations, price math, checkout
│   ├── orders.js              # OrderManager: order history, 10s status polling, ready notifications
│   ├── admin.js               # AdminManager: admin dashboard tabs, order processing, inventory CRUD
│   ├── audio.js               # AudioManager: sound chime, Web Audio API synthesis fallback, toggle UI
│   └── utils.js               # Formatters (currency, dates), escapeHtml, debounce, SVG icon helpers
└── assets/
    ├── food/                  # High-quality local food photography (meals, snacks, beverages, desserts)
    └── sounds/
        └── order-ready.wav    # Two-tone chime audio asset for order pickup notifications
```

---

## Authentication and Session Handling (`frontend/js/auth.js`)

Authentication state is maintained exclusively in browser **`sessionStorage`**:

- **Keys**:
  - `canteen_session_token`: Unique session token from backend login
  - `canteen_user_id`: Authenticated user ID (student ID or admin username)
  - `canteen_user_role`: User role (`student` or `admin`)
- **Key Methods**:
  - `AuthService.login(userId, role)`: Calls `apiClient.login()`, saves credentials to `sessionStorage`, and returns boolean status.
  - `AuthService.logout()`: Calls `apiClient.logout()`, clears `sessionStorage`, and redirects to `index.html`.
  - `AuthService.requireAuth(requiredRole)`: Invoked on `DOMContentLoaded`. If session is missing or role does not match, redirects user immediately to `index.html`. Populates user greeting and avatar on authorized pages.
  - `AuthService.checkGuest()`: Used on `index.html`. If user is already authenticated, redirects them to their respective portal (`student.html` or `admin.html`).

---

## API Communication (`frontend/js/api.js`)

All backend HTTP requests pass through the singleton `apiClient`:

- **Base URL**: Defaults to `http://localhost:8000/api/v1` (or current host if served via reverse proxy).
- **Header Injection**: Automatically attaches `Authorization: Bearer <token>` from `sessionStorage` if present.
- **Error Handling**: On non-2xx responses, attempts to parse JSON error payloads (`errorData.detail?.error?.message`) and throws a typed `ApiError(message, status, code)`.
- **401 Interception**: Automatically clears invalid sessions and redirects unauthenticated requests to `index.html`.

---

## UI Structure and Conventions

### 1. Zero-Emoji Convention (Strict SVG Usage)
**No Unicode emoji characters are permitted in the application UI.** All buttons, icons, status badges, banners, and empty-state placeholders strictly use accessible, inline SVG icons with `aria-hidden="true"` and appropriate text/aria-labels.

### 2. Local Food Photography (`frontend/assets/food/`)
Menu cards, cart line items, and admin item previews display local image assets with reliable fallbacks:
- `assets/food/meals.jpg`, `snacks.jpg`, `beverages.jpg`, `desserts.jpg`
- Specific items: `cheeseburger.jpg`, `chicken-wrap.jpg`, `pizza.jpg`, `berry-smoothie.jpg`, `caramel-latte.jpg`, `brownie.jpg`, `nachos.jpg`, `fries.jpg`
- General fallback: `assets/food/default-food.jpg` (configured via `onerror="this.src='assets/food/default-food.jpg'"`).

### 3. Student Portal Structure (`frontend/student.html`)
- **Top Navigation Bar**: Brand logo, student ID greeting, accessible sound notification toggle button, and logout button.
- **Hero / Menu Navigation**: Category filter chips (`All`, `Meals`, `Snacks`, `Beverages`, `Desserts`) and a real-time search input with a 300ms debounce.
- **Menu Grid**: Responsive grid of food cards showing local food photography, item name, description, price formatted as `$XX.XX`, and "Add to Cart" button.
- **Cart Drawer**: Floating / slide-out cart sidebar showing selected items, quantity increment/decrement controls, live price recalculations, and checkout button.
- **Order Tracking Tab**: Displays past and active orders with a visual order progress timeline (`pending → preparing → ready → completed`), itemized receipt, and cancellation button for allowed states.

### 4. Admin Portal Structure (`frontend/admin.html`)
- **Dashboard Navigation**: Tabs for Incoming Orders, Menu Management, Inventory & Thresholds, and Sales Analytics.
- **Incoming Orders View**: Live table of student orders with fast status advance buttons (`Start Preparing`, `Mark Ready`, `Complete`, `Cancel`).
- **Menu Management**: Grid with item cards, "Add New Item" modal, inline availability toggle switch, and soft-delete confirmation.
- **Inventory Management**: Table with inline stock edit inputs, threshold update inputs, and dynamic low-stock warning indicators.
- **Analytics View**: Visual revenue summary cards, date-range picker, and popular items breakdown.

---

## Real-Time Polling and Sound Notifications

### Polling Mechanism (`frontend/js/orders.js`)
- The student portal initiates order polling via `setInterval` running every **10 seconds**.
- Polling requests `GET /api/v1/orders/history` to detect status updates from the canteen.

### Ready-for-Pickup Notification Transition Logic
Notifications trigger **strictly upon state transition into ready**:

$$\text{previousStatus} \neq \text{"ready"} \quad \land \quad \text{currentStatus} == \text{"ready"}$$

1. **Suppression on Initial Load**: When the page loads, existing orders already in `ready` state are registered without triggering sound or toasts.
2. **Independent Tracking**: Orders are tracked by ID in a `Map<orderId, status>` to ensure multiple concurrent orders notify individually.
3. **No Repeat Chimes**: Repeated polling of an order that remains in `ready` state does NOT trigger additional sounds.
4. **Visual Highlight**: Ready orders render a prominent pickup banner, green card glow, and trigger a top toast notification with a clickable "View Order" button that smoothly scrolls to the card.

### Dual-Strategy Audio System (`frontend/js/audio.js`)
Sound notifications are managed by `AudioManager`:

1. **Primary Playback (HTML5 Audio)**: Attempts to play `assets/sounds/order-ready.wav` (a soft, pleasant 500–800ms two-tone chime).
2. **Web Audio API Synthesis Fallback**: If HTML5 Audio playback fails or is blocked by browser restrictions, `synthesizeChime()` synthesizes a two-tone sine chime directly through the browser's `AudioContext`:
   - Tone 1: **D5 (587.33 Hz)** (0ms to 360ms)
   - Tone 2: **A5 (880.00 Hz)** (180ms to 660ms)
3. **Autoplay Unlock**: Modern browsers require user interaction before playing audio. Early window listeners (`pointerdown`, `keydown`, `click`) resume suspended audio contexts upon first interaction.
4. **User Preference Toggle**: Persisted in `localStorage` under `canteen_sound_notifications` (`true` or `false`).
5. **Accessible Sound Controls**: Sound toggle buttons update their UI with SVG speaker icons (`sound-on` vs `sound-off`) and reflect `aria-pressed`.

---

## Responsive Design Conventions (`frontend/css/responsive.css`)

- **Breakpoints**:
  - `desktop`: $> 1024\text{px}$ (side-by-side split screens, floating cart)
  - `tablet`: $768\text{px} - 1024\text{px}$ (2-column grids, collapsible sidebars)
  - `mobile`: $< 768\text{px}$ (1-column stack, full-screen overlay cart drawer, bottom-sheet controls)
- **Touch Targets**: All interactive elements (buttons, inputs, category chips) have a minimum touch target size of $44\text{px} \times 44\text{px}$.
- **Accessibility**: Support for `prefers-reduced-motion: reduce` disabling animations and smooth scrolls.
