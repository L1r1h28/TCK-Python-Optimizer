# 🚀 優化藍圖目錄

## 📝 使用說明

1. **快速開始**: 閱讀 `BLUEPRINT_SUMMARY.md` 了解所有優化方案
2. **選擇藍圖**: 優先採用 A/B+ 級高效方案
3. **避免陷阱**: 注意 C-/D 級方案的使用限制

## 🎯 評分系統

- **A/B+ 級**: ✅ 推薦使用，效果顯著
- **B/C 級**: ⚠️ 需注意使用場景  
- **C-/D 級**: ❌ 不建議使用，可能降低效能

## 📊 測試環境

所有數據基於 TCK Enhanced Analyzer 實際測試：

- **硬體**: Intel i5-11400F + 32GB RAM
- **方法**: 統計分析，0-100分評分
- **次數**: 每個案例執行 1000+ 次

## 🔗 重要檔案

- `BLUEPRINT_SUMMARY.md`: 📌 **最重要** - 優化方案總覽
- 其他 `.md` 檔案: 具體優化實作指南

---

**建議**: 優先參考 BLUEPRINT_SUMMARY.md 獲取最佳優化策略

---
## 🚀 TCK 專案：O($N$) 核心瓶頸優化循環提示詞

這個提示詞將指導 Copilot 執行一個**完整的「分析-優化-驗證-歸檔」閉環**，並嚴格遵循您的檔案和流程要求。

### 🎯 任務啟動與案例鎖定

> **\[START TCK OPTIMIZATION CYCLE]**
>
> **Optimization Target (Instruction for Copilot):**
>
> 1.  **分析師角色：** 假設已載入 `optimization_blueprints\README_TCK_INDEX.md` 的內容。請**自動挑選**其中一個 **「理論上分數可以再大幅度強化」** 的實用工具函式（例如：頻率高、Big O 複雜度為 $O(N)$ 或更高，且已知有 $O(1)$ 替代方案的模式）。
> 2.  **指令指定案例 (Case Specification):** 請將選定的目標函式和其所在檔案，以以下格式回報給我：
>     ```markdown
>     Optimization Case: [選定函式名稱] in [tck_enhanced_analyzer.py/test_cases.py]
>     ```
>     *（**備註：** 如果您無法存取 Index，請預設選擇 `tck_enhanced_analyzer.py` 中 **`_identify_bottlenecks`** 函式內的 **`list.index()`** 慢速查找。）*

### 🔍 步驟一：深入瓶頸研究與實作優化

> **Task 1: Deep Bottleneck Analysis & Optimization**
>
> 1.  **深入研究真正效能瓶頸：** 詳細說明選定案例中，導致分數較差的 **$O(N)$ 程式碼結構**。特別要指出**重複計算**或**內部迴圈**導致的 $O(N^2)$ 或更高的隱性複雜度。
> 2.  **探索最佳實踐（外部資源搜尋）：**
>       * **精確 MCP/DeepWiki 提示：** `**搜尋 DeepWiki/Microsoft 關於 [選定函式] 替代方案的效能文檔，專注於如何使用 O(1) 資料結構（如 Set/Dict）或攤提 O(1) 技術（如 @lru_cache）來提升該工具的效能。**`
> 3.  **實作優化：**
>       * 根據搜尋到的最佳實踐，重寫並優化該函式。
>       * **強制 Big O 轉換：** 優化後的實作必須將時間複雜度從 $O(N)$ 或更高，**轉化為 $O(1)$ 或攤提 $O(1)$。**
> 4.  **檔案限定：** **所有程式碼變更，僅限於 `tck_enhanced_analyzer.py` 或 `test_cases.py`。**

### 🧪 步驟二：重設計測試案例與結果驗證

> **Task 2: Test Case Redesign & Re-run Verification**
>
> 1.  **重新設計測試案例：** 在 **`test_cases.py`** 中建立或修改一個測試函式，以**重跑測試**驗證優化。
>       * **規模化數據：** 測試案例必須使用足以體現 $O(N)$ 和 $O(1)$ 差異的**大規模輸入**（例如 $N=10^5$）。
>       * **目標：** 測量優化前後的執行時間，結果必須證明性能有**數量級的提升**。
> 2.  **檔案限定與清潔：** 嚴格遵守：**僅使用 `tck_enhanced_analyzer.py` 和 `test_cases.py` 進行操作。除非有特殊要求需要臨時檔案 (`.tmp`)，用完後必須立即從工作空間刪除。**

### 📜 步驟三：藍圖與索引更新（結果歸檔）

> **Task 3: Blueprint & Index Update (Final Output)**
>
> 1.  **生成報告：** 使用 Markdown 格式清晰展示以下三個區塊：
>       * **【優化前 $O(N)$ 程式碼範本】**
>       * **【優化後 $O(1)$ 程式碼範本】**
>       * **【重跑測試案例結果與效能提升總結】**
> 2.  **更新藍圖 (Blueprint Update)：**
>       * 根據這次優化，更新 `optimization_blueprints` 資料庫中的 $O(1)$ **替換範本**（例如：`O1_Lookup_via_Set_Conversion`），該範本應可直接用於 Copilot 的自動替換。
> 3.  **更新索引 (Index Update)：**
>       * 更新 `optimization_blueprints\README_TCK_INDEX.md` 內**選定案例**的記錄：更新**建議複雜度**和**優先級**。
>
> **Task Status:** **Commence Work. Final output must be comprehensive and follow all formatting rules.**
>
> **\[END TCK OPTIMIZATION CYCLE]**