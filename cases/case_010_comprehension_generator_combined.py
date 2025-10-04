"""
TCK Case 010 (科學重設計): 推導式效能瓶頸研究

基於 DeepWiki CPython 研究：
- Python 3.12 comprehension inlining 帶來 2x 基礎提升
- 複雜條件會抵消推導式優勢
- 函數調用開銷是關鍵瓶頸
- 記憶體分配vs惰性評估的權衡

對應藍圖：blueprint_010_comprehension_bottleneck_analysis.md
優化策略：
1. 識別推導式效能瓶頸的具體原因
2. 展示何時推導式會比for迴圈慢
3. 提供科學的選擇指南
效能結果：從負優化到正確選擇的轉變
"""

# 測試案例名稱
name = "case_010_comprehension_bottleneck_analysis"
description = "推導式效能瓶頸科學分析：基於 CPython 內部機制的優化選擇指南。"


def setup_data():
    """準備測試資料 - 設計來暴露推導式瓶頸的特殊場景"""
    # 中等規模資料，足以展現不同模式的效能差異
    data = list(range(100000))  # 10萬元素

    # 準備一些昂貴的函數調用場景
    import math

    def heavy_function(x):
        """複雜的數學計算函數"""
        return math.sqrt(abs(x)) + math.sin(x) * math.cos(x)

    return (data, heavy_function)


def unoptimized_version(data, heavy_function):
    """❌ 原始版本：複雜條件推導式 (展示瓶頸)

    效能問題（基於 DeepWiki 研究）：
    - 多重複雜條件檢查
    - 每個元素都調用昂貴函數
    - 字串操作增加記憶體分配開銷
    - 推導式的優勢被函數調用開銷抵消
    """
    # 這是一個故意設計的"瓶頸推導式"
    result = [
        str(int(heavy_function(x))).upper()  # 昂貴函數 + 字串操作
        for x in data
        if x % 2 == 0 and x > 1000 and heavy_function(x) > 5 and len(str(x)) > 2
    ]
    return len(result)


def optimized_version_simple_comprehension(data, heavy_function):
    """✅ 優化版本 1：簡化推導式 (減少函數調用)

    優化策略：
    - 預先篩選，減少昂貴函數調用次數
    - 先用便宜的條件過濾
    - 利用 Python 3.12 comprehension inlining 優勢
    """
    # 先用便宜的條件過濾
    pre_filtered = [x for x in data if x % 2 == 0 and x > 1000 and len(str(x)) > 2]

    # 再對較小的集合應用昂貴操作
    result = [
        str(int(heavy_function(x))).upper()
        for x in pre_filtered
        if heavy_function(x) > 5
    ]
    return len(result)


def optimized_version_for_loop_with_cache(data, heavy_function):
    """✅ 優化版本 2：for迴圈 + 快取 (控制函數調用)

    優化策略：
    - 使用傳統for迴圈獲得更多控制權
    - 快取昂貴函數的結果
    - 避免重複計算相同值
    """
    result = []
    function_cache = {}

    for x in data:
        # 先進行便宜的篩選
        if x % 2 == 0 and x > 1000 and len(str(x)) > 2:
            # 快取昂貴函數調用
            if x not in function_cache:
                function_cache[x] = heavy_function(x)

            heavy_result = function_cache[x]
            if heavy_result > 5:
                result.append(str(int(heavy_result)).upper())

    return len(result)


def optimized_version_generator_pipeline(data, heavy_function):
    """✅ 優化版本 3：生成器管道 (記憶體 + 懶評估)

    優化策略：
    - 使用生成器避免中間列表
    - 分階段過濾，最小化昂貴操作
    - 利用懶評估，只在需要時計算
    """

    def filtering_pipeline():
        for x in data:
            # 第一階段：便宜的條件
            if x % 2 == 0 and x > 1000 and len(str(x)) > 2:
                # 第二階段：昂貴的計算（懶評估）
                heavy_result = heavy_function(x)
                if heavy_result > 5:
                    yield str(int(heavy_result)).upper()

    # 使用 sum() 對生成器計數，避免中間列表
    return sum(1 for _ in filtering_pipeline())


def optimized_version_numba_vectorized(data, heavy_function):
    """✅ 優化版本 4：NumPy 向量化 (適用於數值計算)

    優化策略：
    - 將計算向量化，利用 NumPy/NumExpr
    - 避免 Python 層級的迴圈
    - 專門針對數值密集型運算優化
    """
    import numpy as np

    # 轉換為 NumPy 陣列
    np_data = np.array(data)

    # 向量化過濾條件
    mask = (np_data % 2 == 0) & (np_data > 1000)

    # 添加字串長度條件（這裡簡化處理）
    mask = mask & (np_data > 99)  # len(str(x)) > 2 的近似

    filtered_data = np_data[mask]

    # 向量化昂貴函數（近似）
    heavy_results = np.sqrt(np.abs(filtered_data)) + np.sin(filtered_data) * np.cos(
        filtered_data
    )

    # 向量化最終過濾
    final_mask = heavy_results > 5
    final_results = heavy_results[final_mask]

    return len(final_results)


# 優化版本字典
optimized_versions = {
    "simple_comprehension": optimized_version_simple_comprehension,
    "for_loop_cache": optimized_version_for_loop_with_cache,
    "generator_pipeline": optimized_version_generator_pipeline,
    "numba_vectorized": optimized_version_numba_vectorized,
}
