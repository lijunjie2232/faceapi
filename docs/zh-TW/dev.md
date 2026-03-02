# 開發環境設定

本指南說明如何建置Face Recognition System的開發環境以及在本機執行的方法。

## 開發環境概覽

開發環境由以下容器組成：

- **frontend**: 基於Vue.js 3的前端應用程式
- **backend**: 基於FastAPI的後端API伺服器
- **postgres**: 儲存使用者資料的PostgreSQL資料庫
- **milvus-standalone**: 儲存臉部特徵向量的向量資料庫
- **minio**: 儲存臉部圖片的物件儲存
- **etcd**: Milvus的元資料管理
- **nginx**: 反向代理與靜態檔案配送

## 本機開發環境啟動

### 1. 啟動開發環境

```bash
# 啟動開發環境
docker-compose -f docker-compose.dev.yml up -d

# 確認服務狀態
docker-compose -f docker-compose.dev.yml ps

# 查看日誌
docker-compose -f docker-compose.dev.yml logs -f
```

### 2. GPU支援開發環境（可選）

若要使用GPU：

```bash
# 啟動GPU支援環境
docker-compose -f docker-compose.dev.gpu.yml up -d
```

## 存取各項服務

啟動後，可透過以下URL存取各項服務：

| 服務 | URL | 說明 |
|------|-----|------|
| 前端介面 | http://localhost:3000 | Vue.js應用程式 |
| 後端API | http://localhost:8000 | FastAPI伺服器 |
| API文件 | http://localhost:8000/docs | Swagger UI |
| MinIO控制台 | http://localhost:9001 | 物件儲存管理 |
| Milvus控制台 | http://localhost:9091 | 向量資料庫管理 |

## 後端開發

### 1. 後端程式碼熱重載

開發期間程式碼變更時會自動重新啟動：

```bash
# 監控後端日誌
docker-compose -f docker-compose.dev.yml logs -f backend
```

### 2. 資料庫遷移

```bash
# 初始化資料庫
docker-compose -f docker-compose.dev.yml exec backend python -m faceapi.db.init_sql

# 建立管理員帳號
docker-compose -f docker-compose.dev.yml exec backend python -m faceapi.db.init_account
```

### 3. API測試

```bash
# 存取API文件
open http://localhost:8000/docs

# 使用curl測試API範例
curl -X POST http://localhost:8000/api/v1/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

## 前端開發

### 1. 前端熱重載

Vue.js開發伺服器支援熱重載：

```bash
# 監控前端日誌
docker-compose -f docker-compose.dev.yml logs -f frontend
```

### 2. 新增依賴套件

```bash
# 安裝新的npm套件
docker-compose -f docker-compose.dev.yml exec frontend pnpm add package-name

# 安裝開發用套件
docker-compose -f docker-compose.dev.yml exec frontend pnpm add -D package-name
```

### 3. 測試建置

```bash
# 測試生產環境建置
docker-compose -f docker-compose.dev.yml exec frontend pnpm build
```

## 資料庫操作

### 1. 連線至PostgreSQL

```bash
# 連線至PostgreSQL容器
docker-compose -f docker-compose.dev.yml exec postgres psql -U faceuser -d facedb

# 實用的SQL指令
\dt                    # 顯示資料表清單
\d table_name          # 顯示資料表結構
SELECT * FROM users;   # 顯示使用者資料表內容
```

### 2. 連線至Milvus

```bash
# 存取Milvus控制台
open http://localhost:9091

# 從Python連線至Milvus
docker-compose -f docker-compose.dev.yml exec backend python
```

```python
from pymilvus import connections, Collection

# 連線
connections.connect(host='milvus-standalone', port='19530')

# 資料表清單
collections = connections.list_collections()
print(collections)
```

## 測試

### 1. 執行單元測試

```bash
# 執行後端測試
docker-compose -f docker-compose.dev.yml exec backend pytest

# 執行特定測試檔案
docker-compose -f docker-compose.dev.yml exec backend pytest tests/test_users.py

# 產生覆蓋率報告
docker-compose -f docker-compose.dev.yml exec backend pytest --cov=faceapi --cov-report=html
```

### 2. E2E測試

```bash
# 執行Cypress測試
docker-compose -f docker-compose.dev.yml exec frontend pnpm test:e2e
```

## 除錯

### 1. 查看日誌

```bash
# 所有服務的日誌
docker-compose -f docker-compose.dev.yml logs

# 特定服務的日誌
docker-compose -f docker-compose.dev.yml logs backend
docker-compose -f docker-compose.dev.yml logs frontend

# 即時監控日誌
docker-compose -f docker-compose.dev.yml logs -f
```

### 2. 容器內操作

```bash
# 存取後端容器
docker-compose -f docker-compose.dev.yml exec backend bash

# 存取前端容器
docker-compose -f docker-compose.dev.yml exec frontend sh

# 存取資料庫容器
docker-compose -f docker-compose.dev.yml exec postgres bash
```

### 3. 以除錯模式啟動

```bash
# 以除錯模式啟動後端
docker-compose -f docker-compose.dev.yml stop backend
docker-compose -f docker-compose.dev.yml run --service-ports backend uvicorn faceapi.main:app --host 0.0.0.0 --port 8000 --reload
```

## 環境變數

### 開發環境的主要環境變數

```bash
# .env檔案範例
DEBUG=True
LOG_LEVEL=DEBUG

# 資料庫
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

## 開發工作流程

### 1. 新功能開發步驟

```bash
# 1. 建立新分支
git checkout -b feature/new-feature

# 2. 程式碼變更

# 3. 執行測試
docker-compose -f docker-compose.dev.yml exec backend pytest

# 4. 提交
git add .
git commit -m "Add new feature"

# 5. 推送
git push origin feature/new-feature
```

### 2. 程式碼品質檢查

```bash
# 後端程式碼格式化
docker-compose -f docker-compose.dev.yml exec backend black .

# 前端程式碼格式化
docker-compose -f docker-compose.dev.yml exec frontend pnpm format

# 程式碼檢查
docker-compose -f docker-compose.dev.yml exec backend flake8 .
docker-compose -f docker-compose.dev.yml exec frontend pnpm lint
```

## 故障排除

### 常見問題與解決方法

#### 1. 容器無法啟動
```bash
# 確認容器狀態
docker-compose -f docker-compose.dev.yml ps

# 查看容器日誌
docker-compose -f docker-compose.dev.yml logs service_name

# 重新建置容器
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d --build
```

#### 2. 資料庫連線錯誤
```bash
# 重新啟動資料庫服務
docker-compose -f docker-compose.dev.yml restart postgres

# 重新執行資料庫初始化
docker-compose -f docker-compose.dev.yml exec backend python -m faceapi.db.init_sql
```

#### 3. 記憶體不足
```bash
# 確認Docker資源限制
docker info | grep -i memory

# 刪除不需要的容器與映像檔
docker system prune -a
```

#### 4. 埠號衝突
```bash
# 確認使用中的埠號
sudo lsof -i :8000
sudo lsof -i :3000

# 修改docker-compose.yml的埠號
```

### 重置開發環境

```bash
# 完全清理開發環境
./scripts/clean-dev-env.sh

# 或手動執行
docker-compose -f docker-compose.dev.yml down -v
docker volume ls | grep face
docker volume rm [volume_names]
```

開發環境設定完成！