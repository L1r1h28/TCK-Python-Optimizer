"""
TCK Atomic Case 002: 記憶體分配與數據複製

目標：
精準量化在迴圈中因重複建立物件（特別是字串）而產生的效能成本。
這將為 `case_004_string_concatenation` 中 `+` vs `join` 的巨大效能差異提供數據支撐。

測試場景：
在一個緊密迴圈中，重複將一個短字串附加到一個增長的字串上。
"""

# 測試案例名稱
name = "case_atomic_002_memory_allocation"
description = "原子操作：量化重複記憶體分配與數據複製的成本。"


def setup_data():
    """準備測試資料，一個迭代次數和一個基礎字串。"""
    # 迭代次數減少到 10 萬次，因為 O(n^2) 的操作會非常慢
    return (100_000, "a")


def unoptimized_version(iterations, char):
    """❌ 基準版本：使用 `+` 進行字串串接

    效能問題：
    - O(n^2) 複雜度：每次迴圈都會創建一個全新的字串物件。
    - 記憶體複製：創建新字串時，需要將舊字串的內容完整複製一遍。
    """
    result = ""
    for _ in range(iterations):
        result += char
    return len(result)


def optimized_version_join_method(iterations, char):
    """✅ 優化版本：使用 list.append + join

    優化點：
    - O(n) 複雜度：list.append 是攤提 O(1) 操作。
    - 單次分配：只在最後的 `join` 操作中進行一次性的高效記憶體分配和字串生成。
    """
    char_list = []
    for _ in range(iterations):
        char_list.append(char)
    return len("".join(char_list))


# 優化版本字典
optimized_versions = {
    "join_method": optimized_version_join_method,
}
