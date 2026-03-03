<div align="center">

# Face Recognition System

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)](https://vuejs.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> 🚀 **Modern face recognition system built with FastAPI + Vue.js + Docker**

[🎮 View Demo](https://huggingface.co/spaces/l2533584225/faceapi-demo) • [📚 Documentation](https://lijunjie2232.github.io/faceapi/)

[:us: English](README.en.md) • [:jp: 日本語](README.ja.md) • [:tw: 繁體中文](README.zh-TW.md)

</div>

## 🌟 Key Features

- 🔐 **Secure Authentication**: JWT-based user authentication system
- 👤 **Face Registration**: Register multiple face images per user
- 🎯 **High-Accuracy Recognition**: Advanced face detection and identification
- 🖼️ **Real-time Processing**: Webcam-based real-time face recognition
- 📊 **Admin Dashboard**: Comprehensive user management interface
- 🐳 **Docker Deployment**: Easy containerized deployment
- 🌐 **Multi-language Support**: Available in Japanese, Traditional Chinese, and English
- 🚀 **GPU Acceleration**: High-performance processing with GPU support

## 🎮 Demo

Try the system online:

[🎮 View Demo](https://huggingface.co/spaces/l2533584225/faceapi-demo)

## 📚 Documentation

**Comprehensive documentation is available in multiple languages:**

- 🌐 **Online Documentation**: https://lijunjie2232.github.io/faceapi/
- 📖 **Local Documentation**: 
  - [English Documentation](docs/en/)
  - [日本語ドキュメント](docs/ja/)
  - [繁體中文文檔](docs/zh-TW/)

> **💡 Quick Access**: Start with [QUICKSTART.md](QUICKSTART.md) for immediate setup

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 1.29+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/lijunjie2232/faceapi.git
cd face_recognition_system

# Generate environment file
./deploy.sh generate-env dev

# Start all services
./deploy.sh up dev
```

### Access Services

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8080/admin

## 🏗️ Architecture

### Technology Stack

**Backend**
- FastAPI - Modern Python web framework
- Milvus - Vector database for face embeddings
- PostgreSQL - Relational database
- Tortoise ORM - Async ORM
- face_recognition - Face detection library
- ONNX Runtime - ML inference engine

**Frontend**
- Vue 3 - Progressive JavaScript framework
- Vite - Next-generation build tool
- face-api.js - JavaScript face recognition
- Element Plus - UI component library

**Infrastructure**
- Docker - Containerization platform
- Docker Compose - Multi-container orchestration
- Nginx - Reverse proxy and load balancer
- MinIO - Object storage for images

## 📖 Detailed Documentation

For comprehensive guides, please refer to our multi-language documentation:

| Document | Description | Languages |
|----------|-------------|-----------|
| [Installation Guide](docs/en/install.md) | Complete installation instructions | 🇯🇵 🇹🇼 🇬🇧 |
| [Deployment Guide](docs/en/deploy.md) | Production deployment strategies | 🇯🇵 🇹🇼 🇬🇧 |
| [Development Guide](docs/en/dev.md) | Local development setup | 🇯🇵 🇹🇼 🇬🇧 |
| [Project Structure](PROJECT_STRUCTURE.md) | Detailed code organization | English |
| [Quick Start](QUICKSTART.md) | Rapid setup guide | Japanese |

## 🐳 Deployment Options

### 1. Docker Compose (Recommended)

```bash
# Development environment
docker-compose -f docker-compose.dev.yml up -d

# Production environment (pre-built images)
docker-compose -f docker-compose.yml up -d

# GPU-enabled environment
docker-compose -f docker-compose.dev.gpu.yml up -d
```

### 2. Manual Build

```bash
# Build backend image
docker build -t face-rec-backend backend/

# Build frontend image
docker build -t face-rec-frontend frontend/
```

## 🛠️ Development

### Local Development Setup

```bash
# Backend setup
cd backend
pip install -e .
faceapi --gen-env .env
faceapi --debug

# Frontend setup
cd frontend
pnpm install
pnpm serve
```

### API Endpoints

- **Authentication**: `/api/v1/users/login`, `/api/v1/users/signup`
- **Face Recognition**: `/api/v1/register-face`, `/api/v1/recognize-face`
- **User Management**: `/api/v1/user/profile`, `/api/v1/user/faces`
- **Admin Functions**: `/api/v1/admin/users`, `/api/v1/admin/stats`

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:

- Check the [documentation](https://lijunjie2232.github.io/faceapi/) first
- Report issues on [GitHub Issues](https://github.com/lijunjie2232/faceapi/issues)
- Refer to [QUICKSTART.md](QUICKSTART.md) for common troubleshooting