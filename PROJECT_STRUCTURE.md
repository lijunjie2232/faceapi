# Face Recognition System - Project Structure

## Overview

```
face_recognition_system/
├── backend/
│   ├── faceapi/                       # Main backend application package
│   │   ├── __cli__.py                 # CLI interface for the application
│   │   ├── __init__.py                # Package initialization
│   │   ├── main.py                    # Main FastAPI application entry point
│   │   ├── core/                      # Core application configuration
│   │   │   ├── __init__.py
│   │   │   └── config.py              # Application configuration settings
│   │   ├── db/                        # Database initialization and setup
│   │   │   ├── __init__.py
│   │   │   ├── init_account.py        # Account database initialization
│   │   │   ├── init_milvus.py         # Milvus vector database setup
│   │   │   └── init_sql.py            # SQL database initialization
│   │   ├── face_rec/                  # Face recognition models and processing
│   │   │   ├── __init__.py
│   │   │   ├── FaceRecModel.py        # Base face recognition model
│   │   │   ├── OnnxModel.py           # ONNX model support
│   │   │   ├── StarNet.py             # StarNet neural network implementation
│   │   │   └── predict_face_demo.py   # Face prediction demonstration
│   │   ├── models/                    # Database models
│   │   │   ├── __init__.py
│   │   │   └── user.py                # User database model
│   │   ├── routes/                    # API route definitions
│   │   │   ├── __init__.py
│   │   │   ├── admin.py               # Administrative API endpoints
│   │   │   ├── face.py                # Face recognition API endpoints
│   │   │   └── user.py                # User management API endpoints
│   │   ├── schemas/                   # Pydantic data schemas
│   │   │   ├── __init__.py
│   │   │   ├── face.py                # Face-related data schemas
│   │   │   ├── response.py            # Response schema definitions
│   │   │   └── user.py                # User-related data schemas
│   │   ├── services/                  # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── admin.py               # Administrative business logic
│   │   │   ├── face.py                # Face recognition business logic
│   │   │   └── user.py                # User management business logic
│   │   └── utils/                     # Utility functions and helpers
│   │       ├── __init__.py
│   │       ├── face_utils.py          # Face processing utilities
│   │       ├── jwt_utils.py           # JWT token handling utilities
│   │       ├── milvus_utils.py        # Milvus database utilities
│   │       └── pass_utils.py          # Password hashing utilities
│   ├── Dockerfile                     # Backend container definition
│   ├── Dockerfile-gpu                 # GPU-enabled backend container
│   ├── README.md                      # Backend documentation
│   ├── pyproject.toml                 # Python project configuration
│   └── requirements.txt               # Python dependencies
├── frontend/
│   ├── public/                        # Static assets
│   │   └── models/                    # Face detection models
│   │       ├── tiny_face_detector_model-shard1
│   │       └── tiny_face_detector_model-weights_manifest.json
│   ├── scripts/                       # Model download scripts
│   │   ├── download_models.js         # Node.js model downloader
│   │   ├── download_models.ps1        # PowerShell model downloader
│   │   └── download_models.sh         # Bash model downloader
│   ├── src/                           # Vue.js source code
│   │   ├── components/                # Vue components
│   │   │   ├── FaceDetectionPopOut.vue     # Face detection popup component
│   │   │   ├── FaceDetectionRecognizer.vue # Face detection and recognition component
│   │   │   ├── FaceRecongnizerPopOut.vue   # Face recognizer popup component
│   │   │   └── UserManager.vue        # User management component
│   │   ├── router/                    # Vue Router configuration
│   │   │   └── index.js               # Route definitions
│   │   ├── styles/                    # CSS styles
│   │   │   └── global.css             # Global CSS styles
│   │   ├── utils/                     # Frontend utilities
│   │   │   └── face.js                # Face processing utilities
│   │   ├── views/                     # Page components
│   │   │   ├── Admin.vue              # Administrator dashboard
│   │   │   ├── Login.vue              # Login page
│   │   │   ├── Signup.vue             # User registration page
│   │   │   └── User.vue               # User dashboard
│   │   ├── App.vue                    # Root Vue component
│   │   └── main.js                    # Vue application entry point
│   ├── .dockerignore                  # Docker ignore rules
│   ├── .env.template                  # Environment variables template
│   ├── .eslintignore                  # ESLint ignore configuration
│   ├── .eslintrc.js                   # ESLint configuration
│   ├── .gitignore                     # Git ignore rules
│   ├── Dockerfile_dev                 # Development container definition
│   ├── Dockerfile_prod                # Production container definition
│   ├── index.html                     # HTML template
│   ├── package.json                   # Frontend dependencies
│   ├── pnpm-lock.yaml                 # Dependency lock file
│   └── vite.config.js                 # Vite build configuration
├── nginx/                             # Nginx reverse proxy configuration
│   ├── nginx.conf                     # Main Nginx configuration
│   └── templates/                     # Configuration templates
│       └── default.conf.template      # Default site configuration template
├── .dockerignore                      # Root Docker ignore rules
├── .env.dev.example                   # Development environment example
├── .env.prod.example                  # Production environment example
├── .gitignore                         # Git ignore rules
├── LICENSE                            # Project license
├── PROJECT_STRUCTURE.md               # This file
├── QUICKSTART.md                      # Quick start guide
├── README.md                          # Project overview and documentation
├── deploy.sh                          # Deployment script
├── docker-compose.dev.gpu.yml         # GPU-enabled development compose
├── docker-compose.dev.yml             # Development environment compose
├── docker-compose.prod.gpu.yml        # GPU-enabled production compose
└── docker-compose.prod.yml            # Production environment compose
```

## Key Components

### Backend Architecture

- **FastAPI**: Modern, fast web framework for building APIs with Python 3.8+
- **Milvus**: Vector database for storing and searching face embeddings
- **Tortoise ORM**: Async ORM for PostgreSQL database operations
- **face_recognition**: Library for face detection and recognition
- **Pydantic**: Data validation and settings management using type hints
- **ONNX Runtime**: High-performance inference engine for machine learning models
- **StarNet**: Custom neural network implementation for face recognition

### Frontend Architecture

- **Vue 3**: Progressive JavaScript framework with Composition API
- **Vite**: Next-generation frontend tooling with fast hot module replacement
- **Face-api.js**: JavaScript face detection and recognition library
- **Axios**: Promise-based HTTP client for API communication
- **PNPM**: Fast, disk space efficient package manager

### Infrastructure

- **Docker**: Containerization for consistent development and deployment
- **Docker Compose**: Multi-container orchestration for development and production
- **Nginx**: Reverse proxy and load balancer
- **Milvus**: Vector database for similarity search operations
- **MinIO**: S3-compatible object storage for image files
- **etcd**: Distributed key-value store for Milvus metadata
- **PostgreSQL**: Relational database for user account management

## API Endpoints

### Authentication
- `POST /api/v1/login`: User authentication and JWT token generation
- `POST /api/v1/signup`: New user registration

### Face Recognition
- `POST /api/v1/register-face`: Register a new face for authenticated user
- `POST /api/v1/recognize-face`: Recognize faces in uploaded image
- `GET /api/v1/user/faces`: Get all registered faces for current user
- `DELETE /api/v1/user/faces/{face_id}`: Delete a registered face

### User Management
- `GET /api/v1/user/profile`: Get current user profile information
- `PUT /api/v1/user/profile`: Update current user profile
- `DELETE /api/v1/user/account`: Delete current user account

### Administrative Functions
- `GET /api/v1/admin/users`: List all users with pagination (Admin only)
- `GET /api/v1/admin/users/{user_id}`: Get specific user details (Admin only)
- `POST /api/v1/admin/users`: Create a new user as administrator (Admin only)
- `PUT /api/v1/admin/users/{user_id}`: Update user information (Admin only)
- `DELETE /api/v1/admin/users/{user_id}`: Deactivate a user account (Admin only)
- `PATCH /api/v1/admin/users/{user_id}/activate`: Activate a deactivated user (Admin only)
- `GET /api/v1/admin/stats`: Get system statistics and metrics (Admin only)

## Data Flow

### User Registration Flow
1. User creates account via `/signup` endpoint with email and password
2. System validates credentials and creates user record in PostgreSQL
3. User receives JWT token for authentication

### Face Registration Flow
1. Authenticated user uploads face image via `/register-face` endpoint
2. Backend processes image using face recognition library:
   - Detects faces in the image
   - Extracts facial features and generates embedding vector
   - Validates image quality and face clarity
3. Face embedding is stored in Milvus vector database with user association
4. Face metadata is stored in PostgreSQL for reference

### Face Recognition Flow
1. User uploads image for recognition via `/recognize-face` endpoint
2. System processes image to detect and extract face embeddings
3. Performs similarity search against Milvus vector database
4. Returns matching users with confidence scores
5. Results are filtered by configurable confidence threshold

### Administrative Operations
1. Admin authenticates with elevated privileges
2. Access administrative endpoints for user management
3. Perform bulk operations and system monitoring
4. View analytics and system performance metrics