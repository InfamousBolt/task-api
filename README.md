# Task Management API

A production-ready RESTful API for task management built with Flask, PostgreSQL, and Docker. This microservice demonstrates best practices for backend development including database design, authentication, containerization, and error handling.

## 🚀 Features

- **RESTful API Design**: Clean, intuitive endpoints following REST principles
- **JWT Authentication**: Secure token-based authentication system
- **PostgreSQL Database**: Normalized schema with foreign key relationships
- **Docker Support**: Fully containerized with docker-compose for easy deployment
- **Database Migrations**: Alembic integration for version-controlled schema changes
- **Connection Pooling**: Optimized database connections for production use
- **Error Handling**: Comprehensive error handling and validation
- **Pagination & Filtering**: Efficient data retrieval with query parameters
- **Task Statistics**: Built-in analytics for task completion rates

## 📋 Tech Stack

- **Backend**: Python 3.11, Flask 3.0
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 3.1
- **Authentication**: JWT (PyJWT)
- **Migrations**: Alembic
- **Containerization**: Docker & Docker Compose

## 🏗️ Architecture

```
task-api/
├── app/
│   ├── __init__.py         # Application factory
│   ├── models.py           # Database models (User, Task, Category)
│   ├── routes.py           # API endpoints
│   ├── auth.py             # JWT authentication logic
│   ├── database.py         # Database connection & pooling
│   └── config.py           # Configuration management
├── migrations/             # Alembic database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/                  # Unit tests (future)
├── docker-compose.yml      # Docker orchestration
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── alembic.ini            # Alembic configuration
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 📊 Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique, Indexed)
- `email` (Unique, Indexed)
- `password_hash`
- `created_at`, `updated_at`

### Categories Table
- `id` (Primary Key)
- `name` (Unique, Indexed)
- `description`
- `color` (Hex color code)
- `created_at`

### Tasks Table
- `id` (Primary Key)
- `title` (Indexed)
- `description`
- `status` (pending/in_progress/completed, Indexed)
- `priority` (low/medium/high)
- `due_date`
- `completed_at`
- `created_at`, `updated_at`
- `user_id` (Foreign Key → users.id, Indexed)
- `category_id` (Foreign Key → categories.id, Indexed)

**Indexes**: Composite index on (status, user_id) for optimized queries

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd task-api
```

### 2. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your configuration (optional for local development)
```

### 3. Start the Application
```bash
docker-compose up --build
```

The API will be available at `http://localhost:5000`

### 4. Verify Installation
```bash
curl http://localhost:5000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "task-management-api"
}
```


## 📖 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication

All endpoints except `/auth/register` and `/auth/login` require authentication.

Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

### 🔐 Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response** (201 Created):
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "message": "Login successful",
  "user": { ... },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

---

### 📂 Category Endpoints

#### Get All Categories
```http
GET /api/categories
Authorization: Bearer <token>
```

#### Create Category
```http
POST /api/categories
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Work",
  "description": "Work-related tasks",
  "color": "#3498db"
}
```

#### Update Category
```http
PUT /api/categories/{category_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Work",
  "description": "Updated description",
  "color": "#2ecc71"
}
```

#### Delete Category
```http
DELETE /api/categories/{category_id}
Authorization: Bearer <token>
```

---

### ✅ Task Endpoints

#### Get All Tasks (with filters & pagination)
```http
GET /api/tasks?status=pending&priority=high&page=1&per_page=10&sort_by=created_at&order=desc
Authorization: Bearer <token>
```

**Query Parameters**:
- `status`: Filter by status (pending, in_progress, completed)
- `priority`: Filter by priority (low, medium, high)
- `category_id`: Filter by category ID
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 10)
- `sort_by`: Sort field (default: created_at)
- `order`: Sort order (asc, desc)

**Response**:
```json
{
  "tasks": [ ... ],
  "total": 45,
  "page": 1,
  "per_page": 10,
  "pages": 5
}
```

#### Get Single Task
```http
GET /api/tasks/{task_id}
Authorization: Bearer <token>
```

#### Create Task
```http
POST /api/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Complete project documentation",
  "description": "Write comprehensive README and API docs",
  "status": "pending",
  "priority": "high",
  "category_id": 1,
  "due_date": "2024-12-31T23:59:59"
}
```

**Response** (201 Created):
```json
{
  "message": "Task created successfully",
  "task": {
    "id": 1,
    "title": "Complete project documentation",
    "description": "Write comprehensive README and API docs",
    "status": "pending",
    "priority": "high",
    "due_date": "2024-12-31T23:59:59",
    "completed_at": null,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "user_id": 1,
    "category": {
      "id": 1,
      "name": "Work",
      "description": "Work-related tasks",
      "color": "#3498db"
    }
  }
}
```

#### Update Task
```http
PUT /api/tasks/{task_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated title",
  "status": "completed",
  "priority": "medium"
}
```

#### Delete Task
```http
DELETE /api/tasks/{task_id}
Authorization: Bearer <token>
```

---

### 📊 Statistics Endpoint

#### Get Task Statistics
```http
GET /api/stats
Authorization: Bearer <token>
```

**Response**:
```json
{
  "total_tasks": 100,
  "pending": 25,
  "in_progress": 30,
  "completed": 45,
  "completion_rate": 45.0
}
```

---

## ☁️ Cloud Deployment (AWS)

This application is ready for AWS deployment:

**Architecture:**
- **Compute**: AWS ECS (Fargate) or EC2
- **Database**: Amazon RDS (PostgreSQL)
- **Container Registry**: Amazon ECR
- **Load Balancer**: Application Load Balancer (ALB)

**Quick Deploy Steps:**
1. Push Docker image to ECR
2. Create RDS PostgreSQL instance
3. Update `DATABASE_URL` environment variable
4. Deploy container to ECS/Fargate
5. Configure ALB for HTTPS traffic

*(Full AWS deployment guide coming soon)*

## 🧪 Testing

### Manual Testing with curl

**Register and Login:**
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"test123"}'

# Login and save token
TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}' \
  | jq -r '.token')

echo $TOKEN
```

**Create Task:**
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My first task",
    "description": "Testing the API",
    "priority": "high",
    "status": "pending"
  }'
```

**Get All Tasks:**
```bash
curl -X GET "http://localhost:5000/api/tasks?status=pending" \
  -H "Authorization: Bearer $TOKEN"
```

## 🏆 Production Considerations

### Implemented Features
✅ Connection pooling (pool_size: 10, max_overflow: 20)
✅ Database health checks (pool_pre_ping)
✅ Password hashing (Werkzeug)
✅ JWT token expiration
✅ SQL injection protection (SQLAlchemy ORM)
✅ CORS support
✅ Error handling and validation
✅ Database indexes for performance
✅ Proper foreign key constraints
✅ Cascade deletes for data integrity

## 🐳 Docker Commands

```bash
# Build and start services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Remove volumes (⚠️ deletes database data)
docker-compose down -v

# Execute commands in running container
docker-compose exec api python
docker-compose exec db psql -U taskuser -d taskdb
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | development |
| `SECRET_KEY` | Flask secret key | dev-secret-key |
| `DATABASE_URL` | PostgreSQL connection string | postgresql://... |
| `JWT_SECRET_KEY` | JWT signing key | jwt-secret-key |
| `JWT_ACCESS_TOKEN_EXPIRES` | Token expiration (seconds) | 3600 |

⚠️ **Important**: Change all secret keys in production!

## 🎯 Project Purpose

Built as part of my portfolio to demonstrate backend engineering skills including:
- **Database Design**: Normalized PostgreSQL schema with proper indexing and relationships
- **RESTful APIs**: Clean endpoint design following industry standards
- **Production Readiness**: Connection pooling, migrations, error handling, and security
- **Containerization**: Docker-based deployment for consistency across environments
- **Scalability**: Pagination, filtering, and query optimization for large datasets

This project showcases my ability to build production-grade microservices ready for cloud deployment.


