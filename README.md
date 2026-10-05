# Smart Canteen Booking System

A full-stack campus canteen management and food booking system built for **Kiro University**. The application enables students to browse interactive menus, place food bookings, and track order progress in real-time with dual-channel audio and visual notifications. It empowers canteen administrators with comprehensive tools to manage food items with image uploads, monitor real-time stock levels with low-stock alerts, process live orders through a robust state machine, and analyze daily and historical sales trends.

---

## 🚀 Key Features

### 🎓 Student Portal (`/student.html`)
- **Interactive Menu Browsing**: Browse menu items categorized by Meals, Snacks, Beverages, and more.
- **Instant Search & Filtering**: Real-time filtering across dish names and descriptions.
- **Cart Management**: Add items to cart with live quantity limits, stock checks, and total calculation.
- **Order Placement & Tracking**: Place bookings and track order status live (`pending` → `preparing` → `ready` → `completed` / `cancelled`).
- **Dual-Channel Notifications**: Real-time audio and visual alerts when an order is ready for pickup (HTML5 Audio with Web Audio API synthesis fallback).
- **Order History**: View past orders with complete item breakdowns, timestamps, and status tags.

### 🛠️ Admin Portal (`/admin.html`)
- **Menu Management**:
  - Add, edit, soft-delete, and toggle availability of food items.
  - **Food Image Upload**: Drag-and-drop / file selector supporting PNG, JPEG, and WebP (up to 5MB) with instant client-side preview, image replacement, and default fallback.
- **Inventory & Stock Control**:
  - Live inventory monitoring with low-stock badges.
  - Configurable alert thresholds (`stock_quantity <= stock_threshold`).
  - Restock action triggers with automatic status updates.
- **Live Order Management**:
  - Filterable order queue (`All`, `Pending`, `Preparing`, `Ready`, `Completed`, `Cancelled`).
  - Status progression workflow with one-click transitions and validation.
- **Sales Analytics Dashboard**:
  - Daily revenue, total orders, and average order value.
  - Top-selling food items ranking.
  - Multi-day revenue and order volume trends.

### 🤖 Model Context Protocol (MCP) Integration (`mcp_server/`)
- Bundled MCP server using stdio transport for IDEs and AI assistants (e.g., Kiro).
- Read-only operational inspection into live menu availability, low-stock inventory alerts, order status, and student order histories without mutating database state.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend API** | Python 3.8+ / 3.13, FastAPI, Uvicorn, Pydantic v2 |
| **Database & ORM** | SQLite (`data/canteen.db`), SQLAlchemy ORM |
| **Frontend** | Vanilla HTML5, CSS3 (Responsive Grid/Flexbox), ES6+ JavaScript modules (zero external UI dependencies) |
| **Media & Audio** | Local asset storage (`frontend/assets/food/`), HTML5 Audio & Web Audio API synthesis |
| **AI / Protocol** | Model Context Protocol (`mcp` Python SDK with FastMCP) |
| **Testing** | pytest, pytest-asyncio, FastAPI TestClient, Hypothesis (property-based testing) |

---

## 📁 Project Structure

```text
my-kiro-project/
├── backend/
│   ├── models/              # SQLAlchemy ORM models (MenuItem, Order, OrderItem, Session)
│   ├── schemas/             # Pydantic validation schemas (Menu, Order, Auth, etc.)
│   ├── routes/              # FastAPI route handlers (auth, menu, orders, admin)
│   ├── services/            # Core business logic layer (Menu, Order, Inventory, Analytics, Auth)
│   ├── middleware/          # Authentication and authorization middleware
│   ├── utils/               # Shared utilities
│   ├── config.py            # Pydantic Settings & environment validation
│   ├── database.py          # SQLAlchemy engine, session maker, init_db
│   └── main.py              # FastAPI application entrypoint & static mounting
├── frontend/
│   ├── assets/              # Static media
│   │   ├── food/            # Food item photos (biryani, curd-rice, lemon-rice, uploads, fallbacks)
│   │   └── audio/           # Notification chimes
│   ├── css/                 # Stylesheets (base, components, layouts, responsive)
│   ├── js/                  # Modular ES6 JavaScript
│   │   ├── api.js           # Centralized API client with multipart support
│   │   ├── auth.js          # Client-side session and auth state
│   │   ├── cart.js          # Cart state, item counters, stock checks
│   │   ├── menu.js          # Menu rendering, category filtering, search
│   │   ├── orders.js        # Order history and live status tracking
│   │   ├── admin.js         # Admin dashboard, inventory, menu CRUD & image upload
│   │   └── utils.js         # Formatting, image fallback logic, notifications
│   ├── index.html           # Landing page & role-based login
│   ├── student.html         # Student ordering and status tracking portal
│   └── admin.html           # Administrator control center
├── mcp_server/
│   ├── server.py            # FastMCP server exposing read-only tools
│   └── README.md            # MCP protocol and tool documentation
├── scripts/
│   ├── add_briyani_to_menu.py     # Menu seeding / migration script
│   ├── add_curd_rice_to_menu.py   # Menu seeding / migration script
│   ├── add_lemon_rice_to_menu.py  # Menu seeding / migration script
│   └── verify_setup.py            # Environment and setup verification
├── steering/                # Architecture, business rules, and UI guidelines
├── tests/
│   ├── unit/                # Unit tests (schemas, models, services, MCP)
│   ├── properties/          # Property-based tests (Hypothesis)
│   └── integration/         # API endpoint integration tests
├── data/                    # SQLite database storage (canteen.db)
├── logs/                    # Application runtime logs (canteen.log)
├── requirements.txt         # Python project dependencies
├── POWER.md                 # Kiro Power specification & MCP server registry
└── README.md                # Project documentation
```

---

## ⚡ Quick Start

### 1. Prerequisites
- **Python 3.8+** (Python 3.11–3.13 recommended)
- **pip** package manager
- Any modern web browser (Chrome, Firefox, Safari, Edge)

### 2. Environment Setup
```bash
# Clone the repository and navigate into project directory
cd my-kiro-project

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (cmd):
.\venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Setup environment variables
cp .env.example .env
```

### 3. Run the Backend API
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger UI Docs: `http://localhost:8000/docs`
- ReDoc Alternative Docs: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

### 4. Run the Frontend Client
In a separate terminal (with the virtual environment active):
```bash
python -m http.server 3000 --directory frontend
```
Open your browser and navigate to:
- **Login / Landing Page**: `http://localhost:3000/index.html`
- **Student Portal**: `http://localhost:3000/student.html`
- **Admin Portal**: `http://localhost:3000/admin.html`

### 5. (Optional) Run the MCP Server
```bash
python -m mcp_server.server
```

---

## 🔑 Login & Roles

The system uses server-side session tokens with role-based authorization. For quick development testing, log in from `index.html`:

| Role | Identifier Format | Access Scope |
| :--- | :--- | :--- |
| **Student** | Any valid student ID (e.g. `STU001`, `STU12345`) | Menu browsing, cart, order creation, order tracking, order history |
| **Admin** | Any valid admin ID (e.g. `ADMIN001`, `admin`) | Menu management, image upload, inventory controls, order processing, analytics |

---

## 📖 REST API Reference

### Health & Static
- `GET /health` - API health check
- `GET /` - Root status and API documentation index
- `GET /assets/{filepath}` - Static assets (food images, fallback assets)

### Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/login` - Authenticate user and issue session token
- `POST /api/v1/auth/logout` - Invalidate current session token

### Menu (Student) (`/api/v1/menu`)
- `GET /api/v1/menu/items` - Retrieve active menu items (supports `?search=` and `?category=`)
- `GET /api/v1/menu/items/{id}` - Retrieve details of a specific available menu item

### Orders (Student) (`/api/v1/orders`)
- `POST /api/v1/orders` - Place a new food booking
- `GET /api/v1/orders/{id}` - Retrieve order details and current status
- `GET /api/v1/orders/history` - Retrieve student's order history (supports `?status=`)

### Admin Management (`/api/v1/admin`)

#### Menu & Food Images
- `POST /api/v1/admin/menu/upload-image` - Upload food image (PNG, JPEG, WebP up to 5MB)
- `POST /api/v1/admin/menu/items` - Create a new menu item
- `GET /api/v1/admin/menu/items` - List all items (including unavailable/soft-deleted items)
- `PUT /api/v1/admin/menu/items/{id}` - Update menu item details and image URL
- `DELETE /api/v1/admin/menu/items/{id}` - Soft-delete a menu item
- `PATCH /api/v1/admin/menu/items/{id}/availability` - Toggle item availability status

#### Inventory
- `GET /api/v1/admin/inventory/low-stock` - List items at or below alert threshold
- `PATCH /api/v1/admin/inventory/{id}/restock` - Restock item inventory quantity
- `PUT /api/v1/admin/inventory/{id}/threshold` - Update low-stock alert threshold

#### Orders
- `GET /api/v1/admin/orders` - List all orders with optional status and date filters
- `GET /api/v1/admin/orders/{id}` - Get detailed order info and line items
- `PATCH /api/v1/admin/orders/{id}/status` - Advance order status (`pending` → `preparing` → `ready` → `completed` / `cancelled`)

#### Analytics
- `GET /api/v1/admin/analytics/daily` - Daily revenue, order counts, and averages
- `GET /api/v1/admin/analytics/popular` - Top-selling menu items
- `GET /api/v1/admin/analytics/sales-trend` - Historical sales revenue trends
- `GET /api/v1/admin/analytics/dashboard` - Unified admin dashboard metrics

---

## 🧪 Testing

The codebase maintains full test coverage with unit, integration, and property-based tests:

```bash
# Run the complete test suite
pytest -q --tb=no

# Run tests with detailed output
pytest tests/ -v

# Run with HTML coverage report
pytest tests/ -v --cov=backend --cov-report=html

# Run property-based tests (Hypothesis)
pytest tests/properties/ -v

# Run MCP server tests
pytest tests/unit/test_mcp_server.py -v
```

**Test Suite Status**: ✅ **323 passed**, 0 failures.

---

## 🔒 Security & Data Integrity

- **Strict Validation**: All payloads validated using Pydantic v2 schemas.
- **SQL Injection Prevention**: All queries execute through SQLAlchemy ORM parameterization (no raw SQL).
- **Role-Based Session Guard**: Route-level dependency injection verifying roles (`require_auth`, `require_admin`).
- **File Upload Safety**: Content-type check, extension whitelisting, file size cap (5MB), and filename sanitization with UUID prefixes.
- **Atomic Operations**: Database transactions ensure stock deductions and order creations remain fully synchronized.

---

## 📄 License

Copyright © 2026 Kiro University. All rights reserved.
