"""
Analytics service for Smart Canteen Manager.
Provides sales analytics, popular items analysis, and revenue calculations.
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession

from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.models.menu_item import MenuItem


class AnalyticsService:
    """
    Service class for analytics and reporting.
    
    Responsibilities:
    - Calculate daily sales revenue and order counts
    - Generate sales data for date ranges
    - Identify popular items with various time periods
    - Calculate average order value
    - Compute popularity scores based on order frequency and quantity
    """
    
    @staticmethod
    def get_daily_sales(
        db: DBSession,
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate sales statistics for a specific day.
        
        Includes total revenue, order count, and average order value.
        Only includes completed orders (not pending, preparing, ready, or cancelled).
        
        Args:
            db: Database session
            target_date: Date to calculate sales for (defaults to today)
            
        Returns:
            Dictionary with keys:
            - date: The date queried
            - total_revenue: Total revenue for the day (Decimal)
            - order_count: Total number of orders for the day
            - average_order_value: Average price per order (Decimal)
        """
        if target_date is None:
            target_date = date.today()
        
        # Query completed orders for the target date
        orders = db.query(Order).filter(
            func.date(Order.created_at) == target_date,
            Order.status == "completed"
        ).all()
        
        # Calculate totals
        total_revenue = sum(Decimal(str(order.total_price)) for order in orders)
        order_count = len(orders)
        
        # Calculate average
        if order_count > 0:
            average_order_value = total_revenue / order_count
        else:
            average_order_value = Decimal("0.00")
        
        return {
            "date": target_date.isoformat(),
            "total_revenue": total_revenue,
            "order_count": order_count,
            "average_order_value": average_order_value
        }
    
    @staticmethod
    def get_sales_by_date_range(
        db: DBSession,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Calculate sales statistics for a range of dates.
        
        Returns daily statistics for each day in the range (inclusive).
        Only includes completed orders.
        
        Args:
            db: Database session
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of daily sales dictionaries, one per day
        """
        sales_data = []
        current_date = start_date
        
        while current_date <= end_date:
            daily_sales = AnalyticsService.get_daily_sales(db, current_date)
            sales_data.append(daily_sales)
            current_date += timedelta(days=1)
        
        return sales_data
    
    @staticmethod
    def get_popular_items(
        db: DBSession,
        days: int = 7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get the most popular menu items based on order frequency.
        
        Excludes cancelled orders. Calculates popularity score based on:
        - Order frequency (number of times ordered)
        - Quantity ordered
        - Recency (recent orders weighted more heavily)
        
        Args:
            db: Database session
            days: Number of days to look back (default: 7 for weekly)
            limit: Maximum number of items to return (default: 10)
            
        Returns:
            List of popular items with details, sorted by popularity score (descending)
            Each item has:
            - menu_item_id: Item ID
            - name: Item name
            - order_count: Number of orders containing this item
            - total_quantity: Total quantity ordered
            - popularity_score: Calculated popularity score
        """
        # Calculate cutoff date
        cutoff_date = datetime.now(datetime.now().astimezone().tzinfo) - timedelta(days=days)
        
        # Query order items from completed orders within the time period
        order_items = db.query(
            OrderItem.menu_item_id,
            MenuItem.name,
            func.count(OrderItem.id).label('order_count'),
            func.sum(OrderItem.quantity).label('total_quantity')
        ).join(
            Order, OrderItem.order_id == Order.id
        ).join(
            MenuItem, OrderItem.menu_item_id == MenuItem.id
        ).filter(
            Order.created_at >= cutoff_date,
            Order.status != "cancelled"
        ).group_by(
            OrderItem.menu_item_id,
            MenuItem.name
        ).all()
        
        # Calculate popularity scores and create result list
        popular_items = []
        for item in order_items:
            menu_item_id, name, order_count, total_quantity = item
            
            # Popularity score = (order_count * 0.7) + (total_quantity * 0.3)
            # Weighted to favor items ordered frequently, with some weight on quantity
            popularity_score = float(order_count) * 0.7 + float(total_quantity) * 0.3
            
            popular_items.append({
                "menu_item_id": menu_item_id,
                "name": name,
                "order_count": int(order_count),
                "total_quantity": int(total_quantity),
                "popularity_score": popularity_score
            })
        
        # Sort by popularity score descending
        popular_items.sort(key=lambda x: x["popularity_score"], reverse=True)
        
        # Return limited results
        return popular_items[:limit]
    
    @staticmethod
    def calculate_average_order_value(
        db: DBSession,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Decimal:
        """
        Calculate average order value for a date range.
        
        Only includes completed orders.
        
        Args:
            db: Database session
            start_date: Start date (defaults to 30 days ago)
            end_date: End date (defaults to today)
            
        Returns:
            Average order value as Decimal
        """
        if end_date is None:
            end_date = date.today()
        
        if start_date is None:
            start_date = end_date - timedelta(days=30)
        
        # Query completed orders in the range
        orders = db.query(Order).filter(
            func.date(Order.created_at) >= start_date,
            func.date(Order.created_at) <= end_date,
            Order.status == "completed"
        ).all()
        
        if not orders:
            return Decimal("0.00")
        
        total_revenue = sum(Decimal(str(order.total_price)) for order in orders)
        average = total_revenue / len(orders)
        
        return average
