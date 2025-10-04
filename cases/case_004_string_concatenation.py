"""
TCK Case 004: 字串拼接優化

對應藍圖：blueprint_004_string_concatenation.md
優化策略：字串累加 O(n²) → join() O(n)
效能提升：100-1000x（大字串）

詳細實現請參考：optimization_blueprints/blueprint_004_string_concatenation.md
"""

# 測試案例名稱
name = "case_004_string_concatenation"
description = "字串拼接優化：O(n²) 累加 → O(n) join()，避免重複記憶體分配。"


def setup_data():
    """準備測試資料"""
    base_words = [
        "hello",
        "world",
        "python",
        "optimization",
        "performance",
        "string",
        "concatenation",
    ]
    words = base_words * 200  # 1400 個單詞，測試大量拼接
    return (words,)


def unoptimized_version(words):
    """❌ 原始版本：字串累加 O(n²)

    效能問題：
    - 每次 += 都要創建新字串物件
    - 複製之前的所有字元
    - 記憶體使用量呈指數增長
    """
    result = ""
    for word in words:
        result += word + " "  # O(n²) - 每次都複製整個字串
    return result.strip()


def optimized_version_join(words):
    """✅ 優化版本：join() O(n)

    優化策略：
    - 使用 join() 方法只做一次記憶體分配
    - 預先計算總長度，避免重複分配
    - 線性時間複雜度 O(n)
    """
    return " ".join(words)  # O(n) - 一次性分配記憶體


# 優化版本字典
optimized_versions = {"join_method": optimized_version_join}
