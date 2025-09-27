# TurboCode Kit MCP Server 使用指南

## 🚀 快速開始

### 1. 啟動 MCP Server

```bash
# Windows
.\start_mcp_server.bat

# 或手動啟動
python mcp_server.py
```

### 2. 驗證服務器運行

```bash
curl http://localhost:8000/
# 應該返回: {"message":"TurboCode Kit MCP Server","version":"1.0.0"}
```

### 3. 測試查詢功能

```bash
# 查詢列表查找優化
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"pattern":"list lookup"}'

# 查詢快取優化
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"pattern":"cache"}'
```

## 📊 API 端點

### GET `/`

- **描述**: 服務器狀態檢查
- **回應**: `{"message":"TurboCode Kit MCP Server","version":"1.0.0"}`

### GET `/patterns`

- **描述**: 列出所有可用的優化模式
- **回應**: `{"patterns": {...}}`

### POST `/query`

- **描述**: 查詢優化建議
- **請求體**:

  ```json
  {
    "pattern": "關鍵字或描述",
    "context": "可選的上下文信息",
    "language": "python"
  }
  ```

- **回應**:

  ```json
  {
    "matches": [...],
    "suggestions": [...],
    "confidence": 0.8
  }
  ```

## 🔍 支持的查詢關鍵字

- **列表操作**: `list`, `lookup`, `search`, `清單`, `查找`
- **快取**: `cache`, `memoization`, `快取`, `記憶`
- **迴圈**: `loop`, `for`, `iteration`, `循環`, `迴圈`
- **字串**: `string`, `concatenation`, `字串`, `串接`
- **集合**: `set`, `operations`, `集合`, `運算`
- **通用**: `optimization`, `performance`, `優化`, `效能`

## 🎯 VSCode Copilot 整合

1. **確保 VSCode 配置**:

   ```json
   {
     "github.copilot.chat.contextProviders": [
       {
         "type": "http",
         "url": "http://localhost:8000/query",
         "name": "TCK Optimization Assistant"
       }
     ]
   }
   ```

2. **在 Copilot Chat 中使用**:

   ```text
   @TCK 幫我優化這個列表查找代碼
   @TCK 如何改善這個迴圈的效能？
   ```

## 📈 效能數據

- **載入模式**: 128 個優化關鍵字索引
- **查詢速度**: O(1) 關鍵字匹配
- **支援語言**: Python
- **優化案例**: 17 個實證測試案例

## 🛑 停止服務器

```bash
# Windows: 在任務管理器中結束 Python 進程
# 或使用 PowerShell:
Stop-Process -Name python -Force
```

## 🔧 故障排除

### 端口衝突

```bash
# 檢查端口使用情況
netstat -ano | findstr :8000

# 殺掉佔用進程
Stop-Process -Id <PID> -Force
```

### 服務器啟動失敗

```bash
# 檢查依賴項
pip install -r requirements.txt

# 檢查 Python 版本 (需要 3.11+)
python --version
```

---

*TurboCode Kit MCP Server v1.0 - 讓 AI 助手成為您的效能優化專家！* 🚀
