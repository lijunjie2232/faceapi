# Docker Support Documentation

このドキュメントは、顔認識システムのDockerデプロイメントに関する詳細な説明を提供します。実際のプロジェクト構成に基づいて、デプロイメントスクリプト、環境変数設定、およびDocker関連の構成について網羅的に解説します。

## 目次

1. [概要](#概要)
2. [デプロイメントスクリプト](#デプロイメントスクリプト)
3. [環境変数設定](#環境変数設定)
4. [Docker Compose構成](#docker-compose構成)
5. [サービスアーキテクチャ](#サービスアーキテクチャ)
6. [GPUサポート](#gpuサポート)
7. [ネットワーク構成](#ネットワーク構成)
8. [ストレージ管理](#ストレージ管理)
9. [セキュリティ設定](#セキュリティ設定)
10. [モニタリングとロギング](#モニタリングとロギング)
11. [トラブルシューティング](#トラブルシューティング)

## 概要

この顔認識システムは、以下の主要コンポーネントで構成されています：

- **フロントエンド**: Vue.js 3 + Viteを使用したモダンなユーザーインターフェース
- **バックエンド**: FastAPIを使用したPythonアプリケーション
- **データベース**: 
  - PostgreSQL（ユーザーデータ管理）
  - Milvus（顔特徴ベクトルのベクトルデータベース）
  - etcd（Milvusのメタデータストア）
  - MinIO（オブジェクトストレージ）
- **リバースプロキシ**: Nginx（本番環境）

すべてのコンポーネントはDockerコンテナとして管理され、Docker Composeでオーケストレーションされます。

## デプロイメントスクリプト

### deploy.sh スクリプト

`deploy.sh`は、システム全体のデプロイメントを自動化するシェルスクリプトです。

#### 主な機能

1. **環境チェック**
   - DockerとDocker Composeの存在確認
   - GPUサポートの検出とテスト
   - 必要なディレクトリ構造の検証

2. **環境変数設定**
   - `.env.dev` または `.env.prod` ファイルの自動生成
   - セキュアなシークレットキーの自動生成
   - パスワードのランダム生成

3. **GPUサポートチェック**
   - NVIDIAドライバーの検出
   - Docker GPUランタイムの確認
   - GPU機能のテスト実行

4. **コンテナビルドと起動**
   - 開発/本番環境に応じたDockerイメージのビルド
   - サービス間の依存関係管理
   - ヘルスチェック付きの起動プロセス

#### 使用方法

```bash
# 開発環境のデプロイ（CPU版）
./deploy.sh dev

# 開発環境のデプロイ（GPU版）
./deploy.sh dev --gpu

# 本番環境のデプロイ（CPU版）
./deploy.sh prod

# 本番環境のデプロイ（GPU版）
./deploy.sh prod --gpu

# GPUサポートのチェックとテスト
./deploy.sh gpu-check

# コンテナの再ビルド
./deploy.sh rebuild backend        # 特定コンテナの再ビルド
./deploy.sh rebuild all            # すべてのコンテナを再ビルド
./deploy.sh rebuild frontend prod  # 本番環境のフロントエンド再ビルド

# サービス管理
./deploy.sh logs                   # 開発環境のログ表示
./deploy.sh logs prod              # 本番環境のログ表示
./deploy.sh status                 # サービス状態確認
./deploy.sh stop                   # サービス停止
```

#### スクリプトの詳細な処理フロー

1. **初期化フェーズ**
   ```bash
   # エラーハンドリングの設定
   set -e  # エラー発生時にスクリプト終了
   
   # 色付き出力の定義
   RED='\033[0;31m'
   GREEN='\033[0;32m'
   YELLOW='\033[1;33m'
   BLUE='\033[0;34m'
   NC='\033[0m' # No Color
   ```

2. **GPUサポートチェック**
   ```bash
   check_gpu_support() {
       # NVIDIAドライバーの確認
       if ! command -v nvidia-smi &> /dev/null; then
           print_warning "NVIDIAドライバーが見つかりません"
           return 1
       fi
       
       # Docker GPUランタイムの確認
       if docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi>/dev/null 2>&1; then
           print_status "Docker GPUサポートが利用可能です"
           return 0
       else
           print_warning "Docker GPUサポートが設定されていません"
           return 1
       fi
   }
   ```

3. **環境変数生成**
   ```bash
   generate_env() {
       local env=${1:-dev}
       env_file=".env.$env"
       env_example_file=".env.$env.example"

       if [[ ! -f $env_file ]]; then
           cp "$env_example_file" "$env_file"
           
           # セキュアなパスワードを生成
           safe_sed_replace "your_jwt_secure_secret_key_here" "$(openssl rand -hex 32)" "$env_file"
           safe_sed_replace "your_secure_db_password_here" "$(openssl rand -hex 8)" "$env_file"
       fi
       
       # 環境設定を表示
       source_env "$env"
   }
   ```

## 環境変数設定

### 環境変数ファイル

プロジェクトには2つの環境変数テンプレートが提供されています：

- `.env.dev.example` - 開発環境用
- `.env.prod.example` - 本番環境用

### 主要な環境変数

#### Milvusデータベース設定
```bash
# Milvus設定
MILVUS_DB_HOST=standalone
MILVUS_DB_PORT=19530
MILVUS_DB_USER=root
MILVUS_DB_PASSWORD=milvus
MILVUS_DB_DB_NAME=default  # またはfaceapi（本番環境）
```

#### SQLデータベース設定
```bash
# PostgreSQL設定
SQL_BACKEND=asyncpg
SQL_HOST=postgres
SQL_PORT=5432
SQL_USERNAME=faceuser
SQL_PASSWORD=facepass123  # 本番環境では自動生成
SQL_DATABASE=faceapi
```

#### モデル設定
```bash
# 顔認識モデル
MODEL_PATH=/faceapi/model.onnx
MODEL_LOADER=onnx
MODEL_THRESHOLD=0.2285
MODEL_DEVICE=cpu  # またはcuda:0（GPU版）
MODEL_EMB_DIM=512
```

#### アプリケーション設定
```bash
# アプリケーション基本設定
API_V1_STR=/api/v1
PROJECT_NAME="FaceAPI (dev)"

# セキュリティ設定
JWT_SECRET_KEY=auto_generated_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# パスワードハッシュ
PASSWORD_HASH_ALGORITHM=sha256_crypt

# サーバー設定
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# 顔重複登録設定
ALLOW_FACE_DEDUPICATION=false
```

#### 開発環境固有設定
```bash
# コンテナ設定
BACKEND_DEV_PORT=6874
FRONTEND_DEV_PORT=3000
DOCKER_VOLUME_DIRECTORY=./volumes_dev
```

#### 本番環境固有設定
```bash
# デプロイメント設定
DOCKER_VOLUME_DIRECTORY=./volumn
HOST_PORT=80
DOMAIN_NAME=""  # カスタムドメイン設定
```

### 環境変数の優先順位

1. コマンドラインで直接指定された値
2. `.env`ファイル内の値
3. Docker Composeファイル内のデフォルト値
4. アプリケーションコード内のハードコードされたデフォルト値

## Docker Compose構成

### 構成ファイルの種類

プロジェクトには4つの主要なDocker Composeファイルがあります：

1. **docker-compose.dev.yml** - 開発環境（CPU版）
2. **docker-compose.prod.yml** - 本番環境（CPU版）
3. **docker-compose.dev.gpu.yml** - 開発環境（GPU版）
4. **docker-compose.prod.gpu.yml** - 本番環境（GPU版）

### サービス構成例（開発環境）

```yaml
version: '3.8'

services:
  # PostgreSQLデータベース
  postgres:
    image: postgres:15-alpine
    container_name: face-rec-postgres
    environment:
      POSTGRES_DB: ${SQL_DATABASE:-faceapi}
      POSTGRES_USER: ${SQL_USERNAME:-faceuser}
      POSTGRES_PASSWORD: ${SQL_PASSWORD:-facepass123}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "${SQL_PORT:-5432}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U faceuser -d faceapi"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Milvusベクトルデータベース
  etcd:
    container_name: milvus-etcd
    image: quay.io/coreos/etcd:v3.5.25
    environment:
      - ETCD_AUTO_COMPACTION_MODE=revision
      - ETCD_AUTO_COMPACTION_RETENTION=1000
      - ETCD_QUOTA_BACKEND_BYTES=4294967296
    volumes:
      - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/etcd:/etcd
    command: etcd -advertise-client-urls=http://etcd:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd
    healthcheck:
      test: ["CMD", "etcdctl", "endpoint", "health"]
      interval: 30s
      timeout: 20s
      retries: 3

  minio:
    container_name: milvus-minio
    image: minio/minio:RELEASE.2024-12-18T13-15-44Z
    environment:
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    ports:
      - "9001:9001"
      - "9000:9000"
    volumes:
      - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/minio:/minio_data
    command: minio server /minio_data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  standalone:
    container_name: milvus-standalone
    image: milvusdb/milvus:v2.6.11  # CPU版
    # GPU版では: milvusdb/milvus:v2.6.11-gpu
    command: ["milvus", "run", "standalone"]
    security_opt:
      - seccomp:unconfined
    environment:
      ETCD_ENDPOINTS: etcd:2379
      MINIO_ADDRESS: minio:9000
      MQ_TYPE: woodpecker
    volumes:
      - ${DOCKER_VOLUME_DIRECTORY:-.}/volumes/milvus:/var/lib/milvus
    ports:
      - "19530:19530"
      - "9091:9091"
    depends_on:
      - "etcd"
      - "minio"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9091/healthz"]
      interval: 30s
      start_period: 90s
      timeout: 20s
      retries: 3

  # バックエンドサービス
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile  # CPU版
      # GPU版では: backend/Dockerfile-gpu
    container_name: face-rec-backend
    environment:
      - SQL_BACKEND=${SQL_BACKEND:-asyncpg}
      - SQL_HOST=${SQL_HOST:-postgres}
      - SQL_PORT=${SQL_PORT:-5432}
      - SQL_USERNAME=${SQL_USERNAME:-faceuser}
      - SQL_PASSWORD=${SQL_PASSWORD:-facepass123}
      - SQL_DATABASE=${SQL_DATABASE:-faceapi}
      - MILVUS_DB_HOST=${MILVUS_DB_HOST:-standalone}
      - MILVUS_DB_PORT=${MILVUS_DB_PORT:-19530}
      - MODEL_PATH=${MODEL_PATH:-/faceapi/model.onnx}
      - MODEL_DEVICE=${MODEL_DEVICE:-cpu}  # GPU版ではcuda:0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./backend/faceapi:/faceapi/faceapi  # 開発用 - 本番では削除
    depends_on:
      postgres:
        condition: service_healthy
      standalone:
        condition: service_healthy
    ports:
      - "${BACKEND_DEV_PORT:-9724}:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    command: faceapi --reload --log-level debug

  # フロントエンドサービス（開発）
  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile_dev
    container_name: face-rec-frontend
    ports:
      - "${FRONTEND_DEV_PORT:-3000}:3000"
    depends_on:
      - backend
    environment:
      - VITE_API_BASE_URL=http://localhost:${BACKEND_DEV_PORT:-9724}
      - VITE_APP_TITLE=Face Recognition System (dev)

volumes:
  postgres_data:
  etcd:
  minio:
  milvus:
```

## サービスアーキテクチャ

### コンテナ間の依存関係

```
┌─────────────┐    ┌─────────────┐    
│   Frontend  │◄──►│   Backend   │    
│   (Vue.js)  │    │  (FastAPI)  │    
└─────────────┘    └─────────────┘    
                         │              
┌─────────────┐    ┌─────────────┐    
│  PostgreSQL │    │   Milvus    │    
│ (UserData)  │    │ (FaceVector)│    
└─────────────┘    └─────────────┘    
                         │              
┌─────────────┐    ┌─────────────┐    
│    etcd     │    │    MinIO    │    
│ (Metadata)  │    │ (Storage)   │    
└─────────────┘    └─────────────┘    

本番環境ではNginxがフロントエンドとバックエンドの前段に配置されます。
```

### サービスポートマッピング

| サービス | 内部ポート | 外部ポート | 説明 |
|---------|-----------|-----------|------|
| Backend | 8000 | 6874 (dev) / 8000 (prod) | APIサーバー |
| Frontend | 3000 | 3000 (dev) | 開発サーバー |
| PostgreSQL | 5432 | 5432 | データベース |
| Milvus | 19530 | 19530 | ベクトルDB |
| Milvus Dashboard | 9091 | 9091 | 管理画面 |
| MinIO Console | 9001 | 9001 | ストレージ管理 |
| Nginx | 80 | 80 (prod) | リバースプロキシ |

## GPUサポート

### GPU対応構成

GPUサポートはNVIDIA Container Toolkitを必要とします：

```bash
# NVIDIA Container Toolkitのインストール（Ubuntu）
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### GPU構成ファイルの違い

GPU対応のDocker Composeファイルでは以下が変更されます：

```yaml
services:
  # MilvusのGPU対応イメージ
  standalone:
    image: milvusdb/milvus:v2.6.11-gpu  # GPU版イメージ
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              capabilities: ["gpu"]
              device_ids: ["0"]

  # バックエンドのGPU対応
  backend:
    build:
      dockerfile: backend/Dockerfile-gpu  # GPU用Dockerfile
    environment:
      - MODEL_DEVICE=cuda:0  # GPUデバイス指定
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              capabilities: ["gpu"]
              device_ids: ["0"]
```

### GPU対応Dockerfile

**backend/Dockerfile-gpu** の主な違い：

```dockerfile
# PyTorch GPU対応のインストール
RUN pip install torch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 --index-url https://download.pytorch.org/whl/cu121
RUN pip install timm  # Vision Transformerモデル用

# その他の依存関係はCPU版と同じ
RUN pip install onnxruntime
RUN pip install -e . -v --no-build-isolation
```

## ネットワーク構成

### 開発環境ネットワーク

```yaml
# 開発環境ではデフォルトのbridgeネットワークを使用
# 各サービスは同じネットワーク上に配置され、サービス名で相互参照可能
```

### 本番環境ネットワーク

```yaml
networks:
  face-rec-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  backend:
    networks:
      - face-rec-network
      
  postgres:
    networks:
      - face-rec-network
```

### セキュリティ設定

```yaml
services:
  backend:
    # 外部からの直接アクセスを制限
    ports:
      - "127.0.0.1:8000:8000"  # localhostのみ
    
  # 本番環境ではNginx経由でのみアクセス
  nginx:
    ports:
      - "80:80"
      - "443:443"  # HTTPS対応時
```

## ストレージ管理

### ボリューム構成

```yaml
volumes:
  # 永続化ボリューム
  postgres_data:
    driver: local
  etcd:
    driver: local
  minio:
    driver: local
  milvus:
    driver: local
    
  # 名前付きボリューム（本番環境）
  postgres_data:
    driver: local
    name: ${POSTGRES_VOLUME_NAME:-postgres_data}
```

### データバックアップ戦略

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$DATE"

mkdir -p $BACKUP_DIR

# PostgreSQLバックアップ
docker exec face-rec-postgres pg_dump -U faceuser faceapi > $BACKUP_DIR/postgres_backup.sql

# Milvusデータバックアップ
docker exec milvus-standalone tar -czf /tmp/milvus_backup.tar.gz /var/lib/milvus
docker cp milvus-standalone:/tmp/milvus_backup.tar.gz $BACKUP_DIR/

# アプリケーションデータバックアップ
tar -czf $BACKUP_DIR/app_data.tar.gz ./backend/uploads ./models
```

### ボリュームの場所

開発環境：
- `./volumes_dev/etcd/`
- `./volumes_dev/minio/`
- `./volumes_dev/milvus/`

本番環境：
- Docker管理ボリューム（`docker volume ls`で確認）

## セキュリティ設定

### コンテナセキュリティ

```yaml
services:
  backend:
    # 非rootユーザーでの実行
    user: "1000:1000"
    
    # 特権の制限
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETUID
      - SETGID
      
    # 読み取り専用ファイルシステム（一部例外）
    read_only: true
    tmpfs:
      - /tmp
      - /var/tmp
```

### 環境変数の保護

```bash
# .envファイルの権限設定
chmod 600 .env.dev
chmod 600 .env.prod

# セキュアなシークレットの生成
openssl rand -hex 32  # JWTシークレット
openssl rand -base64 32  # データベースパスワード
```

### ネットワークセキュリティ

```yaml
# 開発環境での外部アクセス制限
services:
  postgres:
    ports:
      - "127.0.0.1:5432:5432"  # localhostのみ
      
  # 本番環境では内部ネットワークのみ
  backend:
    networks:
      - face-rec-network
    expose:
      - "8000"  # 外部ポート公開なし
```

## モニタリングとロギング

### ログ構成

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        compress: "true"
    environment:
      - LOG_LEVEL=INFO
```

### ヘルスチェック

```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
      
  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U faceuser -d faceapi"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### リソース制限

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
          
  postgres:
    shm_size: 128mb  # 共有メモリの設定
```

### モニタリングコマンド

```bash
# リソース使用量の監視
docker stats

# コンテナログのリアルタイム表示
docker-compose logs -f backend

# 特定サービスのログ
docker-compose logs postgres

# ネットワーク統計
docker network ls
docker network inspect face-rec-network
```

## トラブルシューティング

### よくある問題と解決策

#### 1. コンテナ起動失敗

```bash
# ログ確認
./deploy.sh logs

# 特定サービスのログ
docker-compose logs backend
docker-compose logs postgres

# コンテナの状態確認
docker-compose ps

# クリーンスタート
./deploy.sh stop
docker-compose down -v  # ボリュームも削除
./deploy.sh dev
```

#### 2. データベース接続エラー

```bash
# PostgreSQLの状態確認
docker-compose exec postgres pg_isready -U faceuser -d faceapi

# データベース一覧確認
docker-compose exec postgres psql -U faceuser -d faceapi -c "\dt"

# Milvusの状態確認
docker-compose exec standalone milvus status
```

#### 3. GPU利用不可

```bash
# GPU認識確認
nvidia-smi

# DockerでのGPU利用確認
docker run --rm --gpus all nvidia/cuda:11.0-base-ubuntu20.04 nvidia-smi

# NVIDIA Container Toolkit確認
sudo systemctl status nvidia-docker

# GPU版の再デプロイ
./deploy.sh stop
./deploy.sh dev --gpu
```

#### 4. ポート競合

```bash
# 使用中ポート確認
sudo netstat -tlnp | grep :8000
sudo lsof -i :5432

# Dockerコンテナのポート確認
docker port face-rec-backend
docker-compose port backend 8000

# 環境変数でのポート変更
# .env.devファイルで以下を変更:
# BACKEND_DEV_PORT=8001
# FRONTEND_DEV_PORT=3001
```

#### 5. モデルダウンロードエラー

```bash
# モデルダウンロードスクリプトの実行
cd frontend
node scripts/download_models.js

# 手動でのモデル配置
mkdir -p public/models
# モデルファイルを手動で配置
```

### デバッグコマンド集

```bash
# 全サービス状態確認
docker-compose ps

# サービスログリアルタイム表示
docker-compose logs -f

# コンテナ内に入る
docker-compose exec backend bash
docker-compose exec postgres psql -U faceuser -d faceapi

# ネットワーク確認
docker network ls
docker network inspect [network_name]

# ボリューム確認
docker volume ls
docker volume inspect [volume_name]

# リソース使用量確認
docker stats
docker system df

# コンテナ詳細情報
docker inspect [container_name]
```

### パフォーマンスチューティング

```bash
# リソース制限の調整
# docker-compose.ymlで以下を調整:
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 4G  # 増加
          cpus: '2.0'  # 増加

# データベースパラメータの最適化
# PostgreSQLのpostgresql.confを調整
shared_buffers = 256MB
effective_cache_size = 1GB
```

### エラーメッセージ対応表

| エラーメッセージ | 原因 | 解決策 |
|----------------|------|--------|
| "Connection refused" | サービスが起動していない | `docker-compose ps`で状態確認 |
| "Permission denied" | ファイル権限不足 | `chmod 600 .env.*`を実行 |
| "Port already in use" | ポート競合 | 別のポートを使用 or プロセスを終了 |
| "CUDA out of memory" | GPUメモリ不足 | バッチサイズを小さく or GPUメモリを増設 |
| "Model not found" | モデルファイル不在 | `download_models.js`を実行 |
| "502 Bad Gateway" | バックエンドサービスが起動していないあるいは接続拒絶 | "docker-compose logs -f xxx.yml backend" でログを確認し、dockerを用いる場合、"uvicorn"の"host"は必ず"0.0.0.0"に設定します |

このドキュメントは、顔認識システムのDockerデプロイメントに関する包括的なガイドを提供します。実際の運用では、組織のセキュリティポリシーと要件に応じて設定を調整してください。