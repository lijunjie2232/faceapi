# デプロイガイド

このガイドでは、Face Recognition Systemを本番環境にデプロイする方法について説明します。

## デプロイオプション

### Docker Hubの事前ビルド済みイメージ（推奨）

メインの `docker-compose.yml` ファイルは、直接デプロイのために事前ビルド済みイメージを使用します：

- **バックエンドAPI**: `lijunjie2232/faceapi-server:v1.0`
- **Webインターフェース**: `lijunjie2232/faceapi-web:v1.0`

利点：
- ⚡ **高速デプロイ** - ビルド時間不要
- 🔄 **環境の一貫性** - どこでも同じイメージ
- 📦 **ビルド依存関係なし** - DockerのみでOK
- ⏱️ **セットアップ時間の短縮** - すぐに使用可能

### 1. Docker Compose（推奨）
- シンプルで高速なデプロイ
- 小〜中規模環境に最適
- 自己ホスト型

### 2. Kubernetes
- 大規模環境向け
- 自動スケーリング対応
- 高可用性構成

### 3. クラウドプラットフォーム
- AWS ECS/EKS
- Google Cloud Run/GKE
- Azure Container Instances/AKS

## Docker Composeによるデプロイ

### 1. 本番環境の準備

```bash
# リポジトリのクローン
git clone https://github.com/lijunjie2232/faceapi.git
cd face_recognition_system

# 本番用環境変数ファイルの作成
cp .env.prod.example .env

# 環境変数の設定
vim .env
```

### 2. 重要な環境変数

```bash
# .envファイルの設定例
DEBUG=False
LOG_LEVEL=INFO

# データベース設定
POSTGRES_USER=faceuser
POSTGRES_PASSWORD=your_secure_production_password
POSTGRES_DB=facedb

# JWT設定
JWT_SECRET_KEY=your_very_long_secret_key_here_at_least_32_characters
JWT_EXPIRE_MINUTES=1440  # 24時間

# MinIO設定
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=your_secure_minio_password

# SSL証明書パス（任意）
SSL_CERTIFICATE_PATH=/path/to/certificate.crt
SSL_PRIVATE_KEY_PATH=/path/to/private.key
```

### 3. 本番環境の起動

```bash
# 事前ビルド済みイメージで本番環境を起動（推奨）
docker-compose -f docker-compose.yml up -d

# 代替案：ソースからビルド
docker-compose -f docker-compose.prod.yml up -d --build

# GPU対応環境の場合
docker-compose -f docker-compose.prod.gpu.yml up -d

# サービスの状態確認
docker-compose -f docker-compose.prod.yml ps

# ログの確認
docker-compose -f docker-compose.prod.yml logs -f
```

## SSL/TLS設定

### 1. Let's Encryptによる無料SSL証明書

```bash
# Certbotのインストール
sudo apt install certbot

# SSL証明書の取得
sudo certbot certonly --standalone -d your-domain.com

# 証明書ファイルのパス設定
SSL_CERTIFICATE_PATH=/etc/letsencrypt/live/your-domain.com/fullchain.pem
SSL_PRIVATE_KEY_PATH=/etc/letsencrypt/live/your-domain.com/privkey.pem
```

### 2. NginxのSSL設定

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL設定の強化
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

## バックアップと復旧

### 1. データベースバックアップ

```bash
# PostgreSQLバックアップスクリプト
#!/bin/bash
BACKUP_DIR="/backup/postgres"
DATE=$(date +%Y%m%d_%H%M%S)

# バックアップの作成
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U faceuser facedb > $BACKUP_DIR/backup_$DATE.sql

# 古いバックアップの削除（7日以上前のもの）
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### 2. MinIOデータバックアップ

```bash
# MinIOデータのバックアップ
docker-compose -f docker-compose.prod.yml exec minio mc cp -r local/face-images /backup/minio/
```

### 3. バックアップの自動化

```bash
# crontabに追加
# 毎日午前2時にバックアップ
0 2 * * * /path/to/backup-script.sh
```

## モニタリングとロギング

### 1. ログ管理

```bash
# Dockerログのローテーション設定
cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# Dockerの再起動
sudo systemctl restart docker
```

### 2. ヘルスチェック

```yaml
# docker-compose.prod.ymlに追加
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### 3. パフォーマンスモニタリング

```bash
# Docker statsの監視
docker stats

# システムリソースの監視
htop
iotop
```

## スケーリング

### 1. 水平スケーリング

```bash
# フロントエンドのスケーリング
docker-compose -f docker-compose.prod.yml up -d --scale frontend=3

# バックエンドのスケーリング
docker-compose -f docker-compose.prod.yml up -d --scale backend=2
```

### 2. 負荷分散

```nginx
# Nginx負荷分散設定
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

## セキュリティ対策

### 1. ファイアウォール設定

```bash
# UFWの設定
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 8000/tcp   # バックエンドAPIを直接公開しない
```

### 2. コンテナセキュリティ

```bash
# 非rootユーザーでの実行
# docker-compose.prod.ymlでuserを指定
user: "1000:1000"

# 読み取り専用ファイルシステム
read_only: true
tmpfs:
  - /tmp
  - /var/run
```

### 3. 環境変数の保護

```bash
# 機密情報の外部ファイル化
# secrets.envファイルを作成
JWT_SECRET_KEY=your_secret_key
DATABASE_PASSWORD=your_db_password

# docker-composeで読み込み
env_file:
  - .env
  - secrets.env
```

## 災害復旧計画

### 1. バックアップ戦略

```bash
# バックアップ頻度
- データベース: 毎日
- MinIOデータ: 毎週
- 設定ファイル: 変更時

# バックアップ保存場所
- ローカルストレージ: 即時復旧用
- クラウドストレージ: 長期保存用
- オフサイト: 災害対策用
```

### 2. 復旧手順

```bash
# 1. 最新のバックアップの確認
ls -la /backup/

# 2. データベースの復旧
docker-compose -f docker-compose.prod.yml exec postgres psql -U faceuser facedb < backup_20241201_020000.sql

# 3. MinIOデータの復旧
docker-compose -f docker-compose.prod.yml exec minio mc cp -r /backup/minio/face-images local/

# 4. サービスの再起動
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

## メンテナンス

### 1. 定期メンテナンスタスク

```bash
# 月次のメンテナンススクリプト
#!/bin/bash

# Dockerシステムのクリーンアップ
docker system prune -af

# ログファイルのローテーション
logrotate /etc/logrotate.d/face-recognition

# データベースの最適化
docker-compose -f docker-compose.prod.yml exec postgres vacuumdb -U faceuser facedb

# SSL証明書の更新確認
certbot renew --dry-run
```

### 2. アップグレード手順

```bash
# 1. メンテナンスモードの開始
touch /tmp/maintenance.mode

# 2. 新バージョンの取得
git pull origin main

# 3. バックアップの作成
./scripts/backup.sh

# 4. サービスの停止
docker-compose -f docker-compose.prod.yml down

# 5. 新バージョンのデプロイ
docker-compose -f docker-compose.prod.yml up -d --build

# 6. ヘルスチェック
curl -f http://localhost:8000/health

# 7. メンテナンスモードの終了
rm /tmp/maintenance.mode
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. メモリ不足
```bash
# メモリ使用量の確認
docker stats

# Dockerのリソース制限調整
# /etc/docker/daemon.jsonを編集
```

#### 2. ディスク容量不足
```bash
# ディスク使用量の確認
df -h

# 不要なDockerデータの削除
docker system prune -a
```

#### 3. ネットワーク問題
```bash
# ネットワーク接続の確認
docker network ls
docker network inspect face-recognition_default
```

#### 4. パフォーマンス問題
```bash
# リソースモニタリング
top
iotop
docker stats

# ログ分析
docker-compose -f docker-compose.prod.yml logs --tail=100
```

これで本番環境へのデプロイ準備が完了しました！