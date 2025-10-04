"""
TCK Case 011 (合併): 迭代器鏈結與演算法優化

對應藍圖：iterator_chaining_optimizer.md, iterator_chaining_super_optimizer.md
優化策略：
1. 列表串接 (O(n) 記憶體) → itertools.chain (O(1) 記憶體)
2. 迭代處理 (O(n) 時間) → 數學公式 (O(1) 時間)
效能提升：從記憶體和時間兩個維度進行指數級提升。
"""

import itertools

# 測試案例名稱
name = "case_011_iterator_chaining_combined"
description = (
    "迭代器鏈結優化：從 O(n) 記憶體到 O(1) 記憶體，再到 O(1) 時間的演算法優化。"
)


def setup_data():
    """準備測試資料"""
    # 極大的連續範圍數據，展現數學優化的威力
    start1, end1 = 0, 1000000
    start2, end2 = 1000000, 2000000
    start3, end3 = 2000000, 3000000
    return start1, end1, start2, end2, start3, end3


def unoptimized_version(start1, end1, start2, end2, start3, end3):
    """❌ 原始版本：暴力列表串接

    效能問題：
    - 創建一個包含 300 萬個元素的巨大臨時列表。
    - 極高的記憶體開銷和複製成本 (O(n) 記憶體)。
    - 仍然需要遍歷整個列表 (O(n) 時間)。
    """
    # 創建三個範圍並暴力合併
    range1 = list(range(start1, end1))
    range2 = list(range(start2, end2))
    range3 = list(range(start3, end3))

    combined_list = range1 + range2 + range3

    # 處理合併後的大列表
    result = [item * 2 for item in combined_list if item % 10 == 0]
    return len(result)


def optimized_version_itertools_chain(start1, end1, start2, end2, start3, end3):
    """✅ 優化版本 1：itertools.chain

    記憶體優化：
    - 使用 itertools.chain 避免創建臨時列表。
    - 記憶體複雜度降至 O(1)。
    - 執行時間複雜度仍為 O(n)，因為需要遍歷所有元素。
    """
    # 創建三個範圍
    range1 = range(start1, end1)
    range2 = range(start2, end2)
    range3 = range(start3, end3)

    # 惰性鏈結迭代器
    chained_iterator = itertools.chain(range1, range2, range3)

    # 查找所有能被10整除的數並乘以2
    result = [item * 2 for item in chained_iterator if item % 10 == 0]
    return len(result)


def _count_multiples_in_range(start, end, divisor=10):
    """計算範圍內能被 divisor 整除的數的數量"""
    if start >= end:
        return 0

    # 找到範圍內第一個是 divisor 的倍數的數字
    first_multiple = (start + divisor - 1) // divisor * divisor

    if first_multiple >= end:
        return 0

    # 找到範圍內最後一個是 divisor 的倍數的數字
    last_multiple = (end - 1) // divisor * divisor

    # 計算數量
    return (last_multiple - first_multiple) // divisor + 1


def optimized_version_math_formula(start1, end1, start2, end2, start3, end3):
    """✅✅ 超級優化版本 2：數學公式 O(1)

    演算法優化：
    - 使用數學公式直接計算結果。
    - 完全避免迴圈和條件檢查。
    - 時間複雜度降至 O(1)，實現終極效能。
    """
    # 對三個範圍分別計算
    count1 = _count_multiples_in_range(start1, end1)
    count2 = _count_multiples_in_range(start2, end2)
    count3 = _count_multiples_in_range(start3, end3)

    # 直接返回總數，避免創建列表
    return count1 + count2 + count3


# 優化版本字典
optimized_versions = {
    "itertools_chain_O1_memory": optimized_version_itertools_chain,
    "math_formula_O1_time": optimized_version_math_formula,
}
