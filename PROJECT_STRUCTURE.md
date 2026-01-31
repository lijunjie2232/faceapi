# Face Recognition System - Project Structure

## Overview

```
face_recognition_system/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # Main FastAPI application
│   │   ├── models/                 # Pydantic models
│   │   │   ├── user.py             # User-related models
│   │   │   └── face_recognition.py # Face recognition models
│   │   ├── schemas/                # Response schemas
│   │   │   └── response.py         # Generic response schemas
│   │   ├── routes/                 # API route handlers
│   │   │   ├── face_recognition.py # Face recognition endpoints
│   │   │   └── users.py            # User management endpoints
│   │   ├── database/               # Database connection and initialization
│   │   │   └── __init__.py         # Milvus connection and collections
│   │   ├── core/                   # Core application logic
│   │   │   └── config.py           # Configuration settings
│   │   └── utils/                  # Utility functions
│   │       └── face_processing.py  # Face processing utilities
│   └── Dockerfile                  # Container definition for backend
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── main.js                 # Vue application entry point
│   │   ├── App.vue                 # Main application component
│   │   └── components/             # Reusable Vue components
│   │       ├── FaceRecognizer.vue  # Face recognition UI
│   │       ├── UserManager.vue     # User management UI
│   │       └── FaceRegister.vue    # Face registration UI
│   ├── package.json                # Frontend dependencies
│   └── Dockerfile                  # Container definition for frontend
├── volumes/                        # Docker volume mounts (gitignored)
│   ├── milvus/
│   ├── etcd/
│   └── minio/
├── logs/                           # Application logs (gitignored)
├── uploads/                        # Temporary file uploads (gitignored)
├── .gitignore                      # Files and directories to ignore
├── pyproject.toml                  # Python project metadata and dependencies
├── requirements.txt                # Python dependencies
├── docker-compose.yml              # Multi-container orchestration
├── README.md                       # Project overview
├── QUICKSTART.md                   # Quick start guide
├── PROJECT_STRUCTURE.md            # This file
├── setup_project.py                # Project setup script
└── LICENSE                         # License information
```

## Key Components

### Backend Architecture

- **FastAPI**: Modern, fast web framework for building APIs with Python
- **Milvus**: Vector database for storing and searching face embeddings
- **face_recognition**: Library for face detection and recognition
- **Pydantic**: Data validation and settings management

### Frontend Architecture

- **Vue 3**: Progressive JavaScript framework for building user interfaces
- **Element Plus**: Vue 3 based component library
- **Axios**: Promise-based HTTP client for API communication

### Infrastructure

- **Docker**: Containerization for consistent deployment
- **Docker Compose**: Multi-container orchestration
- **Milvus**: Vector database for similarity search
- **MinIO**: Object storage for image files
- **etcd**: Distributed key-value store for Milvus metadata

## API Endpoints

### Face Recognition
- `POST /api/v1/register-face`: Register a new face for a user
- `POST /api/v1/recognize-face`: Recognize faces in an image

### User Management
- `POST /api/v1/users/`: Create a new user
- `GET /api/v1/users/{user_id}`: Get user by ID
- `PUT /api/v1/users/{user_id}`: Update user information
- `DELETE /api/v1/users/{user_id}`: Delete a user
- `GET /api/v1/users/`: List users with pagination

## Data Flow

1. User registers via the `/users/` endpoint
2. User's face is registered via the `/register-face` endpoint:
   - Image is processed using `face_recognition` library
   - Face embedding is stored in Milvus vector database
3. Face recognition happens via the `/recognize-face` endpoint:
   - Input image is processed to extract face embeddings
   - Embeddings are compared against stored vectors in Milvus
   - Matching user is returned if confidence is above threshold