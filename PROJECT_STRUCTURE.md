# Face Recognition System - Project Structure

## Overview

```
face_recognition_system/
├── backend/
│   └── app/
│       ├── __init__.py
│       ├── main.py                    # Main FastAPI application
│       ├── core/                      # Core application logic
│       │   ├── __init__.py
│       │   └── config.py              # Configuration settings
│       ├── db/                        # Database connections and initialization
│       │   ├── __init__.py
│       │   ├── init_milvus.py         # Milvus database initialization
│       │   └── init_sql.py            # SQL database initialization
│       ├── face_rec/                  # Face recognition models and algorithms
│       │   ├── FaceRecModel.py
│       │   ├── StarNet.py             # StarNet model implementation
│       │   ├── __init__.py
│       │   ├── predict_face_demo.py   # Demo for face prediction
│       │   └── utils.py               # Face recognition utilities
│       ├── models/                    # Database models (Tortoise ORM)
│       │   ├── __init__.py
│       │   └── user.py                # User model
│       ├── routes/                    # API route handlers
│       │   ├── __init__.py
│       │   ├── admin.py               # Admin endpoints
│       │   ├── face.py                # Face recognition endpoints
│       │   └── user.py                # User management endpoints
│       ├── schemas/                   # Request/response schemas (Pydantic)
│       │   ├── __init__.py
│       │   ├── face.py                # Face-related schemas
│       │   ├── response.py            # Generic response schemas
│       │   └── user.py                # User-related schemas
│       ├── services/                  # Business logic services
│       │   ├── __init__.py
│       │   ├── admin.py               # Admin business logic
│       │   ├── face.py                # Face recognition business logic
│       │   └── user.py                # User management business logic
│       └── utils/                     # Utility functions
│           ├── __init__.py
│           ├── face_utils.py          # Face processing utilities
│           ├── jwt_utils.py           # JWT token utilities
│           ├── milvus_utils.py        # Milvus database utilities
│           └── pass_utils.py          # Password utilities
├── frontend/
│   ├── public/
│   │   └── models
│   │       └── tiny_face_detector_model-weights_manifest.json
│   ├── src/
│   │   ├── components/                # Reusable Vue components
│   │   │   ├── FaceDetection.vue      # Face detection UI component
│   │   │   ├── FaceRecognizer.vue     # Face recognition UI component
│   │   │   ├── FaceRegister.vue       # Face registration UI component
│   │   │   └── UserManager.vue        # User management UI component
│   │   ├── styles/
│   │   │   └── global.css             # Global styling
│   │   ├── App.vue                    # Main application component
│   │   └── main.js                    # Vue application entry point
│   ├── Dockerfile                     # Container definition for frontend
│   ├── download_models.js             # Script to download face detection models
│   ├── download_models.ps1            # PowerShell script for model download
│   ├── download_models.sh             # Shell script for model download
│   ├── index.html                     # HTML template
│   ├── package.json                   # Frontend dependencies
│   ├── pnpm-lock.yaml                 # Dependency lock file
│   └── vite.config.js                 # Vite configuration
├── migrations/                        # Database migration files
│   └── models/
│       ├── 0_20260129000201_init.py   # Initial migration
│       ├── 1_20260129002123_update.py # First update migration
│       ├── 2_20260130201414_update.py # Second update migration
│       └── 3_20260130204802_update.py # Third update migration
├── test/                              # Test files and evaluation scripts
│   ├── StarNet.py                     # StarNet model tests
│   ├── api_test.py                    # API integration tests
│   ├── db_test.py                     # Database tests
│   ├── eval.py                        # Evaluation scripts
│   ├── loss.py                        # Loss function implementations
│   ├── partial_fc_v2.py               # Partial FC implementation
│   ├── predict_face.py                # Face prediction tests
│   ├── utils.py                       # Test utilities
│   └── dataset/                       # Test datasets
├── Dockerfile                         # Container definition for backend
├── PROJECT_STRUCTURE.md               # This file
├── QUICKSTART.md                      # Quick start guide
├── README.md                          # Project overview
├── docker-compose.yml                 # Multi-container orchestration
├── pyproject.toml                     # Python project metadata and dependencies
├── setup_project.py                   # Project setup script
└── volumes/                           # Docker volume mounts (gitignored)
    ├── milvus/
    ├── etcd/
    └── minio/
```

## Key Components

### Backend Architecture

- **FastAPI**: Modern, fast web framework for building APIs with Python
- **Milvus**: Vector database for storing and searching face embeddings
- **Tortoise ORM**: Async ORM for database operations
- **face_recognition**: Library for face detection and recognition
- **Pydantic**: Data validation and settings management

### Frontend Architecture

- **Vue 3**: Progressive JavaScript framework for building user interfaces
- **Vite**: Next-generation frontend tooling
- **Face-api.js**: JavaScript face detection and recognition library
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

### Administrative Functions
- `GET /api/v1/admin/users`: List all users with pagination (Admin only)
- `GET /api/v1/admin/users/{user_id}`: Get specific user by ID (Admin only)
- `POST /api/v1/admin/users`: Create a new user as admin (Admin only)
- `PUT /api/v1/admin/users/{user_id}`: Update a specific user by ID (Admin only)
- `DELETE /api/v1/admin/users/{user_id}`: Deactivate a user (Admin only)
- `PATCH /api/v1/admin/users/{user_id}/activate`: Activate a user (Admin only)

## Data Flow

1. User registers via the `/users/` endpoint
2. User's face is registered via the `/register-face` endpoint:
   - Image is processed using `face_recognition` library
   - Face embedding is stored in Milvus vector database
3. Face recognition happens via the `/recognize-face` endpoint:
   - Input image is processed to extract face embeddings
   - Embeddings are compared against stored vectors in Milvus
   - Matching user is returned if confidence is above threshold