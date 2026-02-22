# FaceAPI
---

- [FaceAPI](#faceapi)
- [顔認識システム](#顔認識システム)
  - [特徴](#特徴)
  - [クイックスタート](#クイックスタート)
    - [前提条件](#前提条件)
    - [インストール](#インストール)
  - [Dockerデプロイメント](#dockerデプロイメント)
    - [イメージのビルド](#イメージのビルド)
    - [サービスの実行](#サービスの実行)
    - [環境変数](#環境変数)
    - [データ永続化](#データ永続化)
    - [トラブルシューティング](#トラブルシューティング)
    - [本番環境の考慮事項](#本番環境の考慮事項)
  - [開発環境のセットアップ](#開発環境のセットアップ)
  - [プロジェクト構造](#プロジェクト構造)
  - [APIドキュメント](#apiドキュメント)
  - [主なAPIエンドポイント](#主なapiエンドポイント)
    - [認証](#認証)
    - [顔認識](#顔認識)
    - [ユーザー管理](#ユーザー管理)
    - [管理者機能](#管理者機能)
  - [テクノロジースタック](#テクノロジースタック)
    - [バックエンド](#バックエンド)
    - [フロントエンド](#フロントエンド)
    - [インフラストラクチャ](#インフラストラクチャ)
  - [Dockerサポート](#dockerサポート)
  - [実機開発(おすすめ)](#実機開発おすすめ)
  - [モデル開発](#モデル開発)
  - [ライセンス](#ライセンス)

---

# 顔認識システム

FastAPIバックエンドとVue.jsフロントエンドを使用したモダンな顔認識システム。

## 特徴

- ディープラーニングを使用した顔検出と認識
- ユーザー管理システム
- JWT認証付きRESTful API
- リアルタイム顔処理
- ベクトルデータベース統合（Milvus）
- ONNX対応
- GPU対応（オプション）
- Dockerコンテナ化による簡単なデプロイ

## クイックスタート

### 前提条件

- DockerとDocker Compose
- Git
- （オプション）GPU対応環境（NVIDIA GPU + nvidia-docker）

### インストール

1. リポジトリをクローン:
```bash
git clone https://github.com/lijunjie2232/faceapi.git
cd faceapi
```

2. 環境設定ファイルを生成:
```bash
./deploy.sh generate-env dev
```

3. 全サービスを起動:
```bash
./deploy.sh dev
```

4. アプリケーションにアクセス(デフォールト):
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000

## Dockerデプロイメント

### イメージのビルド

バックエンド:
```bash
docker build -t face-rec-backend backend/
```

フロントエンド:
```bash
docker build -t face-rec-frontend frontend/
```

### サービスの実行

docker-composeですべてのサービスを起動:
```bash
# 開発環境
docker-compose -f docker-compose.dev.yml up -d

# 本番環境
docker-compose -f docker-compose.prod.yml up -d

# GPU対応開発環境
docker-compose -f docker-compose.dev.gpu.yml up -d

# GPU対応本番環境
docker-compose -f docker-compose.prod.gpu.yml up -d

# pre-build docker hub imageを使用
docker-compose -f docker-compose.yml up -d
```

ログの表示:
```bash
docker-compose -f xxx.yml logs [service_name]
```

サービスの停止:
```bash
deploy.sh stop dev
deploy.sh stop prod
```

### 環境変数

Dockerデプロイメント用の主要な環境変数:

```bash
# データベース
DATABASE_URL=sqlite:///./db.sqlite3

# Milvusベクトルデータベース
MILVUS_DB_HOST=milvus-standalone
MILVUS_DB_PORT=19530

# アプリケーション
PROJECT_NAME="Face Recognition System"
API_V1_STR="/api/v1"
DEBUG=False

# セキュリティ
JWT_SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### データ永続化

データ永続化のために以下のボリュームがマウントされています:
- SQLiteデータベース: `./volumes/postgres_data`
- Milvusデータ: `./volumes/milvus`

### トラブルシューティング

一般的な問題と解決策:

1. **ポートの競合**: docker-compose.dev.ymlでポートを変更
2. **権限の問題**: 適切なファイル権限を確認
3. **メモリの問題**: Dockerリソースを増加
4. **ビルドの失敗**: `docker system prune`でDockerキャッシュをクリア
5. **502 Bad Gateway**: リモートサーバーの問題か、nginxとfastapi/unicornのlogと設定を確認

### 本番環境の考慮事項

本番環境デプロイメントの場合:

1. 外部データベースを使用（PostgreSQL、MySQL）
2. 適切なSSL証明書を設定
3. 強力なシークレットキーを設定
4. レート制限を有効化
5. バックアップ戦略を設定
6. リソース使用量を監視
7. ログ集約を実装

## 開発環境のセットアップ

ローカル開発環境のセットアップについては、[QUICKSTART.md](QUICKSTART.md)を参照してください。

## プロジェクト構造

プロジェクト構造の詳細については、[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)を参照してください。

## APIドキュメント

バックエンド実行時に`/docs`で対話型APIドキュメントを利用できます。

## 主なAPIエンドポイント

### 認証
- `POST /api/v1/users/login`: ユーザー認証とJWTトークン生成
- `POST /api/v1/users/signup`: 新規ユーザー登録

### 顔認識
- `POST /api/v1/register-face`: 認証済みユーザーの顔を登録
- `POST /api/v1/recognize-face`: アップロード画像の顔を認識
- `GET /api/v1/user/faces`: 現在のユーザーの登録済み顔を取得
- `DELETE /api/v1/user/faces/{face_id}`: 登録済み顔を削除

### ユーザー管理
- `GET /api/v1/user/profile`: 現在のユーザープロファイル情報を取得
- `PUT /api/v1/user/profile`: 現在のユーザープロファイルを更新
- `DELETE /api/v1/user/account`: 現在のユーザーアカウントを削除

### 管理者機能
- `GET /api/v1/admin/users`: 全ユーザー一覧を取得（管理者のみ）
- `GET /api/v1/admin/users/{user_id}`: 特定ユーザーの詳細を取得（管理者のみ）
- `POST /api/v1/admin/users`: 管理者として新規ユーザーを作成（管理者のみ）
- `PUT /api/v1/admin/users/{user_id}`: ユーザー情報を更新（管理者のみ）
- `DELETE /api/v1/admin/users/{user_id}`: ユーザーアカウントを無効化（管理者のみ）
- `PATCH /api/v1/admin/users/{user_id}/activate`: 無効化されたユーザーを有効化（管理者のみ）
- `GET /api/v1/admin/stats`: システム統計とメトリクスを取得（管理者のみ）

## テクノロジースタック

### バックエンド
- **FastAPI**: モダンで高速なWebフレームワーク
- **Milvus**: 顔埋め込みの保存と検索のためのベクトルデータベース
- **Tortoise ORM**: PostgreSQLデータベース操作用の非同期ORM
- **face_recognition**: 顔検出と認識ライブラリ
- **Pydantic**: 型ヒントを使用したデータ検証と設定管理
- **ONNX Runtime**: 機械学習モデル用の高性能推論エンジン
- **StarNet**: 顔認識用のカスタムニューラルネットワーク

### フロントエンド
- **Vue 3**: Composition APIを使用したプログレッシブJavaScriptフレームワーク
- **Vite**: 高速なホットモジュール置換を備えた次世代フロントエンドツール
- **Face-api.js**: JavaScript顔検出と認識ライブラリ
- **Axios**: API通信用のPromiseベースHTTPクライアント
- **Element Plus**: Vue 3用のUIコンポーネントライブラリ

### インフラストラクチャ
- **Docker**: 一貫した開発とデプロイのためのコンテナ化
- **Docker Compose**: 開発と本番環境のマルチコンテナオーケストレーション
- **Nginx**: リバースプロキシとロードバランサー
- **Milvus**: 類似性検索操作のためのベクトルデータベース
- **MinIO**: 画像ファイル用のS3互換オブジェクトストレージ
- **etcd**: Milvusメタデータ用の分散キーバリューストア
- **PostgreSQL**: ユーザーアカウント管理用リレーショナルデータベース

## Dockerサポート

Dockerデプロイメントの詳細については、[DOCKER_SUPPORT.md](DOCKER_SUPPORT.md)を参照してください。

## 実機開発(おすすめ)

- バックエンド:
  - プロジェクトのインストール: `pip install -e ./backend/`
  - 環境設定ファイルの生成: `faceapi --gen-env .env`
  - 自身のマシンで開発用データベースを起動し、環境設定を変更してください
  - 開発サーバーの実行: `faceapi --debug`
- フロントエンド:
  - `cd frontend && pnpm i && pnpm serve`
  - ブラウザで http://localhost:3000 を開いてください


## モデル開発

- 新しい顔認識モデルを使用ため、onnxフォーマットに導出するのはすすめです。

- もしくは`.pt`を使う場合、先ずは依頼(torch/timm/...)をインストールすべきです。

- `faceapi.face_rec.register_model`を使って、モデルを登録する。

`backend/faceapi/face_rec/StarNet.py`を例にすれば：

```python
# StarNet.py - get_s1
@register_model("star_s1")
def get_s1(
    weight="model.pt",
    train=False,
    device="cpu",
):
    model = StarNet(
        base_dim=24,
        depths=[2, 2, 8, 3],
        num_features=512,
        fp16=True,
    )
    model = model.to(device)
    model.load_state_dict(torch.load(weight, map_location=device))
    return model.train() if train else model.eval()
```

そして、環境設定に、あたらしいモデルをせっていします：

```ini
MODEL_PATH=<path_to_model>
MODEL_LOADER=star_s1
MODEL_THRESHOLD=<threashold_of_model>
MODEL_DEVICE=cpu
MODEL_EMB_DIM=<dimension_of_output_embedding>
```

## ライセンス

MIT License