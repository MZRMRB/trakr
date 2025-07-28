# Trakr Backend

A comprehensive GPS tracking and fleet management backend API built with FastAPI.

## 🚀 Features

- **User Management**: Account creation, authentication, and role-based access control
- **Organization Management**: Multi-tenant support with organization isolation
- **GPS Tracking**: Real-time location tracking and route history
- **Alarm Management**: Geofence alerts, low battery warnings, and movement detection
- **Tag Management**: GPS device management and status monitoring
- **Data Export**: CSV and Excel export functionality
- **Rate Limiting**: API rate limiting for security
- **Metrics**: Prometheus metrics for monitoring
- **Documentation**: Auto-generated API documentation

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Redis (optional, for caching)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd trakr
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=trakr
   DB_USER=postgres
   DB_PASSWORD=postgres
   JWT_SECRET_KEY=your-secret-key-here
   JWT_ALGORITHM=HS256
   JWT_EXPIRE_MINUTES=60
   CORS_ORIGINS=["http://localhost:3000"]
   REDIS_URL=redis://localhost:6379/0
   RATE_LIMIT=5/minute
   ```

5. **Set up the database**
   ```bash
   # Create the database and tables
   python app/database/create_trakr_db.py
   ```

## 🚀 Running the Application

### Option 1: Using the startup script
```bash
python start_server.py
```

### Option 2: Using uvicorn directly
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Using Docker Compose
```bash
cd app/database
docker-compose up -d
```

## 📚 API Documentation

Once the server is running, you can access:

- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative API Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_backend.py
```

This will test:
- ✅ All dependencies are installed
- ✅ Configuration is properly set up
- ✅ All modules can be imported
- ✅ FastAPI app can be created
- ✅ All routers are properly configured

## 📁 Project Structure

```
app/
├── core/                   # Core functionality
│   ├── config.py          # Configuration management
│   ├── security.py        # JWT authentication
│   ├── rate_limiter.py    # API rate limiting
│   ├── metrics.py         # Prometheus metrics
│   ├── error_handlers.py  # Error handling
│   └── logging_config.py  # Logging configuration
├── database/              # Database setup
│   ├── create_trakr_db.py # Database creation script
│   ├── db_init.py         # Database initialization
│   └── docker-compose.yml # Docker setup
├── db/                    # Database connection
│   └── connection.py      # Connection pool management
├── routers/               # API endpoints
│   ├── accounts.py        # User account management
│   ├── organizations.py   # Organization management
│   ├── roles.py           # Role management
│   ├── tracking_objects.py # Tracking object management
│   ├── tags.py            # GPS tag management
│   ├── alarms.py          # Alarm management
│   └── routes.py          # Route history
├── schemas/               # Pydantic models
│   ├── accounts.py        # Account schemas
│   ├── organizations.py   # Organization schemas
│   ├── roles.py           # Role schemas
│   ├── tracking_objects.py # Tracking object schemas
│   ├── tags.py            # Tag schemas
│   ├── alarms.py          # Alarm schemas
│   └── routes.py          # Route schemas
├── services/              # Business logic
│   ├── accounts_service.py # Account operations
│   ├── organizations_service.py # Organization operations
│   ├── roles_service.py   # Role operations
│   ├── tracking_objects_service.py # Tracking object operations
│   ├── tags_service.py    # Tag operations
│   ├── alarms_service.py  # Alarm operations
│   └── routes_service.py  # Route operations
└── main.py                # FastAPI application entry point
```

## 🔧 Configuration

The application uses Pydantic Settings for configuration management. Key settings:

- **Database**: PostgreSQL connection settings
- **JWT**: Authentication token settings
- **CORS**: Cross-origin resource sharing settings
- **Rate Limiting**: API rate limiting configuration
- **Redis**: Cache configuration (optional)

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. Include the JWT token in the Authorization header:
   ```
   Authorization: Bearer <your-jwt-token>
   ```

2. The token should contain user information and permissions.

## 📊 API Endpoints

### Accounts
- `GET /accounts/organizations` - List organizations
- `GET /accounts` - List accounts with filtering
- `POST /accounts` - Create new account
- `GET /accounts/{id}` - Get account details
- `PUT /accounts/{id}` - Update account
- `DELETE /accounts/{id}` - Delete account
- `POST /accounts/{id}/reset-password` - Reset password
- `POST /accounts/{id}/disable` - Disable account

### Organizations
- `GET /organizations` - List organizations
- `POST /organizations` - Create organization
- `GET /organizations/{id}` - Get organization details
- `PUT /organizations/{id}` - Update organization
- `POST /organizations/{id}/transfer` - Transfer ownership

### Tracking Objects
- `GET /tracking-objects/organizations` - List organizations
- `GET /tracking-objects` - List tracking objects
- `POST /tracking-objects` - Create tracking object
- `GET /tracking-objects/{id}` - Get tracking object details
- `PUT /tracking-objects/{id}` - Update tracking object
- `DELETE /tracking-objects/{id}` - Delete tracking object
- `POST /tracking-objects/import` - Import tracking objects
- `POST /tracking-objects/photo-batch-upload` - Upload photos

### Tags
- `GET /tags/organizations` - List organizations
- `GET /tags` - List tags with filtering
- `GET /tags/{id}` - Get tag details
- `POST /tags/export` - Export tags
- `POST /tags/transfer` - Transfer tags

### Alarms
- `GET /alarms/organizations` - List organizations
- `GET /alarms` - List alarms with filtering
- `GET /alarms/{id}` - Get alarm details
- `POST /alarms/export` - Export alarms
- `POST /alarms/handle` - Handle alarms

### Routes
- `GET /routes/organizations` - List organizations
- `GET /routes` - List routes with filtering
- `GET /routes/{id}` - Get route details
- `GET /routes/statistics/{organization}` - Get route statistics
- `POST /routes/export` - Export routes

### Roles
- `GET /roles/organizations` - List organizations
- `GET /roles` - List roles

## 🐳 Docker Support

The application includes Docker Compose configuration for easy deployment:

```bash
cd app/database
docker-compose up -d
```

This will start:
- PostgreSQL database
- Redis cache
- PgAdmin (database management)

## 📈 Monitoring

The application includes Prometheus metrics at `/metrics` endpoint for monitoring:
- Request counts
- Response times
- Error rates

## 🔒 Security Features

- JWT-based authentication
- Rate limiting to prevent abuse
- CORS configuration
- Input validation with Pydantic
- SQL injection protection
- Error handling without information leakage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions, please open an issue in the repository. 