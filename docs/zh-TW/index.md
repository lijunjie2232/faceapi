# 臉部辨識系統

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.x-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 概述

臉部辨識系統是一個基於現代臉部辨識技術的網頁版臉部驗證系統。採用FastAPI後端與Vue.js前端結合的現代化架構建構，支援透過Docker容器進行簡易部署。

## 主要功能

- 🔐 **使用者認證**: 基於JWT令牌的安全認證系統
- 👤 **臉部註冊**: 可為每位使用者註冊多張臉部圖片
- 🎯 **臉部辨識**: 高精準度的臉部檢測與識別功能
- 🖼️ **即時處理**: 支援網路攝影機即時臉部辨識
- 📊 **管理介面**: 提供管理者使用的使用者管理功能
- 🐳 **Docker支援**: 容器化的簡易部署方案
- 🌐 **多GPU支援**: 透過GPU加速實現高速處理

## 技術堆疊

### 後端
- **FastAPI**: 快速且現代化的Python網頁框架
- **Milvus**: 用於大規模向量搜尋的向量資料庫
- **PostgreSQL**: 關聯式資料庫
- **Tortoise ORM**: 非同步ORM
- **face_recognition**: 臉部辨識函式庫
- **ONNX Runtime**: 高效能機器學習推論引擎

### 前端
- **Vue 3**
- **Vite**
- **face-api.js**
- **Axios**

### 基礎設施
- **Docker**: 容器化
- **Docker Compose**: 多容器編排
- **Nginx**: 反向代理

## 快速開始

### 系統需求

- Docker 20.10+
- Docker Compose 1.29+
- Git

### 安裝步驟

```bash
# 克隆程式碼庫
git clone https://github.com/lijunjie2232/faceapi.git
cd face_recognition_system

# 啟動開發環境
docker-compose -f docker-compose.dev.yml up -d

# 存取應用程式
# 前端介面: http://localhost:3000
# 後端API: http://localhost:8000
# API文件: http://localhost:8000/docs
```

## 專案結構

```
face_recognition_system/
├── backend/           # FastAPI應用程式
├── frontend/          # Vue.js前端
├── nginx/             # Nginx設定
├── docker-compose.*.yml  # Docker Compose設定
└── docs/              # 文件
```

## 貢獻

歡迎貢獻！請依照以下步驟：

1. 分叉(Fork)程式碼庫
2. 建立新的分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 建立拉取請求(Pull Request)

## 授權

本專案採用MIT授權條款發布。詳情請參閱[LICENSE](LICENSE)檔案。

## 支援

如有任何疑問或問題，請在[Issues](https://github.com/lijunjie2232/faceapi/issues)頁面回報。