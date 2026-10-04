"""
Smart Canteen Model Context Protocol (MCP) package.

Exposes read-only tools for inspecting menu items, low-stock inventory,
order status, and student order history.
"""
from mcp_server.server import (
    mcp,
    get_available_menu_items,
    get_low_stock_items,
    get_order_status,
    get_order_history,
)

__all__ = [
    "mcp",
    "get_available_menu_items",
    "get_low_stock_items",
    "get_order_status",
    "get_order_history",
]
