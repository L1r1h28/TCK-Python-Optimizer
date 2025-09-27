# VSCode Copilot MCP 整合指南

## 🎯 將 TCK MCP Server 連接到 VSCode Copilot

### 步驟 1: 確保 MCP Server 運行

首先啟動 MCP Server：

```bash
# 在專案根目錄執行
.\start_mcp_server.bat
```

驗證服務器運行：
```bash
curl http://localhost:8000/
# 應該返回: {"message":"TurboCode Kit MCP Server","version":"1.0.0"}
```

### 步驟 2: 配置 VSCode 設定

#### 方法 A: 使用專案設定 (推薦)

1. **開啟專案設定**:
   - 在 VSCode 中開啟 TCK 專案
   - 按 `Ctrl+Shift+P` (或 `Cmd+Shift+P` on Mac)
   - 輸入 "Preferences: Open Workspace Settings (JSON)"

2. **添加 MCP 配置**:
   ```json
   {
     "github.copilot.chat.contextProviders": [
       {
         "type": "http",
         "url": "http://localhost:8000/query",
         "name": "TCK Optimization Assistant",
         "description": "TurboCode Kit Python 效能優化助手 - 提供 17 種實證優化模式",
         "timeout": 5000
       }
     ]
   }
   ```

#### 方法 B: 使用全域設定

1. **開啟使用者設定**:
   - 按 `Ctrl+Shift+P` (或 `Cmd+Shift+P` on Mac)
   - 輸入 "Preferences: Open User Settings (JSON)"

2. **添加相同配置**到您的全域設定

### 步驟 3: 重新載入 VSCode 視窗

- 按 `Ctrl+Shift+P` (或 `Cmd+Shift+P` on Mac)
- 輸入 "Developer: Reload Window"
- 或直接重啟 VSCode

### 步驟 4: 測試整合

1. **開啟 Copilot Chat**:
   - 按 `Ctrl+Alt+I` (或 `Cmd+Alt+I` on Mac)
   - 或點擊側邊欄的 Copilot 圖標

2. **測試查詢**:
   ```
   @TCK 幫我優化這個列表查找代碼
   ```

   或

   ```
   @TCK 如何改善迴圈效能？
   ```

3. **預期回應**:
   - Copilot 應該能夠訪問 TCK 的優化知識庫
   - 提供具體的 O(n) → O(1) 優化建議
   - 包含實測效能數據

## 🔧 故障排除

### 問題: "@TCK 命令無效"

**解決方案**:
1. 確保 MCP Server 正在運行 (`http://localhost:8000/`)
2. 檢查 VSCode 設定中的 URL 是否正確
3. 重新載入 VSCode 視窗
4. 確認 GitHub Copilot 擴充功能已安裝且啟用

### 問題: 查詢超時

**解決方案**:
1. 檢查網路連接
2. 確認 MCP Server 沒有崩潰
3. 增加 timeout 值 (預設 5000ms)

### 問題: 設定無效

**解決方案**:
1. 確保 JSON 格式正確 (無尾隨逗號)
2. 使用 "Preferences: Open Settings (JSON)" 而非 GUI
3. 檢查是否有語法錯誤 (紅色波浪線)

## 📊 支援的功能

一旦整合成功，Copilot 可以：

- ✅ **即時優化建議**: 輸入程式碼片段，獲取優化建議
- ✅ **效能分析**: 提供 O(n) 複雜度分析
- ✅ **實測數據**: 顯示實際效能提升倍數
- ✅ **程式碼範例**: 提供完整的優化實作
- ✅ **多語言支援**: 中英文查詢都支援

## 🎯 使用範例

### 範例 1: 列表查找優化
```
用戶: @TCK 這個代碼效能很慢，如何優化？
if item in my_list: ...

TCK: 建議使用 ListLookupOptimizer，將 O(n) 查找優化為 O(1)，
實測效能提升 32.5x - 325.8x
```

### 範例 2: 快取優化
```
用戶: @TCK 如何優化重複計算？

TCK: 使用 MemoizationCache，複雜度從 O(2^n) 降至 O(1)，
實測效能提升 2803.3x
```

## 🚀 進階配置

### 自訂超時時間
```json
{
  "github.copilot.chat.contextProviders": [
    {
      "type": "http",
      "url": "http://localhost:8000/query",
      "name": "TCK Optimization Assistant",
      "timeout": 10000  // 增加到 10 秒
    }
  ]
}
```

### 多個 MCP Server
```json
{
  "github.copilot.chat.contextProviders": [
    {
      "type": "http",
      "url": "http://localhost:8000/query",
      "name": "TCK Optimization Assistant"
    },
    {
      "type": "http",
      "url": "http://localhost:8001/other-server",
      "name": "Other Assistant"
    }
  ]
}
```

---

**恭喜！** 🎉 現在您的 VSCode Copilot 已經連接到 TurboCode Kit 優化知識庫了！

使用 `@TCK` 命令開始您的效能優化之旅吧！ 🚀