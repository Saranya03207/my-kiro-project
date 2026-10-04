"""
Unit tests for Analytics Service.
Tests daily sales calculations, date range analytics, popular items analysis,
and average order value computations.
"""
import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models.menu_item import MenuItem
from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.services.analytics_service import AnalyticsService


@pytest.fixture
def db_session():
    """Create fresh in-memory database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_menu_items(db_session):
    """Create sample menu items for analytics testing."""
    items = [
        MenuItem(
            name="Burger",
            description="Beef burger",
            price=Decimal("10.00"),
            category="Meals",
            stock_quantity=50,
            stock_threshold=5,
            is_available=True,
            is_deleted=False
        ),
        MenuItem(
            name="Pizza",
            description="Cheese pizza",
            price=Decimal("12.00"),
            category="Meals",
            stock_quantity=30,
            stock_threshold=3,
            is_available=True,
            is_deleted=False
        ),
        MenuItem(
            name="Fries",
            description="Crispy fries",
            price=Decimal("3.00"),
            category="Snacks",
            stock_quantity=100,
            stock_threshold=20,
            is_available=True,
            is_deleted=False
        ),
        MenuItem(
            name="Soda",
            description="Soft drink",
            price=Decimal("2.00"),
            category="Beverages",
            stock_quantity=50,
            stock_threshold=10,
            is_available=True,
            is_deleted=False
        ),
    ]
    for item in items:
        db_session.add(item)
    db_session.commit()
    return items


@pytest.fixture
def sample_orders(db_session, sample_menu_items):
    """Create sample orders for analytics testing."""
    today = date.today()
    burger, pizza, fries, soda = sample_menu_items
    
    # Today: 2 completed, 1 pending, 1 cancelled
    order1 = Order(
        student_id="S001",
        total_price=Decimal("20.00"),
        status="completed",
        created_at=datetime.combine(today, datetime.min.time())
    )
    db_session.add(order1)
    db_session.flush()
    db_session.add(OrderItem(order_id=order1.id, menu_item_id=burger.id, quantity=2, price_at_order_time=Decimal("10.00")))
    
    order2 = Order(student_id="S002", total_price=Decimal("12.00"), status="completed", created_at=datetime.combine(today, datetime.min.time()))
    db_session.add(order2)
    db_session.flush()
    db_session.add(OrderItem(order_id=order2.id, menu_item_id=pizza.id, quantity=1, price_at_order_time=Decimal("12.00")))
    
    order3 = Order(student_id="S003", total_price=Decimal("15.00"), status="pending", created_at=datetime.combine(today, datetime.min.time()))
    db_session.add(order3)
    db_session.flush()
    db_session.add(OrderItem(order_id=order3.id, menu_item_id=burger.id, quantity=1, price_at_order_time=Decimal("10.00")))
    
    order5 = Order(student_id="S002", total_price=Decimal("3.00"), status="cancelled", created_at=datetime.combine(today, datetime.min.time()))
    db_session.add(order5)
    db_session.flush()
    db_session.add(OrderItem(order_id=order5.id, menu_item_id=fries.id, quantity=1, price_at_order_time=Decimal("3.00")))
    
    # Yesterday: 1 completed
    yesterday = today - timedelta(days=1)
    order4 = Order(student_id="S001", total_price=Decimal("25.00"), status="completed", created_at=datetime.combine(yesterday, datetime.min.time()))
    db_session.add(order4)
    db_session.flush()
    db_session.add(OrderItem(order_id=order4.id, menu_item_id=pizza.id, quantity=2, price_at_order_time=Decimal("12.00")))
    
    db_session.commit()


class TestGetDailySales:
    """Test daily sales calculation."""
    
    def test_calculates_daily_sales_completed_only(self, db_session, sample_menu_items, sample_orders):
        """Should calculate sales for completed orders only."""
        today = date.today()
        result = AnalyticsService.get_daily_sales(db_session, today)
        
        # Today: 2 completed (20 + 12), 1 pending (15), 1 cancelled (3) - only completed count
        assert result["date"] == today.isoformat()
        assert result["total_revenue"] == Decimal("32.00")
        assert result["order_count"] == 2
        assert result["average_order_value"] == Decimal("16.00")
    
    def test_defaults_to_today(self, db_session, sample_menu_items, sample_orders):
        """Should default to today's date when not specified."""
        result = AnalyticsService.get_daily_sales(db_session)
        assert result["date"] == date.today().isoformat()
    
    def test_empty_day_returns_zero_values(self, db_session, sample_menu_items):
        """Should return zeros for day with no completed orders."""
        future_date = date.today() + timedelta(days=100)
        result = AnalyticsService.get_daily_sales(db_session, future_date)
        
        assert result["total_revenue"] == Decimal("0.00")
        assert result["order_count"] == 0
        assert result["average_order_value"] == Decimal("0.00")
    
    def test_previous_day_sales(self, db_session, sample_menu_items, sample_orders):
        """Should calculate sales for previous days."""
        yesterday = date.today() - timedelta(days=1)
        result = AnalyticsService.get_daily_sales(db_session, yesterday)
        
        assert result["total_revenue"] == Decimal("25.00")
        assert result["order_count"] == 1


class TestGetSalesByDateRange:
    """Test sales by date range calculation."""
    
    def test_returns_sales_for_date_range(self, db_session, sample_menu_items, sample_orders):
        """Should return daily sales for each day in range."""
        today = date.today()
        start_date = today - timedelta(days=1)
        result = AnalyticsService.get_sales_by_date_range(db_session, start_date, today)
        
        assert len(result) == 2
        assert result[0]["date"] == start_date.isoformat()
        assert result[1]["date"] == today.isoformat()
    
    def test_single_day_range(self, db_session, sample_menu_items, sample_orders):
        """Should handle single day range."""
        today = date.today()
        result = AnalyticsService.get_sales_by_date_range(db_session, today, today)
        
        assert len(result) == 1
        assert result[0]["date"] == today.isoformat()


class TestGetPopularItems:
    """Test popular items analysis."""
    
    def test_returns_popular_items_sorted(self, db_session, sample_menu_items, sample_orders):
        """Should return items sorted by popularity score descending."""
        result = AnalyticsService.get_popular_items(db_session, days=7, limit=10)
        
        assert len(result) > 0
        for i in range(len(result) - 1):
            assert result[i]["popularity_score"] >= result[i + 1]["popularity_score"]
    
    def test_respects_limit_parameter(self, db_session, sample_menu_items):
        """Should respect the limit parameter."""
        today = date.today()
        burger, pizza, fries, soda = sample_menu_items
        
        for i in range(20):
            order = Order(student_id=f"S{i:03d}", total_price=Decimal("10.00"), status="completed", created_at=datetime.combine(today, datetime.min.time()))
            db_session.add(order)
            db_session.flush()
            
            menu_item = [burger, pizza, fries, soda][i % 4]
            db_session.add(OrderItem(order_id=order.id, menu_item_id=menu_item.id, quantity=1, price_at_order_time=menu_item.price))
        
        db_session.commit()
        result = AnalyticsService.get_popular_items(db_session, days=7, limit=2)
        
        assert len(result) <= 2
    
    def test_popularity_score_calculation(self, db_session, sample_menu_items):
        """Should calculate score as (order_count * 0.7) + (quantity * 0.3)."""
        today = date.today()
        burger = sample_menu_items[0]
        
        # 2 orders with burger, 3 total quantity
        for i, qty in enumerate([1, 2]):
            order = Order(student_id=f"S{i}", total_price=Decimal("10.00"), status="completed", created_at=datetime.combine(today, datetime.min.time()))
            db_session.add(order)
            db_session.flush()
            db_session.add(OrderItem(order_id=order.id, menu_item_id=burger.id, quantity=qty, price_at_order_time=Decimal("10.00")))
        
        db_session.commit()
        result = AnalyticsService.get_popular_items(db_session, days=7, limit=10)
        
        burger_item = next((item for item in result if item["name"] == "Burger"), None)
        assert burger_item is not None
        assert burger_item["order_count"] == 2
        assert burger_item["total_quantity"] == 3
        
        expected_score = (2 * 0.7) + (3 * 0.3)
        assert burger_item["popularity_score"] == expected_score
    
    def test_empty_result_for_no_orders(self, db_session, sample_menu_items):
        """Should return empty list when no orders exist."""
        result = AnalyticsService.get_popular_items(db_session, days=7, limit=10)
        assert result == []


class TestCalculateAverageOrderValue:
    """Test average order value calculation."""
    
    def test_calculates_aov_for_date_range(self, db_session, sample_menu_items, sample_orders):
        """Should calculate AOV for specified date range."""
        today = date.today()
        result = AnalyticsService.calculate_average_order_value(db_session, start_date=today-timedelta(days=1), end_date=today)
        
        assert isinstance(result, Decimal)
    
    def test_completed_orders_only(self, db_session, sample_menu_items, sample_orders):
        """Should only include completed orders."""
        today = date.today()
        result = AnalyticsService.calculate_average_order_value(db_session, start_date=today, end_date=today)
        
        # 2 completed orders: 20 + 12 = 32, average 16
        assert result == Decimal("16.00")
    
    def test_returns_zero_for_no_orders(self, db_session, sample_menu_items):
        """Should return 0.00 when no completed orders in range."""
        future_date = date.today() + timedelta(days=100)
        result = AnalyticsService.calculate_average_order_value(db_session, start_date=future_date, end_date=future_date)
        
        assert result == Decimal("0.00")
    
    def test_default_parameters(self, db_session, sample_menu_items, sample_orders):
        """Should default to last 30 days."""
        result = AnalyticsService.calculate_average_order_value(db_session)
        assert isinstance(result, Decimal)


class TestIntegration:
    """Integration tests with complex scenarios."""
    
    def test_multi_item_order_analytics(self, db_session, sample_menu_items):
        """Should handle orders with multiple items."""
        today = date.today()
        burger, pizza, fries, soda = sample_menu_items
        
        order = Order(student_id="S001", total_price=Decimal("28.00"), status="completed", created_at=datetime.combine(today, datetime.min.time()))
        db_session.add(order)
        db_session.flush()
        
        for item_id, qty in [(burger.id, 1), (pizza.id, 1), (fries.id, 2), (soda.id, 1)]:
            db_session.add(OrderItem(order_id=order.id, menu_item_id=item_id, quantity=qty, price_at_order_time=Decimal("10.00")))
        
        db_session.commit()
        
        daily = AnalyticsService.get_daily_sales(db_session, today)
        assert daily["total_revenue"] == Decimal("28.00")
        
        popular = AnalyticsService.get_popular_items(db_session, days=7, limit=10)
        assert len(popular) == 4
    
    def test_multiple_students_analytics(self, db_session, sample_menu_items):
        """Should aggregate analytics across multiple students."""
        today = date.today()
        burger = sample_menu_items[0]
        
        for i in range(3):
            order = Order(student_id=f"S{i}", total_price=Decimal(str(10+i)), status="completed", created_at=datetime.combine(today, datetime.min.time()))
            db_session.add(order)
            db_session.flush()
            db_session.add(OrderItem(order_id=order.id, menu_item_id=burger.id, quantity=1, price_at_order_time=Decimal("10.00")))
        
        db_session.commit()
        
        daily = AnalyticsService.get_daily_sales(db_session, today)
        assert daily["order_count"] == 3
