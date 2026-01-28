# Quick Start Guide

This guide will help you get the Face Recognition System up and running quickly.

## Prerequisites

- Docker and Docker Compose
- Python 3.8+ (if running locally)
- uv package manager

## Running with Docker (Recommended)

1. Clone the repository
2. Navigate to the project directory
3. Start all services with Docker Compose:

```bash
docker-compose up -d
```

This will start:
- Milvus vector database
- etcd key-value store
- MinIO storage
- Backend API server
- Frontend application

4. Access the applications:
   - Backend API: http://localhost:8000
   - Frontend UI: http://localhost:8080
   - Milvus dashboard: http://localhost:9091

## Running Locally

### Backend Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

Or using uv:

```bash
uv pip install -r requirements.txt
```

2. Make sure Milvus is running (either with Docker or standalone)

3. Start the backend server:

```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm run serve
```

## API Usage Example

Once the system is running, you can test the API endpoints:

### Register a new user:

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "password": "securepassword"
  }'
```

### Register a face for the user:

```bash
# This requires a base64-encoded image
curl -X POST "http://localhost:8000/api/v1/register-face" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "image_data": "data:image/jpeg;base64,...",
    "image_format": "jpg"
  }'
```

### Recognize a face:

```bash
curl -X POST "http://localhost:8000/api/v1/recognize-face" \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "data:image/jpeg;base64,...",
    "image_format": "jpg"
  }'
```

## Troubleshooting

- If you encounter issues with face recognition dependencies, make sure your system has the required libraries installed
- Check that Milvus is running and accessible
- Verify that all environment variables are set correctly