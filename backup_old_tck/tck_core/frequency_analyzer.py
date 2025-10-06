#!/usr/bin/env python3
"""
TCK 頻率分析器 (Frequency Analyzer)
====================================

分析 Python 程式碼中重複出現的程式碼模式和片段，
統計其出現頻率，為優化決策提供數據支撐。

Author: TurboCode Kit (TCK)
Version: 1.0
"""

import os
import ast
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List
from tqdm import tqdm


class CodeFrequencyAnalyzer:
    """程式碼頻率分析器"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化分析器"""
        self.config = self._load_config(config_path)
        self.code_patterns = defaultdict(int)
        self.function_calls = Counter()
        
        # 優化：預建忽略資料夾集合 (基於 loop_lookup_optimization.md A+級 221.0x 加速)
        self._ignore_folders_set = set(self.config["global_config"]["ignore_folders"])
        self.loop_patterns = Counter()
        self.import_patterns = Counter()
        
    def _load_config(self, config_path: str) -> Dict:
        """載入配置檔案"""
        default_config = {
            "global_config": {
                "root_directory": ".",
                "output_directory": "../tck_core/analysis_results",
                "file_extensions": [".py"],
                "ignore_folders": ["__pycache__", ".git", "venv", ".venv", "node_modules"],
                "ignore_files": ["*test*.py", "*_test.py", "test_*.py"]
            },
            "frequency_settings": {
                "min_pattern_length": 3,
                "track_function_calls": True,
                "track_imports": True,
                "track_loops": True,
                "similarity_threshold": 0.8
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def scan_directory(self) -> List[str]:
        """掃描目標目錄，找出所有 Python 檔案"""
        root_dir = Path(self.config["global_config"]["root_directory"])
        py_files = []
        
        for file_path in root_dir.rglob("*.py"):
            # 優化：使用集合交集進行 O(1) 查找 (基於 loop_lookup_optimization.md A+級)
            file_path_parts = set(file_path.parts)
            if file_path_parts & self._ignore_folders_set:  # O(1) 集合交集操作
                continue
            py_files.append(str(file_path))
            
        print(f"🔍 找到 {len(py_files)} 個 Python 檔案")
        return py_files
    
    def analyze_file(self, file_path: str) -> Dict:
        """分析單個檔案的頻率特徵"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 AST
            tree = ast.parse(content, filename=file_path)
            
            file_stats = {
                "file_path": file_path,
                "function_calls": [],
                "loop_patterns": [],
                "import_statements": [],
                "code_blocks": []
            }
            
            # 遍歷 AST 節點
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # 函數調用統計
                    func_name = self._get_function_name(node)
                    if func_name:
                        self.function_calls[func_name] += 1
                        file_stats["function_calls"].append(func_name)
                
                elif isinstance(node, (ast.For, ast.While)):
                    # 迴圈模式統計
                    loop_type = type(node).__name__
                    self.loop_patterns[loop_type] += 1
                    file_stats["loop_patterns"].append(loop_type)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    # 導入語句統計
                    import_info = self._get_import_info(node)
                    self.import_patterns[import_info] += 1
                    file_stats["import_statements"].append(import_info)
            
            return file_stats
            
        except Exception as e:
            print(f"⚠️ 無法分析檔案 {file_path}: {e}")
            return {"file_path": file_path, "error": str(e)}
    
    def _get_function_name(self, call_node: ast.Call) -> str:
        """提取函數調用名稱"""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return ""
    
    def _get_import_info(self, import_node) -> str:
        """提取導入資訊"""
        if isinstance(import_node, ast.Import):
            return f"import {import_node.names[0].name}"
        elif isinstance(import_node, ast.ImportFrom):
            module = import_node.module or ""
            names = [alias.name for alias in import_node.names]
            return f"from {module} import {','.join(names[:3])}"  # 限制長度
        return ""
    
    def run_analysis(self) -> Dict:
        """執行完整的頻率分析"""
        print("🚀 開始程式碼頻率分析...")
        
        # 掃描檔案
        python_files = self.scan_directory()
        
        # 使用 tqdm 分析每個檔案
        all_file_stats = []
        with tqdm(total=len(python_files), desc="📊 頻率分析", unit="檔案") as pbar:
            for file_path in python_files:
                pbar.set_description(f"📊 {os.path.basename(file_path)[:25]}")
                file_stats = self.analyze_file(file_path)
                all_file_stats.append(file_stats)
                pbar.update(1)
        
        # 生成總結報告
        summary = {
            "analysis_type": "frequency_analysis",
            "total_files": len(python_files),
            "top_function_calls": dict(self.function_calls.most_common(20)),
            "loop_distribution": dict(self.loop_patterns),
            "popular_imports": dict(self.import_patterns.most_common(15)),
            "file_details": all_file_stats
        }
        
        # 保存結果
        self._save_results(summary, "frequency_analysis.json")
        
        print("✅ 頻率分析完成！")
        return summary
    
    def _save_results(self, results: Dict, filename: str):
        """保存分析結果"""
        output_dir = Path(self.config["global_config"]["output_directory"])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 結果已保存到: {output_path}")


def main():
    """主程式入口"""
    analyzer = CodeFrequencyAnalyzer()
    results = analyzer.run_analysis()
    
    # 顯示簡要統計
    print("\n📈 頻率分析摘要:")
    print(f"總檔案數: {results['total_files']}")
    print(f"最常用函數: {list(results['top_function_calls'].keys())[:5]}")
    print(f"迴圈統計: {results['loop_distribution']}")


if __name__ == "__main__":
    main()