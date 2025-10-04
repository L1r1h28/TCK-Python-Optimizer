#!/usr/bin/env python3
"""
TCK 優化報告生成器 (固定版本)
============================

專注於通用程式模式分析，生成頻率排序的優化清單。

Author: TurboCode Kit (TCK)
Version: 2.0
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class OptimizationReportGenerator:
    """優化報告生成器"""
    
    def __init__(self, output_dir: str = "../tck_core/analysis_results"):
        """初始化報告生成器"""
        self.output_dir = Path(output_dir)
        self.frequency_data = None
        self.complexity_data = None
        
    def load_analysis_data(self) -> bool:
        """載入分析數據"""
        try:
            # 載入頻率分析結果
            frequency_path = self.output_dir / "frequency_analysis.json"
            if frequency_path.exists():
                with open(frequency_path, 'r', encoding='utf-8') as f:
                    self.frequency_data = json.load(f)
                print("✅ 已載入頻率分析結果")
            
            # 載入複雜度分析結果（只讀取摘要部分）
            complexity_path = self.output_dir / "complexity_analysis.json"
            if complexity_path.exists() and complexity_path.stat().st_size < 50 * 1024 * 1024:  # 小於50MB
                with open(complexity_path, 'r', encoding='utf-8') as f:
                    self.complexity_data = json.load(f)
                print("✅ 已載入複雜度分析結果")
            else:
                print("⚠️ 複雜度分析檔案過大，跳過載入")
            
            return self.frequency_data is not None
            
        except Exception as e:
            print(f"❌ 載入分析數據時發生錯誤: {e}")
            return False
    
    def analyze_code_patterns(self) -> List[Dict]:
        """分析通用程式模式並按頻率排序"""
        if not self.frequency_data:
            return []
        
        patterns = []
        
        # 獲取函數調用數據
        function_calls = self.frequency_data.get("top_function_calls", {})
        
        # 1. LIST_LOOKUP 模式分析 - 線性查找操作
        list_operations = {
            "index": function_calls.get("index", 0),
            "count": function_calls.get("count", 0), 
            "remove": function_calls.get("remove", 0),
        }
        list_total = sum(list_operations.values())
        
        if list_total > 5:
            patterns.append({
                "pattern": "LIST_LOOKUP",
                "name": "清單線性查找操作",
                "frequency": list_total,
                "priority_score": list_total * 10,  # 高權重
                "current_complexity": "O(n)",
                "target_complexity": "O(1)", 
                "description": f"發現 {list_total} 次清單線性查找操作 (index: {list_operations['index']}, count: {list_operations['count']}, remove: {list_operations['remove']})",
                "suggestions": [
                    "使用 set 或 dict 進行 O(1) 查找",
                    "建立查找索引映射",
                    "使用 collections.Counter 進行計數操作"
                ],
                "blueprint": "lookup_accelerator.md",
                "example_code": """
# ❌ O(n) 線性查找
if item in my_list:  
    process(item)

# ✅ O(1) 集合查找
lookup_set = set(my_list)
if item in lookup_set:
    process(item)
"""
            })
        
        # 2. PYTHON_FOR_LOOP 模式分析 - 可向量化的迴圈
        loop_count = self.frequency_data.get("loop_distribution", {}).get("For", 0)
        range_calls = function_calls.get("range", 0)
        
        if loop_count > 20:
            patterns.append({
                "pattern": "PYTHON_FOR_LOOP",
                "name": "Python 原生迴圈模式",
                "frequency": loop_count,
                "priority_score": loop_count * 5,
                "current_complexity": "O(n) Python 解釋器開銷",
                "target_complexity": "O(n) C 速度",
                "description": f"發現 {loop_count} 個 for 迴圈，其中 {range_calls} 個使用 range()，可能可以向量化加速",
                "suggestions": [
                    "使用 NumPy 向量化操作替代數值計算迴圈",
                    "使用列表推導式替代簡單迴圈",
                    "使用內建函數 (map, filter, sum) 加速"
                ],
                "blueprint": "vectorization_converter.md",
                "example_code": """
# ❌ Python 迴圈
result = []
for x in data:
    result.append(x ** 2)

# ✅ 向量化操作
import numpy as np
result = np.array(data) ** 2
"""
            })
        
        # 3. CONFIG_LOAD 模式分析 - 重複載入檔案
        io_operations = {
            "open": function_calls.get("open", 0),
            "load": function_calls.get("load", 0),
        }
        
        # 檢查 JSON 相關 imports
        json_usage = 0
        for import_stmt in self.frequency_data.get("popular_imports", {}):
            if "json" in import_stmt.lower():
                json_usage += self.frequency_data["popular_imports"][import_stmt]
        
        config_total = sum(io_operations.values()) + json_usage
        
        if config_total > 10:
            patterns.append({
                "pattern": "CONFIG_LOAD",
                "name": "重複檔案載入模式",
                "frequency": config_total,
                "priority_score": config_total * 8,
                "current_complexity": "O(IO) 重複磁碟讀取",
                "target_complexity": "O(1) 記憶體快取",
                "description": f"發現 {config_total} 次檔案載入操作 (open: {io_operations['open']}, load: {io_operations['load']}, json: {json_usage})，可能重複載入設定檔",
                "suggestions": [
                    "使用 @lru_cache 快取載入結果",
                    "建立全域設定管理器",
                    "預載入常用設定檔到記憶體"
                ],
                "blueprint": "config_cache.md",
                "example_code": """
# ❌ 重複載入
def get_config():
    with open('config.json') as f:
        return json.load(f)

# ✅ 快取載入
from functools import lru_cache

@lru_cache(maxsize=1)
def get_config():
    with open('config.json') as f:
        return json.load(f)
"""
            })
        
        # 4. HIGH_FREQUENCY_CALLS 模式 - 高頻低效調用
        high_freq_inefficient = []
        inefficient_patterns = {
            "print": ("I/O 阻塞", "改用 logging 模組"),
            "len": ("重複計算", "快取長度值"),
            "append": ("記憶體重分配", "使用 extend() 或預分配"),
            "get": ("字典查找", "使用 defaultdict 或 setdefault"),
            "str": ("字串轉換", "減少不必要的轉換"),
        }
        
        for func_name, (problem, solution) in inefficient_patterns.items():
            count = function_calls.get(func_name, 0)
            if count > 100:  # 高頻調用閾值
                high_freq_inefficient.append({
                    "func": func_name,
                    "count": count,
                    "problem": problem,
                    "solution": solution
                })
        
        if high_freq_inefficient:
            total_calls = sum(item["count"] for item in high_freq_inefficient)
            patterns.append({
                "pattern": "HIGH_FREQ_CALLS",
                "name": "高頻低效函數調用",
                "frequency": total_calls,
                "priority_score": total_calls * 3,
                "current_complexity": "累積效能損失",
                "target_complexity": "優化實作",
                "description": f"發現 {len(high_freq_inefficient)} 種高頻低效調用，總計 {total_calls} 次",
                "details": high_freq_inefficient,
                "suggestions": [
                    "將 print() 替換為 logging (避免 I/O 阻塞)",
                    "快取 len() 結果或使用計數器",
                    "批量操作替代頻繁 append()",
                    "使用 defaultdict 減少 get() 調用"
                ],
                "blueprint": "frequency_optimization.md"
            })
        
        # 按優先級分數排序
        patterns.sort(key=lambda x: x["priority_score"], reverse=True)
        return patterns
    
    def generate_report(self) -> str:
        """生成優化報告"""
        patterns = self.analyze_code_patterns()
        
        if not patterns:
            return "# 🤷‍♂️ 未發現明顯的優化機會\n\n您的程式碼看起來已經相當優化了！"
        
        report = f"""# 🚀 TurboCode Kit 程式碼優化分析報告

## 📊 分析摘要

**分析時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**總檔案數**: {(self.frequency_data.get('total_files', 'N/A') if self.frequency_data else 'N/A')}  
**發現模式**: {len(patterns)} 個可優化模式  

---

## 🎯 優化優先級清單 (按頻率排序)

| 排名 | 模式類型 | 發現頻率 | 影響程度 | 優化目標 | 藍圖範本 |
|------|----------|----------|----------|----------|----------|
"""
        
        # 優先級表格
        for i, pattern in enumerate(patterns, 1):
            impact = "🚨 高" if pattern["priority_score"] > 500 else "⚠️ 中" if pattern["priority_score"] > 100 else "💡 低"
            report += f"| **{i}** | **{pattern['pattern']}** | {pattern['frequency']} 次 | {impact} | {pattern['current_complexity']} → {pattern['target_complexity']} | `{pattern.get('blueprint', 'N/A')}` |\n"
        
        report += "\n---\n\n## 📋 詳細優化指南\n\n"
        
        # 詳細說明每個模式
        for i, pattern in enumerate(patterns, 1):
            report += f"### {i}. {pattern['name']}\n\n"
            report += f"**🔍 模式識別**: `{pattern['pattern']}`  \n"
            report += f"**📈 發現頻率**: {pattern['frequency']} 次  \n"
            report += f"**⚡ 優化潛力**: {pattern['current_complexity']} → {pattern['target_complexity']}  \n"
            report += f"**📝 問題描述**: {pattern['description']}  \n\n"
            
            report += "**🛠️ 優化建議**:\n"
            for suggestion in pattern["suggestions"]:
                report += f"- {suggestion}\n"
            
            if pattern.get("example_code"):
                report += f"\n**💡 程式碼範例**:\n```python{pattern['example_code']}\n```\n"
            
            if pattern.get("blueprint"):
                report += f"\n**📖 參考範本**: `optimization_blueprints/{pattern['blueprint']}`\n"
            
            # 特殊處理高頻調用詳情
            if pattern["pattern"] == "HIGH_FREQ_CALLS" and pattern.get("details"):
                report += "\n**📊 詳細調用統計**:\n"
                for detail in pattern["details"]:
                    report += f"- `{detail['func']}()`: {detail['count']} 次調用 - {detail['problem']} → {detail['solution']}\n"
            
            report += "\n" + "="*50 + "\n\n"
        
        # 使用指南
        report += """## 🎯 執行優化的步驟

### 1. 選擇目標 🎪
**從上方清單選擇排名第一的模式開始優化**

### 2. 查看範本 📚
```bash
# 參考對應的優化藍圖
code optimization_blueprints/lookup_accelerator.md
```

### 3. AI 協作優化 🤖
**向 Copilot 下達指令**:
```
請參考 optimization_blueprints/lookup_accelerator.md 範本，
將我程式碼中的 LIST_LOOKUP 模式優化為 O(1) 查找。
請找出所有使用 index()、count()、remove() 的地方並優化。
```

### 4. 效能測試 🧪
```python
# 使用內建工具測試
import time
from turbo_utils import quick_optimization_demo
quick_optimization_demo()
```

### 5. 記錄成果 📝
- 測量優化前後的執行時間
- 記錄加速倍率 (例如: 150ms → 0.5ms = 300x 加速)
- 添加 `# TCK Optimized` 註釋標記

### 6. 重複流程 🔄
**完成第一個模式後，重新執行分析選擇下一個目標**

---

## 📈 預期成效

"""
        
        # 預期成效統計
        total_optimizations = len(patterns)
        high_impact = len([p for p in patterns if p["priority_score"] > 500])
        
        report += f"- **可優化項目**: {total_optimizations} 個模式\n"
        report += f"- **高影響項目**: {high_impact} 個 (預期加速 >10x)\n"
        report += "- **預估總提升**: 20-50% 程式碼執行效能\n\n"
        
        report += "---\n*由 TurboCode Kit (TCK) v2.0 生成*"
        
        return report
    
    def run(self) -> bool:
        """執行報告生成"""
        print("🚀 TurboCode Kit 優化分析報告生成中...")
        
        if not self.load_analysis_data():
            print("❌ 無法載入分析數據")
            return False
        
        report_content = self.generate_report()
        
        # 保存 Markdown 報告
        report_file = self.output_dir / "optimization_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 優化報告已生成: {report_file}")
        
        # 顯示摘要
        patterns = self.analyze_code_patterns()
        if patterns:
            print(f"\n📊 發現 {len(patterns)} 個可優化模式:")
            for i, pattern in enumerate(patterns[:3], 1):
                print(f"  {i}. {pattern['pattern']}: {pattern['frequency']} 次")
            if len(patterns) > 3:
                print(f"  ... 還有 {len(patterns) - 3} 個模式")
        
        return True


def main():
    generator = OptimizationReportGenerator()
    generator.run()


if __name__ == "__main__":
    main()