"""
TCK Case 008: 記憶化快取優化

對應藍圖：memoization_cache_optimizer.md
優化策略：重複計算 → @lru_cache 記憶化
效能提升：指數級提升（避免重複遞迴）
"""

import functools

# 測試案例名稱
name = "case_008_memorization_cache"
description = "記憶化快取：O(2^n) 遞迴 → O(n) @lru_cache，避免重複計算。"


def setup_data():
    """準備測試資料"""
    # 測試較大的費波納契數列項數
    # 注意：原始版本對於較大數值會非常慢，因此選擇一個適中的值
    test_values = [30, 32, 34]
    return (test_values,)


# --- 未優化版本 ---
def _fibonacci_recursive(n):
    """純遞迴實現，無記憶化"""
    if n <= 1:
        return n
    return _fibonacci_recursive(n - 1) + _fibonacci_recursive(n - 2)


def unoptimized_version(test_values):
    """❌ 原始版本：無快取的遞迴計算

    效能問題：
    - 重複計算相同的子問題
    - 指數時間複雜度 O(2^n)
    - 深度遞迴可能造成堆疊溢位
    """
    return [_fibonacci_recursive(n) for n in test_values]


# --- 優化版本 ---
@functools.lru_cache(maxsize=None)
def _fibonacci_memoized(n):
    """記憶化版本，自動快取結果"""
    if n <= 1:
        return n
    return _fibonacci_memoized(n - 1) + _fibonacci_memoized(n - 2)


def optimized_version_lru_cache(test_values):
    """✅ 優化版本：@lru_cache 記憶化快取

    優化策略：
    - 使用 @lru_cache 自動快取結果
    - 避免重複計算相同參數
    - 線性時間複雜度 O(n)
    """
    # 每次測試前清除快取，確保結果公平
    _fibonacci_memoized.cache_clear()
    return [_fibonacci_memoized(n) for n in test_values]


# 優化版本字典
optimized_versions = {"lru_cache": optimized_version_lru_cache}
