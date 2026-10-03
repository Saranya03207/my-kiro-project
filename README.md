# Smart Canteen Manager

A web application for Kiro University that enables students to browse menus and place orders while providing canteen administrators with tools to manage inventory, menu items, orders, and sales analytics.

## Features

### Student Interface
- Browse available menu items with search and filtering
- Add items to shopping cart
- Place orders and track order status
- View order history
- AI-powered canteen assistant

### Admin Interface
- Manage menu items (create, update, delete, toggle availability)
- Monitor and manage inventory levels with low-stock alerts
- Process orders and update order status
- View sales analytics and popular items
- Access AI assistant with admin-specific data

## Technology Stack

### Backend
- **Python 3.8+** - Modern Python with type hints
- **FastAPI** - High-performance REST API framework
- **Uvicorn** - ASGI server
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and serialization
- **SQLite** - Lightweight database

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with Flexbox/Grid
- **Vanilla JavaScript (ES6+)** - No framework dependencies

### Testing
- **pytest** - Unit and integration testing
- **Hypothesis** - Property-based testing

## Project Structure

```
smart-canteen-manager/
├── backend/
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic validation schemas
│   ├── routes/              # API route handlers
│   ├── services/            # Business logic layer
│   ├── middleware/          # Middleware components
│   ├── utils/               # Shared utilities
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   └── main.py              # FastAPI application
├── frontend/
│   ├── html/                # HTML pages
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript modules
│   └── tests/               # Frontend tests
├── tests/
│   ├── unit/                # Unit tests
│   ├── properties/          # Property-based tests
│   └── integration/         # Integration tests
├── data/                    # SQLite database
├── logs/                    # Application logs
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone or download the project**
   ```bash
   cd smart-canteen-manager
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment (optional)**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The server will start at `http://localhost:8000`

2. **Access the application**
   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`
   - Frontend (when implemented): Open HTML files in your browser

### Database Initialization

The database is automatically initialized on first run. The SQLite database file is created at `data/canteen.db` with all necessary tables:
- `menu_items` - Food and beverage items
- `orders` - Customer orders
- `order_items` - Items within orders
- `sessions` - User authentication sessions

## API Endpoints

### Health Check
- `GET /health` - Check API health status
- `GET /` - API information and links

### Authentication (To be implemented)
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout

### Menu (To be implemented)
- `GET /api/v1/menu/items` - Get available menu items
- `GET /api/v1/menu/items/{id}` - Get specific menu item

### Orders (To be implemented)
- `POST /api/v1/orders` - Place new order
- `GET /api/v1/orders/{id}` - Get order details
- `GET /api/v1/orders/history` - Get order history

### Admin (To be implemented)
- Menu Management
- Inventory Management
- Order Management
- Analytics

Full API documentation available at `/docs` when server is running.

## Configuration

Configuration is managed through environment variables. Copy `.env.example` to `.env` and adjust values:

- `DATABASE_URL` - Database connection string (default: `sqlite:///./data/canteen.db`)
- `SERVER_HOST` - Server host (default: `0.0.0.0`)
- `SERVER_PORT` - Server port (default: `8000`)
- `SECRET_KEY` - Secret key for session tokens (change in production!)
- `AI_SERVICE_URL` - External AI service URL (optional)
- `CORS_ORIGINS` - Allowed origins for CORS
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

## Development

### Running Tests
```bash
pytest tests/ -v
```

### Running with Coverage
```bash
pytest tests/ -v --cov=backend --cov-report=html
```

### Code Style
- Python: PEP 8 (88 character line length)
- JavaScript: ES6+ conventions
- Use type hints for all Python functions
- Use docstrings for all public functions

### Property-Based Testing
The project uses Hypothesis for property-based testing of business logic:
```bash
pytest tests/properties/ -v
```

## Logging

Logs are written to:
- Console output
- `logs/canteen.log` file

Log format: `timestamp - name - level - message`

## Security

- Input validation with Pydantic schemas
- SQL injection prevention (ORM only, no raw SQL)
- Session-based authentication
- CORS protection
- Rate limiting
- Secure configuration management

## License

Copyright © 2026 Kiro University. All rights reserved.

## Support

For issues or questions, please contact the development team.

---

**Status**: ✅ Core infrastructure setup complete
- Project structure created
- Python virtual environment configured
- Dependencies installed
- Database connection established
- FastAPI application initialized
- Health check endpoint working
