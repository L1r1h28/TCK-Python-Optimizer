"""
TCK Case 013 (合併): 迴圈查找優化

對應藍圖：loop_lookup_optimizer.md, loop_lookup_super_optimizer.md
優化策略：
1. 巢狀迴圈 O(n²) → 集合查找 O(n)
2. 集合查找 O(n) → 直接集合交集 (C 層級實現)
效能提升：50-1000x（大資料集）
"""

# 測試案例名稱
name = "case_013_loop_lookup_combined"
description = "迴圈查找優化：從 O(n²) 巢狀迴圈到 O(n) 集合查找，再到直接集合交集。"


def setup_data():
    """準備測試資料"""
    # 使用較大的資料集以突顯超級優化的效果
    list_a = list(range(5000))  # 5000 元素
    list_b = list(range(2500, 7500))  # 5000 元素，有重疊
    return list_a, list_b


def unoptimized_version(list_a, list_b):
    """❌ 原始版本：巢狀迴圈 O(n²)

    效能問題：
    - 對每個 list_a 元素都要掃描整個 list_b
    - 時間複雜度 O(n²)
    - 大量無用的比較操作
    """
    common_elements = []
    for a in list_a:
        for b in list_b:
            if a == b:
                common_elements.append(a)
                break  # 找到後就跳出
    common_elements.sort()  # 排序以確保一致性
    return common_elements


def optimized_version_set_lookup(list_a, list_b):
    """✅ 優化版本 1：集合查找 O(n)

    優化策略：
    - 將 list_b 轉換為集合，查找 O(1)
    - 單一迴圈，時間複雜度 O(n)
    """
    set_b = set(list_b)
    common_elements = [a for a in list_a if a in set_b]
    common_elements.sort()  # 排序以確保一致性
    return common_elements


def optimized_version_set_intersection(list_a, list_b):
    """✅✅ 超級優化版本 2：一次性集合交集

    最終優化：
    - 直接使用集合交集運算子 &
    - C 層級實現，效率最高
    - 減少 Python 層級的迴圈開銷
    """
    result = list(set(list_a) & set(list_b))
    result.sort()  # 排序以確保一致性
    return result


# 優化版本字典
optimized_versions = {
    "set_lookup": optimized_version_set_lookup,
    "direct_set_intersection": optimized_version_set_intersection,
}
