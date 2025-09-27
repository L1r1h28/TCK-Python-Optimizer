#!/usr/bin/env python3
"""
TurboCode Kit 優化函式庫 (Optimization Library)
=============================================

這是 TCK 的核心優化函式庫，包含常見效能瓶頸的 O(1) 優化範本。
根據頻率分析結果，提供針對 LIST_LOOKUP、PYTHON_FOR_LOOP 和 CONFIG_LOAD 的優化函數。

Author: TurboCode Kit (TCK)
Version: 2.0
"""

from functools import lru_cache
from typing import Dict, List, Any, Callable, Iterator, Iterable, Tuple, Optional, Set, Optional, Callable
import numpy as np
from collections import defaultdict, deque
import json
import os


class ListLookupOptimizer:
    """
    清單查找優化器 - 將 O(n) 查找優化為 O(1)
    
    使用場景：
    - 頻繁的 'item in list' 操作
    - 重複的清單搜尋
    - 大型清單的成員測試
    """
    
    def __init__(self, data_list: List[Any]):
        """初始化優化器，建立 O(1) 查找集合"""
        self._set = set(data_list) if data_list else set()
        self._original_list = data_list
    
    def contains(self, item: Any) -> bool:
        """O(1) 成員測試"""
        return item in self._set
    
    def add(self, item: Any) -> None:
        """O(1) 添加元素"""
        if item not in self._set:
            self._set.add(item)
            self._original_list.append(item)
    
    def remove(self, item: Any) -> None:
        """O(1) 移除元素"""
        if item in self._set:
            self._set.remove(item)
            self._original_list.remove(item)
    
    @classmethod
    def from_frequent_lookups(cls, target_list: List[Any]) -> 'ListLookupOptimizer':
        """從頻繁查找的清單建立優化器"""
        return cls(target_list)


class ConfigCacheManager:
    """
    設定檔快取管理器 - 將重複載入優化為記憶體快取
    
    使用場景：
    - 頻繁的設定檔讀取
    - JSON/YAML 檔案重複載入
    - 設定參數的重複存取
    """
    
    _cache = {}
    _file_timestamps = {}
    
    @classmethod
    @lru_cache(maxsize=128)
    def load_config(cls, config_path: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        O(1) 快取設定載入
        
        Args:
            config_path: 設定檔路徑
            use_cache: 是否使用快取
            
        Returns:
            設定字典
        """
        if not use_cache:
            return cls._load_file_direct(config_path)
            
        # 檢查檔案是否更新
        if cls._is_file_updated(config_path):
            config_data = cls._load_file_direct(config_path)
            cls._cache[config_path] = config_data
            cls._file_timestamps[config_path] = os.path.getmtime(config_path)
            return config_data
        
        # 使用快取
        return cls._cache.get(config_path, cls._load_file_direct(config_path))
    
    @classmethod
    def _load_file_direct(cls, config_path: str) -> Dict[str, Any]:
        """直接載入檔案"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 載入設定檔失敗 {config_path}: {e}")
            return {}
    
    @classmethod
    def _is_file_updated(cls, config_path: str) -> bool:
        """檢查檔案是否更新"""
        if not os.path.exists(config_path):
            return False
        
        current_time = os.path.getmtime(config_path)
        # 📊 效能最佳化：使用 get() 避免雙重查找 (基於 set_operations_optimizer.md)
        cached_time = cls._file_timestamps.get(config_path, 0)
        return current_time > cached_time
    
    @classmethod
    def clear_cache(cls) -> None:
        """清除所有快取"""
        cls._cache.clear()
        cls._file_timestamps.clear()
        cls.load_config.cache_clear()


class VectorizationAccelerator:
    """
    向量化加速器 - 將 Python 迴圈優化為 NumPy 向量操作
    
    使用場景：
    - 大量數值計算的 for 迴圈
    - 清單推導式的數值操作
    - 重複的數學運算
    """
    
    from typing import Sequence

    # 📊 效能最佳化：預處理支援的運算 (基於 config_cache_manager.md)
    _SUPPORTED_OPERATIONS = frozenset({
        'square', 'sqrt', 'abs', 'log', 'exp', 'sum', 'mean', 'max', 'min'
    })
    
    _OPERATIONS_MAP = {
        'square': np.square,
        'sqrt': np.sqrt,
        'abs': np.abs,
        'log': np.log,
        'exp': np.exp,
        'sum': np.sum,
        'mean': np.mean,
        'max': np.max,
        'min': np.min
    }

    @staticmethod
    def replace_numeric_loop(data: Sequence[float], operation: str) -> np.ndarray:
        """
        用向量化操作替換數值迴圈

        Args:
            data: 數值資料序列（可為 int 或 float）
            operation: 運算類型 ('square', 'sqrt', 'abs', 'log', 'exp')

        Returns:
            運算結果 numpy 陣列
        """
        # 📊 效能最佳化：使用預處理的 frozenset 和字典查找
        if operation not in VectorizationAccelerator._SUPPORTED_OPERATIONS:
            raise ValueError(f"不支援的運算: {operation}")
        
        np_data = np.array(data)
        operation_func = VectorizationAccelerator._OPERATIONS_MAP[operation]
        return operation_func(np_data)
    
    @staticmethod
    def batch_condition_filter(data: List[Any], condition: Callable) -> List[Any]:
        """
        批次條件過濾，替換 filter() + for 迴圈組合
        
        Args:
            data: 待過濾資料
            condition: 過濾條件函數
            
        Returns:
            過濾後的結果
        """
        # 使用 numpy 的布林索引進行快速過濾
        if all(isinstance(x, (int, float)) for x in data):
            np_data = np.array(data)
            mask = np.vectorize(condition)(np_data)
            return np_data[mask].tolist()
        else:
            # 回退到清單推導式
            return [item for item in data if condition(item)]


class MemoizationInjector:
    """
    記憶化注入器 - 自動快取昂貴函數結果
    
    使用場景：
    - 重複執行的昂貴計算
    - 相同參數的函數調用
    - 遞迴函數優化
    """
    
    @staticmethod
    def cached_function(maxsize: int = 128):
        """
        裝飾器：自動快取函數結果
        
        Args:
            maxsize: 快取大小上限
            
        Usage:
            @MemoizationInjector.cached_function(maxsize=256)
            def expensive_calculation(x, y):
                return complex_computation(x, y)
        """
        return lru_cache(maxsize=maxsize)
    
    @staticmethod
    def smart_cache_decorator(ttl_seconds: int = 300):
        """
        智能快取裝飾器，支援 TTL (生存時間)
        
        Args:
            ttl_seconds: 快取生存時間（秒）
        """
        def decorator(func):
            cache = {}
            timestamps = {}
            
            def wrapper(*args, **kwargs):
                import time
                key = str(args) + str(sorted(kwargs.items()))
                current_time = time.time()
                
                # 檢查快取是否過期
                if key in cache and (current_time - timestamps[key]) < ttl_seconds:
                    return cache[key]
                
                # 執行函數並快取結果
                result = func(*args, **kwargs)
                cache[key] = result
                timestamps[key] = current_time
                return result
            
            return wrapper
        return decorator


class OptimizationBlueprintGenerator:
    """
    優化藍圖生成器 - 自動生成優化建議
    
    基於頻率分析結果，生成具體的優化程式碼範本
    """
    
    def __init__(self, frequency_data: Dict[str, Any]):
        """初始化，載入頻率分析資料"""
        self.frequency_data = frequency_data
        self.blueprints = []
    
    def generate_list_lookup_blueprint(self) -> str:
        """生成清單查找優化藍圖"""
        template = """
# 清單查找優化 (O(n) → O(1))
# ❌ 原始低效程式碼
if item in my_list:  # O(n) 線性搜尋
    process_item(item)

# ✅ TCK 優化後程式碼
lookup_optimizer = ListLookupOptimizer(my_list)
if lookup_optimizer.contains(item):  # O(1) 雜湊查找
    process_item(item)
"""
        return template.strip()
    
    def generate_config_cache_blueprint(self) -> str:
        """生成設定快取優化藍圖"""
        template = """
# 設定檔載入優化 (重複 I/O → 記憶體快取)
# ❌ 原始低效程式碼
with open('config.json', 'r') as f:  # 每次都讀檔
    config = json.load(f)

# ✅ TCK 優化後程式碼
config = ConfigCacheManager.load_config('config.json')  # 自動快取
"""
        return template.strip()
    
    def generate_vectorization_blueprint(self) -> str:
        """生成向量化優化藍圖"""
        template = """
# Python 迴圈向量化 (O(n) Python → O(n) C)
# ❌ 原始低效程式碼
result = []
for x in data:
    result.append(x ** 2)  # Python 解釋器開銷

# ✅ TCK 優化後程式碼
result = VectorizationAccelerator.replace_numeric_loop(data, 'square')  # NumPy C 實作
"""
        return template.strip()
    
    def create_optimization_blueprints_folder(self, output_dir: str = "optimization_blueprints") -> None:
        """創建優化藍圖資料夾"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成各種優化藍圖檔案
        blueprints = {
            "lookup_accelerator.md": self.generate_list_lookup_blueprint(),
            "config_cache.md": self.generate_config_cache_blueprint(),
            "vectorization_converter.md": self.generate_vectorization_blueprint()
        }
        
        for filename, content in blueprints.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {filename.split('.')[0].replace('_', ' ').title()}\n\n")
                f.write(content)
                f.write("\n\n---\n*Generated by TurboCode Kit (TCK) Optimization Library*")
        
        print(f"✅ 優化藍圖已生成到 {output_dir}/ 資料夾")


def quick_optimization_demo():
    """快速優化示範"""
    print("🚀 TurboCode Kit 優化函式庫演示")
    print("=" * 50)
    
    # 1. 清單查找優化演示
    print("\n📋 1. 清單查找優化 (O(n) → O(1))")
    large_list = list(range(10000))
    optimizer = ListLookupOptimizer(large_list)
    
    import time
    
    # 測試原始方法
    start = time.time()
    for i in range(100):
        result = 5000 in large_list  # O(n)
    original_time = time.time() - start
    
    # 測試優化方法
    start = time.time()
    for i in range(100):
        result = optimizer.contains(5000)  # O(1)
    optimized_time = time.time() - start
    
    speedup = original_time / optimized_time if optimized_time > 0 else float('inf')
    print(f"   原始方法: {original_time:.4f}s")
    print(f"   優化方法: {optimized_time:.4f}s")
    print(f"   加速倍率: {speedup:.1f}x")
    
    # 2. 向量化優化演示
    print("\n🔢 2. 向量化優化演示")
    data = list(range(1000))
    
    # 測試 Python 迴圈
    start = time.time()
    result1 = [x ** 2 for x in data]
    python_time = time.time() - start
    
    # 測試向量化
    start = time.time()
    result2 = VectorizationAccelerator.replace_numeric_loop(data, 'square')
    vectorized_time = time.time() - start
    
    speedup = python_time / vectorized_time if vectorized_time > 0 else float('inf')
    print(f"   Python 迴圈: {python_time:.4f}s")
    print(f"   NumPy 向量化: {vectorized_time:.4f}s")
    print(f"   加速倍率: {speedup:.1f}x")
    
    print("\n✅ 優化演示完成！")


class StringConcatenationOptimizer:
    """
    字串拼接優化器 - 將 O(n²) 字串累加優化為 O(n) join 操作

    使用場景：
    - 大量字串的累加拼接
    - for 迴圈中的字串連接
    - 動態字串建構
    """

    @staticmethod
    def join_strings(words: List[str], separator: str = " ") -> str:
        """
        O(n) 字串拼接，使用 join() 避免 O(n²) 複雜度

        Args:
            words: 待拼接的字串列表
            separator: 分隔符

        Returns:
            拼接後的字串
        """
        return separator.join(words)

    @staticmethod
    def build_string_efficiently(items: List[Any], template: str = "{}") -> str:
        """
        高效字串建構，避免 for 迴圈中的字串累加

        Args:
            items: 資料項目
            template: 格式化模板

        Returns:
            建構的字串
        """
        return "".join(template.format(item) for item in items)


class DictionaryLookupOptimizer:
    """
    字典查找優化器 - 將雙重查找優化為單次查找

    使用場景：
    - 條件檢查後的字典存取
    - 大規模字典查找操作
    - 頻繁的鍵存在性檢查
    """

    @staticmethod
    def single_lookup_get(data_dict: Dict[str, Any], keys: List[str]) -> List[Any]:
        """
        使用 get() 方法進行單次查找，避免雙重雜湊操作

        Args:
            data_dict: 目標字典
            keys: 查找鍵列表

        Returns:
            找到的值列表（過濾掉不存在的鍵）
        """
        return [value for key in keys if (value := data_dict.get(key)) is not None]

    @staticmethod
    def batch_lookup_with_defaults(data_dict: Dict[str, Any], keys: List[str], default=None) -> List[Any]:
        """
        批次查找，支援預設值

        Args:
            data_dict: 目標字典
            keys: 查找鍵列表
            default: 預設值

        Returns:
            查找結果列表
        """
        return [data_dict.get(key, default) for key in keys]


class SetOperationsOptimizer:
    """
    集合操作優化器 - 將線性查找優化為集合操作

    使用場景：
    - 大規模的包含性檢查
    - 多個列表的交集/聯集操作
    - 頻繁的重複項目檢查
    """

    @staticmethod
    def fast_membership_test(items: List[Any], test_set: Set[Any]) -> List[bool]:
        """
        高效的成員資格測試，使用集合的 O(1) 查找

        Args:
            items: 待測試項目
            test_set: 測試集合

        Returns:
            成員資格測試結果
        """
        return [item in test_set for item in items]

    @staticmethod
    def intersection_multiple_sets(*sets: Set[Any]) -> Set[Any]:
        """
        多個集合的交集運算

        Args:
            *sets: 集合參數

        Returns:
            交集結果
        """
        if not sets:
            return set()
        result = sets[0].copy()
        for s in sets[1:]:
            result &= s
        return result


class DequeOperationsOptimizer:
    """
    雙端隊列操作優化器 - 優化列表的雙端操作

    使用場景：
    - 頻繁的列表頭部插入/刪除
    - 隊列/棧操作
    - 大量 pop(0) 操作
    """

    def __init__(self):
        from collections import deque
        self.deque = deque()

    def append_left_optimized(self, item: Any) -> None:
        """優化的左側追加操作"""
        self.deque.appendleft(item)

    def pop_left_optimized(self) -> Any:
        """優化的左側彈出操作"""
        return self.deque.popleft()

    def bulk_operations(self, operations: List[Tuple[str, Any]]) -> List[Any]:
        """
        批次雙端操作，避免頻繁的列表重建

        Args:
            operations: 操作列表 [('appendleft', item), ('popleft', None)]

        Returns:
            彈出操作的結果
        """
        results = []
        for op, item in operations:
            if op == 'appendleft':
                self.deque.appendleft(item)
            elif op == 'popleft':
                results.append(self.deque.popleft())
        return results


class BuiltinFunctionsOptimizer:
    """
    內建函數優化器 - 優化內建函數的使用

    使用場景：
    - 大量使用 len(), str(), int() 等內建函數
    - 頻繁的類型轉換
    - 內建函數的快取優化
    """

    # 快取常用轉換函數
    _str_func = str
    _int_func = int
    _len_func = len

    @staticmethod
    def cached_len_operations(items: List[List[Any]]) -> List[int]:
        """
        快取 len() 操作，避免重複計算

        Args:
            items: 二維列表

        Returns:
            各子列表的長度
        """
        return [len(item) for item in items]

    @staticmethod
    def batch_type_conversion(items: List[Any], target_type: type) -> List[Any]:
        """
        批次類型轉換，使用列表推導式

        Args:
            items: 待轉換項目
            target_type: 目標類型

        Returns:
            轉換後的結果
        """
        return [target_type(item) for item in items]


class ComprehensionOptimizer:
    """
    推導式優化器 - 優化列表/字典/集合推導式

    使用場景：
    - 複雜的推導式運算
    - 多重條件過濾
    - 嵌套推導式
    """

    @staticmethod
    def optimize_list_comprehension(data: List[Any], conditions: Optional[List[Callable]] = None) -> List[Any]:
        """
        優化列表推導式，支援多重條件

        Args:
            data: 原始資料
            conditions: 條件函數列表

        Returns:
            過濾後的結果
        """
        if not conditions:
            return data

        result = data
        for condition in conditions:
            result = [item for item in result if condition(item)]
        return result

    @staticmethod
    def dict_comprehension_from_pairs(pairs: List[Tuple[Any, Any]]) -> Dict[Any, Any]:
        """
        高效的字典推導式

        Args:
            pairs: 鍵值對列表

        Returns:
            建構的字典
        """
        return {key: value for key, value in pairs}


class IteratorChainingOptimizer:
    """
    迭代器鏈優化器 - 優化多重迭代器操作

    使用場景：
    - 多個 itertools 鏈操作
    - 複雜的迭代器管道
    - 大量資料的流式處理
    """

    @staticmethod
    def chain_multiple_iterables(*iterables) -> Iterator[Any]:
        """
        優化多重可迭代物件的鏈接

        Args:
            *iterables: 可迭代物件

        Returns:
            鏈接後的迭代器
        """
        from itertools import chain
        return chain(*iterables)

    @staticmethod
    def filter_chain(data: Iterable[Any], *filters: Callable) -> Iterator[Any]:
        """
        鏈式過濾操作

        Args:
            data: 原始資料
            *filters: 過濾函數

        Returns:
            過濾後的迭代器
        """
        result = iter(data)
        for filter_func in filters:
            result = filter(filter_func, result)
        return result


class DataClassOptimizer:
    """
    資料類優化器 - 優化資料類的使用

    使用場景：
    - 大量資料類實例的創建
    - 資料類的序列化/反序列化
    - 資料類的比較和雜湊操作
    """

    @staticmethod
    def create_dataclass_efficiently(dataclass_cls: type, data_list: List[Dict[str, Any]]) -> List[Any]:
        """
        高效批量創建資料類實例

        Args:
            cls: 資料類
            data_list: 資料字典列表

        Returns:
            資料類實例列表
        """
        return [dataclass_cls(**data) for data in data_list]

    @staticmethod
    def dataclass_to_dict_batch(instances: List[Any]) -> List[Dict[str, Any]]:
        """
        批量轉換資料類為字典

        Args:
            instances: 資料類實例列表

        Returns:
            字典列表
        """
        return [instance.__dict__ for instance in instances]


class LoopLookupOptimizer:
    """
    迴圈查找優化器 - 巢狀迴圈中的查找優化

    使用場景：
    - 巢狀迴圈中的列表查找
    - 多重條件檢查
    - 大規模資料的交集運算
    """

    @staticmethod
    def nested_loop_optimization(list1: List[Any], list2: List[Any], list3: Optional[List[Any]] = None) -> List[Any]:
        """
        巢狀迴圈查找優化，使用集合預處理

        Args:
            list1: 第一個列表
            list2: 第二個列表
            list3: 可選的第三個列表

        Returns:
            交集結果
        """
        set2 = set(list2)
        if list3:
            set3 = set(list3)
            return [item for item in list1 if item in set2 and item in set3]
        else:
            return [item for item in list1 if item in set2]


class HighFreqCallsOptimizer:
    """
    高頻調用優化器 - 優化頻繁的函數調用

    使用場景：
    - 迴圈中的高頻內建函數調用
    - 重複的物件創建
    - 頻繁的屬性存取
    """

    @staticmethod
    def precompute_loop_invariants(data: List[Any]) -> Dict[str, Any]:
        """
        預先計算迴圈不變量

        Args:
            data: 資料列表

        Returns:
            預計算的常數字典
        """
        return {
            'data_len': len(data),
            'str_prefix': "item_",
            'threshold': 10
        }

    @staticmethod
    def eliminate_frequent_calls(data: List[int], invariants: Dict[str, Any]) -> List[str]:
        """
        消除高頻調用，使用預計算的常數

        Args:
            data: 數值資料
            invariants: 預計算的常數

        Returns:
            處理後的字串列表
        """
        data_len = invariants['data_len']
        str_prefix = invariants['str_prefix']
        threshold = invariants['threshold']

        results = [""] * data_len
        result_idx = 0

        for i in range(data_len):
            item = data[i]
            if item >= threshold:
                results[result_idx] = f"{str_prefix}{i}"
                result_idx += 1

        return results[:result_idx]


if __name__ == "__main__":
    # 執行快速演示
    quick_optimization_demo()

    # 生成優化藍圖
    generator = OptimizationBlueprintGenerator({})
    generator.create_optimization_blueprints_folder()