# Development Environment Setup

This guide explains how to set up the development environment for Face Recognition System and run it locally.

## Development Environment Overview

The development environment consists of the following containers:

- **frontend**: Vue.js 3 based frontend application
- **backend**: FastAPI based backend API server
- **postgres**: PostgreSQL database for storing user data
- **milvus-standalone**: Vector database for storing face feature vectors
- **minio**: Object storage for storing face images
- **etcd**: Metadata management for Milvus
- **nginx**: Reverse proxy and static file delivery

## Starting Local Development Environment

### 1. Starting the Development Environment

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Check service status
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### 2. GPU-enabled Development Environment (Optional)

To use GPU:

```bash
# Start GPU-enabled environment
docker-compose -f docker-compose.dev.gpu.yml up -d
```

## Accessing Services

After startup, you can access the following URLs:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Vue.js application |
| Backend API | http://localhost:8000 | FastAPI server |
| API Documentation | http://localhost:8000/docs | Swagger UI |
| MinIO Console | http://localhost:9001 | Object storage management |
| Milvus Console | http://localhost:9091 | Vector database management |

## Backend Development

### 1. Hot Reload for Backend Code

The code automatically restarts when changes are made during development:

```bash
# Monitor backend logs
docker-compose -f docker-compose.dev.yml logs -f backend
```

### 2. Database Migration

```bash
# Initialize database
docker-compose -f docker-compose.dev.yml exec backend python -m faceapi.db.init_sql

# Create admin account
docker-compose -f docker-compose.dev.yml exec backend python -m faceapi.db.init_account
```

### 3. API Testing

```bash
# Access API documentation
open http://localhost:8000/docs

# API testing example using curl
curl -X POST http://localhost:8000/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

## Frontend Development

### 1. Hot Reload for Frontend

Vue.js development server supports hot reload:

```bash
# Monitor frontend logs
docker-compose -f docker-compose.dev.yml logs -f frontend
```

### 2. Adding Dependencies

```bash
# Install new npm packages
docker-compose -f docker-compose.dev.yml exec frontend pnpm add package-name

# Install development packages
docker-compose -f docker-compose.dev.yml exec frontend pnpm add -D package-name
```

### 3. Testing Builds

```bash
# Test production build
docker-compose -f docker-compose.dev.yml exec frontend pnpm build
```

## Database Operations

### 1. Connecting to PostgreSQL

```bash
# Connect to PostgreSQL container
docker-compose -f docker-compose.dev.yml exec postgres psql -U faceuser -d facedb

# Useful SQL commands
\dt                    # Show table list
\d table_name          # Show table structure
SELECT * FROM users;   # Show user table contents
```

### 2. Connecting to Milvus

```bash
# Access Milvus console
open http://localhost:9091

# Connect to Milvus from Python
docker-compose -f docker-compose.dev.yml exec backend python
```

```python
from pymilvus import connections, Collection

# Connect
connections.connect(host='milvus-standalone', port='19530')

# List collections
collections = connections.list_collections()
print(collections)
```

## Testing

### 1. Running Unit Tests

```bash
# Run backend tests
docker-compose -f docker-compose.dev.yml exec backend pytest

# Run specific test file
docker-compose -f docker-compose.dev.yml exec backend pytest tests/test_users.py

# Generate coverage report
docker-compose -f docker-compose.dev.yml exec backend pytest --cov=faceapi --cov-report=html
```

### 2. E2E Testing

```bash
# Run Cypress tests
docker-compose -f docker-compose.dev.yml exec frontend pnpm test:e2e
```

## Debugging

### 1. Checking Logs

```bash
# Logs for all services
docker-compose -f docker-compose.dev.yml logs

# Logs for specific service
docker-compose -f docker-compose.dev.yml logs backend
docker-compose -f docker-compose.dev.yml logs frontend

# Real-time log monitoring
docker-compose -f docker-compose.dev.yml logs -f
```

### 2. Working Inside Containers

```bash
# Access backend container
docker-compose -f docker-compose.dev.yml exec backend bash

# Access frontend container
docker-compose -f docker-compose.dev.yml exec frontend sh

# Access database container
docker-compose -f docker-compose.dev.yml exec postgres bash
```

### 3. Starting in Debug Mode

```bash
# Start backend in debug mode
docker-compose -f docker-compose.dev.yml stop backend
docker-compose -f docker-compose.dev.yml run --service-ports backend uvicorn faceapi.main:app --host 0.0.0.0 --port 8000 --reload
```

## Environment Variables

### Main Environment Variables for Development

```bash
# .env file example
DEBUG=True
LOG_LEVEL=DEBUG

# Database
POSTGRES_USER=faceuser
POSTGRES_PASSWORD=dev_password
POSTGRES_DB=facedb

# JWT
JWT_SECRET_KEY=development_secret_key
JWT_EXPIRE_MINUTES=30

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
```

## Development Workflow

### 1. New Feature Development Steps

```bash
# 1. Create new branch
git checkout -b feature/new-feature

# 2. Code changes

# 3. Run tests
docker-compose -f docker-compose.dev.yml exec backend pytest

# 4. Commit
git add .
git commit -m "Add new feature"

# 5. Push
git push origin feature/new-feature
```

### 2. Code Quality Checks

```bash
# Backend code formatting
docker-compose -f docker-compose.dev.yml exec backend black .

# Frontend code formatting
docker-compose -f docker-compose.dev.yml exec frontend pnpm format

# Linting checks
docker-compose -f docker-compose.dev.yml exec backend flake8 .
docker-compose -f docker-compose.dev.yml exec frontend pnpm lint
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Containers Won't Start
```bash
# Check container status
docker-compose -f docker-compose.dev.yml ps

# Check container logs
docker-compose -f docker-compose.dev.yml logs service_name

# Rebuild containers
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d --build
```

#### 2. Database Connection Errors
```bash
# Restart database service
docker-compose -f docker-compose.dev.yml restart postgres

# Re-run database initialization
docker-compose -f docker-compose.dev.yml exec backend python -m faceapi.db.init_sql
```

#### 3. Insufficient Memory
```bash
# Check Docker resource limits
docker info | grep -i memory

# Remove unused containers and images
docker system prune -a
```

#### 4. Port Conflicts
```bash
# Check ports in use
sudo lsof -i :8000
sudo lsof -i :3000

# Change ports in docker-compose.yml
```

### Resetting Development Environment

```bash
# Completely clean development environment
./scripts/clean-dev-env.sh

# Or manually
docker-compose -f docker-compose.dev.yml down -v
docker volume ls | grep face
docker volume rm [volume_names]
```

Development environment setup is now complete!