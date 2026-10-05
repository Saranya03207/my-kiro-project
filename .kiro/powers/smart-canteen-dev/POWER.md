---
name: "smart-canteen-dev"
displayName: "Smart Canteen Development"
description: "Reusable domain-specific development guidance and MCP tools for the Smart Canteen Booking System (FastAPI backend, SQLAlchemy/SQLite, Vanilla JS frontend, Pytest & Hypothesis testing)"
keywords: ["smart canteen", "fastapi", "sqlalchemy", "sqlite", "pytest", "hypothesis", "property testing", "student portal", "admin portal", "inventory", "orders", "mcp"]
author: "Saranya03207"
---

# Smart Canteen Development Power

Provides reusable domain-specific development guidance and MCP tools for the **Smart Canteen Booking System** — a full-stack campus canteen food ordering and management application for Kiro University.

## Overview

The Smart Canteen Booking System enables students to browse menus, add items to a cart, place bookings, and track order progress in real time with visual and audio notifications. Simultaneously, canteen administrators manage menu items, monitor stock levels, set low-stock thresholds, process orders through a structured state machine, and analyze daily/historical sales metrics.

### Technology Stack
- **Backend**: FastAPI 0.115+ running on Uvicorn, Python 3.13
- **ORM & Database**: SQLAlchemy with SQLite (`sqlite:///./data/canteen.db`)
- **Validation**: Pydantic v2 schemas with custom field validators
- **Session Auth**: Server-side session tokens (UUIDv4) stored in database with role-based checks
- **Frontend**: Vanilla HTML5, CSS3, ES6+ JavaScript modules (zero external UI frameworks/libraries)
- **Audio & Assets**: Dual-strategy sound notifications (HTML5 Audio + Web Audio API synthesis fallback) and local food photography
- **Testing**: pytest, FastAPI `TestClient`, and Hypothesis property-based testing
- **MCP Integration**: Model Context Protocol server exposing read-only canteen data

## Available MCP Servers

This Power bundles the `smart-canteen` Model Context Protocol (MCP) server:

| Server Name | Transport | Module | Description |
| :--- | :--- | :--- | :--- |
| `smart-canteen` | STDIO | `mcp_server.server` | Exposes read-only queries for canteen menus, stock alerts, order status, and student order history |

### Registered MCP Tools
1. **`get_available_menu_items`**: Returns all active and available menu items with prices, categories, and stock.
2. **`get_low_stock_items`**: Lists food items whose current stock is at or below their configured alert threshold.
3. **`get_order_status`**: Queries current processing status, item breakdown, and timestamps for any order ID.
4. **`get_order_history`**: Retrieves past and active bookings for a student, with optional status filtering.

## Tool Usage

The bundled MCP tools are configured with `autoApprove` for safe read-only operations:

```json
// Example: Query menu items
{
  "name": "get_available_menu_items",
  "arguments": {
    "category": "Meals"
  }
}

// Example: Check order status
{
  "name": "get_order_status",
  "arguments": {
    "order_id": 1
  }
}
```

All tool executions are read-only and guarantee database immutability.

## Configuration

The MCP server configuration is declared in `mcp.json`:

```json
{
  "mcpServers": {
    "smart-canteen": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": ".",
      "env": {},
      "disabled": false,
      "autoApprove": [
        "get_available_menu_items",
        "get_low_stock_items",
        "get_order_status",
        "get_order_history"
      ]
    }
  }
}
```

## When to Use This Power

Use this Power whenever developing, extending, refactoring, or testing features in the Smart Canteen repository:
- **Modifying Backend Logic**: When creating API routes, editing database models, or changing services
- **Enforcing Business Rules**: When updating student/admin permissions, menu availability, stock deduction, or order lifecycle transitions
- **Developing Frontend**: When editing HTML templates, CSS styles, SVG icons, audio notifications, or client-side managers
- **Writing Tests**: When adding unit tests, integration route tests, or Hypothesis property-based invariants
- **Querying System State**: When using MCP tools to inspect live menu, stock levels, or order statuses

## Instructions for Loading Steering Files

Load the appropriate steering file using `readSteering` based on the task:

| Topic | Steering File | When to Load |
| :--- | :--- | :--- |
| **Backend & Architecture** | `architecture-guide.md` | Designing endpoints, database models, schemas, service layer, or session middleware |
| **Domain & Business Rules** | `business-rules.md` | Handling order states, stock constraints, pricing, cancellation rules, or role permissions |
| **Frontend & UI Conventions** | `frontend-patterns.md` | Building UI components, SVG icons, cart/menu management, polling, or sound notifications |
| **Testing & Invariants** | `testing-strategy.md` | Writing pytest tests, constructing Hypothesis strategies, or validating regression invariants |

## Reusable Workflow Guidance

When making changes to this codebase, always follow this workflow:

1. **Verify Baseline**: Run `pytest -q --tb=no` before making changes to confirm all tests pass.
2. **Consult Steering**: Read the corresponding steering file to respect architectural boundaries and invariants.
3. **Respect Separation of Concerns**: Keep FastAPI routes thin; encapsulate business logic inside `backend/services/`.
4. **Enforce Invariants**: Ensure calculations use `Decimal`, stock remains non-negative, and order state transitions strictly adhere to `OrderService.VALID_TRANSITIONS`.
5. **Follow Zero-Emoji Frontend Convention**: UI buttons, badges, and alerts must use accessible SVGs (never Unicode emoji characters).
6. **Protect Test Suite**: Never weaken, delete, or bypass existing tests. Ensure all tests pass cleanly after any change.
