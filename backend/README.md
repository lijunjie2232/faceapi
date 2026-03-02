# Face Recognition System Backend

## Starting the Application

There are several ways to start the backend server:

### 1. Using Console Scripts (Recommended)

After installing the package, you can use the console scripts:

```bash
# Production server (4 workers)
faceapi-server

# Development server with auto-reload
faceapi-dev

# Server with custom arguments
faceapi-server --host 0.0.0.0 --port 8000 --workers 2
```

### 2. Using Python Module

```bash
# Direct module execution
python -m faceapi.main

# With arguments
python -m faceapi.main --host 0.0.0.0 --port 8000 --reload
```

### 3. Using Startup Script

```bash
# Using the provided startup script
python backend/start_server.py --host 0.0.0.0 --port 8000
```

### 4. Using Uvicorn Directly

```bash
# Standard uvicorn command
uvicorn faceapi.main:app --host 0.0.0.0 --port 8000

# With auto-reload for development
uvicorn faceapi.main:app --host 0.0.0.0 --port 8000 --reload

# With multiple workers for production
uvicorn faceapi.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Using Docker

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build and run the backend container directly
docker build -t face-rec-backend .
docker run -p 8000:8000 face-rec-backend
```

## Available Arguments

When using the CLI entry point (`faceapi-server` or `python -m faceapi.main`):

- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port to bind to (default: 8000)
- `--reload`: Enable auto-reload for development
- `--workers`: Number of worker processes (default: 1)
- `--log-level`: Log level [debug|info|warning|error] (default: info)

## Development vs Production

- **Development**: Use `faceapi-dev` or `uvicorn --reload` for auto-reloading
- **Production**: Use `faceapi-server` or `uvicorn --workers N` for multiple workers

## Health Check

The server includes a health check endpoint at `/health` which returns `{"status": "healthy"}`.