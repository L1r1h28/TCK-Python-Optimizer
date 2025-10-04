"""
TCK Case 001: LIST_LOOKUP 優化

對應藍圖：blueprint_001_list_lookup.md
優化策略：線性查找 O(n) → 集合查找 O(1)
效能提升：理論上接近無限倍（隨資料集大小增長）

詳細實現請參考：optimization_blueprints/blueprint_001_list_lookup.md
"""

import random

# --- 測試案例設定 ---
name = "LIST_LOOKUP"
description = "列表查找優化：從 O(n) 線性掃描到 O(1) 雜湊查找"
blueprint_file = "blueprint_001_list_lookup.md"


# --- 測試資料生成 ---
def setup_data():
    """準備測試資料：一個大列表和一些要搜尋的項目"""
    test_data = list(range(100000))
    search_items = random.sample(test_data, 10000)
    return test_data, search_items


# --- 未優化版本 ---
def unoptimized_version(test_data, search_items):
    """❌ 基準版本：使用 list 進行線性查找 O(n)"""
    # 差異註解：每次 `in` 操作都會從頭掃描 `test_data` 列表，
    # 導致總體複雜度為 O(len(search_items) * len(test_data))。
    results = []
    for item in search_items:
        if item in test_data:  # 線性搜尋
            results.append(item)
    return results


# --- 優化版本 ---
def optimized_v1_set_lookup(test_data, search_items):
    """✅ 優化版本 V1：使用 set 進行雜湊查找 O(1)"""
    # 差異註解：預先將列表轉換為集合（set），這需要 O(n) 的時間。
    # 之後的每次查找操作都變為平均 O(1) 的時間複雜度。
    # 總體複雜度為 O(len(test_data) + len(search_items))。
    lookup_set = set(test_data)
    results = []
    for item in search_items:
        if item in lookup_set:  # 雜湊查找
            results.append(item)
    return results


# --- 優化版本字典 ---
# 這是新的核心部分，允許分析器測試多個優化方案
optimized_versions = {
    "SET_LOOKUP": optimized_v1_set_lookup,
    # 未來可以添加更多優化版本，例如：
    # "ANOTHER_OPTIMIZATION": another_optimized_func,
}
