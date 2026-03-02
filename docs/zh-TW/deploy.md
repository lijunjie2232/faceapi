# 部署指南

本指南說明如何將Face Recognition System部署到生產環境。

## 部署選項

### 使用Docker Hub預先建置的映像檔（推薦）

主要的 `docker-compose.yml` 檔案使用預先建置的映像檔進行直接部署：

- **後端API**: `lijunjie2232/faceapi-server:v1.0`
- **網頁介面**: `lijunjie2232/faceapi-web:v1.0`

優點：
- ⚡ **快速部署** - 無需建置時間
- 🔄 **環境一致性** - 到處都是相同的映像檔
- 📦 **無建置依賴** - 只需要Docker
- ⏱️ **減少設定時間** - 立即可用

### 1. Docker Compose（推薦）
- 簡單快速的部署方式
- 適用於中小型環境
- 自主託管型

### 2. Kubernetes
- 適用於大型環境
- 支援自動擴展
- 高可用性架構

### 3. 雲端平台
- AWS ECS/EKS
- Google Cloud Run/GKE
- Azure Container Instances/AKS

## 使用Docker Compose部署

### 1. 生產環境準備

```bash
# 克隆程式碼庫
git clone https://github.com/lijunjie2232/faceapi.git
cd face_recognition_system

# 建立生產環境變數檔案
cp .env.prod.example .env

# 設定環境變數
vim .env
```

### 2. 重要環境變數

```bash
# .env檔案設定範例
DEBUG=False
LOG_LEVEL=INFO

# 資料庫設定
POSTGRES_USER=faceuser
POSTGRES_PASSWORD=your_secure_production_password
POSTGRES_DB=facedb

# JWT設定
JWT_SECRET_KEY=your_very_long_secret_key_here_at_least_32_characters
JWT_EXPIRE_MINUTES=1440  # 24小時

# MinIO設定
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_secure_minio_password

# SSL憑證路徑（可選）
SSL_CERTIFICATE_PATH=/path/to/certificate.crt
SSL_PRIVATE_KEY_PATH=/path/to/private.key
```

### 3. 啟動生產環境

```bash
# 使用預先建置的映像檔啟動生產環境（推薦）
docker-compose -f docker-compose.yml up -d

# 替代方案：從原始碼建置
docker-compose -f docker-compose.prod.yml up -d --build

# GPU支援環境
docker-compose -f docker-compose.prod.gpu.yml up -d

# 確認服務狀態
docker-compose -f docker-compose.prod.yml ps

# 查看日誌
docker-compose -f docker-compose.prod.yml logs -f
```

## SSL/TLS設定

### 1. 使用Let's Encrypt免費SSL憑證

```bash
# 安裝Certbot
sudo apt install certbot

# 取得SSL憑證
sudo certbot certonly --standalone -d your-domain.com

# 設定憑證檔案路徑
SSL_CERTIFICATE_PATH=/etc/letsencrypt/live/your-domain.com/fullchain.pem
SSL_PRIVATE_KEY_PATH=/etc/letsencrypt/live/your-domain.com/privkey.pem
```

### 2. Nginx的SSL設定

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # 強化SSL設定
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

## 備份與還原

### 1. 資料庫備份

```bash
# PostgreSQL備份指令碼
#!/bin/bash
BACKUP_DIR="/backup/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

# 建立備份
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U faceuser facedb > $BACKUP_DIR/backup_$DATE.sql

# 刪除舊備份（7天前的）
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### 2. MinIO資料備份

```bash
# MinIO資料備份
docker-compose -f docker-compose.prod.yml exec minio mc cp -r local/face-images /backup/minio/
```

### 3. 備份自動化

```bash
# 加入crontab
# 每天凌晨2點備份
0 2 * * * /path/to/backup-script.sh
```

## 監控與日誌

### 1. 日誌管理

```bash
# Docker日誌輪轉設定
cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# 重啟Docker
sudo systemctl restart docker
```

### 2. 健康檢查

```yaml
# 在docker-compose.prod.yml中加入
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 3. 效能監控

```bash
# 監控Docker stats
docker stats

# 系統資源監控
htop
iotop
```

## 擴展性

### 1. 水平擴展

```bash
# 前端擴展
docker-compose -f docker-compose.prod.yml up -d --scale frontend=3

# 後端擴展
docker-compose -f docker-compose.prod.yml up -d --scale backend=2
```

### 2. 負載平衡

```nginx
# Nginx負載平衡設定
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

## 安全性措施

### 1. 防火牆設定

```bash
# UFW設定
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 8000/tcp   # 不直接公開後端API
```

### 2. 容器安全性

```bash
# 以非root使用者執行
# 在docker-compose.prod.yml中指定user
user: "1000:1000"

# 讀取唯檔案系統
read_only: true
tmpfs:
  - /tmp
  - /var/run
```

### 3. 環境變數保護

```bash
# 機密資訊外部化
# 建立secrets.env檔案
JWT_SECRET_KEY=your_secret_key
DATABASE_PASSWORD=your_db_password

# 在docker-compose中讀取
env_file:
  - .env
  - secrets.env
```

## 災難恢復計畫

### 1. 備份策略

```bash
# 備份頻率
- 資料庫: 每日
- MinIO資料: 每週
- 設定檔案: 變更時

# 備份儲存位置
- 本機儲存: 即時恢復用
- 雲端儲存: 長期儲存用
- 離站儲存: 災難對策用
```

### 2. 恢復程序

```bash
# 1. 確認最新備份
ls -la /backup/

# 2. 資料庫恢復
docker-compose -f docker-compose.prod.yml exec postgres psql -U faceuser facedb < backup_20241201_020000.sql

# 3. MinIO資料恢復
docker-compose -f docker-compose.prod.yml exec minio mc cp -r /backup/minio/face-images local/

# 4. 重新啟動服務
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## 維護

### 1. 定期維護任務

```bash
# 月度維護指令碼
#!/bin/bash

# Docker系統清理
docker system prune -af

# 日誌檔案輪轉
logrotate /etc/logrotate.d/face-recognition

# 資料庫最佳化
docker-compose -f docker-compose.prod.yml exec postgres vacuumdb -U faceuser facedb

# SSL憑證更新確認
certbot renew --dry-run
```

### 2. 升級程序

```bash
# 1. 開始維護模式
touch /tmp/maintenance.mode

# 2. 取得新版本
git pull origin main

# 3. 建立備份
./scripts/backup.sh

# 4. 停止服務
docker-compose -f docker-compose.prod.yml down

# 5. 部署新版本
docker-compose -f docker-compose.prod.yml up -d --build

# 6. 健康檢查
curl -f http://localhost:8000/health

# 7. 結束維護模式
rm /tmp/maintenance.mode
```

## 故障排除

### 常見問題與解決方法

#### 1. 記憶體不足
```bash
# 確認記憶體使用量
docker stats

# 調整Docker資源限制
# 編輯/etc/docker/daemon.json
```

#### 2. 磁碟空間不足
```bash
# 確認磁碟使用量
df -h

# 刪除不需要的Docker資料
docker system prune -a
```

#### 3. 網路問題
```bash
# 確認網路連線
docker network ls
docker network inspect face-recognition_default
```

#### 4. 效能問題
```bash
# 資源監控
top
iotop
docker stats

# 日誌分析
docker-compose -f docker-compose.prod.yml logs --tail=100
```

生產環境部署準備完成！