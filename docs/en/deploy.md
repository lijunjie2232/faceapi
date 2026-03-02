# Deployment Guide

This guide explains how to deploy the Face Recognition System to production environments.

## Deployment Options

### Pre-built Images from Docker Hub (Recommended)

The main `docker-compose.yml` file uses pre-built images for direct deployment:

- **Backend API**: `lijunjie2232/faceapi-server:v1.0`
- **Web Interface**: `lijunjie2232/faceapi-web:v1.0`

Benefits:
- ⚡ **Faster deployment** - No build time required
- 🔄 **Consistent environments** - Same image everywhere
- 📦 **No build dependencies** - Just Docker needed
- ⏱️ **Reduced setup time** - Ready to use immediately

### 1. Docker Compose (Recommended)
- Simple and fast deployment
- Ideal for small to medium environments
- Self-hosted

### 2. Kubernetes
- For large-scale environments
- Supports auto-scaling
- High availability architecture

### 3. Cloud Platforms
- AWS ECS/EKS
- Google Cloud Run/GKE
- Azure Container Instances/AKS

## Deployment with Docker Compose

### 1. Production Environment Preparation

```bash
# Clone the repository
git clone https://github.com/lijunjie2232/faceapi.git
cd face_recognition_system

# Create production environment variables file
cp .env.prod.example .env

# Configure environment variables
vim .env
```

### 2. Important Environment Variables

```bash
# .env file configuration example
DEBUG=False
LOG_LEVEL=INFO

# Database settings
POSTGRES_USER=faceuser
POSTGRES_PASSWORD=your_secure_production_password
POSTGRES_DB=facedb

# JWT settings
JWT_SECRET_KEY=your_very_long_secret_key_here_at_least_32_characters
JWT_EXPIRE_MINUTES=1440  # 24 hours

# MinIO settings
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_secure_minio_password

# SSL certificate paths (optional)
SSL_CERTIFICATE_PATH=/path/to/certificate.crt
SSL_PRIVATE_KEY_PATH=/path/to/private.key
```

### 3. Starting Production Environment

```bash
# Start production environment with pre-built images (recommended)
docker-compose -f docker-compose.yml up -d

# Alternative: Build from source
docker-compose -f docker-compose.prod.yml up -d --build

# For GPU-enabled environment
docker-compose -f docker-compose.prod.gpu.yml up -d

# Check service status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## SSL/TLS Configuration

### 1. Free SSL Certificate with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot

# Obtain SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Set certificate file paths
SSL_CERTIFICATE_PATH=/etc/letsencrypt/live/your-domain.com/fullchain.pem
SSL_PRIVATE_KEY_PATH=/etc/letsencrypt/live/your-domain.com/privkey.pem
```

### 2. Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Enhanced SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Backup and Recovery

### 1. Database Backup

```bash
# PostgreSQL backup script
#!/bin/bash
BACKUP_DIR="/backup/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U faceuser facedb > $BACKUP_DIR/backup_$DATE.sql

# Delete old backups (older than 7 days)
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### 2. MinIO Data Backup

```bash
# MinIO data backup
docker-compose -f docker-compose.prod.yml exec minio mc cp -r local/face-images /backup/minio/
```

### 3. Backup Automation

```bash
# Add to crontab
# Daily backup at 2 AM
0 2 * * * /path/to/backup-script.sh
```

## Monitoring and Logging

### 1. Log Management

```bash
# Docker log rotation configuration
cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# Restart Docker
sudo systemctl restart docker
```

### 2. Health Checks

```yaml
# Add to docker-compose.prod.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 3. Performance Monitoring

```bash
# Monitor Docker stats
docker stats

# System resource monitoring
htop
iotop
```

## Scaling

### 1. Horizontal Scaling

```bash
# Scale frontend
docker-compose -f docker-compose.prod.yml up -d --scale frontend=3

# Scale backend
docker-compose -f docker-compose.prod.yml up -d --scale backend=2
```

### 2. Load Balancing

```nginx
# Nginx load balancing configuration
upstream backend_servers {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

upstream frontend_servers {
    server frontend1:3000;
    server frontend2:3000;
    server frontend3:3000;
}
```

## Security Measures

### 1. Firewall Configuration

```bash
# UFW configuration
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 8000/tcp   # Don't expose backend API directly
```

### 2. Container Security

```bash
# Run as non-root user
# Specify user in docker-compose.prod.yml
user: "1000:1000"

# Read-only file system
read_only: true
tmpfs:
  - /tmp
  - /var/run
```

### 3. Environment Variable Protection

```bash
# Externalize sensitive information
# Create secrets.env file
JWT_SECRET_KEY=your_secret_key
DATABASE_PASSWORD=your_db_password

# Load in docker-compose
env_file:
  - .env
  - secrets.env
```

## Disaster Recovery Plan

### 1. Backup Strategy

```bash
# Backup frequency
- Database: Daily
- MinIO data: Weekly
- Configuration files: On change

# Backup storage locations
- Local storage: For immediate recovery
- Cloud storage: For long-term storage
- Off-site: For disaster protection
```

### 2. Recovery Procedure

```bash
# 1. Confirm latest backup
ls -la /backup/

# 2. Restore database
docker-compose -f docker-compose.prod.yml exec postgres psql -U faceuser facedb < backup_20241201_020000.sql

# 3. Restore MinIO data
docker-compose -f docker-compose.prod.yml exec minio mc cp -r /backup/minio/face-images local/

# 4. Restart services
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## Maintenance

### 1. Regular Maintenance Tasks

```bash
# Monthly maintenance script
#!/bin/bash

# Docker system cleanup
docker system prune -af

# Log file rotation
logrotate /etc/logrotate.d/face-recognition

# Database optimization
docker-compose -f docker-compose.prod.yml exec postgres vacuumdb -U faceuser facedb

# SSL certificate renewal check
certbot renew --dry-run
```

### 2. Upgrade Procedure

```bash
# 1. Start maintenance mode
touch /tmp/maintenance.mode

# 2. Get new version
git pull origin main

# 3. Create backup
./scripts/backup.sh

# 4. Stop services
docker-compose -f docker-compose.prod.yml down

# 5. Deploy new version
docker-compose -f docker-compose.prod.yml up -d --build

# 6. Health check
curl -f http://localhost:8000/health

# 7. End maintenance mode
rm /tmp/maintenance.mode
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Insufficient Memory
```bash
# Check memory usage
docker stats

# Adjust Docker resource limits
# Edit /etc/docker/daemon.json
```

#### 2. Disk Space Issues
```bash
# Check disk usage
df -h

# Remove unused Docker data
docker system prune -a
```

#### 3. Network Problems
```bash
# Check network connectivity
docker network ls
docker network inspect face-recognition_default
```

#### 4. Performance Issues
```bash
# Resource monitoring
top
iotop
docker stats

# Log analysis
docker-compose -f docker-compose.prod.yml logs --tail=100
```

Production environment deployment is now ready!