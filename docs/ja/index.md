# Face Recognition System

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 概要

Face Recognition Systemは、最新の顔認識技術を活用したWebベースの顔認証システムです。FastAPIバックエンドとVue.jsフロントエンドを組み合わせたモダンなアーキテクチャで構築されており、Dockerコンテナによる簡単なデプロイが可能です。

## 主な機能

- 🔐 **ユーザー認証**: JWTトークンベースの安全な認証システム
- 👤 **顔登録**: 複数の顔画像をユーザーごとに登録可能
- 🎯 **顔認識**: 高精度な顔検出と識別機能
- 🖼️ **リアルタイム処理**: Webカメラからのリアルタイム顔認識
- 📊 **管理画面**: 管理者向けのユーザーマネジメント機能
- 🐳 **Docker対応**: コンテナ化された簡単なデプロイ
- 🌐 **マルチGPU対応**: GPUアクセラレーションによる高速処理

## 技術スタック

### バックエンド
- **FastAPI**: 高速でモダンなPython Webフレームワーク
- **Milvus**: 大規模ベクトル検索のためのベクトルデータベース
- **PostgreSQL**: リレーショナルデータベース
- **Tortoise ORM**: 非同期ORM
- **face_recognition**: 顔認識ライブラリ
- **ONNX Runtime**: 高性能機械学習推論エンジン

### フロントエンド
- **Vue 3**
- **Vite**
- **face-api.js**
- **Axios**

### インフラストラクチャ
- **Docker**: コンテナ化
- **Docker Compose**: マルチコンテナオーケストレーション
- **Nginx**: リバースプロキシ

## クイックスタート

### 前提条件

- Docker 20.10+
- Docker Compose 1.29+
- Git

### インストール

```bash
# リポジトリのクローン
git clone https://github.com/lijunjie2232/faceapi.git
cd face_recognition_system

# 開発環境の起動
docker-compose -f docker-compose.dev.yml up -d

# アプリケーションへのアクセス
# フロントエンド: http://localhost:3000
# バックエンドAPI: http://localhost:8000
# APIドキュメント: http://localhost:8000/docs
```

## プロジェクト構造

```
face_recognition_system/
├── backend/           # FastAPIアプリケーション
├── frontend/          # Vue.jsフロントエンド
├── nginx/             # Nginx設定
├── docker-compose.*.yml  # Docker Compose設定
└── docs/              # ドキュメント
```

## 貢献

貢献を歓迎します！以下の手順に従ってください：

1. リポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルをご確認ください。

## サポート

質問や問題がある場合は、[Issues](https://github.com/lijunjie2232/faceapi/issues)ページで報告してください。