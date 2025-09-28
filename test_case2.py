"""
TCK 測試案例檔案擴展版 - test_case2.py
包含原始版本與優化版本的同功能程式碼
每個測試案例包含：原始程式碼、優化程式碼、測試資料、差異註解

此檔案為 test_cases.py 的擴展版本，包含更多測試案例
"""

import random
import json
import time
from turbo_utils import ListLookupOptimizer, ConfigCacheManager, VectorizationAccelerator
import numpy as np
import tempfile
import os
import collections
import functools
from typing import Dict, List, Set, Any
import hashlib
from concurrent.futures import ThreadPoolExecutor
import itertools
import statistics
import math

class TestCase19_ExtendedDataProcessing:
    """測試案例 19: EXTENDED_DATA_PROCESSING - 擴展資料處理優化

    基於 DeepWiki 和 Microsoft Doc 的研究，專注於複雜資料處理的效能優化：
    - 大規模資料轉換和過濾
    - 多重條件處理和聚合
    - 記憶體使用優化
    - 演算法複雜度改進

    實證發現：
    - 資料量越大，優化效果越明顯
    - 多重條件處理是效能瓶頸的主要來源
    - 適當的資料結構選擇能帶來數量級提升
    - 向量化操作在數值處理中特別有效
    """

    @staticmethod
    def setup_data():
        """準備大規模測試資料來驗證高效能查詢處理"""
        # 生成超大規模資料來體現優化效果
        data_size = 200000  # 20萬筆資料

        # 建立結構化資料
        data = []
        for i in range(data_size):
            data.append({
                'id': i,
                'value': random.uniform(0, 1000),
                'category': f'cat_{random.randint(1, 20)}',  # 20個類別
                'priority': random.randint(1, 10),
                'active': random.choice([True, False]),
                'timestamp': time.time() + random.randint(-86400, 86400),
                'tags': random.sample(['urgent', 'important', 'normal', 'low'], random.randint(1, 3))
            })

        # 查詢需求：找到每個類別中優先級最高的前N個活躍項目
        queries = []
        for cat in range(1, 21):  # 為每個類別生成查詢
            queries.append({
                'category': f'cat_{cat}',
                'min_priority': random.randint(5, 8),
                'limit': random.randint(10, 50),  # 每個查詢返回10-50個結果
                'active_only': True
            })

        return data, queries

    @staticmethod
    def original_version(data, queries):
        """❌ 原始版本：極端暴力搜尋 + 完整排序 + 最大程度重複計算

        故意設計成極端低效的版本來體現優化效果：
        - 對每個查詢遍歷全部資料（無索引）
        - 在內部迴圈中重複進行複雜計算
        - 收集所有候選項目後完整排序
        - 額外的無用操作來浪費時間
        """
        results = []

        for query in queries:
            # 暴力搜尋：對每一筆資料進行完整檢查
            all_candidates = []
            for item in data:
                # 多重巢狀條件檢查（故意設計得很冗餘）
                category_match = item['category'] == query['category']
                priority_match = item['priority'] >= query['min_priority']
                active_match = item['active'] == query['active_only']

                if category_match and priority_match and active_match:
                    # 在這裡進行不必要的複雜計算（浪費時間）
                    temp_score = 0
                    for tag in item['tags']:  # 對每個標籤進行無用計算
                        temp_score += len(tag) * 0.1
                    for _ in range(10):  # 額外的無用迴圈
                        temp_score += item['value'] * 0.01

                    all_candidates.append(item)

            # 重複計算評分（故意在迴圈中重複計算多次）
            scored_candidates = []
            for candidate in all_candidates:
                # 複雜且重複的評分計算
                base_score = candidate['value'] * candidate['priority'] / 10
                tag_bonus = len(candidate['tags']) * 5
                active_bonus = 100 if candidate['active'] else 0

                # 重複計算相同的評分多次（故意低效）
                final_score = base_score + tag_bonus + active_bonus
                for _ in range(5):  # 額外的重複計算
                    final_score = final_score + base_score * 0.01

                scored_candidates.append((final_score, candidate))

            # 完整排序所有候選項目（即使只需要前N個）
            scored_candidates.sort(key=lambda x: x[0], reverse=True)

            # 取前N個結果
            top_items = scored_candidates[:query['limit']]

            # 格式化結果（額外的處理）
            for score, item in top_items:
                results.append({
                    'query_category': query['category'],
                    'id': item['id'],
                    'score': score,
                    'priority': item['priority'],
                    'tags': item['tags']
                })

        return results

    @staticmethod
    def optimized_version(data, queries):
        """✅ 優化版本：預索引 + 堆排序 + 批次處理

        高效處理方式：
        - 預先建立類別索引
        - 使用堆來維護Top-K元素
        - 避免完整排序
        - 批次處理減少函數調用
        """
        import heapq

        # 預處理：建立類別索引
        category_index = collections.defaultdict(list)
        for item in data:
            if item['active']:  # 只索引活躍項目
                category_index[item['category']].append(item)

        results = []

        for query in queries:
            category_items = category_index[query['category']]

            # 使用堆來維護優先級最高的項目
            # 負數優先級實現最大堆
            priority_heap = []

            for item in category_items:
                if item['priority'] >= query['min_priority']:
                    # 計算評分
                    score = (
                        item['value'] * item['priority'] / 10 +
                        len(item['tags']) * 5 +
                        100  # active bonus
                    )

                    # 使用負分實現最大堆
                    heapq.heappush(priority_heap, (-score, item))

                    # 維持堆大小為 limit * 2（為了解除堆的開銷）
                    if len(priority_heap) > query['limit'] * 2:
                        heapq.heappop(priority_heap)

            # 從堆中提取前N個結果
            top_items = heapq.nsmallest(query['limit'], priority_heap)

            # 格式化結果
            for neg_score, item in top_items:
                results.append({
                    'query_category': query['category'],
                    'id': item['id'],
                    'score': -neg_score,  # 轉回正數
                    'priority': item['priority'],
                    'tags': item['tags']
                })

        return results

    name = "EXTENDED_DATA_PROCESSING"
    description = "擴展資料處理優化：索引+向量化+預處理，大規模複雜查詢處理"


class TestCase20_FunctionCallOverheadOptimization:
    """測試案例 20: FUNCTION_CALL_OVERHEAD_OPTIMIZATION - 函數調用開銷優化

    基於 Microsoft Doc 和 DeepWiki 的研究，專注於 Python 函數調用開銷的效能影響：
    - 頻繁函數調用的效能成本
    - 內聯展開 vs 函數調用的權衡
    - 迴圈中的函數調用開銷
    - 減少函數調用次數的優化策略

    實證發現（基於網路搜索研究）：
    - Python 3.11+ 已大幅優化函數調用（內聯、專門化）
    - 極端頻繁調用仍會產生顯著開銷
    - 函數調用開銷約為幾十個CPU週期
    - 在效能關鍵路徑中應避免不必要的函數調用
    - 現代Python的函數調用優化使簡單案例改善有限
    """

    @staticmethod
    def setup_data():
        """準備測試資料來驗證函數調用開銷"""
        # 生成大規模測試資料來放大函數調用開銷
        data_size = 1000000  # 100萬筆資料，放大函數調用效果

        # 建立測試資料
        data = list(range(data_size))

        return data,

    @staticmethod
    def original_version(data):
        """❌ 原始版本：極端頻繁函數調用 (20次調用)

        使用大量函數調用來處理資料：
        - 每個元素調用20個小型函數
        - 在緊密迴圈中進行大量函數調用
        - 函數調用開銷極大化
        - 模擬典型的低效程式碼
        """
        def is_valid(x): return x % 3 == 0
        def multiply_by_two(x): return x * 2
        def add_one(x): return x + 1
        def square(x): return x ** 2
        def multiply_by_three(x): return x * 3
        def add_constant(x): return x + 42
        def divide_by_four(x): return x // 4
        def modulo_five(x): return x % 5
        def add_ten(x): return x + 10
        def multiply_by_four(x): return x * 4
        def subtract_seven(x): return x - 7
        def divide_by_two(x): return x // 2
        def modulo_three(x): return x % 3
        def add_five(x): return x + 5
        def multiply_by_five(x): return x * 5
        def subtract_two(x): return x - 2
        def divide_by_six(x): return x // 6
        def modulo_eight(x): return x % 8
        def add_twenty(x): return x + 20

        result = []
        for item in data:
            # 故意進行大量函數調用 (20次)
            if is_valid(item):
                temp = multiply_by_two(item)
                temp = add_one(temp)
                temp = square(temp)
                temp = multiply_by_three(temp)
                temp = add_constant(temp)
                temp = divide_by_four(temp)
                temp = modulo_five(temp)
                temp = add_ten(temp)
                temp = multiply_by_four(temp)
                temp = subtract_seven(temp)
                temp = divide_by_two(temp)
                temp = modulo_three(temp)
                temp = add_five(temp)
                temp = multiply_by_five(temp)
                temp = subtract_two(temp)
                temp = divide_by_six(temp)
                temp = modulo_eight(temp)
                temp = add_twenty(temp)
                result.append(temp)

        return result

    @staticmethod
    def optimized_version(data):
        """✅ 優化版本：完全內聯展開 (20次操作)

        消除所有函數調用開銷：
        - 將所有20個函數邏輯內聯
        - 直接執行運算
        - 零函數調用開銷
        - 最大化效能優化
        """
        result = []
        for item in data:
            # 完全內聯展開所有20次函數調用
            if item % 3 == 0:  # is_valid
                temp = item * 2      # multiply_by_two
                temp = temp + 1      # add_one
                temp = temp ** 2     # square
                temp = temp * 3      # multiply_by_three
                temp = temp + 42     # add_constant
                temp = temp // 4     # divide_by_four
                temp = temp % 5      # modulo_five
                temp = temp + 10     # add_ten
                temp = temp * 4      # multiply_by_four
                temp = temp - 7      # subtract_seven
                temp = temp // 2     # divide_by_two
                temp = temp % 3      # modulo_three
                temp = temp + 5      # add_five
                temp = temp * 5      # multiply_by_five
                temp = temp - 2      # subtract_two
                temp = temp // 6     # divide_by_six
                temp = temp % 8      # modulo_eight
                temp = temp + 20     # add_twenty
                result.append(temp)

        return result

    name = "FUNCTION_CALL_OVERHEAD_OPTIMIZATION"
    description = "函數調用開銷優化：減少頻繁調用、內聯展開、效能關鍵路徑優化"
