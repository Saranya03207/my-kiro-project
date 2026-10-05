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
- **Dual-Channel Audio Notifications**: Plays audio chime and displays a toast banner when an order status advances to `ready` (utilizes HTML5 Audio with Web Audio API synthesis fallback).
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
- **Live Order Queue**:
  - Filter orders by status (`All`, `Pending`, `Preparing`, `Ready`, `Completed`, `Cancelled`).
  - One-click order state transitions.
- **Sales Analytics Dashboard**:
  - Daily sales metrics, total order counts, and average transaction values.
  - Top-selling food items rankings.

---

## 📁 Directory Structure

```text
frontend/
├── assets/
│   ├── food/              # Food imagery (biryani, curd-rice, lemon-rice, default fallbacks, uploaded files)
│   └── audio/             # Sound notification assets (notification.mp3)
├── css/
│   ├── base.css           # Global typography, color variables, resets
│   ├── components.css     # Buttons, cards, badges, inputs, modals
│   ├── layout.css         # Page shells, grids, and flex containers
│   └── responsive.css     # Mobile, tablet, and desktop breakpoints
├── js/
│   ├── admin.js           # Admin UI interactions, menu CRUD, image upload preview & state
│   ├── api.js             # Centralized ApiClient supporting JSON & multipart/form-data
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
