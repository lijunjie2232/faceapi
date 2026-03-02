# Installation Guide

This guide provides detailed instructions for installing the Face Recognition System.

## System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04 LTS / CentOS 8 / macOS 10.15+ / Windows 10+
- **Memory**: 8GB RAM (Recommended: 16GB+)
- **Storage**: 20GB free space
- **CPU**: 4 cores or more

### Recommended Requirements
- **Memory**: 16GB RAM or more
- **GPU**: NVIDIA GPU (CUDA compatible, Recommended: RTX 3060+)
- **Storage**: 50GB free space (SSD recommended)

## Installing Required Software

### 1. Installing Docker

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install dependencies
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Grant permissions to non-root user
sudo usermod -aG docker $USER
```

#### CentOS/RHEL
```bash
# Set up repository
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker Engine
sudo yum install docker-ce docker-ce-cli containerd.io

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Grant permissions to non-root user
sudo usermod -aG docker $USER
```

#### macOS
```bash
# Install Docker Desktop using Homebrew
brew install --cask docker
```

### 2. Installing Docker Compose

#### Linux/macOS
```bash
# Get the latest version
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)

# Download and install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make it executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### 3. Installing Git

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install git
```

#### CentOS/RHEL
```bash
sudo yum install git
```

#### macOS
```bash
# Git is usually pre-installed
git --version
```

## Project Setup

### 1. Cloning the Repository

```bash
# Clone the repository
git clone https://github.com/lijunjie2232/faceapi.git
cd face_recognition_system

# Copy environment variables file
cp .env.dev.example .env
```

### 2. Configuring Environment Variables

Edit the `.env` file to configure necessary settings:

```bash
# Database settings
POSTGRES_USER=faceuser
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=facedb

# JWT secret key
JWT_SECRET_KEY=your_very_secret_key_here

# MinIO settings
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123

# Milvus settings
MILVUS_HOST=milvus-standalone
MILVUS_PORT=19530
```

### 3. GPU Support Configuration (Optional)

If you want to use GPU, follow these steps:

#### Installing NVIDIA Docker
```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install nvidia-docker2

# Restart Docker
sudo systemctl restart docker
```

#### Using GPU-enabled Docker Compose File
```bash
# Start GPU-enabled development environment
docker-compose -f docker-compose.dev.gpu.yml up -d
```

## First Launch

### Starting the Development Environment

```bash
# Build and start development environment
docker-compose -f docker-compose.dev.yml up -d --build

# Check service status
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Accessing Services

After startup is complete, you can access the following URLs:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001
- **Milvus Console**: http://localhost:9091

## Troubleshooting

### Common Issues and Solutions

#### 1. Docker Permission Errors
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Re-login or run the following command
newgrp docker
```

#### 2. Port Already in Use
```bash
# Check ports in use
sudo netstat -tlnp | grep :8000

# To use different ports, edit docker-compose.yml
```

#### 3. Insufficient Memory Error
```bash
# Adjust Docker resource limits
# Docker Desktop: Preferences → Resources
# Linux: Configure resource limits in /etc/docker/daemon.json
```

#### 4. GPU Not Detected
```bash
# Check NVIDIA drivers
nvidia-smi

# Verify nvidia-docker2 installation
docker info | grep -i nvidia
```

### Getting Support

If you can't resolve the issue, please create an Issue with the following information:

1. OS version and Docker version
2. Error messages
3. Docker-compose file being used
4. Environment variable settings (excluding passwords and sensitive information)

```bash
# Collect system information
uname -a
docker --version
docker-compose --version
```