"""
TCK Case 006: 集合操作優化

對應藍圖：set_operations_optimizer.md
優化策略：O(n²) 列表查找 → O(n) 集合交集
效能提升：50-100x（大資料集）
"""

# 測試案例名稱
name = "case_006_set_operations"
description = "集合操作優化：O(n²) 列表查找 → O(n) 集合交集，利用雜湊表效率。"


def setup_data():
    """準備測試資料"""
    # 創建有重疊部分的大型列表
    list1 = list(range(1000, 3000))  # [1000, 1001, ..., 2999]
    list2 = list(range(2000, 4000))  # [2000, 2001, ..., 3999]
    # 交集範圍：[2000, 2001, ..., 2999]，共1000個元素
    return list1, list2


def unoptimized_version(list1, list2):
    """❌ 原始版本：列表推導式查找交集

    效能問題：
    - 對每個元素都要掃描整個第二個列表
    - 雙重迴圈，時間複雜度 O(n²)
    - 沒有利用雜湊查找優勢
    """
    intersection = [x for x in list1 if x in list2]  # O(n²)
    # 為了確保結果順序一致以便比較，對結果進行排序
    intersection.sort()
    return intersection


def optimized_version_set_intersection(list1, list2):
    """✅ 優化版本：集合交集運算

    優化策略：
    - 使用集合內建交集運算 &
    - 雜湊表查找，時間複雜度 O(n)
    - 利用 Python 底層 C 實現
    """
    intersection = list(set(list1) & set(list2))  # O(n)
    # 為了確保結果順序一致以便比較，對結果進行排序
    intersection.sort()
    return intersection


# 優化版本字典
optimized_versions = {"set_intersection": optimized_version_set_intersection}
