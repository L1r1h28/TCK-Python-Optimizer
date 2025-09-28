"""
TCK 增強統計測試腳本 - 包含記憶體和 I/O 統計的中文版本
"""

import time
import json
import importlib.util
import sys
import argparse
import os
import gc
from pathlib import Path
from typing import List, Dict, Any, Optional

# 系統監控庫導入
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️  建議安裝 psutil: pip install psutil")

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False
    print("⚠️  安裝 GPUtil 以監控 GPU: pip install gputil")

try:
    import threading
    SYSTEM_INFO_AVAILABLE = True
except ImportError:
    SYSTEM_INFO_AVAILABLE = False

import platform

class TCKEnhancedAnalyzer:
    """TCK 增強統計分析器 - 包含完整的系統資源監控"""
    
    def __init__(self, test_cases_file: str = "test_cases.py"):
        self.test_cases_file = test_cases_file
        self.results = {}
        self.test_cases = []
        print("📊 TCK 增強統計分析器啟動")
        print("=" * 60)
    
    def load_test_cases(self) -> bool:
        """動態載入測試案例檔案"""
        try:
            spec = importlib.util.spec_from_file_location("test_cases", self.test_cases_file)
            if spec is None or spec.loader is None:
                raise ImportError("無法載入測試案例檔案")
                
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            self.test_cases = test_module.TEST_CASES
            print(f"✅ 成功載入 {len(self.test_cases)} 個測試案例")
            return True
        except Exception as e:
            print(f"❌ 載入測試案例失敗: {e}")
            return False
    
    def _get_comprehensive_system_stats(self) -> Dict[str, Any]:
        """取得完整系統統計資訊"""
        stats = {
            # 基本程序統計
            '記憶體_MB': 0.0,
            '虛擬記憶體_MB': 0.0,
            '記憶體使用率_%': 0.0,
            '讀取次數': 0,
            '寫入次數': 0,
            '讀取位元組': 0,
            '寫入位元組': 0,
            # 系統資源統計
            'CPU使用率_%': 0.0,
            '系統記憶體使用率_%': 0.0,
            '系統可用記憶體_GB': 0.0,
            '磁碟使用率_%': 0.0,
            '網路傳送_KB': 0.0,
            '網路接收_KB': 0.0,
            # GPU 統計
            'GPU數量': 0,
            'GPU使用率_%': 0.0,
            'GPU記憶體使用_MB': 0.0,
            'GPU溫度_C': 0.0,
            # 系統訊息
            '系統平台': platform.system() if SYSTEM_INFO_AVAILABLE else 'Unknown',
            'CPU核心數': os.cpu_count() or 0,
            '執行緒數': threading.active_count() if SYSTEM_INFO_AVAILABLE else 0
        }
        
        if PSUTIL_AVAILABLE:
            try:
                # 程序統計
                process = psutil.Process()
                memory = process.memory_info()
                io_stats = process.io_counters()
                
                stats.update({
                    '記憶體_MB': memory.rss / 1024 / 1024,
                    '虛擬記憶體_MB': memory.vms / 1024 / 1024,
                    '記憶體使用率_%': process.memory_percent(),
                    '讀取次數': io_stats.read_count,
                    '寫入次數': io_stats.write_count,
                    '讀取位元組': io_stats.read_bytes,
                    '寫入位元組': io_stats.write_bytes
                })
                
                # 系統資源統計
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_info = psutil.virtual_memory()
                disk_info = psutil.disk_usage('/')
                net_info = psutil.net_io_counters()
                
                stats.update({
                    'CPU使用率_%': cpu_percent,
                    '系統記憶體使用率_%': memory_info.percent,
                    '系統可用記憶體_GB': memory_info.available / 1024 / 1024 / 1024,
                    '磁碟使用率_%': (disk_info.used / disk_info.total) * 100,
                    '網路傳送_KB': net_info.bytes_sent / 1024 if net_info else 0,
                    '網路接收_KB': net_info.bytes_recv / 1024 if net_info else 0
                })
            except Exception as e:
                print(f"⚠️  系統資源監控錯誤: {e}")
        
        # GPU 監控
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # 使用第一個 GPU
                    stats.update({
                        'GPU數量': len(gpus),
                        'GPU使用率_%': gpu.load * 100,
                        'GPU記憶體使用_MB': gpu.memoryUsed,
                        'GPU溫度_C': gpu.temperature
                    })
            except Exception as e:
                print(f"⚠️  GPU 監控錯誤: {e}")
        
        return stats
    
    def measure_comprehensive_performance(self, func, *args, **kwargs) -> Dict[str, Any]:
        """測量完整系統效能統計"""
        # 執行前清理和統計
        gc.collect()
        time.sleep(0.1)  # 穩定系統狀態
        
        # 記錄啟動時間
        startup_start = time.perf_counter()
        import_start = time.time()
        
        # 獲取初始統計
        start_time = time.perf_counter()
        start_cpu = time.process_time()
        start_stats = self._get_comprehensive_system_stats()
        
        startup_time = time.perf_counter() - startup_start
        
        try:
            # 執行函數
            execution_start = time.perf_counter()
            result = func(*args, **kwargs)
            execution_end = time.perf_counter()
            success = True
            error_msg = None
        except Exception as e:
            execution_end = time.perf_counter()
            result = None
            success = False
            error_msg = str(e)
        
        # 執行後統計
        end_time = time.perf_counter()
        end_cpu = time.process_time()
        end_stats = self._get_comprehensive_system_stats()
        
        pure_execution_time = execution_end - execution_start
        total_time = end_time - start_time
        
        return {
            '純執行時間_秒': pure_execution_time,
            '總執行時間_秒': total_time,
            'CPU時間_秒': end_cpu - start_cpu,
            '啟動時間_秒': startup_time,
            '執行前統計': start_stats,
            '執行後統計': end_stats,
            '結果': result,
            '成功': success,
            '錯誤訊息': error_msg
        }
    
    def run_test_case(self, test_case_class) -> Dict[str, Any]:
        """執行單一測試案例並收集完整統計"""
        print(f"\n🔍 測試案例: {test_case_class.name}")
        print(f"📝 說明: {test_case_class.description}")
        print("-" * 50)
        
        # 準備測試資料
        test_data = test_case_class.setup_data()
        
        # 執行原始版本
        print("❌ 測試原始版本...")
        original_result = self.measure_comprehensive_performance(
            test_case_class.original_version, *test_data
        )
        
        # 執行優化版本
        print("✅ 測試優化版本...")
        optimized_result = self.measure_comprehensive_performance(
            test_case_class.optimized_version, *test_data
        )
        
        # 計算改善指標（修正 infinity 問題）
        if original_result['成功'] and optimized_result['成功']:
            # 使用安全的除法，避免 infinity
            time_improvement = self._safe_divide(original_result['純執行時間_秒'], optimized_result['純執行時間_秒'])
            cpu_improvement = self._safe_divide(original_result['CPU時間_秒'], optimized_result['CPU時間_秒'])
            startup_improvement = self._safe_divide(original_result['啟動時間_秒'], optimized_result['啟動時間_秒'])
            
            # 記憶體變化
            memory_change = optimized_result['執行後統計']['記憶體_MB'] - optimized_result['執行前統計']['記憶體_MB']
            
            # I/O 變化
            io_read_original = original_result['執行後統計']['讀取次數'] - original_result['執行前統計']['讀取次數']
            io_write_original = original_result['執行後統計']['寫入次數'] - original_result['執行前統計']['寫入次數']
            io_read_optimized = optimized_result['執行後統計']['讀取次數'] - optimized_result['執行前統計']['讀取次數']
            io_write_optimized = optimized_result['執行後統計']['寫入次數'] - optimized_result['執行前統計']['寫入次數']
            
            # 資料量變化
            bytes_read_original = original_result['執行後統計']['讀取位元組'] - original_result['執行前統計']['讀取位元組']
            bytes_write_original = original_result['執行後統計']['寫入位元組'] - original_result['執行前統計']['寫入位元組']
            bytes_read_optimized = optimized_result['執行後統計']['讀取位元組'] - optimized_result['執行前統計']['讀取位元組']
            bytes_write_optimized = optimized_result['執行後統計']['寫入位元組'] - optimized_result['執行前統計']['寫入位元組']
            
            # 系統資源變化
            cpu_usage_change = optimized_result['執行後統計']['CPU使用率_%'] - optimized_result['執行前統計']['CPU使用率_%']
            gpu_usage_change = optimized_result['執行後統計']['GPU使用率_%'] - optimized_result['執行前統計']['GPU使用率_%']
            
            # 驗證正確性
            correctness = self._verify_correctness(original_result['結果'], optimized_result['結果'])
            
        else:
            time_improvement = cpu_improvement = startup_improvement = 1.0
            correctness = False
            memory_change = cpu_usage_change = gpu_usage_change = 0
            io_read_original = io_write_original = io_read_optimized = io_write_optimized = 0
            bytes_read_original = bytes_write_original = bytes_read_optimized = bytes_write_optimized = 0
        
        # 建立完整指標字典
        performance_metrics = {
            '時間改善倍數': time_improvement,
            'CPU改善倍數': cpu_improvement,
            '啟動時間改善倍數': startup_improvement,
            '記憶體變化_MB': memory_change,
            'IO統計': {
                '原始讀取次數': io_read_original,
                '優化讀取次數': io_read_optimized,
                '原始寫入次數': io_write_original,
                '優化寫入次數': io_write_optimized,
                '原始讀取KB': bytes_read_original/1024,
                '優化讀取KB': bytes_read_optimized/1024,
                '原始寫入KB': bytes_write_original/1024,
                '優化寫入KB': bytes_write_optimized/1024
            },
            '正確性': correctness
        }
        
        # 計算效能評分
        performance_scores = self._calculate_performance_score(performance_metrics)
        
        # 顯示詳細結果
        print(f"⏱️  執行時間: 原始 {original_result['純執行時間_秒']:.6f} 秒 → 優化 {optimized_result['純執行時間_秒']:.6f} 秒")
        print(f"� 執行時間改善: {time_improvement:.1f} 倍 (評分: {performance_scores['時間改善評分']:.1f}/100)")
        print(f"�💻 CPU 時間: 原始 {original_result['CPU時間_秒']:.6f} 秒 → 優化 {optimized_result['CPU時間_秒']:.6f} 秒")
        print(f"⚡ CPU 效率改善: {cpu_improvement:.1f} 倍 (評分: {performance_scores['CPU效率評分']:.1f}/100)")
        print(f"🔄 啟動時間改善: {startup_improvement:.1f} 倍")
        print(f"✨ 結果正確性: {'✅ 正確' if correctness else '❌ 錯誤'}")
        
        if PSUTIL_AVAILABLE:
            print(f"💾 記憶體變化: {memory_change:+.2f} MB (評分: {performance_scores['記憶體效率評分']:.1f}/100)")
            print(f"🖥️  CPU 使用率變化: {cpu_usage_change:+.1f}%")
            if GPU_AVAILABLE and gpu_usage_change != 0:
                print(f"🎮 GPU 使用率變化: {gpu_usage_change:+.1f}%")
            
            if io_read_original > 0 or io_read_optimized > 0:
                print(f"📁 讀取操作: 原始 {io_read_original} 次 → 優化 {io_read_optimized} 次")
            if io_write_original > 0 or io_write_optimized > 0:
                print(f"✏️  寫入操作: 原始 {io_write_original} 次 → 優化 {io_write_optimized} 次")
            if bytes_read_original > 0 or bytes_read_optimized > 0:
                print(f"📖 讀取資料: 原始 {bytes_read_original/1024:.1f} KB → 優化 {bytes_read_optimized/1024:.1f} KB")
            if bytes_write_original > 0 or bytes_write_optimized > 0:
                print(f"📝 寫入資料: 原始 {bytes_write_original/1024:.1f} KB → 優化 {bytes_write_optimized/1024:.1f} KB")
            
            print(f"📊 I/O 效率評分: {performance_scores['IO效率評分']:.1f}/100")
        
        # 顯示總體評分和等級
        total_score = performance_scores['總體效能評分']
        grade = self._get_performance_grade(total_score)
        print(f"\n🏆 總體效能評分: {total_score:.1f}/100 - {grade}")
        
        # 清理資源
        if hasattr(test_case_class, 'cleanup_data'):
            test_case_class.cleanup_data(*test_data)
        
        return {
            '測試名稱': test_case_class.name,
            '測試描述': test_case_class.description,
            '原始執行時間': original_result['純執行時間_秒'],
            '優化執行時間': optimized_result['純執行時間_秒'],
            '原始CPU時間': original_result['CPU時間_秒'],
            '優化CPU時間': optimized_result['CPU時間_秒'],
            '原始啟動時間': original_result['啟動時間_秒'],
            '優化啟動時間': optimized_result['啟動時間_秒'],
            '時間改善倍數': time_improvement,
            'CPU改善倍數': cpu_improvement,
            '啟動時間改善倍數': startup_improvement,
            '記憶體變化_MB': memory_change,
            'CPU使用率變化_%': cpu_usage_change,
            'GPU使用率變化_%': gpu_usage_change,
            'IO統計': performance_metrics['IO統計'],
            '效能評分': performance_scores,
            '總體等級': grade,
            '正確性': correctness,
            '成功': original_result['成功'] and optimized_result['成功'],
            '系統資訊': {
                '原始系統統計': original_result['執行前統計'],
                '優化系統統計': optimized_result['執行前統計']
            }
        }
    
    def _safe_divide(self, numerator: float, denominator: float, min_threshold: float = 1e-9) -> float:
        """安全除法，避免 infinity"""
        if abs(denominator) < min_threshold:
            # 分母太小，返回一個大值但不是 infinity
            return 999.9
        return numerator / denominator
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """計算效能評分 (0-100 分)"""
        scores = {}
        
        # 時間改善評分 (0-100)
        time_improvement = metrics.get('時間改善倍數', 1.0)
        if time_improvement >= 50:
            scores['時間改善評分'] = 100.0
        elif time_improvement >= 10:
            scores['時間改善評分'] = 80.0 + (time_improvement - 10) * 0.5
        elif time_improvement >= 2:
            scores['時間改善評分'] = 60.0 + (time_improvement - 2) * 2.5
        else:
            scores['時間改善評分'] = max(0.0, time_improvement * 30)
        
        # CPU 效率評分
        cpu_improvement = metrics.get('CPU改善倍數', 1.0)
        if cpu_improvement >= 999:  # 極大改善
            scores['CPU效率評分'] = 100.0
        elif cpu_improvement >= 10:
            scores['CPU效率評分'] = 90.0
        elif cpu_improvement >= 5:
            scores['CPU效率評分'] = 80.0
        elif cpu_improvement >= 2:
            scores['CPU效率評分'] = 70.0
        else:
            scores['CPU效率評分'] = max(0.0, cpu_improvement * 35)
        
        # 記憶體效率評分
        memory_change = metrics.get('記憶體變化_MB', 0)
        if memory_change <= 0:  # 節省記憶體
            scores['記憶體效率評分'] = 100.0
        elif memory_change <= 10:  # 少量增加
            scores['記憶體效率評分'] = 90.0 - memory_change * 2
        elif memory_change <= 50:
            scores['記憶體效率評分'] = 70.0 - (memory_change - 10) * 1.5
        else:
            scores['記憶體效率評分'] = max(10.0, 70.0 - memory_change * 0.5)
        
        # I/O 效率評分（已優化：避免雙重字典查找）
        io_stats = metrics.get('IO統計', {})
        io_reduction = io_stats.get('原始讀取次數', 0) - io_stats.get('優化讀取次數', 0)
        if io_reduction >= 100:
            scores['IO效率評分'] = 100.0
        elif io_reduction >= 50:
            scores['IO效率評分'] = 90.0
        elif io_reduction >= 10:
            scores['IO效率評分'] = 80.0
        elif io_reduction > 0:
            scores['IO效率評分'] = 60.0 + io_reduction * 2
        else:
            scores['IO效率評分'] = 50.0  # 無 I/O 優化
        
        # 總體評分（加權平均）
        weights = {
            '時間改善評分': 0.4,
            'CPU效率評分': 0.3,
            '記憶體效率評分': 0.2,
            'IO效率評分': 0.1
        }
        
        total_score = sum(scores[key] * weight for key, weight in weights.items())
        scores['總體效能評分'] = total_score
        
        return scores
    
    def _get_performance_grade(self, score: float) -> str:
        """根據評分獲得等級"""
        if score >= 95:
            return 'A+ (卓越)'
        elif score >= 85:
            return 'A (優秀)'
        elif score >= 75:
            return 'B+ (良好)'
        elif score >= 65:
            return 'B (中等)'
        elif score >= 55:
            return 'C+ (合格)'
        elif score >= 45:
            return 'C (勉強通過)'
        else:
            return 'D (需要改善)'
    
    def _verify_correctness(self, original_result, optimized_result) -> bool:
        """驗證結果正確性"""
        if original_result is None or optimized_result is None:
            return False

        if isinstance(original_result, list) and isinstance(optimized_result, list):
            # 檢查長度和內容是否完全相同
            return len(original_result) == len(optimized_result) and original_result == optimized_result
        else:
            return original_result == optimized_result
    
    def generate_detailed_report(self, result: Dict[str, Any]):
        """生成詳細測試報告"""
        print("\n" + "=" * 60)
        print(f"📊 {result['測試名稱']} 詳細效能報告")
        print("=" * 60)
        
        if result['成功'] and result['正確性']:
            print("✅ 測試狀態: 成功")
            print(f"🚀 執行時間改善: {result['時間改善倍數']:.1f} 倍")
            print(f"⚡ CPU 效率改善: {result['CPU改善倍數']:.1f} 倍")
            print(f"⏱️  時間節省: {result['原始執行時間'] - result['優化執行時間']:.6f} 秒")
            print(f"💾 記憶體變化: {result['記憶體變化_MB']:+.2f} MB")
            
            io_stats = result['IO統計']
            print("\n📊 I/O 效能分析:")
            print(f"  📁 讀取操作減少: {io_stats['原始讀取次數'] - io_stats['優化讀取次數']} 次")
            print(f"  ✏️  寫入操作減少: {io_stats['原始寫入次數'] - io_stats['優化寫入次數']} 次")
            print(f"  📖 讀取資料節省: {io_stats['原始讀取KB'] - io_stats['優化讀取KB']:.1f} KB")
            print(f"  📝 寫入資料節省: {io_stats['原始寫入KB'] - io_stats['優化寫入KB']:.1f} KB")
        else:
            print("❌ 測試狀態: 失敗")
        
        print("=" * 60)
        
        # 保存詳細報告至專用資料夾
        timestamp = int(time.time())
        report_dir = "test_reports"
        os.makedirs(report_dir, exist_ok=True)
        
        # 處理同功能的覆蓋問題：使用時間戳區分
        base_filename = f"TCK詳細報告_{result['測試名稱']}"
        report_file = os.path.join(report_dir, f"{base_filename}_{timestamp}.json")
        
        # 檢查是否存在舊版本，如有則移動到歷史子資料夾
        history_dir = os.path.join(report_dir, "history")
        os.makedirs(history_dir, exist_ok=True)
        
        # 移動所有舊的同名報告到歷史資料夾
        import glob
        old_reports = glob.glob(os.path.join(report_dir, f"{base_filename}_*.json"))
        for old_report in old_reports:
            if old_report != report_file:  # 不移動當前檔案
                import shutil
                old_basename = os.path.basename(old_report)
                history_path = os.path.join(history_dir, old_basename)
                shutil.move(old_report, history_path)
                print(f"📜 舊報告已移至歷史: {history_path}")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                '生成時間': time.strftime('%Y-%m-%d %H:%M:%S'),
                '詳細結果': result
            }, f, indent=2, ensure_ascii=False)
        
        print(f"🎯 詳細報告已保存: {report_file}")
    
    def list_tests(self):
        """列出所有可用測試案例"""
        print("📋 可用的測試案例:")
        print("=" * 50)
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"{i}. {test_case.name}")
            print(f"   📝 {test_case.description}")
            print()
    
    def run_all_tests(self):
        """執行所有測試案例並產生綜合報告"""
        all_results = []
        
        for i, test_case in enumerate(self.test_cases, 1):
            print(f"\n🔬 執行測試 {i}/{len(self.test_cases)}: {test_case.name}")
            print("-" * 50)
            
            result = self.run_test_case(test_case)
            all_results.append(result)
            
            # 顯示簡要結果
            print(f"⭐ {result['測試名稱']}: {result['效能評分']['總體效能評分']:.1f}/100 - {result['總體等級']}")
        
        # 產生綜合統計報告
        self.generate_summary_report(all_results)
    
    def generate_summary_report(self, results: List[Dict[str, Any]]):
        """產生綜合統計報告"""
        print("\n" + "=" * 60)
        print("📊 TCK 綜合效能分析報告")
        print("=" * 60)
        
        # 按評分排序
        sorted_results = sorted(results, key=lambda x: x['效能評分']['總體效能評分'], reverse=True)
        
        print("🏆 測試案例效能排行榜:")
        print("=" * 50)
        for i, result in enumerate(sorted_results, 1):
            grade = result['總體等級']
            score = result['效能評分']['總體效能評分']
            time_improvement = result.get('時間改善倍數', 1.0)
            
            # 根據評級使用不同的emoji
            grade_emoji = {
                'A+': '🥇', 'A': '🥈', 'B+': '🥉', 'B': '🎖️ ',
                'C+': '🏅', 'C': '🎗️ ', 'D': '📝'
            }.get(grade, '📊')
            
            print(f"{grade_emoji} {i:2d}. {result['測試名稱']:<25} "
                  f"評分: {score:5.1f}/100 ({grade:2s}) "
                  f"提升: {time_improvement:6.1f}x")
        
        # 統計各評級數量（已優化：使用 defaultdict 避免重複 get 調用）
        from collections import defaultdict
        grade_counts = defaultdict(int)
        total_improvement = 0
        for result in results:
            grade = result['總體等級']
            grade_counts[grade] += 1
            total_improvement += result.get('時間改善倍數', 1.0)
        
        print(f"\n📈 統計摘要:")
        print("=" * 30)
        print(f"🎯 測試案例總數: {len(results)}")
        print(f"⚡ 平均效能提升: {total_improvement/len(results):.1f}x")
        
        for grade in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D']:
            count = grade_counts.get(grade, 0)
            if count > 0:
                emoji = {'A+': '🥇', 'A': '🥈', 'B+': '🥉', 'B': '🎖️',
                        'C+': '🏅', 'C': '🎗️', 'D': '📝'}.get(grade, '📊')
                print(f"{emoji} {grade} 級: {count} 個案例")
        
        print("\n🔍 建議執行順序（按效能提升排序）:")
        print("=" * 45)
        for i, result in enumerate(sorted_results[:5], 1):  # 只顯示前5名
            improvement = result.get('時間改善倍數', 1.0)
            print(f"{i}. {result['測試名稱']:<25} (提升 {improvement:6.1f}x)")
        
        print(f"\n📄 完整報告已保存至各個詳細JSON檔案")
        print("=" * 60)

    def run_specific_test(self, test_name: str):
        """執行指定的測試案例（已優化：使用字典查找替代線性搜尋）"""
        # 📊 TCK 優化：建立測試案例名稱到類別的字典映射，實現 O(1) 查找
        test_case_mapping = {test_case.name.upper(): test_case for test_case in self.test_cases}
        
        target_test = test_case_mapping.get(test_name.upper())
        
        if target_test is None:
            print(f"❌ 找不到測試案例: {test_name}")
            self.list_tests()
            return
        
        print(f"🎯 執行測試案例: {test_name}")
        print("=" * 60)
        
        result = self.run_test_case(target_test)
        self.generate_detailed_report(result)

def main():
    """主程式"""
    parser = argparse.ArgumentParser(
        description='TCK 增強統計分析器 - 完整的效能與資源監控',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python tck_enhanced_analyzer.py --list                     # 列出所有測試案例
  python tck_enhanced_analyzer.py --test LIST_LOOKUP        # 執行特定測試
  python tck_enhanced_analyzer.py --test CONFIG_LOAD        # 執行配置測試
        """)
    
    parser.add_argument('--list', '-l', action='store_true', 
                       help='列出所有可用的測試案例')
    parser.add_argument('--test', '-t', type=str,
                       help='執行指定的測試案例')
    parser.add_argument('--cases-file', '-f', default='test_cases.py',
                       help='測試案例檔案路徑')
    
    args = parser.parse_args()
    
    # 檢查檔案
    if not Path(args.cases_file).exists():
        print(f"❌ 找不到 {args.cases_file} 檔案")
        return
    
    # 創建分析器
    analyzer = TCKEnhancedAnalyzer(args.cases_file)
    
    if not analyzer.load_test_cases():
        return
    
    # 執行命令
    if args.list:
        analyzer.list_tests()
    elif args.test:
        analyzer.run_specific_test(args.test)
    else:
        # 如果沒有指定參數，執行所有測試案例
        print("🚀 執行所有測試案例...")
        print("=" * 60)
        analyzer.run_all_tests()

if __name__ == "__main__":
    main()