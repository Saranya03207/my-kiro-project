# Smart Canteen Frontend

The frontend for the **Smart Canteen Booking System** is built with **Vanilla HTML5, CSS3, and ES6+ JavaScript modules**. It has zero runtime external library or framework dependencies, providing lightweight performance, responsive layouts, and native browser capabilities.

---

## 🖥️ Portals & Pages

### 1. `index.html` - Authentication & Portal Selector
- User login interface for both Students and Administrators.
- Saves session tokens and user context in `localStorage`.
- Directs users to the appropriate portal based on their assigned role (`student` or `admin`).

### 2. `student.html` - Student Food Ordering & Tracking
- **Category Browsing & Search**: Filter dishes by category (Meals, Snacks, Beverages) or search by name and description in real-time.
- **Visual Food Cards**: Displays local high-resolution food photography (e.g., South Indian Chicken Biryani, Curd Rice, Lemon Rice) with automatic fallback to category/default imagery.
- **Live Cart Management**: Adjust item quantities, preview order totals, and validate against current stock limits.
- **Real-Time Order Tracking**: Order status cards updated via polling (`pending` → `preparing` → `ready` → `completed`).
- **Dual-Channel Audio Notifications**: Plays pleasant audio chimes and displays visual confirmations for order confirmation and when orders become ready for pickup (utilizes local HTML5 Audio with Web Audio API synthesis fallback).
- **Order History**: Review past bookings, line item breakdowns, timestamps, and order statuses.

### 3. `admin.html` - Canteen Operations Center
- **Menu Management**:
  - Add new menu items or update existing ones.
  - Upload custom food photos (`image/png`, `image/jpeg`, `image/webp` up to 5MB).
  - Client-side drag-and-drop / file selector with instant thumbnail preview and remove/replace controls.
  - Soft-delete items and toggle immediate availability on the student menu.
- **Inventory & Alert Center**:
  - Monitor stock levels in real time.
  - Visual warning badges for items at or below low-stock thresholds.
  - Quick-restock dialog and threshold adjustments.
- **Live Order Queue & Audio Alerts**:
  - Background order polling (5s interval) detecting genuinely new student orders with ID tracking.
  - Incoming order audio chime notification (`new-order.wav`) with resilient Web Audio API fallback.
  - Accessible Sound On/Off control in header synced with `localStorage` (`canteen_sound_notifications`).
  - Filter orders by status (`All`, `Pending`, `Preparing`, `Ready`, `Completed`, `Cancelled`).
  - One-click order state transitions.
- **Sales Analytics Dashboard**:
  - Daily sales metrics, total order counts, and average transaction values.
  - Top-selling food items rankings.

---

## 🔊 Audio Notification System

The application features a zero-dependency, local-first audio notification architecture managed by `frontend/js/audio.js`:

| Event | Target Portal | Sound Asset | Fallback Web Audio Tones | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Order Confirmation** | Student | `assets/sounds/order-confirmed.wav` | G5 (783.99 Hz) → C6 (1046.50 Hz) | Confirms booking was successfully placed and submitted to the canteen. |
| **Ready for Pickup** | Student | `assets/sounds/order-ready.wav` | D5 (587.33 Hz) → G5 (783.99 Hz) | Alerts student that kitchen has finished preparing their meal for pickup. |
| **Incoming New Order** | Admin | `assets/sounds/new-order.wav` | F5/C6 (698/1046 Hz) → A5/E6 (880/1318 Hz) | Alerts kitchen staff that a new student order has been received. |

### Key Audio Features:
- **Zero External Dependencies**: All sound assets are bundled locally in `frontend/assets/sounds/`.
- **Web Audio API Synthesis Fallback**: If HTML5 Audio element playback fails or is blocked, synthetic oscillator tones automatically generate the chime.
- **Autoplay Policy Handling**: Early user gesture capture (`pointerdown`, `keydown`, `click`) unlocks the browser's `AudioContext` seamlessly.
- **Unified Sound Toggle**: Both Student and Admin headers include an accessible SVG Sound On / Sound Off button synced with `localStorage` (`canteen_sound_notifications`). When disabled, the UI continues updating silently.
- **Deduplicated Audio Triggers**: Order polling uses ID tracking (`Set`) ensuring chimes play exactly once per event and never overlap during bulk updates.

---

## 📁 Directory Structure

```text
frontend/
├── assets/
│   ├── food/              # Food imagery (biryani, curd-rice, lemon-rice, default fallbacks, uploaded files)
│   └── sounds/            # Sound notification assets (order-ready.wav, order-confirmed.wav, new-order.wav)
├── css/
│   ├── base.css           # Global typography, color variables, resets
│   ├── components.css     # Buttons, cards, badges, inputs, modals
│   ├── layout.css         # Page shells, grids, and flex containers
│   └── responsive.css     # Mobile, tablet, and desktop breakpoints
├── js/
│   ├── admin.js           # Admin UI interactions, menu CRUD, image upload, new order polling & sound alert
│   ├── api.js             # Centralized ApiClient supporting JSON & multipart/form-data
│   ├── audio.js           # Audio notification manager (order-ready, order-confirmed, new-order, Web Audio fallback)
│   ├── auth.js            # Authentication state and route protection
│   ├── cart.js            # Shopping cart management and stock validation
│   ├── menu.js            # Menu card rendering and category filtering
│   ├── orders.js          # Order placement, polling, and status tracking
│   └── utils.js           # Currency formatters, notification chimes, image fallback resolver
├── index.html             # Login page
├── student.html           # Student ordering portal
├── admin.html             # Administrator dashboard
└── README.md              # Frontend architecture documentation
```

---

## 🚀 Running the Frontend

To serve the frontend static files locally:

```bash
# From the project root
python -m http.server 3000 --directory frontend
```

Then open `http://localhost:3000` in your web browser.

Ensure the backend API server is also running on `http://localhost:8000` (FastAPI with CORS enabled).
