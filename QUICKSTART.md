# 🚀 Quick Start Guide

このガイドでは、顔認識システムを素早く起動・実行する方法を説明します。

## 📋 前提条件

- **Docker** と **Docker Compose**
- **Python 3.8+** （ローカル実行の場合）
- **uv package manager**
- **GPU**（任意 - GPU対応コンテナ用）

## 🎯 クイックスタート（3ステップ）

### 1. 環境設定
```bash
# リポジトリをクローン
git clone <repository-url>
cd face_recognition_system

# 開発環境ファイルを生成
./deploy.sh generate-env dev
```

### 2. システム起動
```bash
# すべてのサービスを起動
./deploy.sh up dev
```

### 3. アクセス
- **フロントエンド**: http://localhost:8080
- **APIドキュメント**: http://localhost:8000/docs
- **管理者画面**: http://localhost:8080/admin

🎉 これで準備完了！

## 🐳 Dockerによる実行（推奨）

> **💡 ヒント**: `deploy.sh`スクリプトを使用すると、環境設定からサービス管理までを自動化できます。

### 方法1: 自動デプロイメントスクリプトを使用（推奨）

```bash
# 開発環境の起動
./deploy.sh up dev

# または本番環境の起動
./deploy.sh up prod

# GPU対応バージョン（利用可能な場合）
./deploy.sh up dev --gpu
```

### 方法2: 手動でDocker Composeを使用

```bash
# 開発環境
docker-compose -f docker-compose.dev.yml up -d

# 本番環境
docker-compose -f docker-compose.prod.yml up -d

# GPU対応開発環境
docker-compose -f docker-compose.dev.gpu.yml up -d
```

起動されるサービス：
- **Milvus** ベクトルデータベース
- **etcd** キー・バリューストア
- **MinIO** オブジェクトストレージ
- **PostgreSQL** リレーショナルデータベース
- **Backend API** サーバー
- **Frontend** アプリケーション
- **Nginx** リバースプロキシ（本番環境）

### アクセス先

- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:8080
- **Milvus Dashboard**: http://localhost:9091
- **Admin Panel**: http://localhost:8080/admin

## 💻 ローカルでの実行

### 🔧 バックエンドのセットアップ

1. 依存関係のインストール：

```bash
# uvを使用（推奨）
uv pip install -r backend/requirements.txt

# またはpipを使用
pip install -r backend/requirements.txt
```

2. 環境変数の設定：

```bash
# 開発用環境ファイルの作成
cp .env.dev.example .env.dev

# 必要に応じて編集
nano .env.dev
```

3. Milvusの起動（Docker経由）：

```bash
# Milvusスタックのみを起動
docker-compose -f docker-compose.dev.yml up -d etcd minio standalone
```

4. バックエンドサーバーの起動：

```bash
cd backend
export $(cat ../.env.dev | xargs)
uvicorn faceapi.main:app --reload --host 0.0.0.0 --port 8000
```

### 🖥️ フロントエンドのセットアップ

1. フロントエンドディレクトリに移動：

```bash
cd frontend
```

2. 依存関係のインストール：

```bash
# npmを使用
npm install

# またはpnpmを使用（推奨）
pnpm install
```

3. 顔認識モデルのダウンロード：

```bash
# 必要なモデルファイルをダウンロード
node scripts/download_models.js
```

4. 開発サーバーの起動：

```bash
# Vite開発サーバー
npm run dev

# またはビルド済みバージョン
npm run build
npm run preview
```

## 📡 API使用例

システムが起動したら、以下のAPIエンドポイントをテストできます：

### 新規ユーザー登録

```bash
curl -X POST "http://localhost:8000/api/v1/users/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "password": "securepassword"
  }'
```

### ユーザー認証（ログイン）

```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "securepassword"
  }'
```

### 顔画像の登録

```bash
# base64エンコードされた画像が必要
curl -X POST "http://localhost:8000/api/v1/register-face" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/...",
    "image_format": "jpg"
  }'
```

### 顔認識

```bash
curl -X POST "http://localhost:8000/api/v1/recognize-face" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/...",
    "image_format": "jpg"
  }'
```

### 管理者機能

```bash
# 全ユーザー一覧取得（管理者権限が必要）
curl -X GET "http://localhost:8000/api/v1/admin/users" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN"

# ユーザー削除
curl -X DELETE "http://localhost:8000/api/v1/admin/users/1" \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN"
```

## 🛠️ 利用可能なコマンド

`deploy.sh`スクリプトには以下のコマンドが用意されています：

```bash
# システムの起動
./deploy.sh up dev          # 開発環境を起動
./deploy.sh up prod         # 本番環境を起動
./deploy.sh up dev --gpu    # GPU対応開発環境

# システムの停止
./deploy.sh down dev        # 開発環境を停止
./deploy.sh down prod       # 本番環境を停止

# 状態確認
./deploy.sh status dev      # サービスの状態を確認
./deploy.sh logs dev        # ログを表示

# 設定管理
./deploy.sh generate-env dev    # 環境ファイルを生成
./deploy.sh show-config dev     # 現在の設定を表示

# GPUテスト
./deploy.sh test-gpu        # GPU機能をテスト

# ヘルプ
./deploy.sh help            # すべてのコマンドを表示
```

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 🔴 Dockerコンテナが起動しない
```bash
# コンテナの状態を確認
./deploy.sh status dev

# ログを確認
docker-compose logs

# クリーンスタート
./deploy.sh down dev
./deploy.sh up dev
```

#### 🔴 Milvus接続エラー
```bash
# Milvusサービスの状態を確認
docker-compose ps standalone etcd minio

# ポートが使用中か確認
sudo lsof -i :19530
```

#### 🔴 フロントエンドがAPIに接続できない
```bash
# CORS設定を確認
# .env.devファイルでALLOWED_ORIGINSを設定

# ネットワーク接続を確認
curl http://localhost:8000/api/v1/health
```

#### 🔴 GPU機能が動作しない
```bash
# GPU対応をテスト
./deploy.sh test-gpu

# nvidia-dockerが正しくインストールされているか確認
nvidia-smi
```

#### 🔴 顔認識精度が低い
```bash
# モデルの閾値を調整（.envファイルで）
MODEL_THRESHOLD=0.2285

# 重複顔登録の許可設定を確認
ALLOW_FACE_DEDUPICATION=true
```

### 環境変数の確認

```bash
# 現在の設定を表示
./deploy.sh show-config dev

# 環境ファイルの生成
./deploy.sh generate-env dev
```

### デバッグコマンド

```bash
# すべてのサービスのログをリアルタイムで表示
./deploy.sh logs dev

# 特定のサービスのログ
docker-compose logs backend

# データベースの内容を確認
docker-compose exec postgres psql -U faceuser -d faceapi -c "\dt"
```

### サポート

問題が解決しない場合は、以下の情報を提供してください：
- 使用しているOSとバージョン
- DockerおよびDocker Composeのバージョン
- 実行したコマンドとエラーメッセージ
- `.env`ファイルの内容（機密情報は除く）

---
- problem:
```shell
asyncclick.exceptions.UsageError: You may need to run `aerich init-db` first to initialize the database.
```
- solution:
  - delete the content in folder `./migrations`