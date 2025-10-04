"""
TCK Case 007: 雙端佇列操作優化

對應藍圖：deque_operations_optimizer.md
優化策略：list 頭部插入 O(n) → deque 頭部插入 O(1)
效能提升：線性倍數提升（隨資料量增長）
"""

from collections import deque

# 測試案例名稱
name = "case_007_deque_operations"
description = "雙端佇列優化：O(n²) list 頭部插入 → O(n) deque 操作。"


def setup_data():
    """準備測試資料 - 大規模數據以體現 O(n) vs O(1) 差異"""
    operations_count = 10000  # 大量頭部插入操作
    return (operations_count,)


def unoptimized_version(operations_count):
    """❌ 原始版本：列表頭部插入 O(n)

    效能問題：
    - 每次 insert(0) 都要移動所有現有元素
    - 總時間複雜度 O(n²)
    - 記憶體重新分配頻繁
    """
    result = []
    for i in range(operations_count):
        result.insert(0, i)  # O(n) - 需要移動所有現有元素
    return len(result)


def optimized_version_deque(operations_count):
    """✅ 優化版本：deque 頭部插入 O(1)

    優化策略：
    - deque 是雙向鏈結實現
    - appendleft() 常數時間操作
    - 總時間複雜度 O(n)
    """
    result = deque()
    for i in range(operations_count):
        result.appendleft(i)  # O(1) - 常數時間插入
    return len(result)


# 優化版本字典
optimized_versions = {"deque_appendleft": optimized_version_deque}
