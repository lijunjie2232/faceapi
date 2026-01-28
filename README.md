# Face Recognition System

A comprehensive face recognition system built with Python, FastAPI, Vue.js, and Milvus.

## Overview

This project is a face recognition system that allows for:
- Face registration and recognition
- User account management
- Storing face features in Milvus vector database
- RESTful API for integration with various frontends
- Vue.js frontend for user interaction

## Architecture

- **Backend**: FastAPI-based server handling face recognition and user management
- **Frontend**: Vue.js application for user interface
- **Database**: Milvus vector database for storing face features and user accounts
- **Face Recognition**: Powered by the face_recognition library

## Features

- Face detection and recognition
- User registration and authentication
- Face feature extraction and comparison
- Vector storage in Milvus for efficient similarity search
- REST API endpoints for face operations

## Installation

### Prerequisites

- Python 3.8+
- Milvus database instance
- Node.js (for the frontend)

### Backend Setup

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables (see `.env.example`)
4. Start the FastAPI server:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run serve
   ```

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_USER=
MILVUS_PASSWORD=
SECRET_KEY=your-super-secret-key-change-this-in-production
```

## API Endpoints

### Face Recognition
- `POST /api/v1/register-face` - Register a new face for a user
- `POST /api/v1/recognize-face` - Recognize faces in an image

### Users
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user information
- `DELETE /api/v1/users/{user_id}` - Delete a user
- `GET /api/v1/users/` - List users with pagination

## Usage

1. Register a user via the `/api/v1/users/` endpoint
2. Register the user's face via the `/api/v1/register-face` endpoint
3. Recognize faces using the `/api/v1/recognize-face` endpoint

## Project Structure

```
face_recognition_system/
├── backend/
│   └── app/
│       ├── main.py
│       ├── models/
│       ├── schemas/
│       ├── routes/
│       ├── database/
│       ├── core/
│       └── utils/
├── frontend/
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see the LICENSE file for details.