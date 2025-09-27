# 🚀 向量化轉換器

## 🎯 優化目標
**將 Python 迴圈轉換為 NumPy 向量化運算**

## 📊 實際測試結果
- **等級**: C級 (48.5分) ⚠️  
- **加速倍率**: **1.4x** (效果有限)
- **適用場景**: **僅限超大資料集 (100k+ 元素)**
- **成功率**: 30% (小資料集反而變慢)

## 🚨 重要警告
**小資料集使用向量化會因 NumPy 初始化開銷反而變慢！**

## 🔧 核心程式碼範本

### 數值運算向量化
```python
import numpy as np

# ❌ 原始程式碼 - Python 迴圈 (小資料集適用)
def multiply_python(data, factor):
    result = []
    for item in data:
        result.append(item * factor)
    return result

# ✅ 優化程式碼 - NumPy 向量化 (大資料集適用)
def multiply_vectorized(data, factor):
    return np.array(data) * factor

# ⚠️ 適用場景判斷
def smart_multiply(data, factor):
    if len(data) > 100000:  # 大資料集才使用向量化
        return np.array(data) * factor
    else:  # 小資料集使用 Python 原生
        return [item * factor for item in data]
```

### 統計運算向量化
```python
# ❌ 原始程式碼 - 手動計算
def calculate_stats_python(data):
    n = len(data)
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    std_dev = variance ** 0.5
    return {"mean": mean, "std": std_dev}

# ✅ 優化程式碼 - NumPy 內建函數 (僅大資料集)
def calculate_stats_vectorized(data):
    arr = np.array(data)
    return {
        "mean": np.mean(arr),
        "std": np.std(arr)
    }
```

### 條件過濾向量化
```python
# ❌ 原始程式碼 - 迴圈過濾
def filter_positive_python(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item)
    return result

# ✅ 優化程式碼 - 向量化過濾 (僅大資料集)
def filter_positive_vectorized(data):
    arr = np.array(data)
    return arr[arr > 0].tolist()

# 🔥 最佳實作 - 智能選擇
def filter_positive_smart(data):
    if len(data) > 50000:  # 大資料集使用 NumPy
        arr = np.array(data)
        return arr[arr > 0].tolist()
    else:  # 小資料集使用推導式
        return [x for x in data if x > 0]
```

## 🎯 使用指南

### ✅ 建議使用場景
- **科學計算**: 大型數值陣列運算
- **機器學習**: 特徵工程、矩陣運算
- **影像處理**: 像素級運算
- **資料分析**: 大型 DataFrame 運算
- **訊號處理**: 時間序列分析

### ⚠️ 效能閾值
- **< 1,000 元素**: 不建議使用，Python 原生更快
- **1,000 - 10,000 元素**: 效果不明顯
- **10,000 - 100,000 元素**: 小幅提升 (1.2-1.5x)
- **> 100,000 元素**: 顯著提升 (2-10x)

### 🚨 不適用場景
- 小資料集 (< 10,000 元素)
- 複雜邏輯運算 (無法向量化)
- 字串處理
- 記憶體敏感環境

## 💡 實際範例

### 範例 1: 資料清理 (謹慎使用)
```python
# ❌ 小資料集 - 使用原生 Python
small_data = list(range(1000))
result = [x * 2 for x in small_data if x > 500]  # 更快

# ✅ 大資料集 - 使用 NumPy
large_data = list(range(1000000))
arr = np.array(large_data)
result = arr[arr > 500000] * 2  # 顯著更快
```

### 範例 2: 智能閾值判斷
```python
def smart_process(data, threshold=10000):
    """根據資料大小智能選擇處理方式"""
    if len(data) < threshold:
        # 小資料集：使用 Python 原生
        return [x ** 2 + 1 for x in data if x > 0]
    else:
        # 大資料集：使用 NumPy 向量化
        arr = np.array(data)
        mask = arr > 0
        return (arr[mask] ** 2 + 1).tolist()

# 使用範例
small_result = smart_process(list(range(100)))      # Python 原生
large_result = smart_process(list(range(100000)))   # NumPy 向量化
```

### 範例 3: 錯誤示範 (避免)
```python
# 🚨 錯誤 - 小資料集強用 NumPy (反而變慢)
def bad_example(small_list):
    arr = np.array(small_list)          # 不必要的轉換開銷
    return np.sum(arr) / len(arr)       # 簡單運算不需要 NumPy

# ✅ 正確 - 小資料集使用原生
def good_example(small_list):
    return sum(small_list) / len(small_list)  # 原生更快
```

## 🧪 效能測試建議

```python
import time
import numpy as np

def benchmark_comparison(data_size):
    data = list(range(data_size))
    
    # 測試 Python 原生
    start = time.time()
    result1 = [x * 2 for x in data]
    python_time = time.time() - start
    
    # 測試 NumPy 向量化
    start = time.time()
    result2 = (np.array(data) * 2).tolist()
    numpy_time = time.time() - start
    
    speedup = python_time / numpy_time
    print(f"資料量: {data_size:,}")
    print(f"Python: {python_time:.4f}s")
    print(f"NumPy:  {numpy_time:.4f}s")
    print(f"加速倍率: {speedup:.2f}x")
    return speedup

# 測試不同資料量
for size in [100, 1000, 10000, 100000, 1000000]:
    benchmark_comparison(size)
    print("-" * 30)
```

---

**實測結論**: 只在超大資料集 (100k+) 使用，小資料集請繼續使用 Python 原生語法 ⚠️