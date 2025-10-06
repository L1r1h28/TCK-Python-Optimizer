"""
TCK 增強統計測試腳本 - 包含記憶體和 I/O 統計的中文版本
"""

import time
import json
import importlib.util
import argparse
import os
import gc
import inspect
import math
from pathlib import Path
from typing import List, Dict, Any, Optional

# 程式碼品質分析庫導入
try:
    from radon.visitors import ComplexityVisitor
    from radon.metrics import mi_visit
    from radon.raw import analyze as analyze_raw

    RADON_AVAILABLE = True
except ImportError:
    RADON_AVAILABLE = False
    ComplexityVisitor = None
    mi_visit = None
    analyze_raw = None
    print("⚠️  安裝 radon 以進行程式碼品質分析: pip install radon")

# 系統監控庫導入
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False
    print("⚠️  建議安裝 psutil: pip install psutil")

try:
    import GPUtil

    GPU_AVAILABLE = True
except ImportError:
    GPUtil = None
    GPU_AVAILABLE = False
    print("⚠️  安裝 GPUtil 以監控 GPU: pip install gputil")

import threading
import platform

SYSTEM_INFO_AVAILABLE = True


class TCKEnhancedAnalyzer:
    """TCK 增強統計分析器 - 包含完整的系統資源監控"""

    def __init__(self, cases_dir: str = "cases"):
        self.base_cases_dir = Path(cases_dir)
        self.results = {}
        self.test_cases = {}  # 改為字典來儲存案例
        print("📊 TCK 增強統計分析器啟動 (一對多模式)")
        print("=" * 60)

    def _analyze_code_quality(self, source_code: str) -> Dict[str, Any]:
        """使用 radon 分析原始碼的品質。"""
        if not RADON_AVAILABLE:
            return {
                "錯誤": "radon 套件未安裝",
                "圈複雜度": -1,
                "可維護性指數": -1,
                "程式碼行數": -1,
            }

        # 只有在 radon 可用時才執行以下程式碼
        try:
            # 1. 圈複雜度
            # mypy 會在此處報錯，因為它無法確定 ComplexityVisitor 已被定義
            # 但因為我們有 RADON_AVAILABLE 守衛，所以執行時是安全的
            visitor = ComplexityVisitor.from_code(source_code)  # type: ignore
            # 假設每個原始碼片段只有一個主要函式
            complexity = visitor.functions[0].complexity if visitor.functions else -1

            # 2. 可維護性指數
            maintainability_index = mi_visit(source_code, multi=True)  # type: ignore

            # 3. 原始碼指標 (行數)
            raw_metrics = analyze_raw(source_code)  # type: ignore
            sloc = raw_metrics.sloc

            # 4. 依賴套件數量分析
            import re
            import_lines = re.findall(r'^\s*(?:import|from)\s+(\w+)', source_code, re.MULTILINE)
            # 過濾標準庫和常見內建模組
            standard_libs = {
                'os', 'sys', 're', 'math', 'time', 'datetime', 'json', 'collections',
                'itertools', 'functools', 'operator', 'pathlib', 'typing', 'inspect',
                'gc', 'platform', 'threading', 'multiprocessing', 'subprocess'
            }
            external_deps = [imp for imp in import_lines if imp not in standard_libs]
            dependency_count = len(set(external_deps))  # 去重

            # 5. 技術棧複雜度分析
            tech_indicators = {
                'numpy': 2, 'numba': 3, 'pandas': 2, 'scipy': 2,
                'torch': 3, 'tensorflow': 3, 'jax': 3, 'cython': 3,
                'multiprocessing': 2, 'concurrent': 2, 'asyncio': 2
            }
            tech_complexity = 1  # 預設純 Python
            for dep in external_deps:
                if dep in tech_indicators:
                    tech_complexity = max(tech_complexity, tech_indicators[dep])

            return {
                "圈複雜度": complexity,
                "可維護性指數": maintainability_index,
                "程式碼行數": sloc,
                "依賴套件數量": dependency_count,
                "技術棧複雜度": tech_complexity,
            }
        except Exception as e:
            return {
                "錯誤": str(e),
                "圈複雜度": -1,
                "可維護性指數": -1,
                "程式碼行數": -1,
            }

    def discover_cases(self):
        """遞迴地從 cases 目錄及其子目錄（如 micro）中發現測試案例。- TCK 優化版本"""
        print(f"🔍 正在從 '{self.base_cases_dir}' 及其子目錄探索測試案例...")

        # 優化1: 使用生成器表達式進行文件過濾，減少記憶體使用
        valid_files = (
            path
            for path in self.base_cases_dir.rglob("*.py")
            if not path.name.startswith("__")
        )

        # 優化2: 批量處理模組載入，減少重複操作
        for path in valid_files:
            case_name = path.stem

            # 優化3: 使用 get() 替代可能的異常處理
            try:
                spec = importlib.util.spec_from_file_location(case_name, path)
                if not (spec and spec.loader):
                    print(f"⚠️ 無法為 {path} 建立模組規範。")
                    continue

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # 優化4: 使用 getattr() 與預設值，避免 AttributeError
                module_name = getattr(module, "name", case_name)
                self.test_cases[module_name] = module

            except Exception as e:
                print(f"❌ 載入測試案例 '{case_name}' 失敗: {e}")

        print(f"✅ 成功載入 {len(self.test_cases)} 個測試案例。")

    def load_test_cases(self) -> bool:
        """動態地從 'cases' 目錄及其所有子目錄中載入測試案例檔案。"""
        self.test_cases = {}
        if not self.base_cases_dir.is_dir():
            print(f"❌ 錯誤: 案例目錄 '{self.base_cases_dir}' 不存在或不是一個目錄。")
            return False

        print(f"🔍 正在從 '{self.base_cases_dir}' 及其子目錄探索測試案例...")

        # 使用 rglob 進行遞迴搜索
        for case_file in self.base_cases_dir.rglob("*.py"):
            if case_file.name.startswith("__"):
                continue

            try:
                module_name = case_file.stem
                spec = importlib.util.spec_from_file_location(module_name, case_file)
                if spec is None or spec.loader is None:
                    print(f"⚠️  警告: 無法為 '{case_file.name}' 創建模組規格。")
                    continue

                test_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(test_module)

                # 統一處理模組型案例
                case_name = getattr(test_module, "name", module_name)
                description = getattr(test_module, "description", "無描述")
                setup_data = getattr(test_module, "setup_data")
                unoptimized_func = getattr(test_module, "unoptimized_version")
                optimized_versions = getattr(test_module, "optimized_versions", {})

                # 檢查必要屬性是否存在
                if not all([case_name, description, setup_data, unoptimized_func]):
                    print(
                        f"⚠️  警告: 案例 '{case_file.name}' 缺少必要的屬性 (name, description, setup_data, unoptimized_version)。跳過此案例。"
                    )
                    continue

                self.test_cases[case_name] = {
                    "name": case_name,
                    "description": description,
                    "setup_data": setup_data,
                    "unoptimized": unoptimized_func,
                    "optimized_versions": optimized_versions,
                    "module": test_module,
                }
            except Exception as e:
                print(f"⚠️  警告: 載入案例 '{case_file.name}' 失敗: {e}")

        if not self.test_cases:
            print(f"❌ 錯誤: 在 '{self.base_cases_dir}' 中沒有找到任何有效的測試案例。")
            return False

        print(f"✅ 成功載入 {len(self.test_cases)} 個測試案例。")
        return True

    def run_test_case(self, case_name: str) -> Optional[Dict[str, Any]]:
        """
        執行單一測試案例（一對多版本），並收集所有版本的完整統計數據。
        """
        # 實現大小寫不敏感的查找
        target_key = next(
            (k for k in self.test_cases if k.lower() == case_name.lower()), None
        )

        if not target_key:
            print(f"❌ 找不到測試案例: {case_name}")
            self.list_tests()
            return None

        case_data = self.test_cases[target_key]

        print(f"\n🔍 測試案例: {case_data['name']}")
        print(f"📝 說明: {case_data['description']}")
        print("-" * 50)

        # 準備測試資料
        test_data = case_data["setup_data"]()

        # 1. 執行未優化版本作為基準 (重複測試以獲取統計可靠性)
        print("❌ 測試基準版本 (unoptimized)...")
        unoptimized_func = case_data["unoptimized"]
        baseline_results_list = []
        for i in range(3):  # 重複 3 次
            result = self.measure_comprehensive_performance(
                unoptimized_func, *test_data
            )
            if result["成功"]:
                baseline_results_list.append(result)
            if len(baseline_results_list) >= 2:  # 至少 2 次成功
                break

        if not baseline_results_list:
            print("❌ 基準版本執行失敗")
            return None

        # 計算統計：中位數和 IQR
        import statistics
        times = [r["純執行時間_秒"] for r in baseline_results_list]
        baseline_median_time = statistics.median(times)
        if len(times) > 1:
            baseline_iqr = statistics.quantiles(times, n=4)[2] - statistics.quantiles(times, n=4)[0]
        else:
            baseline_iqr = 0

        # 使用中位數作為基準
        baseline_results = baseline_results_list[0].copy()
        baseline_results["純執行時間_秒"] = baseline_median_time
        baseline_results["IQR_秒"] = baseline_iqr

        unoptimized_source = inspect.getsource(unoptimized_func)
        unoptimized_quality = self._analyze_code_quality(unoptimized_source)

        all_versions_results = {
            "unoptimized": {
                "metrics": baseline_results,
                "source": unoptimized_source,
                "quality": unoptimized_quality,
            }
        }

        # 2. 遍歷並測試所有優化版本
        optimized_versions = case_data.get("optimized_versions", {})
        if not optimized_versions:
            print("⚠️  警告: 該案例沒有提供優化版本。")
            # 即使沒有優化版本，也回傳基準測試的結果
            return {
                "測試名稱": case_data["name"],
                "測試描述": case_data["description"],
                "版本比較結果": all_versions_results,
                "成功": True,
            }

        for version_name, optimized_func in optimized_versions.items():
            print(f"✅ 測試優化版本: {version_name}...")

            # 重複測試優化版本
            optimized_results_list = []
            for i in range(3):
                result = self.measure_comprehensive_performance(
                    optimized_func, *test_data
                )
                if result["成功"]:
                    optimized_results_list.append(result)
                if len(optimized_results_list) >= 2:
                    break

            if not optimized_results_list:
                print(f"⚠️  優化版本 {version_name} 執行失敗")
                continue

            # 計算統計
            times = [r["純執行時間_秒"] for r in optimized_results_list]
            optimized_median_time = statistics.median(times)
            if len(times) > 1:
                optimized_iqr = statistics.quantiles(times, n=4)[2] - statistics.quantiles(times, n=4)[0]
            else:
                optimized_iqr = 0

            optimized_results = optimized_results_list[0].copy()
            optimized_results["純執行時間_秒"] = optimized_median_time
            optimized_results["IQR_秒"] = optimized_iqr

            # 計算與基準的比較指標
            comparison_metrics = self._compare_metrics(
                baseline_results, optimized_results
            )

            # 分析程式碼品質
            optimized_source = inspect.getsource(optimized_func)
            optimized_quality = self._analyze_code_quality(optimized_source)

            performance_scores = self._calculate_performance_score(
                comparison_metrics, optimized_quality, unoptimized_quality
            )
            total_score = performance_scores["總體效能評分"]
            practicality_score = performance_scores.get("實用性評分", 0)
            grade = self._get_performance_grade(total_score, practicality_score)

            all_versions_results[version_name] = {
                "metrics": optimized_results,
                "comparison": comparison_metrics,
                "scores": performance_scores,
                "grade": grade,
                "source": optimized_source,
                "quality": optimized_quality,
            }

            # 顯示即時結果
            print(f"  ⏱️  執行時間改善: {comparison_metrics['時間改善倍數']:.1f} 倍")
            print(f"  🏆 評分: {total_score:.1f}/100 - {grade}")

        # 3. 組合最終報告數據
        final_report = {
            "測試名稱": case_data["name"],
            "測試描述": case_data["description"],
            "版本比較結果": all_versions_results,
            "成功": True,
        }

        # 清理資源
        if hasattr(case_data["module"], "cleanup_data"):
            case_data["module"].cleanup_data(*test_data)

        return final_report

    def _get_comprehensive_system_stats(self) -> Dict[str, Any]:
        """取得完整系統統計資訊 - TCK 優化版本"""
        # 優化1: 使用字典推導式初始化數值統計 (減少重複鍵值對創建)
        numeric_keys = [
            "記憶體_MB",
            "虛擬記憶體_MB",
            "記憶體使用率_%",
            "讀取次數",
            "寫入次數",
            "讀取位元組",
            "寫入位元組",
            "CPU使用率_%",
            "系統記憶體使用率_%",
            "系統可用記憶體_GB",
            "磁碟使用率_%",
            "網路傳送_KB",
            "網路接收_KB",
            "GPU數量",
            "GPU使用率_%",
            "GPU記憶體使用_MB",
            "GPU溫度_C",
            "CPU核心數",
            "執行緒數",
        ]
        # 創建混合類型字典
        stats: Dict[str, Any] = {key: 0.0 for key in numeric_keys}
        stats["系統平台"] = "Unknown"

        # 優化2: 合併系統資訊收集，減少條件檢查
        if SYSTEM_INFO_AVAILABLE:
            stats["系統平台"] = platform.system()
            stats["CPU核心數"] = float(os.cpu_count() or 0)
            stats["執行緒數"] = float(threading.active_count())

        # 優化3: 使用 getattr() 避免異常處理，合併多個 update 調用
        if PSUTIL_AVAILABLE and psutil:
            try:
                process = psutil.Process()
                memory = process.memory_info()
                io_stats = process.io_counters()

                # 合併第一組統計數據
                process_stats = {
                    "記憶體_MB": memory.rss / 1024 / 1024,
                    "虛擬記憶體_MB": memory.vms / 1024 / 1024,
                    "記憶體使用率_%": process.memory_percent(),
                    "讀取次數": float(io_stats.read_count),
                    "寫入次數": float(io_stats.write_count),
                    "讀取位元組": float(io_stats.read_bytes),
                    "寫入位元組": float(io_stats.write_bytes),
                }

                # 合併第二組統計數據
                memory_info = psutil.virtual_memory()
                disk_info = psutil.disk_usage("/")
                net_info = psutil.net_io_counters()

                system_stats = {
                    "CPU使用率_%": psutil.cpu_percent(interval=0.1),
                    "系統記憶體使用率_%": memory_info.percent,
                    "系統可用記憶體_GB": memory_info.available / (1024**3),
                    "磁碟使用率_%": (disk_info.used / disk_info.total) * 100,
                    "網路傳送_KB": getattr(net_info, "bytes_sent", 0) / 1024,
                    "網路接收_KB": getattr(net_info, "bytes_recv", 0) / 1024,
                }

                # 單次更新替代多次 update
                stats.update(process_stats)
                stats.update(system_stats)

            except Exception as e:
                print(f"⚠️  psutil 監控錯誤: {e}")

        # 優化4: GPU 統計數據收集優化
        if GPU_AVAILABLE and GPUtil:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    stats.update(
                        {
                            "GPU數量": float(len(gpus)),
                            "GPU使用率_%": gpu.load * 100,
                            "GPU記憶體使用_MB": float(getattr(gpu, "memoryUsed", 0)),
                            "GPU溫度_C": float(getattr(gpu, "temperature", 0)),
                        }
                    )
            except Exception as e:
                print(f"⚠️  GPUtil 監控錯誤: {e}")

        return stats

    def measure_comprehensive_performance(
        self, func, *args, **kwargs
    ) -> Dict[str, Any]:
        """測量完整系統效能統計"""
        gc.collect()
        time.sleep(0.1)

        startup_start = time.perf_counter()
        start_time = time.perf_counter()
        start_cpu = time.process_time()
        start_stats = self._get_comprehensive_system_stats()
        startup_time = time.perf_counter() - startup_start

        result, success, error_msg = None, False, None
        execution_start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            error_msg = str(e)
        finally:
            execution_end = time.perf_counter()

        end_cpu = time.process_time()
        end_stats = self._get_comprehensive_system_stats()

        return {
            "純執行時間_秒": execution_end - execution_start,
            "總執行時間_秒": time.perf_counter() - start_time,
            "CPU時間_秒": end_cpu - start_cpu,
            "啟動時間_秒": startup_time,
            "執行前統計": start_stats,
            "執行後統計": end_stats,
            "結果": result,
            "成功": success,
            "錯誤訊息": error_msg,
        }

    def _compare_metrics(
        self, baseline: Dict[str, Any], optimized: Dict[str, Any]
    ) -> Dict[str, Any]:
        """比較兩個效能結果並計算改善指標 - TCK 優化版本"""
        # 優化1: 使用 get() 方法避免潛在的 KeyError，提供預設值
        baseline_time = baseline.get("純執行時間_秒", 1e-9)
        optimized_time = optimized.get("純執行時間_秒", 1e-9)
        baseline_cpu = baseline.get("CPU時間_秒", 1e-9)
        optimized_cpu = optimized.get("CPU時間_秒", 1e-9)

        time_improvement = self._safe_divide(baseline_time, optimized_time)
        cpu_improvement = self._safe_divide(baseline_cpu, optimized_cpu)

        # 加入絕對時間改善檢查：至少節省 0.01 秒才有意義
        absolute_time_saving = baseline_time - optimized_time
        if absolute_time_saving < 0.01 and baseline_time > 0.1:  # 對於慢函數
            time_improvement *= 0.5  # 懲罰邊際絕對改善

        # 優化2: 使用 get() 和嵌套字典安全訪問，避免重複字典查詢
        opt_after = optimized.get("執行後統計", {})
        opt_before = optimized.get("執行前統計", {})
        memory_change = opt_after.get("記憶體_MB", 0.0) - opt_before.get(
            "記憶體_MB", 0.0
        )

        # 優化3: 批量處理 IO 統計，減少字典查詢次數
        baseline_after = baseline.get("執行後統計", {})
        baseline_before = baseline.get("執行前統計", {})

        io_metrics = {
            "io_read_baseline": baseline_after.get("讀取次數", 0)
            - baseline_before.get("讀取次數", 0),
            "io_write_baseline": baseline_after.get("寫入次數", 0)
            - baseline_before.get("寫入次數", 0),
            "io_read_optimized": opt_after.get("讀取次數", 0)
            - opt_before.get("讀取次數", 0),
            "io_write_optimized": opt_after.get("寫入次數", 0)
            - opt_before.get("寫入次數", 0),
        }

        # 優化4: 安全的結果比較
        correctness = self._verify_correctness(
            baseline.get("結果"), optimized.get("結果")
        )

        # 優化5: 單次字典創建，避免多次賦值
        return {
            "時間改善倍數": time_improvement,
            "CPU改善倍數": cpu_improvement,
            "記憶體變化_MB": memory_change,
            "IO統計": {
                "原始讀取次數": io_metrics["io_read_baseline"],
                "優化讀取次數": io_metrics["io_read_optimized"],
                "原始寫入次數": io_metrics["io_write_baseline"],
                "優化寫入次數": io_metrics["io_write_optimized"],
            },
            "正確性": correctness,
        }

    def _safe_divide(
        self, numerator: float, denominator: float, min_threshold: float = 1e-9
    ) -> float:
        """安全除法，避免 infinity"""
        if abs(denominator) < min_threshold:
            return 9999.9
        return numerator / denominator

    def _calculate_performance_score(
        self, metrics: Dict[str, Any], quality_metrics: Dict[str, Any], baseline_quality: Optional[Dict[str, Any]] = None
    ) -> Dict[str, float]:
        """計算效能評分 (0-100 分)，包含程式碼品質 - 使用TCK最佳化技術：映射表和批次計算"""

        # TCK 優化：預定義評分計算函數，避免多重條件判斷
        def calculate_time_score(improvement: float) -> float:
            # 加入最小顯著改善門檻：小於1.5x的改善視為邊際效益不足
            if improvement < 1.5:
                return max(0.0, improvement * 20)  # 顯著降低分數
            if improvement >= 50:
                return 100.0
            elif improvement >= 10:
                return 80.0 + (improvement - 10) * 0.5
            elif improvement >= 2:
                return 60.0 + (improvement - 2) * 2.5
            return max(0.0, improvement * 30)

        def calculate_cpu_score(improvement: float) -> float:
            if improvement >= 999:
                return 100.0
            elif improvement >= 10:
                return 90.0
            elif improvement >= 5:
                return 80.0
            elif improvement >= 2:
                return 70.0
            return max(0.0, improvement * 35)

        def calculate_memory_score(change: float) -> float:
            if change <= 0:
                return 100.0
            elif change <= 10:
                return 90.0 - change * 2
            elif change <= 50:
                return 70.0 - (change - 10) * 1.5
            return max(10.0, 70.0 - change * 0.5)

        def calculate_io_score(reduction: int) -> float:
            if reduction >= 100:
                return 100.0
            elif reduction >= 50:
                return 90.0
            elif reduction >= 10:
                return 80.0
            elif reduction > 0:
                return 60.0 + reduction * 2
            return 50.0

        # TCK 優化：使用字典 get() 方法和批次提取數據
        time_improvement = metrics.get("時間改善倍數", 1.0)
        cpu_improvement = metrics.get("CPU改善倍數", 1.0)
        memory_change = metrics.get("記憶體變化_MB", 0)

        # 計算 IO 效率（安全字典存取）
        io_stats = metrics.get("IO統計", {})
        io_reduction = io_stats.get("原始讀取次數", 0) - io_stats.get("優化讀取次數", 0)

        # TCK 優化：批次計算核心評分，避免逐一賦值
        scores = {
            "時間改善評分": calculate_time_score(time_improvement),
            "CPU效率評分": calculate_cpu_score(cpu_improvement),
            "記憶體效率評分": calculate_memory_score(memory_change),
            "IO效率評分": calculate_io_score(io_reduction),
        }

        # 程式碼品質評分計算 - 使用 TCK 安全字典存取
        quality_score = 0.0
        practicality_score = 0.0
        if quality_metrics and "錯誤" not in quality_metrics:
            # TCK 優化：使用映射表避免多重條件判斷
            complexity_thresholds = [(5, 100), (10, 80), (20, 60)]
            length_thresholds = [(15, 100), (30, 80), (60, 60)]

            mi_score = max(0, quality_metrics.get("可維護性指數", 0))
            cc = quality_metrics.get("圈複雜度", 25)
            sloc = quality_metrics.get("程式碼行數", 100)

            # 使用 next() 和生成器表達式快速查找評分
            cc_score = next(
                (
                    score
                    for threshold, score in complexity_thresholds
                    if cc <= threshold
                ),
                30,
            )
            sloc_score = next(
                (score for threshold, score in length_thresholds if sloc <= threshold),
                30,
            )

            # 新增實用性指標
            dependency_count = quality_metrics.get("依賴套件數量", 0)
            tech_stack_complexity = quality_metrics.get("技術棧複雜度", 1)
            complexity_ratio = 1.0
            if baseline_quality:
                baseline_sloc = baseline_quality.get("程式碼行數", 1)
                optimized_sloc = quality_metrics.get("程式碼行數", 1)
                complexity_ratio = optimized_sloc / baseline_sloc if baseline_sloc > 0 else 1.0

            # 依賴數量評分：越少越好
            if dependency_count == 0:
                dep_score = 100
            elif dependency_count <= 2:
                dep_score = 80
            elif dependency_count <= 5:
                dep_score = 60
            else:
                dep_score = max(20, 60 - (dependency_count - 5) * 10)

            # 技術棧複雜度評分：1=純Python, 2=NumPy, 3=Numba等
            if tech_stack_complexity == 1:
                tech_score = 100
            elif tech_stack_complexity == 2:
                tech_score = 80
            elif tech_stack_complexity == 3:
                tech_score = 60
            else:
                tech_score = max(20, 60 - (tech_stack_complexity - 3) * 20)

            # 複雜度倍數評分：優化行數/原始行數，越接近1越好
            if complexity_ratio <= 1.2:
                ratio_score = 100
            elif complexity_ratio <= 2.0:
                ratio_score = 80
            elif complexity_ratio <= 5.0:
                ratio_score = 60
            else:
                ratio_score = max(20, 60 - (complexity_ratio - 5) * 5)

            # TCK 優化：預計算權重，單次計算
            quality_score = mi_score * 0.4 + cc_score * 0.3 + sloc_score * 0.3
            # 技術棧壽命評分：考慮長期維護成本
            # Numba/Torch 等複雜技術可能有相容性問題，給低分
            tech_lifetime_score = 100
            if tech_stack_complexity >= 3:
                tech_lifetime_score = 60  # 複雜技術長期維護成本高
            elif tech_stack_complexity == 2:
                tech_lifetime_score = 80

            practicality_score = dep_score * 0.3 + tech_score * 0.3 + ratio_score * 0.2 + tech_lifetime_score * 0.2

        scores["程式碼品質評分"] = quality_score
        scores["實用性評分"] = practicality_score

        # TCK 優化：預定義權重字典，使用生成器表達式計算總分
        # 調整權重：減少效能權重，增加品質與實用性權重以平衡實用性
        weights = {
            "時間改善評分": 0.25,  # 進一步降至 0.25
            "CPU效率評分": 0.15,  # 降至 0.15
            "記憶體效率評分": 0.10,  # 降至 0.10
            "IO效率評分": 0.05,
            "程式碼品質評分": 0.20,  # 降至 0.20
            "實用性評分": 0.25,  # 新增實用性評分
        }
        scores["總體效能評分"] = sum(
            scores[key] * weight for key, weight in weights.items()
        )

        # 正確性懲罰：如果結果不正確，總分減半
        correctness = metrics.get("正確性", True)
        if not correctness:
            scores["總體效能評分"] *= 0.5
            scores["正確性懲罰"] = True

        return scores

    def _get_performance_grade(self, score: float, practicality_score: float = 0) -> str:
        """根據評分獲得等級 - 考慮實用性權衡"""
        # 調整門檻：提高 A級要求，加入實用性懲罰
        if practicality_score < 60:  # 實用性差，降級
            grade_thresholds = (
                (98, "A+ (卓越)"),
                (90, "A (優秀)"),
                (80, "B+ (良好)"),
                (70, "B (中等)"),
                (60, "C+ (合格)"),
                (50, "C (勉強通過)"),
            )
        else:  # 實用性好，正常門檻
            grade_thresholds = (
                (95, "A+ (卓越)"),
                (85, "A (優秀)"),
                (75, "B+ (良好)"),
                (65, "B (中等)"),
                (55, "C+ (合格)"),
                (45, "C (勉強通過)"),
            )

        return next(
            (grade for threshold, grade in grade_thresholds if score >= threshold),
            "D (需要改善)",
        )

    def _deep_compare(self, obj1: Any, obj2: Any, precision: int = 5) -> bool:
        """
        遞迴比較兩個物件，特別處理浮點數和 NumPy 型別的精度問題。
        使用TCK最佳化技術：類型檢查最佳化和早期返回
        """
        # TCK 優化：使用 hasattr() 批次檢查，避免重複調用
        if hasattr(obj1, "item"):
            obj1 = obj1.item()
        if hasattr(obj2, "item"):
            obj2 = obj2.item()

        # TCK 優化：類型統一檢查，減少重複的 type() 調用
        obj1_type, obj2_type = type(obj1), type(obj2)

        # 型別不同時的數字比較優化
        if obj1_type is not obj2_type:
            # TCK 優化：使用元組包含檢查，避免多次 isinstance 調用
            if obj1_type in (int, float) and obj2_type in (int, float):
                return math.isclose(
                    obj1, obj2, rel_tol=1e-9, abs_tol=10 ** (-precision)
                )
            return False

        # TCK 優化：使用早期返回和預計算閾值
        abs_tolerance = 10 ** (-precision)

        # 字典比較優化
        if obj1_type is dict:
            # TCK 優化：先檢查鍵集合，避免不必要的遞迴
            if obj1.keys() != obj2.keys():
                return False
            # 使用 all() 和生成器表達式
            return all(self._deep_compare(obj1[k], obj2[k], precision) for k in obj1)

        # 序列比較優化（list, tuple）
        if obj1_type in (list, tuple):
            # TCK 優化：長度檢查優先
            if len(obj1) != len(obj2):
                return False
            # 使用 zip() 和 all() 批次比較
            return all(
                self._deep_compare(i1, i2, precision) for i1, i2 in zip(obj1, obj2)
            )

        # 浮點數比較
        if obj1_type is float:
            return math.isclose(obj1, obj2, rel_tol=1e-9, abs_tol=abs_tolerance)

        # TCK 優化：其他型別直接相等比較
        return obj1 == obj2

    def _verify_correctness(self, original_result, optimized_result) -> bool:
        """
        使用深度比較驗證結果的正確性，以處理浮點數精度問題。
        使用TCK最佳化技術：早期返回和異常處理最佳化
        """
        # TCK 優化：早期返回，避免不必要的計算
        if original_result is None and optimized_result is None:
            return True
        if original_result is None or optimized_result is None:
            return False

        try:
            return self._deep_compare(original_result, optimized_result)
        except Exception as e:
            # TCK 優化：使用 f-string 代替字串格式化
            print(f"⚠️  正確性驗證時發生錯誤: {e}")
            return False

    def _print_baseline_report(
        self, result: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """打印基準版本報告 - TCK優化：函數拆分降低複雜度"""
        baseline_data = result["版本比較結果"].get("unoptimized")
        if not baseline_data:
            print("❌ 報告錯誤：找不到基準版本 (unoptimized) 的數據。")
            return None

        baseline_metrics = baseline_data["metrics"]
        baseline_quality = baseline_data["quality"]
        print("### 基準版本 (unoptimized)")
        print(f"  - 執行時間: {baseline_metrics['純執行時間_秒']:.6f} 秒")
        print(f"  - CPU 時間: {baseline_metrics['CPU時間_秒']:.6f} 秒")
        print(
            f"  - 記憶體使用 (開始/結束): {baseline_metrics['執行前統計']['記憶體_MB']:.2f} MB / {baseline_metrics['執行後統計']['記憶體_MB']:.2f} MB"
        )
        if "錯誤" not in baseline_quality:
            print(
                f"  - 程式碼品質: CC={baseline_quality['圈複雜度']}, MI={baseline_quality['可維護性指數']:.1f}, Lines={baseline_quality['程式碼行數']}"
            )
        print("-" * 30)
        return baseline_data

    def _print_optimized_versions_report(self, result: Dict[str, Any]):
        """打印優化版本報告 - TCK優化：函數拆分降低複雜度"""
        optimized_versions_data = {
            k: v for k, v in result["版本比較結果"].items() if k != "unoptimized"
        }

        if not optimized_versions_data:
            print("### 該案例沒有提供可比較的優化版本。")
            print("=" * 60)
            return

        # TCK 優化：使用 sorted() 而非手動排序
        sorted_versions = sorted(
            optimized_versions_data.items(),
            key=lambda item: item[1]["scores"]["總體效能評分"],
            reverse=True,
        )

        print("### 優化版本效能排名")
        grade_emoji_map = {"A+": "🥇", "A": "🥈", "B+": "🥉"}

        for i, (version_name, version_data) in enumerate(sorted_versions, 1):
            comp = version_data["comparison"]
            scores = version_data["scores"]
            quality = version_data["quality"]
            grade_emoji = grade_emoji_map.get(version_data["grade"].split(" ")[0], "📊")

            print(
                f"{grade_emoji} {i}. {version_name} (評分: {scores['總體效能評分']:.1f}/100 - {version_data['grade']})"
            )
            print(f"  - 正確性: {'✅ 正確' if comp['正確性'] else '❌ 錯誤'}")
            print(f"  - 時間改善: {comp['時間改善倍數']:.1f} 倍 (vs unoptimized)")
            print(f"  - CPU 改善: {comp['CPU改善倍數']:.1f} 倍 (vs unoptimized)")
            print(f"  - 記憶體變化: {comp['記憶體變化_MB']:+.2f} MB")
            if "錯誤" not in quality:
                print(
                    f"  - 程式碼品質: CC={quality['圈複雜度']}, MI={quality['可維護性指數']:.1f}, Lines={quality['程式碼行數']} (品質評分: {scores['程式碼品質評分']:.1f})"
                )
            print("-" * 30)

    def generate_detailed_report(self, result: Dict[str, Any]):
        """為一對多比較結果生成詳細測試報告 - TCK優化：函數拆分降低複雜度"""
        if not result or not result.get("成功"):
            print("❌ 無法生成報告：測試執行失敗或沒有結果。")
            return

        print("\n" + "=" * 60)
        print(f"📊 {result['測試名稱']} 詳細效能報告")
        print("=" * 60)

        # TCK 優化：函數拆分，降低複雜度
        baseline_data = self._print_baseline_report(result)
        if not baseline_data:
            return

        self._print_optimized_versions_report(result)

        # TCK 優化：將報告保存拆分為獨立函數
        self._save_detailed_report(result)

    def _save_detailed_report(self, result: Dict[str, Any]):
        """保存詳細報告到 JSON 文件 - TCK優化：函數拆分降低複雜度"""
        report_dir = Path("test_reports")
        report_dir.mkdir(exist_ok=True)
        timestamp = int(time.time())
        report_file = report_dir / f"TCK報告_{result['測試名稱']}_{timestamp}.json"

        # TCK 優化：使用字典推導簡化數據清理
        simplified_result = result.copy()
        for version, data in simplified_result["版本比較結果"].items():
            if "metrics" in data:
                # 移除龐大的執行結果數據
                for key in ["結果", "執行前統計", "執行後統計"]:
                    data["metrics"].pop(key, None)

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(simplified_result, f, indent=2, ensure_ascii=False)

        print(f"\n🎯 詳細報告已保存: {report_file}")

    def run_all_tests(self):
        """執行所有測試案例並產生綜合報告"""
        all_results = []

        for i, name in enumerate(self.test_cases.keys(), 1):
            print(f"\n🔬 執行測試 {i}/{len(self.test_cases)}: {name}")
            print("-" * 50)

            result = self.run_test_case(name)
            if result:
                all_results.append(result)
                # 為每個測試案例生成詳細報告
                self.generate_detailed_report(result)

        self.generate_summary_report(all_results)

    def run_specific_test(self, test_name: str):
        """執行指定的測試案例 - 使用TCK最佳化技術：字典查找最佳化"""

        # TCK 優化：使用字典推導和 next() 進行高效查找
        target_name = next(
            (k for k in self.test_cases if k.upper() == test_name.upper()), None
        )

        if target_name is None:
            print(f"❌ 找不到測試案例: {test_name}")
            self.list_tests()
            return

        print(f"🎯 執行測試案例: {target_name}")
        print("=" * 60)

        result = self.run_test_case(target_name)
        if result:
            self.generate_detailed_report(result)

    def generate_summary_report(self, results: List[Dict[str, Any]]):
        """產生綜合統計報告 - 使用TCK最佳化技術：列表推導和預計算"""
        if not results:
            print("📊 沒有有效的測試結果可供生成報告。")
            return

        print("\n" + "=" * 60)
        print("📊 TCK 綜合效能分析報告")
        print("=" * 60)

        # TCK 優化：使用列表推導和生成器表達式，避免嵌套循環
        def extract_best_version(result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            """提取每個案例的最佳版本"""
            # 使用字典推導過濾優化版本
            optimized_versions = {
                k: v for k, v in result["版本比較結果"].items() if k != "unoptimized"
            }

            if not optimized_versions:
                return None

            # TCK 優化：使用 max() 而非手動迭代找最大值
            best_version_name, best_version_data = max(
                optimized_versions.items(),
                key=lambda item: item[1]["scores"]["總體效能評分"],
            )

            return {
                "case_name": result["測試名稱"],
                "version_name": best_version_name,
                "score": best_version_data["scores"]["總體效能評分"],
                "grade": best_version_data["grade"],
                "improvement": best_version_data["comparison"]["時間改善倍數"],
            }

        # TCK 優化：使用列表推導和 filter() 批次處理
        ranked_list = sorted(
            filter(None, (extract_best_version(result) for result in results)),
            key=lambda x: x["score"],
            reverse=True,
        )

        print("🏆 測試案例效能排行榜 (最佳版本):")
        print("=" * 50)

        # TCK 優化：預定義等級映射表，避免重複字典查詢
        grade_emoji_map = {"A+": "🥇", "A": "🥈", "B+": "🥉"}

        for i, item in enumerate(ranked_list, 1):
            grade_prefix = item["grade"].split(" ")[0]
            grade_emoji = grade_emoji_map.get(grade_prefix, "📊")
            print(
                f"{grade_emoji} {i:2d}. {item['case_name']:<25} "
                f"評分: {item['score']:5.1f}/100 ({item['grade']}) "
                f"提升: {item['improvement']:6.1f}x"
            )

        print("\n📄 完整報告已保存至各個詳細JSON檔案")
        print("=" * 60)

    def list_tests(self):
        """列出所有可用測試案例"""
        print("📋 可用的測試案例:")
        for case_name, case_data in self.test_cases.items():
            print(f" - {case_name}: {case_data['description']}")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description="TCK 增強統計分析器 - 完整的效能與資源監控 (一對多模式)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python tck_enhanced_analyzer.py                # 執行所有測試
  python tck_enhanced_analyzer.py --list         # 列出所有測試案例
  python tck_enhanced_analyzer.py --test LIST_LOOKUP # 執行特定測試
        """,
    )

    parser.add_argument(
        "--list", "-l", action="store_true", help="列出所有可用的測試案例"
    )
    parser.add_argument("--test", "-t", type=str, help="執行指定的測試案例")
    parser.add_argument("--cases-dir", "-d", default="cases", help="測試案例目錄路徑")

    args = parser.parse_args()

    # 創建分析器
    analyzer = TCKEnhancedAnalyzer(args.cases_dir)

    if not analyzer.load_test_cases():
        return

    # 執行命令
    if args.list:
        analyzer.list_tests()
    elif args.test:
        if args.test.upper() == "ALL":
            analyzer.run_all_tests()
        else:
            analyzer.run_specific_test(args.test)
    else:
        # 如果沒有指定參數，執行所有測試案例
        print("🚀 執行所有測試案例...")
        print("=" * 60)
        analyzer.run_all_tests()


if __name__ == "__main__":
    main()
