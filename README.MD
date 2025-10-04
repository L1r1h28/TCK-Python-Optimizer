[📖 English Version](README_EN.md) | [繁體中文版](README.MD)

---

## 📋 專案概述

TurboC### 階段二：藍圖自動生成與歸檔

系統接收到最新的測試報告後，將自動完成以下步驟：

1. **數據驗證**: 解析 `test_reports/` 中最新的 JSON 報告，提取效能數據，計算加速倍數並生成評分。
2. **模式識別**: 辨識常見的效能反模式，並定義安全的應用條件與風險。
3. **文件生成**: 根據報告數據，在 `optimization_blueprints/` 目錄下建立或更新標準化的藍圖檔案，內容包含：
    * 優化前的瓶頸（O(n) 程式碼結構）
    * 採用的優化策略（O(1) 或攤提 O(1) 的設計）
    * 效能結果摘要（加速倍率、資源變化、評分）
    * 適用場景與風險提示
4. **索引更新**: 將新藍圖更新至 `README_TCK_INDEX.md`，並標記其建議複雜度與優先級。
5. **歸檔**: 僅在達到品質門檻（如預設評分和加速倍率）時，才將藍圖歸檔並標記為「已驗證」。 是一個專門為 Python 開發者設計的高效能程式碼優化工具箱，通過 **17 個實測優化模式** 和 **AI 驅動的效能分析**，幫助您將最常見的效能瓶頸從線性複雜度優化為常數複雜度。

### 🎯 核心價值

* **⚡ 實測效能數據** - 所有優化都基於實際測試結果，而非理論估計
* **🤖 AI 協作就緒** - 完整的優化範本庫，與 GitHub Copilot 完美配合
* **📊 完整資源監控** - CPU、記憶體、I/O 統計和自動化效能評分
* **🔧 即用型工具** - 提供優化函數庫和一鍵測試工具

---

## 🛠️ TCK Enhanced Analyzer - 您的主要工具

### 🚀 快速開始

#### 1. 查看所有可用測試案例

```bash
python tck_enhanced_analyzer.py --list
```

#### 2. 執行效能測試

```bash
# 測試最高效的優化模式
python tck_enhanced_analyzer.py --test MEMOIZATION_CACHE         # 2803.3x 加速
python tck_enhanced_analyzer.py --test LOOP_LOOKUP_OPTIMIZATION # 221.0x 加速
python tck_enhanced_analyzer.py --test CONFIG_LOAD              # 28.1x 加速

# 測試其他高效模式
python tck_enhanced_analyzer.py --test SET_OPERATIONS           # 37.7x 加速
python tck_enhanced_analyzer.py --test STRING_CONCATENATION     # 7.0x 加速
```

---

## 📁 專案結構

```bash
TurboCode Kit (TCK)/
├── tck_core/
│   ├── test_cases.py
│   └── ... (核心分析引擎)
├── cases/
│   ├── case_001_...
│   └── ... (21個獨立案例)
├── optimization_blueprints/
│   ├── README.md
│   ├── README_TCK_INDEX.md
│   └── ... (21個藍圖)
├── tck_enhanced_analyzer.py
├── tck_main.py
└── README.md
```

| 檔案/目錄 | 🎯 說明 |
| :--- | :--- |
| `tck_main.py` | 主控制器 (完整分析流程) |
| `tck_enhanced_analyzer.py` | 主要測試工具 (動態載入案例) |
| `tck_core/` | 核心分析引擎與共用工具 |
| `cases/` | 存放所有獨立的效能測試案例檔案 |
| `optimization_blueprints/` | AI 協作藍圖與自動化流程說明 |

---

## ⚙️ 自動化優化閉環流程

此流程分為「準備階段」與「系統自動執行階段」，以確保優化工作的品質與可追溯性。

### 階段一：準備與數據收集

1. **建立或修改案例**: 在 `cases/` 目錄下建立或修改 `case_XXX_descriptive_name.py` 檔案。
2. **實作程式碼**: 在檔案中實作 `unoptimized_version` 和多個 `optimized_version_*` 函式。
3. **執行分析**: 使用 `TCK Enhanced Analyzer` 執行測試，並輸出包含時間、記憶體、環境等元數據的結構化報告。

    ```bash
    # 使用 --test 參數指定案例名稱
    python tck_enhanced_analyzer.py --test YOUR_CASE_NAME
    ```

### 階段二：藍圖自動生成與歸檔

系統接收到測試報告後，將自動完成以下步驟：

1. **數據驗證**: 解析報告，提取效能數據，計算加速倍數並生成評分。
2. **模式識別**: 辨識常見的效能反模式，並定義安全的應用條件與風險。
3. **文件生成**: 建立標準化的藍圖檔案，內容包含：
    * 優化前的瓶頸（O(n) 程式碼結構）
    * 採用的優化策略（O(1) 或攤提 O(1) 的設計）
    * 效能結果摘要（加速倍率、資源變化、評分）
    * 適用場景與風險提示
4. **索引更新**: 將新藍圖更新至 `README_TCK_INDEX.md`，並標記其建議複雜度與優先級。
5. **歸檔**: 僅在達到品質門檻（如預設評分和加速倍率）時，才將藍圖歸檔並標記為「已驗證」。

---

## 🤖 AI 協作指令 (Copilot Automation Prompt)

此區塊為指導 AI 執行 TCK 優化週期的核心指令。

### 1. 任務啟動：鎖定優化目標

* **角色**: 分析師。
* **指令**:

  1. 載入並分析 `README_TCK_INDEX.md`。
  2. 自動挑選一個「理論上可大幅強化」的案例（例如，複雜度為 O(N) 或更高，且存在 O(1) 替代方案）。
  3. 以 `Optimization Case: [函式名稱] in [檔案路徑]` 格式回報目標。
  4. 若無法存取索引，預設選擇 `tck_enhanced_analyzer.py` 中的慢速查找模式。

### 2. 步驟一：分析與優化

* **指令**:

  1. **深入分析**: 詳細說明目標案例的 O(N) 瓶頸，特別是重複計算或內部迴圈導致的隱性複雜度。
  2. **外部研究**: 使用 MCP/DeepWiki 搜尋 O(1) 替代方案，例如 `Set/Dict` 或 `@lru_cache`。
  3. **實作優化**: 根據研究結果，將目標函式的時間複雜度強制轉換為 O(1) 或攤提 O(1)，並僅在 `tck_enhanced_analyzer.py` 或 `test_cases.py` 中修改。

### 3. 步驟二：測試與驗證

* **指令**:

  1. **設計測試**: 在對應的 `case_XXX` 檔案中建立或修改測試案例，使用大規模數據（N > 10^5）以驗證效能提升。
  2. **結果驗證**: 證明優化前後存在「數量級」的效能差異。
  3. **清理**: 任務完成後，立即刪除所有臨時檔案。

### 4. 步驟三：歸檔與報告

* **指令**:

  1. **生成報告**: 使用 Markdown 格式展示「優化前範本」、「優化後範本」與「效能提升總結」。
  2. **更新藍圖**: 更新 `optimization_blueprints` 中的對應藍圖範本。
  3. **更新索引**: 在 `README_TCK_INDEX.md` 中更新目標案例的評分與優先級。

---

## 🎯 設計理念

### 為什麼需要多個版本的實現？

TCK 專案包含多個版本的相同優化實現，是為了滿足不同學習階段和使用場景的需求：

#### 📚 學習版本 (Blueprints)

* 詳細的理論解釋和逐步推導
* 包含失敗案例和教訓總結
* 適合深入理解優化原理

#### 🧪 測試版本 (Test Cases)

* 專注於效能驗證和基準測試
* 大規模數據測試，確保優化效果
* 適合驗證優化在實際場景中的表現

#### 🔧 生產版本 (Turbo Utils)

* 簡潔高效的生產就緒代碼
* 最小化依賴，最大化相容性
* 適合直接集成到生產環境

---

## 🔧 測試環境

所有藍圖的效能數據均基於以下環境的 `TCK Enhanced Analyzer` 實際測試：

* **硬體**: Intel i5-11400F + RTX 2060 Super + 32GB RAM
* **系統**: Windows 11
* **軟體**: Python 3.11.9
* **方法**: 每個案例執行 1000+ 次以進行統計分析。

---

## 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

### 開發環境設置

```bash
git clone [repository-url]
cd "TurboCode Kit (TCK)"
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 測試新優化模式

```bash
# 在 cases/ 目錄下建立新的 case_XXX.py 檔案
# 運行你的新案例
python tck_enhanced_analyzer.py --test YOUR_CASE_NAME
```

---

## 📄 授權

本專案採用 **MIT 授權條款** - 詳見 **[LICENSE 文件](LICENSE.md)**

---

## 📞 聯絡方式

* **專案維護者**: **L1r1h28**
* **問題回報** (Bug/建議)：[GitHub Issues](https://github.com/L1r1h28/TCK-Python-Optimizer/issues)
* **功能請求/廣泛討論**：[GitHub Discussions](https://github.com/L1r1h28/TCK-Python-Optimizer/discussions)

---

最後更新: 2025年10月5日 | TCK Enhanced Analyzer v3.1
