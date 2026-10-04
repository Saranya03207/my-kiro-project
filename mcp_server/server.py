"""
Smart Canteen Model Context Protocol (MCP) Server.

Provides a minimal, secure, read-only MCP interface exposing
Smart Canteen operations to AI assistants and IDE tools.

Architecture:
    MCP Tool Request
          │
          ▼
    Existing Service Layer (MenuService, InventoryService, OrderService)
          │
          ▼
    SQLAlchemy ORM / SQLite Database
"""
import os
import sys
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp.server.fastmcp import FastMCP
from backend.database import SessionLocal
from backend.services.menu_service import MenuService
from backend.services.inventory_service import InventoryService
from backend.services.order_service import OrderService

# Initialize the MCP Server
mcp = FastMCP("SmartCanteenServer")


@contextmanager
def get_db_session():
    """
    Provide a read-only database session context.
    Ensures connection is closed cleanly after query execution.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# TOOL 1: get_available_menu_items
# ============================================================
@mcp.tool()
def get_available_menu_items() -> list:
    """
    Return currently available menu items in the canteen.

    Queries the menu service for non-deleted, available items
    sorted by category and item name.

    Returns:
        List of dictionaries containing menu item details:
        id, name, description, price, category, stock_quantity, is_available.
    """
    with get_db_session() as db:
        items = MenuService.get_available_menu_items(db, include_unavailable=False)
        return [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "price": float(item.price),
                "category": item.category,
                "stock_quantity": item.stock_quantity,
                "is_available": item.is_available,
            }
            for item in items
        ]


# ============================================================
# TOOL 2: get_low_stock_items
# ============================================================
@mcp.tool()
def get_low_stock_items() -> list:
    """
    Return menu items currently at or below their configured stock threshold.

    Identifies inventory that requires restocking attention without
    modifying stock levels or item availability.

    Returns:
        List of dictionaries with items at or below threshold:
        id, name, category, stock_quantity, stock_threshold, price, is_available.
    """
    with get_db_session() as db:
        items = InventoryService.get_low_stock_items(db)
        return [
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "stock_quantity": item.stock_quantity,
                "stock_threshold": item.stock_threshold,
                "price": float(item.price),
                "is_available": item.is_available,
            }
            for item in items
        ]


# ============================================================
# TOOL 3: get_order_status
# ============================================================
@mcp.tool()
def get_order_status(order_id: int) -> dict:
    """
    Return the status and full details of a specific order by order ID.

    Read-only inspection of order status and associated line items.
    Does not modify order state or customer information.

    Args:
        order_id: Unique integer identifier of the order.

    Returns:
        Dictionary containing order status, total price, timestamps,
        item breakdown, or an error payload if the order does not exist.
    """
    with get_db_session() as db:
        order = OrderService.get_order_by_id(db, order_id)
        if not order:
            return {
                "found": False,
                "order_id": order_id,
                "error": f"Order #{order_id} not found",
            }

        return {
            "found": True,
            "order_id": order.id,
            "student_id": order.student_id,
            "status": order.status,
            "total_price": float(order.total_price),
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
            "items": [
                {
                    "menu_item_id": item.menu_item_id,
                    "name": item.menu_item.name if item.menu_item else "Unknown",
                    "quantity": item.quantity,
                    "price_at_order_time": float(item.price_at_order_time),
                }
                for item in order.items
            ],
        }


# ============================================================
# TOOL 4: get_order_history
# ============================================================
@mcp.tool()
def get_order_history(student_id: str, status: Optional[str] = None) -> list:
    """
    Return order history for a specific student, optionally filtered by status.

    Safe, read-only query that retrieves orders placed by the student.
    Does not expose sensitive credentials, tokens, or other students' data.

    Args:
        student_id: Unique student identifier (e.g. 'STU001').
        status: Optional filter by status ('pending', 'preparing', 'ready', 'completed', 'cancelled').

    Returns:
        List of order summary dictionaries sorted by creation date descending.
    """
    with get_db_session() as db:
        orders = OrderService.get_orders_by_student(db, student_id, status=status)
        return [
            {
                "order_id": order.id,
                "student_id": order.student_id,
                "status": order.status,
                "total_price": float(order.total_price),
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "item_count": len(order.items),
                "items": [
                    {
                        "menu_item_id": item.menu_item_id,
                        "name": item.menu_item.name if item.menu_item else "Unknown",
                        "quantity": item.quantity,
                        "price_at_order_time": float(item.price_at_order_time),
                    }
                    for item in order.items
                ],
            }
            for order in orders
        ]


# ============================================================
# SERVER ENTRY POINT
# ============================================================
if __name__ == "__main__":
    # In stdio transport mode, all JSON-RPC communication happens via stdin/stdout.
    # Diagnostic and lifecycle messages must only be printed to stderr.
    print("Starting Smart Canteen MCP Server (stdio transport)...", file=sys.stderr, flush=True)
    mcp.run(transport="stdio")
