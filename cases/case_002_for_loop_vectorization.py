"""
TCK Case 002: Python For-Loop 向量化優化

對應藍圖：blueprint_002_python_for_loop_vectorization.md
優化策略：傳統迴圈 → NumPy 向量化，規模自適應最佳化
效能提升：小資料 2-3x，大資料 10-20x

詳細實現請參考：optimization_blueprints/blueprint_002_python_for_loop_vectorization.md
"""

import numpy as np

# --- 測試案例設定 ---
name = "FOR_LOOP_VECTORIZATION"
description = "Python For-Loop 進階向量化優化 (NumPy)"
blueprint_file = "blueprint_002_python_for_loop_vectorization.md"


# --- 測試資料生成 ---
def setup_data():
    """準備針對性測試資料，涵蓋不同規模"""
    small_data = np.random.rand(500).tolist()
    medium_data = np.random.rand(5000).tolist()
    large_data = np.random.rand(50000).tolist()
    # 返回一個包含所有資料集的元組，以符合 `*args` 的傳遞方式
    return ((small_data, medium_data, large_data),)


# --- 未優化版本 ---
def unoptimized_version(all_data_sets):
    """❌ 原始版本：傳統 for 迴圈 + 顯式條件處理"""
    small_data, medium_data, large_data = all_data_sets
    results = []
    for data_set in [small_data, medium_data, large_data]:
        processed = []
        total_sum = 0.0
        valid_count = 0
        for x in data_set:
            if x > 0.1:
                y = x**2 + (x**0.5) * 1.5
                if y < 10.0:
                    processed.append(y)
                    total_sum += y
                    valid_count += 1
        results.append(
            {
                "sum": total_sum,
                "count": valid_count,
                "avg": total_sum / valid_count if valid_count > 0 else 0,
            }
        )
    return results


# --- 優化版本 ---
def optimized_v1_numpy_vectorization(all_data_sets):
    """✅ 優化 V1：NumPy 向量化運算"""
    small_data, medium_data, large_data = all_data_sets
    results = []
    for data_set in [small_data, medium_data, large_data]:
        # 將 list 轉換為 NumPy array 以進行向量化操作
        arr = np.array(data_set)

        # 向量化條件過濾
        mask1 = arr > 0.1
        arr_filtered1 = arr[mask1]

        # 向量化數值運算
        y = arr_filtered1**2 + np.sqrt(arr_filtered1) * 1.5

        # 第二次向量化過濾
        mask2 = y < 10.0
        final_arr = y[mask2]

        # 使用 NumPy 內建函式進行高效統計
        total_sum = np.sum(final_arr)
        valid_count = final_arr.size

        results.append(
            {
                "sum": total_sum,
                "count": valid_count,
                "avg": total_sum / valid_count if valid_count > 0 else 0,
            }
        )
    return results


def optimized_v2_list_comprehension(all_data_sets):
    """✅ 優化 V2：列表推導式 (適用於小資料)"""
    small_data, medium_data, large_data = all_data_sets
    results = []
    for data_set in [small_data, medium_data, large_data]:
        # 使用列表推導式進行過濾和計算
        processed = [
            y for x in data_set if x > 0.1 and (y := x**2 + x**0.5 * 1.5) < 10.0
        ]

        total_sum = sum(processed)
        valid_count = len(processed)

        results.append(
            {
                "sum": total_sum,
                "count": valid_count,
                "avg": total_sum / valid_count if valid_count > 0 else 0,
            }
        )
    return results


# --- 優化版本字典 ---
optimized_versions = {
    "NUMPY_VECTORIZATION": optimized_v1_numpy_vectorization,
    "LIST_COMPREHENSION": optimized_v2_list_comprehension,
}
