"""
TCK Case 005: 字典查詢異常處理開銷分析 (高缺失率場景)

對應藍圖：blueprint_005_dictionary_exception_overhead.md
優化策略：在高缺失率場景下展現 try/except 的真實開銷
效能提升：2.5-4.2x（高缺失率場景下異常處理 vs 其他方法）

詳細實現請參考：optimization_blueprints/blueprint_005_dictionary_exception_overhead.md
"""

import random
from collections import defaultdict

# 測試案例名稱
name = "case_005_dictionary_lookup"
description = "字典查詢異常處理開銷分析：在高缺失率場景下展現 try/except vs get() 的真實效能差異。"


def setup_data():
    """準備測試資料 - 高缺失率場景（80% 缺失）"""
    # 創建中型字典
    large_dict = {f"key_{i}": f"value_{i}" for i in range(10000)}

    # 80% 缺失率 - 突出異常處理開銷
    existing_keys = random.sample(list(large_dict.keys()), 2000)  # 20% 存在
    missing_keys = [f"missing_{i}" for i in range(8000)]  # 80% 缺失
    test_keys = existing_keys + missing_keys
    random.shuffle(test_keys)

    return large_dict, test_keys


def unoptimized_version(large_dict, test_keys):
    """❌ 原始版本：高頻異常處理

    在 80% 缺失率下：
    - 8000 次 KeyError 異常創建和捕獲
    - 每次異常都要構建異常物件、回溯信息
    - 異常處理機制涉及棧展開和清理
    """
    results = []
    for key in test_keys:
        try:
            value = large_dict[key]
            results.append(value)
        except KeyError:
            results.append("default_value")
    return results


def optimized_version_get_simple(large_dict, test_keys):
    """✅ 基礎優化：dict.get() 列表推導

    簡潔的 dict.get() 實現：
    - 無異常開銷
    - 列表推導式的 C 層級優化
    """
    return [large_dict.get(key, "default_value") for key in test_keys]


def optimized_version_get_loop(large_dict, test_keys):
    """✅ 對照組：dict.get() for迴圈

    展現列表推導 vs for迴圈的差異：
    - 同樣使用 dict.get() 避免異常
    - 但使用傳統 for 迴圈結構
    """
    results = []
    for key in test_keys:
        results.append(large_dict.get(key, "default_value"))
    return results


def optimized_version_defaultdict_lambda(large_dict, test_keys):
    """✅ 進階優化：defaultdict + lambda

    使用 __missing__ 機制：
    - lambda 函數作為 default_factory
    - 自動處理缺失鍵，無需顯式檢查
    """
    default_dict = defaultdict(lambda: "default_value")
    default_dict.update(large_dict)

    return [default_dict[key] for key in test_keys]


def optimized_version_defaultdict_constant(large_dict, test_keys):
    """✅ 超級優化：defaultdict + 常數工廠

    避免 lambda 調用開銷：
    - 使用 str 作為 default_factory
    - 預設空字串，後續統一替換
    """
    default_dict = defaultdict(str)
    default_dict.update(large_dict)

    results = []
    for key in test_keys:
        value = default_dict[key]
        # 空字串表示缺失的鍵
        results.append("default_value" if value == "" else value)
    return results


def optimized_version_batch_filter(large_dict, test_keys):
    """✅ 終極優化：批量過濾策略

    最小化字典查詢次數：
    - 預先過濾存在的鍵
    - 批量處理，避免逐一查詢
    """
    # 快速分離存在和缺失的鍵
    dict_keys = set(large_dict.keys())

    results = []
    for key in test_keys:
        if key in dict_keys:
            results.append(large_dict[key])
        else:
            results.append("default_value")
    return results


# 優化版本字典
optimized_versions = {
    "get_simple": optimized_version_get_simple,
    "get_loop": optimized_version_get_loop,
    "defaultdict_lambda": optimized_version_defaultdict_lambda,
    "defaultdict_constant": optimized_version_defaultdict_constant,
    "batch_filter": optimized_version_batch_filter,
}
