# Smart Canteen MCP Integration

This directory contains the **Model Context Protocol (MCP)** server for the Smart Canteen Booking System.

---

## 1. Purpose of MCP in this Project

The Model Context Protocol (MCP) server provides a standard, secure protocol for external AI agents, developer assistants, and IDEs (such as Kiro) to inspect real-time canteen data without needing custom API glue or database access.

It strictly provides **read-only** operational inspection into:
- Current menu availability
- Low-stock inventory alerts
- Specific order status details
- Student order histories

---

## 2. Architecture & Service Layer Integration

The MCP server connects directly to the existing Smart Canteen service layer rather than duplicating queries or business logic:

```
External AI / MCP Client (e.g. Kiro IDE, stdio)
                     │
                     ▼
             MCP Tool Interface
             (mcp_server/server.py)
                     │
                     ▼
           Existing Service Layer
   (MenuService, InventoryService, OrderService)
                     │
                     ▼
           SQLAlchemy ORM Models
          (backend/models/*.py)
                     │
                     ▼
           SQLite Database (data/canteen.db)
```

The MCP server is isolated from the REST API endpoints and does not alter any existing application behavior.

---

## 3. How to Start the MCP Server

The server uses the standard MCP `stdio` transport. It can be launched directly or as a subprocess by MCP clients:

```bash
# Run directly with Python module syntax
python -m mcp_server.server

# Or run the script directly
python mcp_server/server.py
```

> **Note**: Stdio transport transmits JSON-RPC messages across `stdin` and `stdout`. Status and log messages are redirected to `stderr` to maintain protocol integrity.

---

## 4. Available MCP Tools

All tools are strictly **read-only**.

### Tool 1: `get_available_menu_items`
- **Description**: Returns all currently active, non-deleted menu items available for order.
- **Input Parameters**: None (`{}`)
- **Output**: Array of menu item objects:
  ```json
  [
    {
      "id": 1,
      "name": "Veggie Burger",
      "description": "Crispy vegetable patty with fresh lettuce",
      "price": 5.50,
      "category": "Meals",
      "stock_quantity": 15,
      "is_available": true
    }
  ]
  ```

### Tool 2: `get_low_stock_items`
- **Description**: Returns all items currently at or below their configured stock threshold (`stock_quantity <= stock_threshold`).
- **Input Parameters**: None (`{}`)
- **Output**: Array of low-stock item objects:
  ```json
  [
    {
      "id": 2,
      "name": "Cold Coffee",
      "category": "Beverages",
      "stock_quantity": 3,
      "stock_threshold": 5,
      "price": 2.50,
      "is_available": true
    }
  ]
  ```

### Tool 3: `get_order_status`
- **Description**: Returns real-time status and line items for a specific order.
- **Input Parameters**:
  - `order_id` (*integer*, required): The ID of the order.
- **Output**: Order detail object:
  ```json
  {
    "found": true,
    "order_id": 101,
    "student_id": "STU12345",
    "status": "ready",
    "total_price": 8.00,
    "created_at": "2026-10-04T12:00:00",
    "updated_at": "2026-10-04T12:15:00",
    "items": [
      {
        "menu_item_id": 1,
        "name": "Veggie Burger",
        "quantity": 1,
        "price_at_order_time": 5.50
      }
    ]
  }
  ```

### Tool 4: `get_order_history`
- **Description**: Returns all orders placed by a specific student, with optional status filtering.
- **Input Parameters**:
  - `student_id` (*string*, required): The student identifier.
  - `status` (*string*, optional): Filter by status (`pending`, `preparing`, `ready`, `completed`, `cancelled`).
- **Output**: Array of order summaries sorted newest first:
  ```json
  [
    {
      "order_id": 101,
      "student_id": "STU12345",
      "status": "ready",
      "total_price": 8.00,
      "created_at": "2026-10-04T12:00:00",
      "item_count": 1,
      "items": [...]
    }
  ]
  ```

---

## 5. Security & Read-Only Guarantees

1. **No Data Mutation**: None of the tools create, update, cancel, or delete records. No `db.commit()` is ever invoked.
2. **No Privilege Escalation**: Tools do not bypass session authentication or expose admin credentials.
3. **No Secret Exposure**: Password hashes, session tokens, JWTs, and API keys are completely excluded from all responses.
4. **Isolated Database Sessions**: Every tool execution runs in its own scoped session that is immediately closed upon completion.
