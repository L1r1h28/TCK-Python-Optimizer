"""
TCK Case 019: 擴展資料處理優化

對應藍圖：019_EXTENDED_DATA_PROCESSING_HEAP_INDEX_OPTIMIZATION.md
優化策略：暴力搜尋 → 預索引 + 堆排序 + 批次處理
效能提升：10-50x（大規模複雜查詢）
"""

import random
import collections
import heapq

# 測試案例名稱
name = "case_019_extended_data_processing"
description = "擴展資料處理優化：暴力搜尋 → 預索引 + 堆排序。"


def setup_data():
    """準備大規模測試資料來驗證高效能查詢處理"""
    data_size = 50000
    data = [
        {
            "id": i,
            "value": random.uniform(0, 1000),
            "category": f"cat_{random.randint(1, 20)}",
            "priority": random.randint(1, 10),
            "active": random.choice([True, False]),
        }
        for i in range(data_size)
    ]

    queries = [
        {
            "category": f"cat_{cat}",
            "min_priority": random.randint(5, 8),
            "limit": random.randint(10, 30),
            "active_only": True,
        }
        for cat in range(1, 11)
    ]

    return data, queries


def unoptimized_version(data, queries):
    """❌ 原始版本：極端暴力搜尋 + 完整排序"""
    results = {}
    for query in queries:
        candidates = []
        for item in data:
            if (
                item["category"] == query["category"]
                and item["priority"] >= query["min_priority"]
                and item["active"] == query["active_only"]
            ):
                candidates.append(item)

        # 完整排序
        candidates.sort(key=lambda x: x["priority"], reverse=True)
        results[query["category"]] = [
            item["id"] for item in candidates[: query["limit"]]
        ]
    return results


def optimized_version_heap_index(data, queries):
    """✅ 優化版本：預索引 + 堆排序"""
    # 1. 預索引
    indexed_data = collections.defaultdict(list)
    for item in data:
        if item["active"]:
            indexed_data[item["category"]].append(item)

    results = {}
    for query in queries:
        category = query["category"]
        limit = query["limit"]
        min_priority = query["min_priority"]

        # 2. 從索引中獲取候選
        candidates = [
            item
            for item in indexed_data.get(category, [])
            if item["priority"] >= min_priority
        ]

        # 3. 使用堆排序找到 Top-N
        if len(candidates) > limit:
            top_n = heapq.nlargest(limit, candidates, key=lambda x: x["priority"])
        else:
            top_n = sorted(candidates, key=lambda x: x["priority"], reverse=True)

        results[category] = [item["id"] for item in top_n]
    return results


# 優化版本字典
optimized_versions = {"heap_and_index": optimized_version_heap_index}
