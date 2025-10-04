"""
TCK Case 020: 函數調用開銷優化

對應藍圖：020_FUNCTION_CALL_OVERHEAD_OPTIMIZATION_IO_ELIMINATION.md
優化策略：頻繁函數調用 → 內聯展開，消除調用開銷
效能提升：10-30%（高頻調用場景）
"""

# 測試案例名稱
name = "case_020_function_call_overhead"
description = "函數調用開銷優化：頻繁函數調用 → 內聯展開。"


def setup_data():
    """準備測試資料來驗證函數調用開銷"""
    data_size = 200000
    data = list(range(data_size))
    return (data,)


# --- 未優化版本 ---
def _is_valid(x):
    return x % 3 == 0


def _multiply_by_two(x):
    return x * 2


def _add_one(x):
    return x + 1


def unoptimized_version(data):
    """❌ 原始版本：極端頻繁函數調用"""

    def is_valid(x):
        return x % 3 == 0

    def multiply_by_two(x):
        return x * 2

    def add_one(x):
        return x + 1

    def square(x):
        return x**2

    def multiply_by_three(x):
        return x * 3

    def add_constant(x):
        return x + 42

    def divide_by_four(x):
        return x // 4

    def modulo_five(x):
        return x % 5

    result = []
    for item in data:
        if is_valid(item):
            temp = multiply_by_two(item)
            temp = add_one(temp)
            temp = square(temp)
            temp = multiply_by_three(temp)
            temp = add_constant(temp)
            temp = divide_by_four(temp)
            temp = modulo_five(temp)
            result.append(temp)
    return result


def optimized_version_inlined(data):
    """✅ 優化版本：完全內聯展開"""
    result = []
    for item in data:
        if item % 3 == 0:
            temp = item * 2
            temp = temp + 1
            temp = temp**2
            temp = temp * 3
            temp = temp + 42
            temp = temp // 4
            temp = temp % 5
            result.append(temp)
    return result


# 優化版本字典
optimized_versions = {"inlined_logic": optimized_version_inlined}
