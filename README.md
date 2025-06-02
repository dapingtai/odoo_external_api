# Odoo 外部 API 服務

此專案實現了 Odoo v18 的外部 API 服務，提供標準化的 REST API 端點以及 OAuth 認證支援。

## 技術架構

### 使用技術
- **程式語言**: Python
- **Web 框架**: FastAPI
- **整合**: Odoo v18 XML-RPC
- **認證**: OAuth Provider
- **容器化**: Docker 和 Docker Compose
- **CI/CD**: GitLab CI/CD pipeline
- **日誌**: GELF 驅動

### 專案結構
```
app/
├── application/        # 應用服務層
│   ├── bind_table.py      # 資料表綁定
│   ├── department.py      # 部門管理
│   ├── employee.py        # 員工管理
│   └── main.py           # 基礎服務類
├── core/              # 核心邏輯
├── domain/            # 領域模型
│   └── v18/          # v18 版本相關實作
├── infra/            # 基礎設施
└── interface/        # API 介面
    └── api/
        ├── oauth_provider.py  # OAuth 認證提供者
        └── v18/          # 版本 18 API 實現
            ├── main.py           # 主要 API 路由
            ├── advance.py        # 進階操作
            └── xml_rpc_execute.py # XML-RPC 執行器
```

## 安裝指南

### 環境要求
- Python 3.x
- Docker
- Docker Compose

### 環境變數設定
```bash
MODE=dev        # 執行模式：dev 或 prod
APP_TAG=latest  # 容器標籤
BASE_URL=/      # API 基礎 URL
```

### 安裝步驟

1. **使用 Docker Compose 部署**:
   ```bash
   docker-compose up -d
   ```
   - 服務將在 port 8081 啟動
   - 使用 GELF 日誌驅動收集日誌

2. **本地開發環境設定**:
   ```bash
   # 建立虛擬環境
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # 安裝依賴
   pip install -r requirements.txt
   
   # 啟動應用
   python run.py --dev
   ```

## 核心功能與使用說明

### 主要功能

## 支援版本
- Odoo v18

1. **測試 端點**
   * **服務狀態檢查**:
     ```http
     GET /api/v18/
     ```
     回傳: `{"message": "Service is running"}`

   * **登入認證**:
     ```http
     POST /api/v18/login
     Content-Type: application/json
     
     {
         "url": "your-odoo-url",
         "db": "database-name",
         "username": "user",
         "password": "password"
     }
     ```
     回傳: `{"message": "Login successful", "version": "版本號", "uid": "使用者ID"}`

2. **Odoo 整合 API**
   - XML-RPC 與 Odoo 通訊
   - 標準化 REST API 端點 
   - 安全認證機制

3. **進階功能**
   - 部門管理 API
   - 員工資料處理
   - 資料表綁定操作

4. ** 中繼層 **
   - OAuth 認證 (處理 odoo web 沒有的 SSO_CLIENT_SECRET )

### BaseService 類別
```python
class BaseService:
    def __init__(self, url, db, uid, password, api_version: str = 'v18'):
        self.url = url
        self.db = db
        self.uid = uid
        self.password = password
        self.api_version = api_version
```
- 提供基礎服務類別
- 支援多版本 API
- 統一的認證管理

### 系統特性
1. **安全性**
   - OAuth 認證機制
   - 安全的密碼處理
   - API 存取控制

2. **可維護性**
   - 模組化設計
   - 版本控制支援
   - 完整的錯誤處理

3. **擴展性**
   - 支援多版本 API
   - 模組化的服務層
   - 彈性的配置系統

### 錯誤處理
- 標準 HTTP 狀態碼
- 詳細的錯誤訊息
- 系統日誌整合

如需更多技術支援或文件說明，請聯絡開發團隊。