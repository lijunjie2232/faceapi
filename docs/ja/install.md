# インストールガイド

このガイドでは、Face Recognition Systemのインストール方法について詳しく説明します。

## システム要件

### 最低要件
- **OS**: Ubuntu 20.04 LTS / CentOS 8 / macOS 10.15+ / Windows 10+
- **メモリ**: 8GB RAM (推奨: 16GB以上)
- **ストレージ**: 20GB空き容量
- **CPU**: 4コア以上

### 推奨要件
- **メモリ**: 16GB RAM以上
- **GPU**: NVIDIA GPU (CUDA対応、推奨: RTX 3060以上)
- **ストレージ**: 50GB空き容量 (SSD推奨)

## 必要ソフトウェアのインストール

### 1. Dockerのインストール

#### Ubuntu/Debian
```bash
# パッケージリストの更新
sudo apt update

# 依存パッケージのインストール
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release

# Docker公式GPGキーの追加
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# リポジトリの設定
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker Engineのインストール
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

# Dockerの起動と有効化
sudo systemctl start docker
sudo systemctl enable docker

# 非rootユーザーの権限付与
sudo usermod -aG docker $USER
```

#### CentOS/RHEL
```bash
# リポジトリの設定
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Docker Engineのインストール
sudo yum install docker-ce docker-ce-cli containerd.io

# Dockerの起動と有効化
sudo systemctl start docker
sudo systemctl enable docker

# 非rootユーザーの権限付与
sudo usermod -aG docker $USER
```

#### macOS
```bash
# Homebrewを使用してDocker Desktopをインストール
brew install --cask docker
```

### 2. Docker Composeのインストール

#### Linux/macOS
```bash
# 最新バージョンの取得
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)

# Docker Composeのダウンロードとインストール
sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 実行権限の付与
sudo chmod +x /usr/local/bin/docker-compose

# バージョン確認
docker-compose --version
```

### 3. Gitのインストール

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
# Gitは通常事前にインストールされています
git --version
```

## プロジェクトのセットアップ

### 1. リポジトリのクローン

```bash
# リポジトリのクローン
git clone https://github.com/lijunjie2232/faceapi.git
cd face_recognition_system

# 環境変数ファイルのコピー
cp .env.dev.example .env
```

### 2. 環境変数の設定

`.env`ファイルを編集して必要な設定を行います：

```bash
# データベース設定
POSTGRES_USER=faceuser
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=facedb

# JWTシークレットキー
JWT_SECRET_KEY=your_very_secret_key_here

# MinIO設定
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123

# Milvus設定
MILVUS_HOST=milvus-standalone
MILVUS_PORT=19530
```

### 3. GPUサポートの設定（任意）

GPUを使用する場合、以下の手順が必要です：

#### NVIDIA Dockerのインストール
```bash
# NVIDIA Container Toolkitのインストール
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install nvidia-docker2

# Dockerの再起動
sudo systemctl restart docker
```

#### GPU対応のDocker Composeファイルの使用
```bash
# GPU対応の開発環境を起動
docker-compose -f docker-compose.dev.gpu.yml up -d
```

## 初回起動

### 開発環境の起動

```bash
# 開発環境のビルドと起動
docker-compose -f docker-compose.dev.yml up -d --build

# サービスの状態確認
docker-compose -f docker-compose.dev.yml ps

# ログの確認
docker-compose -f docker-compose.dev.yml logs -f
```

### サービスへのアクセス

起動が完了したら、以下のURLにアクセスできます：

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs
- **MinIOコンソール**: http://localhost:9001
- **Milvusコンソール**: http://localhost:9091

## トラブルシューティング

### よくある問題と解決方法

#### 1. Dockerの権限エラー
```bash
# ユーザーをdockerグループに追加
sudo usermod -aG docker $USER

# 再ログインまたは以下のコマンドを実行
newgrp docker
```

#### 2. ポートが使用中の場合
```bash
# 使用中のポートを確認
sudo netstat -tlnp | grep :8000

# 別のポートを使用する場合、docker-compose.ymlを編集
```

#### 3. メモリ不足エラー
```bash
# Dockerのリソース制限を調整
# Docker Desktop: Preferences → Resources
# Linux: /etc/docker/daemon.jsonでリソース制限を設定
```

#### 4. GPUが認識されない場合
```bash
# NVIDIAドライバの確認
nvidia-smi

# nvidia-docker2のインストール確認
docker info | grep -i nvidia
```

### サポートの取得

問題が解決しない場合は、以下の情報を添えてIssueを作成してください：

1. OSバージョンとDockerバージョン
2. エラーメッセージ
3. 使用しているdocker-composeファイル
4. 環境変数の設定（パスワード等を除く）

```bash
# システム情報の収集
uname -a
docker --version
docker-compose --version
```