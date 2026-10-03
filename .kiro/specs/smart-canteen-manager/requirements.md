# Requirements Document

## Introduction

The Smart Canteen Manager is a web application for Kiro University that enables students to browse menus and place orders while providing canteen administrators with tools to manage inventory, menu items, orders, and sales analytics. The system includes an AI-powered assistant that provides intelligent responses based on current canteen data while maintaining full functionality when AI services are unavailable.

## Glossary

- **System**: The Smart Canteen Manager web application
- **Student**: A university student user who can browse menus and place orders
- **Admin**: A canteen administrator who manages menu items, inventory, and orders
- **Menu_Item**: A food or beverage item available for purchase
- **Order**: A collection of menu items requested by a student
- **Cart**: A temporary collection of menu items before order placement
- **Inventory**: The stock levels for all menu items
- **AI_Assistant**: The optional AI-powered chatbot component
- **Frontend**: The HTML/CSS/JavaScript web interface
- **Backend**: The FastAPI REST API server
- **Database**: The SQLite data persistence layer
- **Stock_Threshold**: A configurable minimum quantity that triggers low-stock alerts
- **Order_Status**: The current state of an order (pending, preparing, ready, completed, cancelled)
- **API**: The REST API endpoints for communication between frontend and backend
- **Session**: A user's authenticated interaction with the system

## Requirements

### Requirement 1: Student Menu Browsing

**User Story:** As a student, I want to view today's available menu items, so that I can decide what to order.

#### Acceptance Criteria

1. WHEN a student accesses the menu page, THE Frontend SHALL display all menu items marked as available
2. FOR EACH menu item displayed, THE Frontend SHALL show the item name, description, price, and availability status
3. THE Backend SHALL provide an API endpoint that returns all available menu items with their details
4. WHEN the menu data is requested, THE Backend SHALL return items sorted by category and name
5. IF no menu items are available, THEN THE Frontend SHALL display a message indicating the menu is currently empty

### Requirement 2: Menu Search and Filtering

**User Story:** As a student, I want to search and filter menu items, so that I can quickly find specific food items.

#### Acceptance Criteria

1. THE Frontend SHALL provide a search input field that filters menu items by name or description
2. WHEN a student types in the search field, THE Frontend SHALL update the displayed menu items in real-time
3. THE Frontend SHALL provide filter options for food categories
4. WHEN a filter is applied, THE Frontend SHALL display only menu items matching the selected criteria
5. THE Frontend SHALL allow clearing all filters to return to the full menu view

### Requirement 3: Shopping Cart Management

**User Story:** As a student, I want to add items to a cart and modify quantities, so that I can prepare my order before submitting.

#### Acceptance Criteria

1. WHEN a student clicks an add-to-cart button, THE Frontend SHALL add the selected menu item to the cart with quantity of one
2. THE Frontend SHALL allow students to increment or decrement item quantities in the cart
3. THE Frontend SHALL allow students to remove individual items from the cart
4. THE Frontend SHALL display the current cart contents with item names, quantities, individual prices, and total price
5. THE Frontend SHALL persist cart contents in browser local storage until order placement or explicit cart clearing
6. WHEN cart contents change, THE Frontend SHALL recalculate and display the updated total price

### Requirement 4: Order Placement

**User Story:** As a student, I want to place an order from my cart, so that the canteen can prepare my food.

#### Acceptance Criteria

1. WHEN a student submits a cart with at least one item, THE Frontend SHALL send an order creation request to the Backend
2. THE Backend SHALL validate that all items in the order exist and are currently available
3. THE Backend SHALL create a new order record with a unique order ID, timestamp, student identifier, order items, quantities, and total price
4. THE Backend SHALL set the initial order status to "pending"
5. WHEN the order is successfully created, THE Backend SHALL return the order ID and confirmation details
6. THE Frontend SHALL display an order confirmation message with the order ID
7. THE Frontend SHALL clear the cart after successful order placement
8. IF order creation fails, THEN THE Backend SHALL return a descriptive error message

### Requirement 5: Order Status Tracking

**User Story:** As a student, I want to view my current order status, so that I know when my food is ready.

#### Acceptance Criteria

1. THE Backend SHALL provide an API endpoint that returns order details and current status by order ID
2. WHEN a student requests order status, THE Frontend SHALL display the order ID, order items, total price, and current status
3. THE Frontend SHALL display status in human-readable form (Pending, Preparing, Ready for Pickup, Completed, Cancelled)
4. THE Frontend SHALL provide a way for students to refresh the order status
5. WHEN an order status is "ready", THE Frontend SHALL highlight this visually to attract attention

### Requirement 6: Order History

**User Story:** As a student, I want to view my past orders, so that I can reorder items I enjoyed or track my spending.

#### Acceptance Criteria

1. THE Backend SHALL provide an API endpoint that returns all orders for a given student identifier
2. WHEN a student accesses order history, THE Frontend SHALL display orders sorted by date (newest first)
3. FOR EACH historical order, THE Frontend SHALL display the order ID, date, items, total price, and final status
4. THE Frontend SHALL allow filtering order history by date range
5. THE Frontend SHALL provide a way to view full details of any historical order

### Requirement 7: Admin Menu Management

**User Story:** As an admin, I want to add, edit, and delete menu items, so that I can keep the menu current.

#### Acceptance Criteria

1. THE Backend SHALL provide API endpoints for creating, reading, updating, and deleting menu items
2. WHEN an admin creates a menu item, THE Backend SHALL require name, description, price, category, and initial stock quantity
3. THE Backend SHALL validate that menu item names are unique
4. THE Backend SHALL validate that prices are positive numbers
5. WHEN an admin edits a menu item, THE Backend SHALL update only the provided fields
6. WHEN an admin deletes a menu item, THE Backend SHALL mark it as deleted without removing historical order references
7. THE Frontend SHALL provide an admin interface with forms for creating and editing menu items
8. THE Frontend SHALL display confirmation dialogs before deleting menu items

### Requirement 8: Menu Item Availability Control

**User Story:** As an admin, I want to enable or disable menu item availability, so that I can control what students can order.

#### Acceptance Criteria

1. THE Backend SHALL store an availability status (available or unavailable) for each menu item
2. THE Backend SHALL provide an API endpoint to toggle menu item availability
3. WHEN a menu item is marked unavailable, THE Backend SHALL exclude it from student menu queries
4. WHEN a menu item is marked unavailable, THE Backend SHALL reject new orders containing that item
5. THE Frontend SHALL provide a toggle control in the admin interface for each menu item's availability
6. THE Frontend SHALL visually distinguish between available and unavailable items in the admin view

### Requirement 9: Inventory Management

**User Story:** As an admin, I want to manage inventory levels, so that I can track stock and prevent ordering unavailable items.

#### Acceptance Criteria

1. THE Backend SHALL maintain a stock quantity for each menu item
2. THE Backend SHALL provide API endpoints to view and update inventory levels
3. WHEN an admin updates inventory, THE Backend SHALL validate that quantities are non-negative integers
4. THE Frontend SHALL display current stock levels in the admin inventory view
5. THE Frontend SHALL allow admins to increment or decrement stock quantities
6. THE Frontend SHALL allow admins to set specific stock quantities directly
7. WHEN an order is placed, THE Backend SHALL decrement stock quantities for ordered items
8. IF insufficient stock exists for an order, THEN THE Backend SHALL reject the order with a descriptive error message

### Requirement 10: Order Queue Management

**User Story:** As an admin, I want to view incoming orders and update their status, so that I can manage order fulfillment.

#### Acceptance Criteria

1. THE Backend SHALL provide an API endpoint that returns all orders sorted by creation time
2. THE Backend SHALL provide an API endpoint to update order status
3. THE Backend SHALL validate that order status transitions are valid (pending → preparing → ready → completed)
4. THE Frontend SHALL display all orders in the admin dashboard with order ID, student identifier, items, total price, timestamp, and current status
5. THE Frontend SHALL allow filtering orders by status
6. THE Frontend SHALL provide controls to update order status for each order
7. WHEN an admin updates order status, THE Frontend SHALL send the update request to the Backend and refresh the order list
8. THE Frontend SHALL visually group orders by status for easy scanning

### Requirement 11: Low Stock Alerts

**User Story:** As an admin, I want to receive alerts for low-stock items, so that I can restock before running out.

#### Acceptance Criteria

1. THE Backend SHALL maintain a configurable stock threshold value for each menu item
2. THE Backend SHALL identify menu items where current stock is at or below the threshold
3. THE Backend SHALL provide an API endpoint that returns all low-stock items
4. THE Frontend SHALL display low-stock alerts prominently on the admin dashboard
5. THE Frontend SHALL show the item name, current stock, and threshold for each low-stock alert
6. THE Frontend SHALL allow admins to configure stock thresholds for individual menu items
7. WHEN stock is replenished above the threshold, THE Frontend SHALL remove the item from the alert list

### Requirement 12: Sales Analytics

**User Story:** As an admin, I want to view daily sales statistics, so that I can understand revenue and order patterns.

#### Acceptance Criteria

1. THE Backend SHALL calculate total daily revenue from completed orders
2. THE Backend SHALL calculate total daily order count
3. THE Backend SHALL provide an API endpoint that returns daily sales statistics for a specified date
4. THE Frontend SHALL display daily sales statistics on the admin dashboard including total revenue, order count, and average order value
5. THE Frontend SHALL allow selecting different dates to view historical sales data
6. THE Backend SHALL support date range queries for sales statistics
7. THE Frontend SHALL display sales trends when a date range is selected

### Requirement 13: Popular Items Analysis

**User Story:** As an admin, I want to identify popular menu items, so that I can make informed stocking and menu decisions.

#### Acceptance Criteria

1. THE Backend SHALL calculate popularity scores based on order frequency and quantity
2. THE Backend SHALL provide an API endpoint that returns the top N most popular items for a specified time period
3. THE Frontend SHALL display popular items on the admin dashboard with item name, total quantity ordered, and number of orders
4. THE Frontend SHALL allow configuring the time period for popularity analysis (daily, weekly, monthly)
5. THE Frontend SHALL allow configuring how many top items to display
6. THE Backend SHALL exclude cancelled orders from popularity calculations

### Requirement 14: AI Canteen Assistant

**User Story:** As a student or admin, I want to ask questions to an AI assistant, so that I can get quick answers about the canteen.

#### Acceptance Criteria

1. THE Frontend SHALL provide a chat interface for interacting with the AI Assistant
2. WHEN a user submits a question, THE Frontend SHALL send the question to the Backend
3. THE Backend SHALL send the question and relevant context (menu items, orders, inventory, sales data) to an external AI service
4. THE Backend SHALL receive the AI response and return it to the Frontend
5. THE Frontend SHALL display the AI response in the chat interface
6. IF the AI service is unavailable or returns an error, THEN THE Backend SHALL return a fallback message indicating the assistant is temporarily unavailable
7. THE System SHALL remain fully functional for all core features when the AI Assistant is unavailable
8. THE Backend SHALL implement a timeout for AI service requests to prevent indefinite waiting
9. THE Backend SHALL sanitize user input before sending to the AI service to prevent injection attacks

### Requirement 15: User Authentication and Sessions

**User Story:** As a user, I want to log in with my role, so that I can access appropriate features.

#### Acceptance Criteria

1. THE Frontend SHALL provide a login interface that accepts a user identifier and role selection
2. THE Backend SHALL provide an API endpoint for creating user sessions
3. THE Backend SHALL generate a unique session token upon successful authentication
4. THE Backend SHALL associate each session with a user identifier and role (student or admin)
5. THE Frontend SHALL store the session token and include it in subsequent API requests
6. THE Backend SHALL validate session tokens for protected endpoints
7. THE Backend SHALL restrict admin endpoints to users with admin role
8. THE Backend SHALL allow student endpoints for users with student or admin role
9. IF a session token is invalid or expired, THEN THE Backend SHALL return an authentication error
10. THE Frontend SHALL redirect unauthenticated users to the login page when authentication errors occur

### Requirement 16: API Error Handling

**User Story:** As a developer, I want consistent error responses from the API, so that the frontend can handle errors appropriately.

#### Acceptance Criteria

1. THE Backend SHALL return HTTP status codes that accurately reflect the error type (400 for bad requests, 404 for not found, 500 for server errors)
2. THE Backend SHALL return error responses in a consistent JSON format with error code, message, and optional details
3. WHEN validation fails, THE Backend SHALL return a 400 status with descriptive error messages indicating which fields are invalid
4. WHEN a requested resource is not found, THE Backend SHALL return a 404 status with a message identifying the missing resource
5. WHEN an authentication error occurs, THE Backend SHALL return a 401 status
6. WHEN an authorization error occurs, THE Backend SHALL return a 403 status
7. WHEN an unexpected server error occurs, THE Backend SHALL return a 500 status and log the error details for debugging

### Requirement 17: Input Validation

**User Story:** As a developer, I want comprehensive input validation, so that the system is protected from invalid data.

#### Acceptance Criteria

1. THE Backend SHALL validate all API request parameters before processing
2. THE Backend SHALL validate that required fields are present in request bodies
3. THE Backend SHALL validate that numeric fields contain valid numbers within acceptable ranges
4. THE Backend SHALL validate that string fields do not exceed maximum length limits
5. THE Backend SHALL validate that prices are positive numbers with at most two decimal places
6. THE Backend SHALL validate that quantities are non-negative integers
7. THE Backend SHALL sanitize string inputs to prevent SQL injection attacks
8. THE Backend SHALL reject requests with invalid or malformed JSON bodies

### Requirement 18: Database Schema and Persistence

**User Story:** As a developer, I want a well-designed database schema, so that data is stored reliably and efficiently.

#### Acceptance Criteria

1. THE Database SHALL store menu items with id, name, description, price, category, stock_quantity, stock_threshold, availability_status, created_at, and updated_at
2. THE Database SHALL store orders with id, student_id, total_price, status, created_at, and updated_at
3. THE Database SHALL store order items with id, order_id, menu_item_id, quantity, and price_at_order_time
4. THE Database SHALL store user sessions with id, user_id, role, token, created_at, and expires_at
5. THE Database SHALL enforce foreign key constraints between orders and order_items
6. THE Database SHALL enforce foreign key constraints between order_items and menu_items
7. THE Backend SHALL create all necessary database tables on first startup if they do not exist
8. THE Backend SHALL use database transactions for operations that modify multiple tables
9. THE Backend SHALL maintain referential integrity for all relationships

### Requirement 19: Frontend Responsive Design

**User Story:** As a user, I want the application to work well on different screen sizes, so that I can use it on mobile or desktop.

#### Acceptance Criteria

1. THE Frontend SHALL use responsive CSS that adapts to different screen widths
2. THE Frontend SHALL remain usable on screen widths from 320px to 1920px
3. WHEN viewed on mobile devices, THE Frontend SHALL display navigation in a mobile-friendly menu
4. WHEN viewed on mobile devices, THE Frontend SHALL stack content vertically for readability
5. THE Frontend SHALL use appropriate font sizes that remain readable on all screen sizes
6. THE Frontend SHALL ensure interactive elements (buttons, inputs) are appropriately sized for touch interaction on mobile devices

### Requirement 20: System Modularity and Architecture

**User Story:** As a developer, I want a modular architecture, so that the system is maintainable and extensible.

#### Acceptance Criteria

1. THE Backend SHALL organize code into separate modules for routes, services, models, and database operations
2. THE Backend SHALL separate business logic from API route handlers
3. THE Backend SHALL implement a service layer that encapsulates business logic and can be tested independently
4. THE Frontend SHALL organize code into separate files for different pages and components
5. THE Frontend SHALL separate API communication logic from UI rendering logic
6. THE Backend SHALL use dependency injection or similar patterns to manage component dependencies
7. THE System SHALL maintain clear separation between frontend, backend, database, and external services

### Requirement 21: Configuration Management

**User Story:** As a developer, I want configuration values separated from code, so that the application can be easily configured for different environments.

#### Acceptance Criteria

1. THE Backend SHALL read configuration from environment variables or a configuration file
2. THE Backend SHALL support configurable values for database path, AI service URL, AI service timeout, and server port
3. THE Backend SHALL provide sensible defaults for all configuration values
4. THE Backend SHALL validate configuration values on startup
5. IF required configuration is missing or invalid, THEN THE Backend SHALL log a descriptive error and exit gracefully
6. THE System SHALL not hard-code environment-specific values like URLs or credentials in source code

### Requirement 22: Local Development Setup

**User Story:** As a developer, I want simple setup instructions, so that I can run the application locally quickly.

#### Acceptance Criteria

1. THE System SHALL include a README file with clear setup and run instructions
2. THE System SHALL require only Python 3.8 or higher and a web browser to run
3. THE Backend SHALL automatically create the SQLite database file on first run
4. THE System SHALL include a requirements.txt file listing all Python dependencies
5. THE System SHALL start successfully after installing dependencies and running the server command
6. THE README SHALL document how to access the application after starting the server
7. THE System SHALL include sample data or a data seeding script for testing and demonstration

### Requirement 23: API Documentation

**User Story:** As a developer, I want API documentation, so that I can understand and use the available endpoints.

#### Acceptance Criteria

1. THE Backend SHALL expose OpenAPI/Swagger documentation at /docs endpoint
2. THE API documentation SHALL include all endpoints with HTTP methods, paths, parameters, request bodies, and response schemas
3. THE API documentation SHALL include example requests and responses
4. THE API documentation SHALL describe authentication requirements for protected endpoints
5. THE API documentation SHALL be automatically generated from FastAPI route definitions

### Requirement 24: Security Best Practices

**User Story:** As a developer, I want the system to follow security best practices, so that user data and operations are protected.

#### Acceptance Criteria

1. THE Backend SHALL validate and sanitize all user inputs before processing
2. THE Backend SHALL use parameterized queries for all database operations to prevent SQL injection
3. THE Backend SHALL implement rate limiting on API endpoints to prevent abuse
4. THE Backend SHALL set appropriate CORS headers to restrict cross-origin requests
5. THE Backend SHALL not expose sensitive information in error messages or logs
6. THE Backend SHALL implement session timeout and expiration
7. THE Backend SHALL use secure token generation for session tokens
8. THE Frontend SHALL not store sensitive information in browser local storage beyond session tokens

### Requirement 25: Logging and Debugging

**User Story:** As a developer, I want comprehensive logging, so that I can debug issues and monitor system behavior.

#### Acceptance Criteria

1. THE Backend SHALL log all API requests with timestamp, endpoint, method, and response status
2. THE Backend SHALL log all errors with stack traces and contextual information
3. THE Backend SHALL use different log levels (debug, info, warning, error) appropriately
4. THE Backend SHALL write logs to both console and a log file
5. THE Backend SHALL include request identifiers in logs to trace related log entries
6. THE Backend SHALL not log sensitive information like passwords or full session tokens
7. THE Backend SHALL be configurable to adjust log verbosity level

