"""
Unit tests for Smart Canteen Model Context Protocol (MCP) server.

Verifies:
- MCP server initialization and tool registration
- Schema definitions and argument specifications
- Accurate data retrieval using service layer
- Protocol execution via FastMCP interface
- Strict read-only invariants and security guarantees
"""
import pytest
import json
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.models.menu_item import MenuItem
from backend.models.order import Order
from backend.models.order_item import OrderItem

import mcp_server.server as mcp_module
from mcp_server import (
    mcp,
    get_available_menu_items,
    get_low_stock_items,
    get_order_status,
    get_order_history,
)


@pytest.fixture
def mcp_test_db(monkeypatch):
    """
    Create an isolated in-memory SQLite database populated with test fixtures
    and monkeypatch mcp_server.server.SessionLocal.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Monkeypatch the MCP server session factory
    monkeypatch.setattr(mcp_module, "SessionLocal", TestingSession)

    session = TestingSession()

    # Seed menu items
    # Item 1: Available, adequate stock (stock 10 > threshold 5)
    item_adequate = MenuItem(
        name="Veggie Burger",
        description="Fresh vegetarian burger",
        price=Decimal("6.50"),
        category="Meals",
        stock_quantity=10,
        stock_threshold=5,
        is_available=True,
        is_deleted=False,
    )
    # Item 2: Available, low stock (stock 2 <= threshold 5)
    item_low_stock = MenuItem(
        name="Apple Juice",
        description="Fresh cold-pressed apple juice",
        price=Decimal("3.00"),
        category="Beverages",
        stock_quantity=2,
        stock_threshold=5,
        is_available=True,
        is_deleted=False,
    )
    # Item 3: Unavailable, low stock (stock 0 <= threshold 2)
    item_unavailable = MenuItem(
        name="Choco Muffin",
        description="Double chocolate muffin",
        price=Decimal("2.50"),
        category="Snacks",
        stock_quantity=0,
        stock_threshold=2,
        is_available=False,
        is_deleted=False,
    )
    # Item 4: Soft-deleted item
    item_deleted = MenuItem(
        name="Discontinued Tea",
        description="Old tea",
        price=Decimal("1.00"),
        category="Beverages",
        stock_quantity=0,
        stock_threshold=0,
        is_available=False,
        is_deleted=True,
    )
    session.add_all([item_adequate, item_low_stock, item_unavailable, item_deleted])
    session.commit()

    # Seed orders for student STU001
    order1 = Order(
        student_id="STU001",
        total_price=Decimal("9.50"),
        status="preparing",
    )
    order2 = Order(
        student_id="STU001",
        total_price=Decimal("6.50"),
        status="completed",
    )
    # Seed order for student STU002
    order3 = Order(
        student_id="STU002",
        total_price=Decimal("3.00"),
        status="ready",
    )
    session.add_all([order1, order2, order3])
    session.flush()

    # Order items
    oi1 = OrderItem(
        order_id=order1.id,
        menu_item_id=item_adequate.id,
        quantity=1,
        price_at_order_time=Decimal("6.50"),
    )
    oi2 = OrderItem(
        order_id=order1.id,
        menu_item_id=item_low_stock.id,
        quantity=1,
        price_at_order_time=Decimal("3.00"),
    )
    oi3 = OrderItem(
        order_id=order2.id,
        menu_item_id=item_adequate.id,
        quantity=1,
        price_at_order_time=Decimal("6.50"),
    )
    oi4 = OrderItem(
        order_id=order3.id,
        menu_item_id=item_low_stock.id,
        quantity=1,
        price_at_order_time=Decimal("3.00"),
    )
    session.add_all([oi1, oi2, oi3, oi4])
    session.commit()

    yield {
        "session": session,
        "item_adequate": item_adequate,
        "item_low_stock": item_low_stock,
        "item_unavailable": item_unavailable,
        "order1": order1,
        "order2": order2,
        "order3": order3,
    }

    session.close()


class TestMCPServerRegistration:
    """Tests for MCP server tool registration and schema validation."""

    @pytest.mark.asyncio
    async def test_server_metadata(self):
        """Verify server instance name."""
        assert mcp.name == "SmartCanteenServer"

    @pytest.mark.asyncio
    async def test_expected_tools_registered(self):
        """Verify that all 4 required read-only tools are registered with MCP."""
        tools = await mcp.list_tools()
        registered_names = {t.name for t in tools}

        expected_tools = {
            "get_available_menu_items",
            "get_low_stock_items",
            "get_order_status",
            "get_order_history",
        }
        assert expected_tools.issubset(registered_names)

    @pytest.mark.asyncio
    async def test_tool_schemas(self):
        """Verify that tool parameter schemas match expectations."""
        tools = await mcp.list_tools()
        tool_map = {t.name: t for t in tools}

        # get_order_status requires order_id (integer)
        status_tool = tool_map["get_order_status"]
        assert "order_id" in status_tool.inputSchema["properties"]
        assert "order_id" in status_tool.inputSchema["required"]

        # get_order_history requires student_id (string)
        history_tool = tool_map["get_order_history"]
        assert "student_id" in history_tool.inputSchema["properties"]
        assert "student_id" in history_tool.inputSchema["required"]


class TestMCPToolsExecution:
    """Tests for tool execution logic and data accuracy."""

    def test_get_available_menu_items(self, mcp_test_db):
        """Verify get_available_menu_items only returns available, non-deleted items."""
        items = get_available_menu_items()

        # Should include item_adequate and item_low_stock, but exclude unavailable and deleted
        names = [item["name"] for item in items]
        assert "Veggie Burger" in names
        assert "Apple Juice" in names
        assert "Choco Muffin" not in names
        assert "Discontinued Tea" not in names

        # Verify item structure
        sample = next(i for i in items if i["name"] == "Veggie Burger")
        assert sample["price"] == 6.50
        assert sample["category"] == "Meals"
        assert sample["stock_quantity"] == 10
        assert sample["is_available"] is True

    def test_get_low_stock_items(self, mcp_test_db):
        """Verify get_low_stock_items returns items where stock <= threshold."""
        low_items = get_low_stock_items()
        names = [item["name"] for item in low_items]

        # Apple Juice (2 <= 5) and Choco Muffin (0 <= 2) are low stock
        assert "Apple Juice" in names
        assert "Choco Muffin" in names
        # Veggie Burger (10 > 5) is NOT low stock
        assert "Veggie Burger" not in names
        # Discontinued Tea is deleted, so excluded
        assert "Discontinued Tea" not in names

    def test_get_order_status_existing(self, mcp_test_db):
        """Verify get_order_status returns complete details for existing order."""
        order_id = mcp_test_db["order1"].id
        result = get_order_status(order_id)

        assert result["found"] is True
        assert result["order_id"] == order_id
        assert result["student_id"] == "STU001"
        assert result["status"] == "preparing"
        assert result["total_price"] == 9.50
        assert len(result["items"]) == 2

    def test_get_order_status_not_found(self, mcp_test_db):
        """Verify get_order_status returns graceful not-found object for invalid ID."""
        result = get_order_status(99999)

        assert result["found"] is False
        assert result["order_id"] == 99999
        assert "not found" in result["error"].lower()

    def test_get_order_history_all(self, mcp_test_db):
        """Verify get_order_history returns all orders for a student."""
        orders = get_order_history("STU001")
        assert len(orders) == 2

        # Check order IDs
        order_ids = [o["order_id"] for o in orders]
        assert mcp_test_db["order1"].id in order_ids
        assert mcp_test_db["order2"].id in order_ids

    def test_get_order_history_with_status_filter(self, mcp_test_db):
        """Verify get_order_history filters orders by status."""
        orders = get_order_history("STU001", status="preparing")
        assert len(orders) == 1
        assert orders[0]["status"] == "preparing"
        assert orders[0]["order_id"] == mcp_test_db["order1"].id

    def test_get_order_history_unknown_student(self, mcp_test_db):
        """Verify get_order_history returns empty list for student with no orders."""
        orders = get_order_history("NONEXISTENT_STUDENT")
        assert orders == []


class TestMCPProtocolCall:
    """Tests calling tools through the FastMCP protocol call_tool interface."""

    @pytest.mark.asyncio
    async def test_call_tool_menu(self, mcp_test_db):
        """Verify async call_tool invocation for get_available_menu_items."""
        results = await mcp.call_tool("get_available_menu_items", {})
        assert len(results) > 0
        items = [json.loads(r.text) for r in results]
        names = [item["name"] for item in items]
        assert "Veggie Burger" in names

    @pytest.mark.asyncio
    async def test_call_tool_low_stock(self, mcp_test_db):
        """Verify async call_tool invocation for get_low_stock_items."""
        results = await mcp.call_tool("get_low_stock_items", {})
        assert len(results) > 0
        items = [json.loads(r.text) for r in results]
        names = [item["name"] for item in items]
        assert "Apple Juice" in names

    @pytest.mark.asyncio
    async def test_call_tool_order_status(self, mcp_test_db):
        """Verify async call_tool invocation for get_order_status."""
        order_id = mcp_test_db["order3"].id
        results = await mcp.call_tool("get_order_status", {"order_id": order_id})
        assert len(results) > 0
        content = json.loads(results[0].text)
        assert content["found"] is True
        assert content["status"] == "ready"

    @pytest.mark.asyncio
    async def test_call_tool_order_history(self, mcp_test_db):
        """Verify async call_tool invocation for get_order_history."""
        results = await mcp.call_tool("get_order_history", {"student_id": "STU001"})
        assert len(results) > 0
        orders = [json.loads(r.text) for r in results]
        assert len(orders) == 2


class TestMCPSecurityAndReadOnlyInvariants:
    """Tests verifying read-only safety guarantees of the MCP server."""

    @pytest.mark.asyncio
    async def test_no_mutation_tools_exposed(self):
        """Verify that no mutating tool names exist on the MCP server."""
        tools = await mcp.list_tools()
        mutation_keywords = [
            "create",
            "insert",
            "update",
            "delete",
            "drop",
            "modify",
            "cancel",
            "checkout",
            "pay",
            "login",
            "auth",
            "password",
            "token",
        ]
        for tool in tools:
            for keyword in mutation_keywords:
                assert keyword not in tool.name.lower(), (
                    f"Forbidden mutation keyword '{keyword}' found in tool name '{tool.name}'"
                )

    def test_database_unmodified_after_tool_calls(self, mcp_test_db):
        """Verify tool executions do not alter database counts or record contents."""
        db = mcp_test_db["session"]
        initial_menu_count = db.query(MenuItem).count()
        initial_order_count = db.query(Order).count()
        initial_order_item_count = db.query(OrderItem).count()

        # Run all tools
        get_available_menu_items()
        get_low_stock_items()
        get_order_status(mcp_test_db["order1"].id)
        get_order_history("STU001")

        # Verify record counts are completely unchanged
        assert db.query(MenuItem).count() == initial_menu_count
        assert db.query(Order).count() == initial_order_count
        assert db.query(OrderItem).count() == initial_order_item_count
