"""
TCK Case 017: 高頻調用優化

對應藍圖：high_freq_calls_optimizer.md
優化策略：高頻函數調用 → 預快取 + 迴圈不變數
效能提升：3-5x（減少函數調用開銷）
"""

# 測試案例名稱
name = "case_017_high_freq_calls"
description = "高頻調用優化：預快取迴圈不變數，減少重複函數調用。"


def setup_data():
    """準備測試資料 - 模擬高頻調用場景"""
    # 大規模數據模擬實際應用
    data = list(range(50000))
    keys = [f"key_{i}" for i in range(1000)]  # 1000個字典鍵
    return data, keys


def unoptimized_version(data, keys):
    """❌ 原始版本：高頻低效調用

    效能問題：
    - 每次迭代都調用 len(), str()
    - 重複計算不變數
    - 頻繁的字典 get() 操作
    """
    results = []

    # 模擬高頻調用場景
    for i, item in enumerate(data):
        # 高頻 len() 和 str() 調用
        if len(str(item)) > 1:
            # 高頻 len() 調用
            key_index = i % len(keys)
            key = keys[key_index]
            # 模擬一個字典操作
            value = {"count": i}.get("count", 0)
            results.append(f"item_{value}_key_{key}")

    return results


def optimized_version_pre_caching(data, keys):
    """✅ 優化版本：預快取 + 迴圈不變數優化

    優化策略：
    - 預先快取所有迴圈不變數
    - 使用數學運算替代字串轉換
    - 減少不必要的字典創建和 get() 調用
    """
    # 預先快取迴圈不變數
    keys_len = len(keys)
    str_prefix = "item_"

    results = []

    for i, item in enumerate(data):
        # 數學運算替代字串長度檢查
        if item >= 10:  # len(str(item)) > 1 的數學等價
            key_index = i % keys_len
            key = keys[key_index]
            # 直接使用索引 i，避免創建臨時字典和 get()
            results.append(f"{str_prefix}{i}_key_{key}")

    return results


# 優化版本字典
optimized_versions = {"pre_caching_and_inlining": optimized_version_pre_caching}
