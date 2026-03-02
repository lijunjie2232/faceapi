# 開発環境設定

このガイドでは、Face Recognition Systemの開発環境構築とローカルでの実行方法について説明します。

## 開発環境の概要

開発環境は以下のコンテナで構成されています：

- **frontend**: Vue.js 3ベースのフロントエンドアプリケーション
- **backend**: FastAPIベースのバックエンドAPIサーバー
- **postgres**: ユーザーデータを格納するPostgreSQLデータベース
- **milvus-standalone**: 顔特徴ベクトルを格納するベクトルデータベース
- **minio**: 顔画像を格納するオブジェクトストレージ
- **etcd**: Milvusのメタデータ管理用
- **nginx**: リバースプロキシと静的ファイル配信

## ローカル開発環境の起動

### 1. 開発環境の起動

```bash
# 開発環境の起動
docker-compose -f docker-compose.dev.yml up -d

# サービスの状態確認
docker-compose -f docker-compose.dev.yml ps

# ログの確認
docker-compose -f docker-compose.dev.yml logs -f
```

### 2. GPU対応開発環境（任意）

GPUを使用する場合：

```bash
# GPU対応環境の起動
docker-compose -f docker-compose.dev.gpu.yml up -d
```

## 各サービスへのアクセス

起動後、以下のURLから各サービスにアクセスできます：

| サービス | URL | 説明 |
|---------|-----|------|
| フロントエンド | http://localhost:3000 | Vue.jsアプリケーション |
| バックエンドAPI | http://localhost:8000 | FastAPIサーバー |
| APIドキュメント | http://localhost:8000/docs | Swagger UI |
| MinIOコンソール | http://localhost:9001 | オブジェクトストレージ管理 |
| Milvusコンソール | http://localhost:9091 | ベクトルデータベース管理 |

## バックエンド開発

### 1. バックエンドコードのホットリロード

開発中はコード変更時に自動的に再起動されます：

```bash
# バックエンドログの監視
docker-compose -f docker-compose.dev.yml logs -f backend
```

### 2. データベースマイグレーション

```bash
# データベース初期化
docker-compose -f docker-compose.dev.yml exec backend python -m faceapi.db.init_sql

# 管理者アカウント作成
docker-compose -f docker-compose.dev.yml exec backend python -m faceapi.db.init_account
```

### 3. APIテスト

```bash
# APIドキュメントへのアクセス
open http://localhost:8000/docs

# curlを使ったAPIテスト例
curl -X POST http://localhost:8000/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

## フロントエンド開発

### 1. フロントエンドのホットリロード

Vue.jsの開発サーバーはホットリロードに対応しています：

```bash
# フロントエンドログの監視
docker-compose -f docker-compose.dev.yml logs -f frontend
```

### 2. 依存関係の追加

```bash
# 新しいnpmパッケージのインストール
docker-compose -f docker-compose.dev.yml exec frontend pnpm add package-name

# 開発用パッケージのインストール
docker-compose -f docker-compose.dev.yml exec frontend pnpm add -D package-name
```

### 3. ビルドのテスト

```bash
# 本番ビルドのテスト
docker-compose -f docker-compose.dev.yml exec frontend pnpm build
```

## データベース操作

### 1. PostgreSQLへの接続

```bash
# PostgreSQLコンテナへの接続
docker-compose -f docker-compose.dev.yml exec postgres psql -U faceuser -d facedb

# 便利なSQLコマンド
\dt                    # テーブル一覧表示
\d table_name          # テーブル構造表示
SELECT * FROM users;   # ユーザーテーブルの内容表示
```

### 2. Milvusへの接続

```bash
# Milvusコンソールへのアクセス
open http://localhost:9091

# PythonからMilvusに接続
docker-compose -f docker-compose.dev.yml exec backend python
```

```python
from pymilvus import connections, Collection

# 接続
connections.connect(host='milvus-standalone', port='19530')

# コレクション一覧
collections = connections.list_collections()
print(collections)
```

## テスト

### 1. 単体テストの実行

```bash
# バックエンドテストの実行
docker-compose -f docker-compose.dev.yml exec backend pytest

# 特定のテストファイルの実行
docker-compose -f docker-compose.dev.yml exec backend pytest tests/test_users.py

# カバレッジレポートの生成
docker-compose -f docker-compose.dev.yml exec backend pytest --cov=faceapi --cov-report=html
```

### 2. E2Eテスト

```bash
# Cypressテストの実行
docker-compose -f docker-compose.dev.yml exec frontend pnpm test:e2e
```

## デバッグ

### 1. ログの確認

```bash
# すべてのサービスのログ
docker-compose -f docker-compose.dev.yml logs

# 特定サービスのログ
docker-compose -f docker-compose.dev.yml logs backend
docker-compose -f docker-compose.dev.yml logs frontend

# ログのリアルタイム監視
docker-compose -f docker-compose.dev.yml logs -f
```

### 2. コンテナ内での作業

```bash
# バックエンドコンテナへのアクセス
docker-compose -f docker-compose.dev.yml exec backend bash

# フロントエンドコンテナへのアクセス
docker-compose -f docker-compose.dev.yml exec frontend sh

# データベースコンテナへのアクセス
docker-compose -f docker-compose.dev.yml exec postgres bash
```

### 3. デバッグモードでの起動

```bash
# バックエンドをデバッグモードで起動
docker-compose -f docker-compose.dev.yml stop backend
docker-compose -f docker-compose.dev.yml run --service-ports backend uvicorn faceapi.main:app --host 0.0.0.0 --port 8000 --reload
```

## 環境変数

### 開発環境用の主な環境変数

```bash
# .envファイルの例
DEBUG=True
LOG_LEVEL=DEBUG

# データベース
POSTGRES_USER=faceuser
POSTGRES_PASSWORD=dev_password
POSTGRES_DB=facedb

# JWT
JWT_SECRET_KEY=development_secret_key
JWT_EXPIRE_MINUTES=30

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
```

## 開発ワークフロー

### 1. 新機能の開発手順

```bash
# 1. 新しいブランチの作成
git checkout -b feature/new-feature

# 2. コードの変更

# 3. テストの実行
docker-compose -f docker-compose.dev.yml exec backend pytest

# 4. コミット
git add .
git commit -m "Add new feature"

# 5. プッシュ
git push origin feature/new-feature
```

### 2. コード品質チェック

```bash
# バックエンドのコードフォーマット
docker-compose -f docker-compose.dev.yml exec backend black .

# フロントエンドのコードフォーマット
docker-compose -f docker-compose.dev.yml exec frontend pnpm format

# リントチェック
docker-compose -f docker-compose.dev.yml exec backend flake8 .
docker-compose -f docker-compose.dev.yml exec frontend pnpm lint
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. コンテナが起動しない
```bash
# コンテナの状態確認
docker-compose -f docker-compose.dev.yml ps

# コンテナのログ確認
docker-compose -f docker-compose.dev.yml logs service_name

# コンテナの再ビルド
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d --build
```

#### 2. データベース接続エラー
```bash
# データベースサービスの再起動
docker-compose -f docker-compose.dev.yml restart postgres

# データベース初期化の再実行
docker-compose -f docker-compose.dev.yml exec backend python -m faceapi.db.init_sql
```

#### 3. メモリ不足
```bash
# Dockerのリソース制限確認
docker info | grep -i memory

# 不要なコンテナ・イメージの削除
docker system prune -a
```

#### 4. ポート競合
```bash
# 使用中のポート確認
sudo lsof -i :8000
sudo lsof -i :3000

# docker-compose.ymlのポート変更
```

### 開発環境のリセット

```bash
# 開発環境の完全クリーンアップ
./scripts/clean-dev-env.sh

# または手動で
docker-compose -f docker-compose.dev.yml down -v
docker volume ls | grep face
docker volume rm [volume_names]
```

これで開発環境の準備が完了しました！