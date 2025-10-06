#!/usr/bin/env python3
"""
TCK 主控制器 (Main Controller)
=============================

執行所有 TurboCode Kit 分析腳本的主要控制程式。
按照順序執行頻率分析、複雜度計算、相似度檢測和報告生成。
支援智慧跳過已完成的分析和檢查點續傳功能。
新增 SimHash 高效能相似度檢測支援。

Author: TurboCode Kit (TCK)
Version: 2.0
"""

import os
import sys
import time
import json
import hashlib
from datetime import datetime
from pathlib import Path

# 導入優化工具 (基於 config_cache.md A級 28.1x 加速)
from turbo_utils import ConfigCacheManager

# 導入 SimHash 相似度測試函數
def load_existing_blocks():
    """從 code_repository.json 載入現有程式碼塊"""
    try:
        with open("tck_core/analysis_results/code_repository.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 新的結構使用 fragments 而不是 code_blocks
            fragments = data.get("fragments", {})
            if fragments:
                # 將 fragments 轉換為相似度檢測期望的格式
                code_blocks = []
                for fragment_id, fragment in fragments.items():
                    code_block = {
                        "file_path": fragment.get("file_path", ""),
                        "start_line": fragment.get("start_line", 0),
                        "end_line": fragment.get("end_line", 0),
                        "raw_code": fragment.get("raw_code", ""),
                        "normalized_code": fragment.get("normalized_code", ""),
                        "type": fragment.get("type", ""),
                        "name": fragment.get("name", ""),
                        "hash": fragment.get("hash_code", "")
                    }
                    code_blocks.append(code_block)
                return code_blocks
            else:
                # 回退到舊的 code_blocks 格式
                return data.get("code_blocks", [])
    except FileNotFoundError:
        print("WARNING: code_repository.json not found, please run code repository creation first")
        return []
    except Exception as e:
        print(f"Error loading code blocks: {e}")
        return []


# 導入各個分析模組
try:
    from tck_core.code_repository import CodeRepository
    from tck_core.frequency_analyzer import CodeFrequencyAnalyzer
    from tck_core.complexity_calculator import ComplexityCalculator
    from tck_core.report_generator import OptimizationReportGenerator
except ImportError as e:
    print(f"❌ 導入模組失敗: {e}")
    print("請確保所有 TCK 腳本檔案都在同一目錄中")
    sys.exit(1)


class TCKController:
    """TurboCode Kit 主控制器"""
    
    def __init__(self, config_path: str = "tck_core/config.json"):
        """初始化控制器"""
        self.config_path = config_path
        self.start_time = None
        self.checkpoint_file = "tck_core/tck_checkpoint.json"
        self.progress_state = self._load_checkpoint()
        
    def _load_checkpoint(self) -> dict:
        """載入檢查點"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                print(f"Checkpoint loaded: last run at {checkpoint.get('last_run', 'unknown')}")
                return checkpoint
            except Exception as e:
                print(f"WARNING: Failed to load checkpoint: {e}")
                return {}
        return {}
        
    def _save_checkpoint(self, step_name: str, status: str = "completed"):
        """儲存檢查點"""
        self.progress_state[step_name] = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "file_hash": self._get_config_hash()
        }
        self.progress_state["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 儲存檢查點失敗: {e}")
    
    def _get_config_hash(self) -> str:
        """獲取配置檔案的雜湊值"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'rb') as f:
                    return hashlib.md5(f.read()).hexdigest()
        except Exception:
            pass
        return ""
    
    def _is_step_completed(self, step_name: str, output_file: str) -> bool:
        """檢查步驟是否已完成且結果檔案存在"""
        if not os.path.exists(output_file):
            return False
            
        step_info = self.progress_state.get(step_name, {})
        if step_info.get("status") != "completed":
            return False
            
        # 檢查配置檔案是否有變化
        current_hash = self._get_config_hash()
        if step_info.get("file_hash") != current_hash:
            print(f"⚠️ 配置檔案已變更，需要重新執行 {step_name}")
            return False
            
        return True
        
    def run_full_analysis(self, force_refresh: bool = False):
        """執行完整的分析流程"""
        print("🚀 TurboCode Kit (TCK) 啟動 v2.0")
        print("=" * 50)
        self.start_time = time.time()
        
        steps = [
            ("🏗️ 程式碼倉庫建立", self._run_repository_setup, "tck_core/analysis_results/code_repository.json"),
            ("📊 頻率分析", self._run_frequency_analysis, "tck_core/analysis_results/frequency_analysis.json"),
            ("🔧 複雜度計算", self._run_complexity_analysis, "tck_core/analysis_results/complexity_analysis.json"),
            ("🔍 相似度檢測", self._run_similarity_analysis, "tck_core/analysis_results/similarity_analysis.json"),
            ("📋 報告生成", self._run_report_generation, "tck_core/analysis_results/optimization_report.md"),
        ]
        
        for step_name, step_function, output_file in steps:
            print(f"\n{step_name}")
            print("-" * 30)
            
            # 智慧跳過檢查
            if not force_refresh and self._is_step_completed(step_name, output_file):
                print(f"✅ {step_name} 已完成，跳過執行")
                print(f"   結果檔案: {output_file}")
                continue
            
            try:
                print(f"🔄 執行 {step_name}...")
                success = step_function()
                if success:
                    self._save_checkpoint(step_name, "completed")
                    print(f"✅ {step_name} 完成")
                else:
                    print(f"❌ {step_name} 失敗")
                    self._save_checkpoint(step_name, "failed")
                    return False
                    
            except Exception as e:
                print(f"❌ {step_name} 執行時發生錯誤: {e}")
                self._save_checkpoint(step_name, "error")
                return False
        
        self._show_completion_summary()
        return True
    
    def _run_repository_setup(self) -> bool:
        """執行程式碼倉庫建立"""
        try:
            output_dir = Path("tck_core/analysis_results")
            output_file = output_dir / "code_repository.json"
            
            # 檢查是否需要重新掃描
            if output_file.exists() and not self._should_rescan():
                print("✅ 程式碼倉庫已存在且無需更新")
                return True
                
            repo = CodeRepository(self.config_path)
            repo.scan_and_extract_all()
            return True
        except Exception as e:
            print(f"程式碼倉庫建立錯誤: {e}")
            return False
    
    def _should_rescan(self) -> bool:
        """檢查是否需要重新掃描程式碼"""
        try:
            # 檢查程式碼倉庫檔案的最後修改時間
            repo_file = Path("tck_core/analysis_results/code_repository.json")
            if not repo_file.exists():
                return True
                
            repo_mtime = repo_file.stat().st_mtime
            
            # 讀取配置檔案中的掃描目錄 (優化：使用快取避免重複I/O)
            config = ConfigCacheManager.load_config(self.config_path, use_cache=True)
            
            scan_dir = Path(config["scan_settings"]["root_directory"])
            if not scan_dir.exists():
                return False
            
            # 檢查掃描目錄中是否有檔案比倉庫檔案新
            for py_file in scan_dir.rglob("*.py"):
                if py_file.stat().st_mtime > repo_mtime:
                    print(f"⚠️ 發現更新的程式碼檔案: {py_file.name}")
                    return True
                    
            return False
            
        except Exception as e:
            print(f"檢查檔案變更時發生錯誤: {e}")
            return True
    
    def _run_frequency_analysis(self) -> bool:
        """執行頻率分析"""
        try:
            analyzer = CodeFrequencyAnalyzer(self.config_path)
            analyzer.run_analysis()
            return True
        except Exception as e:
            print(f"頻率分析錯誤: {e}")
            return False
    
    def _run_complexity_analysis(self) -> bool:
        """執行複雜度分析"""
        try:
            calculator = ComplexityCalculator(self.config_path)
            calculator.run_analysis()
            return True
        except Exception as e:
            print(f"複雜度分析錯誤: {e}")
            return False
    
    def _run_similarity_analysis(self) -> bool:
        """執行相似度檢測 - 使用新的 SimHash 優化版本"""
        try:
            # 載入程式碼塊
            code_blocks = load_existing_blocks()
            if not code_blocks:
                print("ERROR: Cannot load code blocks, please run code repository creation first")
                return False
            
            # 執行相似度分析 (使用 test_similarity.py 的邏輯)
            from tck_core.similarity_detector import SimilarityDetector
            import hashlib
            
            print("Generating SimHash fingerprints for code blocks...")
            
            # 為載入的程式碼塊確保有 hash（如果沒有）
            for block in code_blocks:
                if not block.get('hash'):  # 優化：使用 .get() 方法避免雙重查找
                    # 生成程式碼雜湊
                    block['hash'] = hashlib.md5(block['normalized_code'].encode()).hexdigest()
            
            detector = SimilarityDetector(self.config_path)
            detector.code_blocks = code_blocks
            
            print(f"Starting SimHash similarity comparison from {len(code_blocks)} code blocks...")
            
            # 執行 SimHash 相似度檢測
            similar_groups = detector.find_similar_blocks_parallel()
            function_patterns = detector._analyze_function_patterns()
            
            # 生成報告
            summary = {
                "analysis_type": "similarity_analysis", 
                "total_files": "From repository",
                "total_code_blocks": len(code_blocks),
                "similar_groups": similar_groups,
                "function_patterns": function_patterns,
                "optimization_summary": {
                    "duplicate_groups": len([g for g in similar_groups if g["similarity_type"] == "exact"]),
                    "similar_groups": len([g for g in similar_groups if g["similarity_type"] == "similar"]),
                    "total_potential_savings": sum(
                        g["optimization_potential"]["duplicate_lines"] 
                        for g in similar_groups
                    )
                }
            }
            
            # 儲存結果到正確的目錄
            output_dir = Path("tck_core/analysis_results")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = output_dir / "similarity_analysis.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            print("SimHash similarity detection completed")
            print(f"   - Exact duplicate groups: {summary['optimization_summary']['duplicate_groups']}")
            print(f"   - Similar code groups: {summary['optimization_summary']['similar_groups']}")
            print(f"   - Potential line savings: {summary['optimization_summary']['total_potential_savings']}")
            
            return True
        except Exception as e:
            print(f"Similarity detection error: {e}")
            return False
    
    def _run_report_generation(self) -> bool:
        """執行報告生成"""
        try:
            generator = OptimizationReportGenerator("tck_core/analysis_results")
            return generator.run()
        except Exception as e:
            print(f"報告生成錯誤: {e}")
            return False
    
    def _show_completion_summary(self):
        """顯示完成摘要"""
        elapsed_time = time.time() - (self.start_time or time.time())
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        print("\n" + "=" * 50)
        print("🎉 TurboCode Kit 分析完成！")
        print(f"⏱️  總耗時: {minutes}分{seconds}秒")
        print("\n📁 生成的檔案:")
        print("  - frequency_analysis.json (頻率分析結果)")
        print("  - complexity_analysis.json (複雜度分析結果)")
        print("  - similarity_analysis.json (相似度分析結果)")
        print("  - optimization_report.md (完整優化報告)")
        print("  - optimization_summary.json (優化摘要)")
        print("\n📋 下一步操作:")
        print("  1. 開啟 optimization_report.md 查看完整報告")
        print("  2. 從優先級表格中選擇要優化的項目")
        print("  3. 使用 Copilot + optimization_blueprints 進行優化")
        print("  4. 完成後重新執行分析驗證效果")


def main():
    """主程式入口"""
    print("TurboCode Kit (TCK) - 高性能程式碼加速工具箱")
    print("版本: 1.0")
    print()
    
    # 檢查配置檔案
    if not os.path.exists("tck_core/config.json"):
        print("⚠️ 找不到 tck_core/config.json，將使用預設配置")
        print("請編輯 tck_core/config.json 設定您的專案路徑")
        print()
    
    # 詢問使用者是否要執行完整分析
    response = input("是否開始執行完整的 TCK 分析？(y/n): ").lower().strip()
    
    # 優化：使用集合進行 O(1) 查找而不是 O(n) 列表查找
    positive_responses = {'y', 'yes', '是', ''}
    if response in positive_responses:
        controller = TCKController()
        success = controller.run_full_analysis()
        
        if not success:
            print("\n❌ 分析過程中遇到問題，請檢查錯誤訊息")
            sys.exit(1)
    else:
        print("分析已取消")
        
        print("\n您也可以單獨執行各個分析:")
        print("  python frequency_analyzer.py    # 頻率分析")
        print("  python complexity_calculator.py # 複雜度計算")
        print("  python similarity_detector.py   # 相似度檢測")
        print("  python report_generator.py      # 報告生成")


if __name__ == "__main__":
    main()