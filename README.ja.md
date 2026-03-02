<div align="center">

# 顔認識システム

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)](https://vuejs.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> 🚀 **FastAPI + Vue.js + Dockerで構築された現代的な顔認識システム**

[:us: English](README.en.md) • [:jp: 日本語](README.ja.md) • [:tw: 繁體中文](README.zh-TW.md)

</div>

## 📚 ドキュメント

**包括的なドキュメントが複数言語でご利用いただけます：**

- 🌐 **オンラインドキュメント**: https://lijunjie2232.github.io/faceapi/
- 📖 **ローカルドキュメント**: 
  - [日本語ドキュメント](docs/ja/)
  - [繁體中文文檔](docs/zh-TW/)
  - [English Documentation](docs/en/)

> **💡 クイックアクセス**: 即座にセットアップするには [QUICKSTART.md](QUICKSTART.md) をご覧ください

## 🌟 主な機能

- 🔐 **安全な認証**: JWTベースのユーザー認証システム
- 👤 **顔登録**: ユーザーごとに複数の顔画像を登録可能
- 🎯 **高精度認識**: 先進的な顔検出と識別機能
- 🖼️ **リアルタイム処理**: ウェブカメラによるリアルタイム顔認識
- 📊 **管理ダッシュボード**: 総合的なユーザー管理インターフェース
- 🐳 **Dockerデプロイ**: 簡単なコンテナ化デプロイ
- 🌐 **多言語対応**: 日本語、繁体中文、英語に対応
- 🚀 **GPU加速**: GPUサポートによる高性能処理

## 🚀 クイックスタート

### 前提条件

- Docker 20.10+
- Docker Compose 1.29+
- Git

### インストール

```bash
# リポジトリをクローン
git clone https://github.com/lijunjie2232/faceapi.git
cd face_recognition_system

# 環境ファイルを生成
./deploy.sh generate-env dev

# すべてのサービスを起動
./deploy.sh up dev
```

### サービスへのアクセス

- **フロントエンド**: http://localhost:8080
- **バックエンドAPI**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs
- **管理パネル**: http://localhost:8080/admin

## 🏗️ アーキテクチャ

### 技術スタック

**バックエンド**
- FastAPI - モダンなPython Webフレームワーク
- Milvus - 顔埋め込み用のベクトルデータベース
- PostgreSQL - リレーショナルデータベース
- Tortoise ORM - 非同期ORM
- face_recognition - 顔検出ライブラリ
- ONNX Runtime - ML推論エンジン

**フロントエンド**
- Vue 3 - プログレッシブJavaScriptフレームワーク
- Vite - 次世代ビルドツール
- face-api.js - JavaScript顔認識
- Element Plus - UIコンポーネントライブラリ

**インフラストラクチャ**
- Docker - コンテナ化プラットフォーム
- Docker Compose - マルチコンテナオーケストレーション
- Nginx - リバースプロキシとロードバランサー
- MinIO - 画像用オブジェクトストレージ

## 📖 詳細ドキュメント

包括的なガイドについては、多言語ドキュメントをご参照ください：

| ドキュメント | 説明 | 対応言語 |
|------------|------|---------|
| [インストールガイド](docs/ja/install.md) | 完全なインストール手順 | 🇯🇵 🇹🇼 🇬🇧 |
| [デプロイガイド](docs/ja/deploy.md) | 本番環境デプロイ戦略 | 🇯🇵 🇹🇼 🇬🇧 |
| [開発ガイド](docs/ja/dev.md) | ローカル開発環境 | 🇯🇵 🇹🇼 🇬🇧 |
| [プロジェクト構造](PROJECT_STRUCTURE.md) | 詳細なコード構成 | 英語 |
| [クイックスタート](QUICKSTART.md) | 迅速セットアップガイド | 日本語 |

## 🐳 デプロイオプション

### 1. Docker Compose (推奨)

```bash
# 開発環境
docker-compose -f docker-compose.dev.yml up -d

# 本番環境 (事前ビルド済みイメージ)
docker-compose -f docker-compose.yml up -d

# GPU対応環境
docker-compose -f docker-compose.dev.gpu.yml up -d
```

### 2. 手動ビルド

```bash
# バックエンドイメージをビルド
docker build -t face-rec-backend backend/

# フロントエンドイメージをビルド
docker build -t face-rec-frontend frontend/
```

## 🛠️ 開発

### ローカル開発環境

```bash
# バックエンドセットアップ
cd backend
pip install -e .
faceapi --gen-env .env
faceapi --debug

# フロントエンドセットアップ
cd frontend
pnpm install
pnpm serve
```

### APIエンドポイント

- **認証**: `/api/v1/users/login`, `/api/v1/users/signup`
- **顔認識**: `/api/v1/register-face`, `/api/v1/recognize-face`
- **ユーザー管理**: `/api/v1/user/profile`, `/api/v1/user/faces`
- **管理機能**: `/api/v1/admin/users`, `/api/v1/admin/stats`

## 🤝 貢献

貢献を歓迎します！以下の手順に従ってください：

1. リポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルをご覧ください。

## 🆘 サポート

問題や質問がある場合：

- 最初に[ドキュメント](https://lijunjie2232.github.io/faceapi/)をご確認ください
- [GitHub Issues](https://github.com/lijunjie2232/faceapi/issues)で問題を報告
- 一般的なトラブルシューティングについては[QUICKSTART.md](QUICKSTART.md)を参照