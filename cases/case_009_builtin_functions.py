"""
TCK Case 009: 內建函數優化

對應藍圖：builtin_functions_optimizer.md
優化策略：手動迴圈 → 內建函數，利用 C 層級優化
效能提升：3-5x（數值計算）
"""

import statistics
import random
import numpy as np
import pandas as pd

# 測試案例名稱
name = "case_009_builtin_functions"
description = "內建函數與高效能函式庫優化：手動迴圈 → 內建函數 → NumPy → Pandas。"


def setup_data():
    """準備測試資料"""
    # 大規模數值資料
    numbers = [random.uniform(0, 1000) for _ in range(10000)]
    return (numbers,)


def unoptimized_version(numbers):
    """❌ 原始版本：手動迴圈計算統計值

    效能問題：
    - Python 層級的迴圈計算
    - 重複遍歷資料集
    - 精度可能不如專業實現
    """
    # 手動計算最大值、最小值、總和、平均值
    if not numbers:
        return {"max": 0, "min": 0, "sum": 0, "avg": 0, "std": 0}

    max_val = numbers[0]
    min_val = numbers[0]
    total = 0

    for num in numbers:
        if num > max_val:
            max_val = num
        if num < min_val:
            min_val = num
        total += num

    n = len(numbers)
    avg = total / n

    # 手動計算標準差
    variance_sum = sum((num - avg) ** 2 for num in numbers)
    std_dev = (variance_sum / n) ** 0.5

    return {"max": max_val, "min": min_val, "sum": total, "avg": avg, "std": std_dev}


def optimized_version_builtins(numbers):
    """✅ 優化版本 1：內建函數 + statistics 模組

    優化策略：
    - 使用 C 實現的內建函數 (max, min, sum)
    - statistics 模組提供更穩定和快速的統計實現
    - 程式碼更簡潔，可讀性更高
    """
    if not numbers:
        return {"max": 0, "min": 0, "sum": 0, "avg": 0, "std": 0}

    # 注意：為了與手動計算的母體標準差(population standard deviation)保持一致，
    # 我們使用 statistics.pstdev 而不是 statistics.stdev (樣本標準差)。
    return {
        "max": max(numbers),  # C 層級最佳化
        "min": min(numbers),  # C 層級最佳化
        "sum": sum(numbers),  # C 層級最佳化
        "avg": statistics.fmean(numbers),  # 使用 statistics.fmean 更快
        "std": statistics.pstdev(numbers),  # 母體標準差
    }


def optimized_version_numpy(numbers):
    """✅✅ 優化版本 2：NumPy 向量化計算

    超級優化：
    - 將資料轉換為 NumPy 陣列，利用 SIMD 指令進行並行計算
    - 所有計算都在 C/Fortran 層級完成，極大減少 Python 開銷
    - 一次性計算所有統計值，記憶體存取更高效
    """
    if not numbers:
        return {"max": 0, "min": 0, "sum": 0, "avg": 0, "std": 0}

    arr = np.array(numbers)
    return {
        "max": np.max(arr),
        "min": np.min(arr),
        "sum": np.sum(arr),
        "avg": np.mean(arr),
        "std": np.std(arr),
    }


def optimized_version_pandas(numbers):
    """✅✅✅ 優化版本 3：Pandas Series

    超級優化：
    - 類似 NumPy，但提供更豐富的資料分析 API
    - .describe() 方法可以一次性生成多個統計指標，但需注意其預設行為
    """
    if not numbers:
        return {"max": 0, "min": 0, "sum": 0, "avg": 0, "std": 0}

    s = pd.Series(numbers)

    # 警告：s.describe() 回傳的是「樣本標準差」。
    # 為了與其他方法保持一致性，我們需要手動計算「母體標準差」。
    # 在 Pandas 中，std() 函數的 ddof 參數預設為 1（樣本），我們將其設為 0（母體）。
    return {
        "max": s.max(),
        "min": s.min(),
        "sum": s.sum(),
        "avg": s.mean(),
        "std": s.std(ddof=0),  # 修正：ddof=0 計算母體標準差
    }


# 優化版本字典
optimized_versions = {
    "builtins_and_stats": optimized_version_builtins,
    "numpy_vectorization": optimized_version_numpy,
    "pandas_series": optimized_version_pandas,
}
