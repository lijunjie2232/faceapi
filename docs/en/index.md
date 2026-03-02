# Face Recognition System

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Overview

Face Recognition System is a web-based facial authentication system leveraging cutting-edge facial recognition technology. Built with a modern architecture combining FastAPI backend and Vue.js frontend, it enables easy deployment through Docker containers.

## Key Features

- 🔐 **User Authentication**: Secure authentication system based on JWT tokens
- 👤 **Face Registration**: Register multiple face images per user
- 🎯 **Face Recognition**: High-accuracy face detection and identification capabilities
- 🖼️ **Real-time Processing**: Real-time face recognition from webcam
- 📊 **Admin Dashboard**: User management functionality for administrators
- 🐳 **Docker Support**: Containerized easy deployment
- 🌐 **Multi-GPU Support**: High-speed processing through GPU acceleration

## Technology Stack

### Backend
- **FastAPI**: Fast and modern Python web framework
- **Milvus**: Vector database for large-scale vector search
- **PostgreSQL**: Relational database
- **Tortoise ORM**: Asynchronous ORM
- **face_recognition**: Facial recognition library
- **ONNX Runtime**: High-performance machine learning inference engine

### Frontend
- **Vue 3**
- **Vite**
- **face-api.js**
- **Axios**

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy

## Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 1.29+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/lijunjie2232/faceapi.git
cd face_recognition_system

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

## Project Structure

```
face_recognition_system/
├── backend/           # FastAPI application
├── frontend/          # Vue.js frontend
├── nginx/             # Nginx configuration
├── docker-compose.*.yml  # Docker Compose configuration
└── docs/              # Documentation
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## License

This project is released under the MIT license. See the [LICENSE](LICENSE) file for details.

## Support

If you have any questions or issues, please report them on the [Issues](https://github.com/lijunjie2232/faceapi/issues) page.