# OrderBot - AI-Powered Restaurant Order Management System

An intelligent restaurant order management system that combines conversational AI with efficient order processing and management capabilities. OrderBot streamlines the ordering process through natural language interactions while providing comprehensive admin tools for restaurant operations.

##  Features

###  Conversational Ordering
- Natural language processing for customer orders
- Context-aware conversation flow
- Menu item recommendations
- Order confirmation and modifications

###  Admin Dashboard
- Real-time order monitoring
- Customer order history
- Analytics and reporting
- Menu management interface

###  RESTful API
- Comprehensive API endpoints for order management
- Secure authentication system
- Integration-friendly architecture
- RESTful design principles

###  Database Management
- SQLite database for order persistence
- Efficient data storage and retrieval
- Order history tracking
- Customer data management

##  Project Structure

```
orderbot/
├── admin/               Admin dashboard and management tools
├── api/                 API endpoints
├── core/                Core business logic
├── data/                Data handling and processing
├── deployment/          Deployment configurations
├── docs/                Documentation files
├── models/              Database models and schemas
├── services/            Service layer for business operations
├── templates/           HTML templates for web interface
├── tests/               Unit and integration tests
├── utils/               Utility functions and helpers
├── app.py               Main application entry point
├── config.py            Configuration management
├── requirements.txt     Python dependencies
├── Dockerfile           Docker container configuration
├── docker-compose.yml   Multi-container orchestration
└── Procfile             Heroku deployment configuration
```

##  Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- SQLite3
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/adithya0101/orderbot.git
cd orderbot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
python -c "from app import init_db; init_db()"
```

6. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

##  Docker Deployment

1. Build and start containers:
```bash
docker-compose up -d
```

2. Stop containers:
```bash
docker-compose down
```

### Using Docker

```bash
# Build the image
docker build -t orderbot .

# Run the container
docker run -p 5000:5000 orderbot
```

##  Cloud Deployment

### Heroku
```bash
heroku login
```

```bash
heroku create your-app-name
```

4. Deploy:
```bash
git push heroku main
```

##  Configuration
```env
# Application Settings
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///restaurant_orders.db

# API Configuration
API_KEY=your-api-key-here

# AI/NLP Settings
NLP_MODEL=your-model-name
CONFIDENCE_THRESHOLD=0.85
```

##  API Documentation

### Authentication
All API requests require authentication via API key:
```
Authorization: Bearer YOUR_API_KEY
```

### Endpoints

#### Orders
- `POST /api/orders` - Create new order
- `GET /api/orders` - List all orders
- `GET /api/orders/<id>` - Get specific order
- `PUT /api/orders/<id>` - Update order
- `DELETE /api/orders/<id>` - Cancel order

#### Menu
- `GET /api/menu` - Get menu items
- `POST /api/menu` - Add menu item (admin only)
- `PUT /api/menu/<id>` - Update menu item (admin only)
- `DELETE /api/menu/<id>` - Remove menu item (admin only)

#### Chat
- `POST /api/chat` - Process conversational order

For detailed API documentation, visit `/docs` endpoint when the server is running.

##  Testing

Run the test suite:
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/test_orders.py
```

## 🛠️ Development

### Setting up development environment

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Set Flask to development mode:
```bash
export FLASK_ENV=development
```

3. Enable debug mode:
```bash
export FLASK_DEBUG=1
```

### Code Style

This project follows PEP 8 style guidelines. Format code using:
```bash
black .
flake8 .
```

##  Features in Detail

### Conversational AI
The bot uses natural language processing to understand customer orders, handle modifications, and provide recommendations based on menu availability and customer preferences.

### Admin Dashboard
Comprehensive dashboard for restaurant staff to monitor orders, manage menu items, view analytics, and handle customer inquiries.

### Order Management
Complete order lifecycle management from creation to fulfillment, including status tracking, modification handling, and customer notifications.

---

**Note:** This project is under active development. Features and documentation may change. 


