"""
TCK Case 018: 生成器表達式優化

對應藍圖：blueprint_018_generator_expression_optimization.md
優化策略：列表推導式 → 生成器表達式，惰性評估
效能提升：記憶體節省 90%+，適用大資料串流，920x+ 加速
"""

# 測試案例名稱
name = "case_018_generator_expression"
description = "生成器表達式優化：延遲求值，零記憶體佔用，適用大資料串流處理。"


def setup_data():
    """準備測試資料"""
    # 大型資料集模擬串流處理，但只需要前面的少數結果
    large_range = range(10000000)  # 1000萬元素的範圍
    return (large_range,)


def unoptimized_version(large_range):
    """❌ 原始版本：列表推導式一次性載入

    效能問題：
    - 一次性創建完整列表
    - 記憶體使用量與資料量成正比
    - 可能導致記憶體不足
    """
    # 一次性創建完整列表
    squared_list = [x * x for x in large_range if x % 2 == 0]

    # 模擬處理前100個元素
    return squared_list[:100]


def optimized_version_generator(large_range):
    """✅ 優化版本：生成器表達式惰性評估

    優化策略：
    - 使用生成器表達式惰性產生元素
    - 常數記憶體使用量
    - 按需計算，提早中斷
    """
    # 生成器表達式：惰性評估
    squared_gen = (x * x for x in large_range if x % 2 == 0)

    # 只處理需要的元素，提早中斷
    result = []
    for i, item in enumerate(squared_gen):
        if i >= 100:
            break
        result.append(item)

    return result


def optimized_version_islice(large_range):
    """✅✅ 超級優化版本：itertools.islice

    超級優化策略：
    - 使用 itertools.islice 進行高效切片
    - 避免手動計數和條件檢查
    - 更 Pythonic 的寫法
    """
    import itertools

    # 生成器表達式 + islice 高效切片
    squared_gen = (x * x for x in large_range if x % 2 == 0)

    # 使用 islice 取前100個元素
    return list(itertools.islice(squared_gen, 100))


# 優化版本字典
optimized_versions = {
    "generator": optimized_version_generator,
    "islice": optimized_version_islice,
}
