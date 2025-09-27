#!/usr/bin/env python3
"""
TCK 複雜度計算器 (Complexity Calculator)
======================================

分析 Python 程式碼的時間複雜度和空間複雜度，
識別效能瓶頸，為優化提供理論依據。

Author: TurboCode Kit (TCK)
Version: 1.0
"""

import os
import ast
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp


def get_function_name(call_node: ast.Call) -> str:
    """提取函數調用名稱"""
    if isinstance(call_node.func, ast.Name):
        return call_node.func.id
    elif isinstance(call_node.func, ast.Attribute):
        return call_node.func.attr
    return ""


def analyze_file_worker(args: Tuple[str, Dict]) -> Dict:
    """
    工作進程函數：分析單個檔案的複雜度
    用於 ProcessPoolExecutor 的全域函數
    """
    file_path, config = args
    
    def calculate_complexity_score(node: ast.AST) -> int:
        """計算複雜度分數"""
        score = 1  # 基礎分數
        
        for child in ast.walk(node):
            if isinstance(child, ast.For):
                score *= 10  # 每個迴圈增加一個數量級
            elif isinstance(child, ast.While):
                score *= 8   # while 迴圈稍低
            elif isinstance(child, ast.ListComp):
                score *= 5   # 列表推導式
            elif isinstance(child, ast.Call):
                # 檢查是否為已知高複雜度函數
                func_name = get_function_name(child)
                if func_name in ['sort', 'sorted']:
                    score *= 15  # O(n log n)
                elif func_name in ['index', 'count', 'remove']:
                    score *= 8   # O(n)
        
        return min(score, 10000)  # 設定上限
    
    def score_to_big_o(score: int) -> str:
        """將分數轉換為大O表示法"""
        if score <= 1:
            return "O(1)"
        elif score <= 10:
            return "O(log n)"
        elif score <= 50:
            return "O(n)"
        elif score <= 200:
            return "O(n log n)"
        elif score <= 1000:
            return "O(n^2)"
        else:
            return "O(n^3+)"
    
    def count_nested_loops(node: ast.AST) -> int:
        """計算嵌套迴圈層數"""
        max_depth = 0
        
        def visit_node(n: ast.AST, depth: int):
            nonlocal max_depth
            if isinstance(n, (ast.For, ast.While)):
                depth += 1
                max_depth = max(max_depth, depth)
            
            for child in ast.iter_child_nodes(n):
                visit_node(child, depth)
        
        visit_node(node, 0)
        return max_depth
    
    def count_recursive_calls(node: ast.AST, function_name: str) -> int:
        """計算遞迴調用次數"""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func_name = get_function_name(child)
                if func_name == function_name:
                    count += 1
        return count
    
    def analyze_data_structures(node: ast.AST) -> List[str]:
        """分析資料結構使用情況"""
        structures = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.List):
                structures.append("list")
            elif isinstance(child, ast.Dict):
                structures.append("dict")
            elif isinstance(child, ast.Set):
                structures.append("set")
            elif isinstance(child, ast.Call):
                func_name = get_function_name(child)
                if func_name in ['list', 'dict', 'set', 'tuple']:
                    structures.append(func_name)
        
        return list(set(structures))  # 去重
    
    def identify_bottlenecks(node: ast.AST) -> List[Dict]:
        """識別潛在的效能瓶頸"""
        bottlenecks = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func_name = get_function_name(child)
                
                # 檢查已知的效能陷阱
                if func_name == "index" and hasattr(child, 'lineno'):
                    bottlenecks.append({
                        "type": "list_search",
                        "line": child.lineno,
                        "description": "list.index() 是 O(n) 操作，考慮使用 dict 或 set",
                        "suggestion": "使用 dict 或 set 進行 O(1) 查找"
                    })
                
                elif func_name in ["remove", "count"] and hasattr(child, 'lineno'):
                    bottlenecks.append({
                        "type": "list_operation",
                        "line": child.lineno,
                        "description": f"list.{func_name}() 是 O(n) 操作",
                        "suggestion": "考慮使用更高效的資料結構"
                    })
        
        return bottlenecks
    
    def analyze_function_complexity(node: ast.FunctionDef, file_path: str) -> Dict:
        """分析函數的複雜度"""
        function_info = {
            "name": node.name,
            "file_path": file_path,
            "line_number": node.lineno,
            "time_complexity": "O(1)",
            "space_complexity": "O(1)",
            "complexity_score": 1,
            "nested_loops": 0,
            "recursive_calls": 0,
            "data_structures": [],
            "bottleneck_details": []
        }
        
        # 分析函數體
        complexity_score = calculate_complexity_score(node)
        function_info["complexity_score"] = complexity_score
        function_info["time_complexity"] = score_to_big_o(complexity_score)
        
        # 檢查嵌套迴圈
        nested_loops = count_nested_loops(node)
        function_info["nested_loops"] = nested_loops
        
        # 檢查遞迴調用
        recursive_calls = count_recursive_calls(node, node.name)
        function_info["recursive_calls"] = recursive_calls
        
        # 分析資料結構使用
        data_structures = analyze_data_structures(node)
        function_info["data_structures"] = data_structures
        
        # 識別瓶頸
        bottlenecks = identify_bottlenecks(node)
        function_info["bottleneck_details"] = bottlenecks
        
        return function_info
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=file_path)
        
        file_results = {
            "file_path": file_path,
            "functions": [],
            "classes": [],
            "file_complexity_score": 0
        }
        
        total_complexity = 0
        
        # 分析函數
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = analyze_function_complexity(node, file_path)
                file_results["functions"].append(func_info)
                total_complexity += func_info["complexity_score"]
            
            elif isinstance(node, ast.ClassDef):
                # 簡單的類別分析
                class_info = {
                    "name": node.name,
                    "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                }
                file_results["classes"].append(class_info)
        
        file_results["file_complexity_score"] = total_complexity
        return file_results
        
    except Exception as e:
        return {"file_path": file_path, "error": str(e)}


class ComplexityCalculator:
    """程式碼複雜度計算器"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化計算器"""
        self.config = self._load_config(config_path)
        self.complexity_results = []
        
    def _load_config(self, config_path: str) -> Dict:
        """載入配置檔案"""
        default_config = {
            "global_config": {
                "root_directory": ".",
                "output_directory": "../tck_core/analysis_results",
                "file_extensions": [".py"]
            },
            "complexity_settings": {
                "analyze_functions": True,
                "analyze_classes": True,
                "track_nested_loops": True,
                "track_recursion": True,
                "complexity_threshold": "O(n^2)"
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
            py_files.append(str(file_path))
            
        print(f"🔍 找到 {len(py_files)} 個 Python 檔案進行複雜度分析")
        return py_files
    
    def analyze_function_complexity(self, node: ast.FunctionDef, file_path: str) -> Dict:
        """分析函數的複雜度"""
        function_info = {
            "name": node.name,
            "file_path": file_path,
            "line_number": node.lineno,
            "time_complexity": "O(1)",
            "space_complexity": "O(1)",
            "complexity_score": 1,
            "nested_loops": 0,
            "recursive_calls": 0,
            "data_structures": [],
            "bottleneck_details": []
        }
        
        # 分析函數體
        complexity_score = self._calculate_complexity_score(node)
        function_info["complexity_score"] = complexity_score
        function_info["time_complexity"] = self._score_to_big_o(complexity_score)
        
        # 檢查嵌套迴圈
        nested_loops = self._count_nested_loops(node)
        function_info["nested_loops"] = nested_loops
        
        # 檢查遞迴調用
        recursive_calls = self._count_recursive_calls(node, node.name)
        function_info["recursive_calls"] = recursive_calls
        
        # 分析資料結構使用
        data_structures = self._analyze_data_structures(node)
        function_info["data_structures"] = data_structures
        
        # 識別瓶頸
        bottlenecks = self._identify_bottlenecks(node)
        function_info["bottleneck_details"] = bottlenecks
        
        return function_info
    
    def _calculate_complexity_score(self, node: ast.AST) -> int:
        """計算複雜度分數"""
        score = 1  # 基礎分數
        
        for child in ast.walk(node):
            if isinstance(child, ast.For):
                score *= 10  # 每個迴圈增加一個數量級
            elif isinstance(child, ast.While):
                score *= 8   # while 迴圈稍低
            elif isinstance(child, ast.ListComp):
                score *= 5   # 列表推導式
            elif isinstance(child, ast.Call):
                # 檢查是否為已知高複雜度函數
                func_name = self._get_function_name(child)
                if func_name in ['sort', 'sorted']:
                    score *= 15  # O(n log n)
                elif func_name in ['index', 'count', 'remove']:
                    score *= 8   # O(n)
        
        return min(score, 10000)  # 設定上限
    
    def _score_to_big_o(self, score: int) -> str:
        """將分數轉換為大O表示法"""
        if score <= 1:
            return "O(1)"
        elif score <= 10:
            return "O(log n)"
        elif score <= 50:
            return "O(n)"
        elif score <= 200:
            return "O(n log n)"
        elif score <= 1000:
            return "O(n^2)"
        else:
            return "O(n^3+)"
    
    def _count_nested_loops(self, node: ast.AST) -> int:
        """計算嵌套迴圈層數"""
        max_depth = 0
        current_depth = 0
        
        def visit_node(n: ast.AST, depth: int):
            nonlocal max_depth
            if isinstance(n, (ast.For, ast.While)):
                depth += 1
                max_depth = max(max_depth, depth)
            
            for child in ast.iter_child_nodes(n):
                visit_node(child, depth)
        
        visit_node(node, 0)
        return max_depth
    
    def _count_recursive_calls(self, node: ast.AST, function_name: str) -> int:
        """計算遞迴調用次數"""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func_name = self._get_function_name(child)
                if func_name == function_name:
                    count += 1
        return count
    
    def _analyze_data_structures(self, node: ast.AST) -> List[str]:
        """分析資料結構使用情況"""
        structures = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.List):
                structures.append("list")
            elif isinstance(child, ast.Dict):
                structures.append("dict")
            elif isinstance(child, ast.Set):
                structures.append("set")
            elif isinstance(child, ast.Call):
                func_name = self._get_function_name(child)
                if func_name in ['list', 'dict', 'set', 'tuple']:
                    structures.append(func_name)
        
        return list(set(structures))  # 去重
    
    def _identify_bottlenecks(self, node: ast.AST) -> List[Dict]:
        """識別潛在的效能瓶頸"""
        bottlenecks = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func_name = self._get_function_name(child)
                
                # 檢查已知的效能陷阱
                if func_name == "index" and hasattr(child, 'lineno'):
                    bottlenecks.append({
                        "type": "list_search",
                        "line": child.lineno,
                        "description": "list.index() 是 O(n) 操作，考慮使用 dict 或 set",
                        "suggestion": "使用 dict 或 set 進行 O(1) 查找"
                    })
                
                elif func_name in ["remove", "count"] and hasattr(child, 'lineno'):
                    bottlenecks.append({
                        "type": "list_operation",
                        "line": child.lineno,
                        "description": f"list.{func_name}() 是 O(n) 操作",
                        "suggestion": "考慮使用更高效的資料結構"
                    })
        
        return bottlenecks
    
    def _get_function_name(self, call_node: ast.Call) -> str:
        """提取函數調用名稱"""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return ""
    
    def analyze_file(self, file_path: str) -> Dict:
        """分析單個檔案的複雜度"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            
            file_results = {
                "file_path": file_path,
                "functions": [],
                "classes": [],
                "file_complexity_score": 0
            }
            
            total_complexity = 0
            
            # 分析函數
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self.analyze_function_complexity(node, file_path)
                    file_results["functions"].append(func_info)
                    total_complexity += func_info["complexity_score"]
                
                elif isinstance(node, ast.ClassDef):
                    # 簡單的類別分析
                    class_info = {
                        "name": node.name,
                        "methods": len([n for n in node.body if isinstance(n, ast.FunctionDef)])
                    }
                    file_results["classes"].append(class_info)
            
            file_results["file_complexity_score"] = total_complexity
            return file_results
            
        except Exception as e:
            print(f"⚠️ 無法分析檔案 {file_path}: {e}")
            return {"file_path": file_path, "error": str(e)}
    
    def run_analysis(self) -> Dict:
        """執行完整的複雜度分析（並行版本）"""
        print("🚀 開始程式碼複雜度分析...")
        
        python_files = self.scan_directory()
        all_results = []
        high_complexity_functions = []
        
        # 確定工作進程數量（使用 CPU 核心數，但限制最大值避免過度並行)
        max_workers = min(mp.cpu_count(), 8)  # 最多8個進程
        print(f"🔧 使用 {max_workers} 個並行進程進行分析")
        
        # 準備任務參數
        tasks = [(file_path, self.config) for file_path in python_files]
        
        # 使用 ProcessPoolExecutor 進行並行處理
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任務
            future_to_file = {executor.submit(analyze_file_worker, task): task[0] 
                             for task in tasks}
            
            # 使用 tqdm 追蹤進度
            with tqdm(total=len(python_files), desc="🔧 複雜度分析", unit="檔案") as pbar:
                # 處理完成的任務
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    
                    try:
                        file_result = future.result()
                        all_results.append(file_result)
                        
                        # 收集高複雜度函數
                        if "functions" in file_result:
                            for func in file_result["functions"]:
                                if func.get("complexity_score", 0) > 100:  # 閾值
                                    high_complexity_functions.append(func)
                        
                        # 更新進度條顯示
                        pbar.set_description(f"🔧 {os.path.basename(file_path)[:25]}")
                        
                    except Exception as e:
                        # 處理個別檔案的錯誤
                        error_result = {"file_path": file_path, "error": str(e)}
                        all_results.append(error_result)
                        print(f"⚠️ 無法分析檔案 {file_path}: {e}")
                    
                    finally:
                        pbar.update(1)
        
        # 生成摘要報告
        summary = {
            "analysis_type": "complexity_analysis",
            "total_files": len(python_files),
            "total_functions": sum(len(r.get("functions", [])) for r in all_results),
            "high_complexity_functions": sorted(
                high_complexity_functions, 
                key=lambda x: x["complexity_score"], 
                reverse=True
            )[:20],  # 前20個最複雜的函數
            "file_details": all_results,
            "performance_info": {
                "parallel_processes": max_workers,
                "cpu_cores": mp.cpu_count()
            }
        }
        
        self._save_results(summary, "complexity_analysis.json")
        
        print(f"✅ 複雜度分析完成！（使用 {max_workers} 個並行進程）")
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
    calculator = ComplexityCalculator()
    results = calculator.run_analysis()
    
    # 顯示簡要統計
    print("\n📊 複雜度分析摘要:")
    print(f"總檔案數: {results['total_files']}")
    print(f"總函數數: {results['total_functions']}")
    print(f"高複雜度函數: {len(results['high_complexity_functions'])}")
    
    if results['high_complexity_functions']:
        print("\n⚠️ 最需要優化的函數:")
        for func in results['high_complexity_functions'][:5]:
            print(f"  - {func['name']} ({func['time_complexity']}) - {os.path.basename(func['file_path'])}")


if __name__ == "__main__":
    main()