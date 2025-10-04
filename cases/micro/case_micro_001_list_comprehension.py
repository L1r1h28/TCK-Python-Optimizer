"""
TCK Micro Case 001: 列表推導式 vs. For 迴圈

對應藍圖：bp_micro_001_list_comprehension.md
優化策略：使用列表推導式替換 for 迴圈中的 .append()。
"""

# 測試案例名稱
name = "case_micro_001_list_comprehension"
description = "微模式：比較 for 迴圈 + .append() 與列表推導式的效能。"


def setup_data():
    """準備一個包含 1,000,000 個整數的列表。"""
    source_data = list(range(1000000))
    return (source_data,)


def unoptimized_version(source_data):
    """❌ 原始版本：使用 for 迴圈和 .append() 建立新列表。

    效能問題：
    - 在迴圈的每次迭代中，都需要解析 .append 屬性並呼叫該函數，這會產生額外的 Python 層級開銷。
    - 列表大小是動態調整的，可能涉及多次記憶體重新分配。
    """
    result = []
    for i in source_data:
        if i % 2 == 0:
            result.append(i * 2)
    return result


def optimized_version_comprehension(source_data):
    """✅ 優化版本：使用列表推導式。

    優化策略：
    - 列表推導式在 C 層級進行了高度優化。
    - 迭代和附加操作在更低的層級執行，減少了 Python 直譯器的開銷。
    - Python 直譯器可以預先計算最終列表的大小，進行單次記憶體分配，從而提高效率。
    """
    return [i * 2 for i in source_data if i % 2 == 0]


def optimized_version_map_filter(source_data):
    """✅✅ 優化版本 2：使用 map 和 filter 函數。

    優化策略：
    - `filter` 和 `map` 都會回傳惰性求值的迭代器，記憶體效率高。
    - 這些函數也在 C 層級實現，效能優於手動迴圈。
    - 最終由 `list()` 構造函數一次性遍歷迭代器並建立列表。
    """
    # 先過濾出偶數，然後將結果乘以 2
    filtered_data = filter(lambda i: i % 2 == 0, source_data)
    mapped_data = map(lambda i: i * 2, filtered_data)
    return list(mapped_data)


def optimized_version_numpy(source_data):
    """✅✅✅ 優化版本 3：使用 NumPy 向量化操作。

    優化策略：
    - 將 Python 列表轉換為 NumPy 陣列，以便進行向量化操作。
    - 使用布林遮罩 (boolean mask) 一次性篩選出所有偶數。
    - 直接對篩選後的陣列進行廣播乘法 (* 2)。
    - 雖然有轉換成本，但後續的計算極其高效。
    """
    import numpy as np

    arr = np.array(source_data)
    # 向量化篩選和計算
    result_arr = arr[arr % 2 == 0] * 2
    return result_arr.tolist()


def optimized_version_operator(source_data):
    """✅✅✅✅ 優化版本 4：使用 operator 模組避免 lambda。

    優化策略：
    - 使用 operator.mul 替換 lambda i: i * 2，避免了函數呼叫的開銷。
    - operator 函數是 C 層級實現，比 lambda 更快。
    - 結合 filter 使用，保持函數式程式設計風格。
    - 使用 itertools.repeat 避免建立大型列表。
    """
    import operator
    import itertools

    filtered_data = filter(lambda i: i % 2 == 0, source_data)
    # 使用 itertools.repeat 建立無限的 2 值序列，避免記憶體浪費
    mapped_data = map(operator.mul, filtered_data, itertools.repeat(2))
    return list(mapped_data)


def optimized_version_itertools(source_data):
    """✅✅✅✅✅ 優化版本 5：使用 itertools 進行函數式處理。

    優化策略：
    - itertools.compress 使用布林遮罩來選擇元素，比 filter 更高效。
    - itertools.repeat 提供無限的 2 值序列，用於乘法。
    - itertools.starmap 結合 operator.mul 進行元素級運算。
    - 整個管道都是惰性求值的，直到 list() 呼叫才進行具體計算。
    """
    import itertools
    import operator

    # 建立布林遮罩：True for 偶數, False for 奇數
    mask = itertools.cycle([True, False])
    # 壓縮資料，只保留偶數
    compressed_data = itertools.compress(source_data, mask)
    # 使用 starmap 進行乘法運算
    result_iter = itertools.starmap(
        operator.mul, zip(compressed_data, itertools.repeat(2))
    )
    return list(result_iter)


def optimized_version_numba_jit(source_data):
    """✅✅✅✅✅✅ 優化版本 6：使用 Numba JIT 編譯。

    優化策略：
    - 使用 @jit(nopython=True) 將函式編譯為機器碼。
    - 列表推導式直接編譯為高效的迴圈。
    - 避免 Python 直譯器開銷，接近 C 語言效能。
    - 首次呼叫有編譯開銷，但後續呼叫極快。
    """
    from numba import jit

    @jit(nopython=True)
    def numba_comprehension(data):
        return [x * 2 for x in data if x % 2 == 0]

    return numba_comprehension(source_data)


def optimized_version_numba_parallel(source_data):
    """✅✅✅✅✅✅✅ 優化版本 7：使用 Numba 並行處理。

    優化策略：
    - 使用 @njit(parallel=True) 啟用自動並行化。
    - prange 進行並行迴圈，自動分配到多核心。
    - 結合 fastmath=True 啟用浮點數優化。
    - 適合大規模資料處理，可超越單核心極限。
    """
    from numba import njit
    import numpy as np

    @njit(parallel=True, fastmath=True)
    def numba_parallel(data):
        # 使用 NumPy 陣列進行並行處理，避免列表操作問題
        arr = np.array(data)
        mask = arr % 2 == 0
        result = arr[mask] * 2
        return result

    return numba_parallel(source_data).tolist()


def optimized_version_numexpr(source_data):
    """✅✅✅✅✅✅✅✅ 優化版本 8：使用 NumExpr 多核心評估。

    優化策略：
    - 使用 NumExpr 評估數學運算式，利用多核心。
    - 避免建立中間陣列，直接在記憶體中運算。
    - 支援區塊處理，優化快取使用。
    - 對於數學密集運算有顯著加速效果。
    """
    import numexpr as ne
    import numpy as np

    # 轉換為 NumPy 陣列進行 NumExpr 處理
    arr = np.array(source_data)
    # 先用 NumExpr 創建條件陣列，再用 NumPy 完成篩選和計算
    condition = ne.evaluate("arr % 2 == 0")
    # 使用條件索引和直接運算
    result = arr[condition] * 2
    return result.tolist()


def optimized_version_numba_typed_list(source_data):
    """✅✅✅✅✅✅✅✅✅ 優化版本 9：使用 Numba Typed List。

    優化策略：
    - 使用 numba.typed.List 進行類型同質列表操作。
    - 編譯時類型推斷，運行時高效操作。
    - 避免 Python 物件開銷，直接操作原生類型。
    - 適合需要動態列表建構的場景。
    """
    from numba import njit
    from numba.typed import List

    @njit
    def numba_typed_list(data):
        result = List()
        for x in data:
            if x % 2 == 0:
                result.append(x * 2)
        return result

    return list(numba_typed_list(source_data))


# 要比較的優化版本字典
optimized_versions = {
    "list_comprehension": optimized_version_comprehension,
    "map_and_filter": optimized_version_map_filter,
    "numpy_vectorization": optimized_version_numpy,
    "operator_optimized": optimized_version_operator,
    "itertools_pipeline": optimized_version_itertools,
    "numba_jit": optimized_version_numba_jit,
    "numba_parallel": optimized_version_numba_parallel,
    "numexpr_evaluation": optimized_version_numexpr,
    "numba_typed_list": optimized_version_numba_typed_list,
}
