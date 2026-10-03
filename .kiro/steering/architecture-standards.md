# Architecture and Technology Standards

## Technology Stack

### Frontend
- **HTML5**: Semantic HTML with proper structure
- **CSS3**: Modern CSS with Flexbox/Grid for layouts
- **Vanilla JavaScript (ES6+)**: No frameworks - use modules, classes, and modern syntax
- **No external dependencies**: Keep frontend lightweight and framework-free

### Backend
- **Python 3.8+**: Modern Python with type hints
- **FastAPI**: For REST API endpoints with automatic OpenAPI docs
- **Uvicorn**: ASGI server for running FastAPI
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Request/response validation schemas

### Database
- **SQLite**: File-based database for simplicity
- **SQLAlchemy ORM**: Always use ORM - never write raw SQL

### Architecture
- **REST API**: Stateless HTTP endpoints following REST principles
- **Three-tier architecture**: Frontend ↔ Backend API ↔ Database
- **Service layer pattern**: Separate business logic from route handlers

## Project Structure

```
smart-canteen-manager/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection setup
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── menu_item.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   └── session.py
│   ├── schemas/                # Pydantic validation schemas
│   │   ├── menu_item.py
│   │   ├── order.py
│   │   └── auth.py
│   ├── routes/                 # API route handlers
│   │   ├── auth.py
│   │   ├── menu.py
│   │   ├── orders.py
│   │   ├── admin.py
│   │   └── ai_assistant.py
│   ├── services/               # Business logic layer
│   │   ├── menu_service.py
│   │   ├── order_service.py
│   │   ├── inventory_service.py
│   │   ├── analytics_service.py
│   │   └── ai_service.py
│   ├── middleware/             # Middleware components
│   │   ├── auth_middleware.py
│   │   ├── logging_middleware.py
│   │   └── rate_limit_middleware.py
│   └── utils/                  # Shared utilities
│       ├── validation.py
│       └── security.py
├── frontend/
│   ├── index.html              # Login page
│   ├── student.html            # Student interface
│   ├── admin.html              # Admin interface
│   ├── css/
│   │   ├── main.css            # Global styles
│   │   ├── components.css      # Component styles
│   │   └── responsive.css      # Media queries
│   └── js/
│       ├── auth.js             # Authentication
│       ├── api.js              # API client
│       ├── menu.js             # Menu display
│       ├── cart.js             # Shopping cart
│       ├── orders.js           # Order management
│       ├── admin.js            # Admin features
│       ├── chat.js             # AI assistant
│       └── utils.js            # Utilities
├── tests/
│   ├── unit/                   # Unit tests
│   ├── properties/             # Property-based tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
├── scripts/
│   ├── init_db.py              # Database initialization
│   └── seed_data.py            # Sample data seeding
├── logs/                       # Application logs
├── data/                       # SQLite database file
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
└── README.md                   # Setup and usage docs
```

## Architectural Principles

### Separation of Concerns
- **Routes**: Handle HTTP request/response only
- **Services**: Contain all business logic
- **Models**: Define data structure and relationships
- **Schemas**: Validate request/response data

### Example Pattern
```python
# Route handler (minimal logic)
@router.post("/orders")
async def create_order(order_data: OrderCreate, user: User = Depends(get_current_user)):
    order = order_service.create_order(user.id, order_data)
    return order

# Service layer (business logic)
class OrderService:
    def create_order(self, student_id: str, order_data: OrderCreate):
        # Validate items
        # Check stock
        # Create order
        # Decrement stock
        # Return order
```

### Database Access
- **Always use SQLAlchemy ORM** - no raw SQL queries
- **Use transactions** for multi-table operations
- **Use relationships** instead of manual joins

### API Design
- **RESTful endpoints**: Use proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- **Consistent URL structure**: `/api/v1/{resource}/{id}/{action}`
- **Status codes**: 200 (OK), 201 (Created), 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found), 500 (Server Error)

### Error Handling
- **Consistent format**: All errors return `{"error": {"code": "...", "message": "...", "details": {...}}}`
- **Never expose internals**: Don't leak stack traces or database details to clients
- **Log everything**: Use proper logging levels (DEBUG, INFO, WARNING, ERROR)

### Configuration
- **Environment variables**: Use `.env` file for configuration
- **No hardcoded values**: All URLs, keys, timeouts should be configurable
- **Sensible defaults**: Provide defaults for optional config

### Security First
- **Input validation**: Validate all user input with Pydantic
- **SQL injection prevention**: Always use ORM (never raw SQL)
- **Authentication**: Require session tokens for protected endpoints
- **Authorization**: Check user roles before allowing actions
- **Rate limiting**: Prevent abuse with request limits

## Dependencies Management

### Python Dependencies (requirements.txt)
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pytest>=7.4.0
hypothesis>=6.90.0
```

### No Frontend Dependencies
- Use browser-native APIs
- No npm, webpack, or build tools required
- Simple HTTP server for local development

## Development Workflow

1. **Set up environment**: Create venv, install dependencies
2. **Configure**: Copy `.env.example` to `.env`, adjust settings
3. **Initialize database**: Run init script to create tables
4. **Seed data**: Load sample data for testing
5. **Start backend**: Run uvicorn server
6. **Serve frontend**: Use Python HTTP server or open HTML directly
7. **Develop**: Edit code, tests pass, iterate
8. **Test**: Run property tests, unit tests, integration tests
9. **Document**: Keep README and API docs updated

## API Documentation

- **Auto-generated**: FastAPI generates OpenAPI docs at `/docs`
- **Keep updated**: Add descriptions and examples to route decorators
- **Test with Swagger UI**: Use `/docs` to test endpoints interactively
