"""
TCK Case 003: 配置檔案快取優化

對應藍圖：blueprint_003_config_load.md
優化策略：重複檔案讀取 → 記憶體快取機制
效能提升：5-10x（取決於 I/O 速度和檔案大小）

詳細實現請參考：optimization_blueprints/blueprint_003_config_load.md
"""

import json
import tempfile
import os
import functools

# --- 測試案例設定 ---
name = "CONFIG_LOAD"
description = "配置快取：重複檔案讀取 → 記憶體快取，避免 I/O 瓶頸"
blueprint_file = "blueprint_003_config_load.md"

# --- 測試資料生成與清理 ---
# 將暫存檔案路徑儲存在模組級別，以便清理
_temp_config_path = None


def setup_data():
    """準備測試資料：建立一個暫存的 JSON 設定檔"""
    global _temp_config_path
    config_data = {
        "database": {"host": "localhost", "port": 5432},
        "cache": {"timeout": 300, "size": 1000},
        "features": ["logging", "monitoring", "analytics"],
        "version": "1.2.3",
    }
    # 使用 delete=False 確保檔案在關閉後仍然存在
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        json.dump(config_data, f)
        _temp_config_path = f.name

    # 返回檔案路徑和重複讀取次數
    return _temp_config_path, 100


def cleanup_data(temp_config_path, repeat_count):
    """清理測試資料：刪除暫存檔案"""
    # 確保比較的檔案路徑是同一個
    if temp_config_path and os.path.exists(temp_config_path):
        os.unlink(temp_config_path)
        # 清理快取，避免影響下一個測試
        load_config_lru_cached.cache_clear()


# --- 未優化版本 ---
def unoptimized_version(temp_config_path, repeat_count):
    """❌ 原始版本：在迴圈中重複讀取和解析檔案"""
    results = []
    for _ in range(repeat_count):
        with open(temp_config_path, "r", encoding="utf-8") as f:
            data = json.load(f)  # 每次都觸發磁碟 I/O 和 JSON 解析
            results.append(data["database"]["host"])
    return results


# --- 優化版本 ---
# 將快取函式定義在模組層級，以便在 cleanup 中可以清除快取
@functools.lru_cache(maxsize=128)
def load_config_lru_cached(file_path):
    """使用 @lru_cache 裝飾器實現自動快取的載入函式"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def optimized_v1_lru_cache(temp_config_path, repeat_count):
    """✅ 優化 V1：使用 functools.lru_cache 實現記憶體快取"""
    results = []
    for _ in range(repeat_count):
        # 只有第一次呼叫會真正讀取檔案，後續直接從記憶體返回快取結果
        data = load_config_lru_cached(temp_config_path)
        results.append(data["database"]["host"])
    return results


# --- 優化版本字典 ---
optimized_versions = {
    "LRU_CACHE": optimized_v1_lru_cache,
}
