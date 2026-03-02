# 安裝指南

本指南將詳細說明Face Recognition System的安裝方法。

## 系統需求

### 最低需求
- **作業系統**: Ubuntu 20.04 LTS / CentOS 8 / macOS 10.15+ / Windows 10+
- **記憶體**: 8GB RAM (建議: 16GB以上)
- **儲存空間**: 20GB可用空間
- **CPU**: 4核心以上

### 建議需求
- **記憶體**: 16GB RAM以上
- **GPU**: NVIDIA GPU (支援CUDA，建議: RTX 3060以上)
- **儲存空間**: 50GB可用空間 (建議使用SSD)

## 必要軟體安裝

### 1. Docker安裝

#### Ubuntu/Debian
```bash
# 更新套件清單
sudo apt update

# 安裝依賴套件
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release

# 加入Docker官方GPG金鑰
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 設定repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安裝Docker Engine
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io

# 啟動並啟用Docker
sudo systemctl start docker
sudo systemctl enable docker

# 為非root使用者授予权限
sudo usermod -aG docker $USER
```

#### CentOS/RHEL
```bash
# 設定repository
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安裝Docker Engine
sudo yum install docker-ce docker-ce-cli containerd.io

# 啟動並啟用Docker
sudo systemctl start docker
sudo systemctl enable docker

# 為非root使用者授予权限
sudo usermod -aG docker $USER
```

#### macOS
```bash
# 使用Homebrew安裝Docker Desktop
brew install --cask docker
```

### 2. Docker Compose安裝

#### Linux/macOS
```bash
# 取得最新版本
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)

# 下載並安裝Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 授予執行權限
sudo chmod +x /usr/local/bin/docker-compose

# 確認版本
docker-compose --version
```

### 3. Git安裝

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
# Git通常已預先安裝
git --version
```

## 專案設定

### 1. 克隆程式碼庫

```bash
# 克隆程式碼庫
git clone https://github.com/lijunjie2232/faceapi.git
cd face_recognition_system

# 複製環境變數檔案
cp .env.dev.example .env
```

### 2. 環境變數設定

編輯`.env`檔案進行必要設定：

```bash
# 資料庫設定
POSTGRES_USER=faceuser
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=facedb

# JWT密鑰
JWT_SECRET_KEY=your_very_secret_key_here

# MinIO設定
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123

# Milvus設定
MILVUS_HOST=milvus-standalone
MILVUS_PORT=19530
```

### 3. GPU支援設定（可選）

若要使用GPU，需要以下步驟：

#### 安裝NVIDIA Docker
```bash
# 安裝NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install nvidia-docker2

# 重啟Docker
sudo systemctl restart docker
```

#### 使用GPU支援的Docker Compose檔案
```bash
# 啟動GPU支援的開發環境
docker-compose -f docker-compose.dev.gpu.yml up -d
```

## 首次啟動

### 啟動開發環境

```bash
# 建置並啟動開發環境
docker-compose -f docker-compose.dev.yml up -d --build

# 確認服務狀態
docker-compose -f docker-compose.dev.yml ps

# 查看日誌
docker-compose -f docker-compose.dev.yml logs -f
```

### 存取服務

啟動完成後，可以透過以下URL存取：

- **前端介面**: http://localhost:3000
- **後端API**: http://localhost:8000
- **API文件**: http://localhost:8000/docs
- **MinIO控制台**: http://localhost:9001
- **Milvus控制台**: http://localhost:9091

## 故障排除

### 常見問題與解決方法

#### 1. Docker權限錯誤
```bash
# 將使用者加入docker群組
sudo usermod -aG docker $USER

# 重新登入或執行以下指令
newgrp docker
```

#### 2. 埠號被佔用
```bash
# 確認使用中的埠號
sudo netstat -tlnp | grep :8000

# 若要使用其他埠號，請編輯docker-compose.yml
```

#### 3. 記憶體不足錯誤
```bash
# 調整Docker資源限制
# Docker Desktop: Preferences → Resources
# Linux: 在/etc/docker/daemon.json設定資源限制
```

#### 4. GPU無法識別
```bash
# 確認NVIDIA驅動程式
nvidia-smi

# 確認nvidia-docker2安裝
docker info | grep -i nvidia
```

### 取得支援

若問題無法解決，請建立Issue時提供以下資訊：

1. 作業系統版本和Docker版本
2. 錯誤訊息
3. 使用的docker-compose檔案
4. 環境變數設定（不含密碼等敏感資訊）

```bash
# 收集系統資訊
uname -a
docker --version
docker-compose --version
```