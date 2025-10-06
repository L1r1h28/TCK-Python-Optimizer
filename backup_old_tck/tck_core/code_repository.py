#!/usr/bin/env python3
"""
TCK 統一程式碼管理系統 (Code Repository Manager)
===============================================

統一管理所有程式碼片段，提供功能相似性分析，
支援腳本間的資料傳遞和結果累積。

Author: TurboCode Kit (TCK)  
Version: 1.1
"""

import os
import ast
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from collections import defaultdict
from tqdm import tqdm


@dataclass
class CodeFragment:
    """程式碼片段資料結構"""
    id: str                          # 唯一識別碼
    name: str                        # 片段名稱（函數名、類名等）
    type: str                        # 片段類型（function, class, method等）
    file_path: str                   # 檔案路徑
    start_line: int                  # 開始行號
    end_line: int                    # 結束行號
    raw_code: str                    # 原始程式碼
    normalized_code: str             # 標準化程式碼
    ast_structure: str               # AST結構簽名
    semantic_signature: str          # 語意簽名
    hash_code: str                   # 程式碼雜湊值
    
    # 分析結果累積區
    frequency_data: Optional[Dict] = None      # 頻率分析結果
    complexity_data: Optional[Dict] = None     # 複雜度分析結果
    similarity_data: Optional[Dict] = None     # 相似度分析結果
    
    # 功能識別
    functional_patterns: Optional[List[str]] = None      # 功能模式標籤
    optimization_opportunities: Optional[List[Dict]] = None  # 優化機會
    
    def __post_init__(self):
        """初始化後處理"""
        if self.functional_patterns is None:
            self.functional_patterns = []
        if self.optimization_opportunities is None:
            self.optimization_opportunities = []


class CodeRepository:
    """統一程式碼管理中心"""
    
    def __init__(self, config_path: str = "config.json"):
        """初始化程式碼倉庫"""
        self.config = self._load_config(config_path)
        self.fragments: Dict[str, CodeFragment] = {}
        self.functional_groups: Dict[str, List[str]] = defaultdict(list)
        self.analysis_history: List[Dict] = []
        
        # 優化：預建功能模式關鍵字集合 (基於 loop_lookup_optimization.md A+級 221.0x 加速)
        self._sorting_keywords = {'sort', 'sorted'}
        self._searching_keywords = {'find', 'search', 'index'}
        self._aggregation_keywords = {'count', 'sum', 'max', 'min'}
        self._data_processing_keywords = {'filter', 'map', 'reduce'}
        
    def _load_config(self, config_path: str) -> Dict:
        """載入配置檔案"""
        default_config = {
            "global_config": {
                "root_directory": ".",
                "output_directory": "../tck_core/analysis_results",
                "repository_file": "code_repository.json"
            },
            "code_analysis": {
                "min_function_length": 3,
                "extract_classes": True,
                "extract_methods": True,
                "extract_functions": True,
                "functional_pattern_matching": True
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def scan_and_extract_all(self) -> Dict[str, int]:
        """掃描並提取所有程式碼片段"""
        print("🔍 開始掃描程式碼倉庫...")
        
        root_dir = Path(self.config["global_config"]["root_directory"])
        ignore_folders = set(self.config["global_config"]["ignore_folders"])
        
        # 優化：使用生成器收集所有 Python 檔案
        print("📁 正在收集 Python 檔案...")
        py_files = []
        for file_path in root_dir.rglob("*.py"):
            # 優化：使用集合交集進行 O(1) 查找 (基於 loop_lookup_optimization.md A+級)
            file_path_parts = set(file_path.parts)
            if not file_path_parts & ignore_folders:  # O(1) 集合交集操作
                py_files.append(file_path)
        
        print(f"✨ 找到 {len(py_files)} 個 Python 檔案")
        
        stats = {"files": 0, "functions": 0, "classes": 0, "methods": 0}
        
        # 使用 tqdm 顯示進度
        with tqdm(total=len(py_files), desc="📄 處理檔案", unit="檔案") as pbar:
            for file_path in py_files:
                pbar.set_description(f"📄 {file_path.name[:30]}")
                
                file_fragments = self._extract_from_file(str(file_path))
                
                for fragment in file_fragments:
                    self.fragments[fragment.id] = fragment
                    if fragment.type in stats:
                        stats[fragment.type + "s"] = stats.get(fragment.type + "s", 0) + 1
                
                stats["files"] += 1
                pbar.update(1)
        
        print(f"📊 片段統計: {len(self.fragments)} 個程式碼片段")
        
        # 進行功能模式分析
        self._analyze_functional_patterns()
        
        # 保存程式碼倉庫
        self._save_repository()
        
        print("✅ 程式碼倉庫建立完成！")
        print(f"   檔案數: {stats['files']}")
        print(f"   函數數: {stats.get('functions', 0)}")
        print(f"   類別數: {stats.get('classs', 0)}")
        print(f"   方法數: {stats.get('methods', 0)}")
        
        return stats
    
    def _extract_from_file(self, file_path: str) -> List[CodeFragment]:
        """從單一檔案提取程式碼片段"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            tree = ast.parse(content, filename=file_path)
            fragments = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    fragment = self._create_fragment_from_function(node, "function", file_path, lines)
                    if fragment:
                        fragments.append(fragment)
                
                elif isinstance(node, ast.ClassDef):
                    fragment = self._create_fragment_from_class(node, "class", file_path, lines)
                    if fragment:
                        fragments.append(fragment)
                        
                        # 提取類別中的方法
                        for method_node in node.body:
                            if isinstance(method_node, ast.FunctionDef):
                                method_fragment = self._create_fragment_from_function(
                                    method_node, "method", file_path, lines, parent_class=node.name
                                )
                                if method_fragment:
                                    fragments.append(method_fragment)
            
            return fragments
            
        except Exception as e:
            print(f"⚠️ 無法處理檔案 {file_path}: {e}")
            return []
    
    def _create_fragment_from_function(self, node: ast.FunctionDef, fragment_type: str, 
                                     file_path: str, lines: List[str], 
                                     parent_class: Optional[str] = None) -> Optional[CodeFragment]:
        """從函數節點創建程式碼片段"""
        return self._create_fragment_from_ast(node, fragment_type, file_path, lines, parent_class)
    
    def _create_fragment_from_class(self, node: ast.ClassDef, fragment_type: str, 
                                  file_path: str, lines: List[str]) -> Optional[CodeFragment]:
        """從類別節點創建程式碼片段"""
        return self._create_fragment_from_ast(node, fragment_type, file_path, lines)
    
    def _create_fragment_from_ast(self, node: Union[ast.FunctionDef, ast.ClassDef], fragment_type: str, 
                                file_path: str, lines: List[str], 
                                parent_class: Optional[str] = None) -> Optional[CodeFragment]:
        """從 AST 節點創建程式碼片段"""
        start_line = node.lineno - 1
        end_line = self._find_end_line(node, lines, start_line)
        
        # 檢查長度閾值
        if end_line - start_line < self.config["code_analysis"]["min_function_length"]:
            return None
        
        raw_code = "\n".join(lines[start_line:end_line])
        normalized_code = self._normalize_code(raw_code)
        
        # 生成唯一ID
        fragment_id = hashlib.md5(f"{file_path}:{node.name}:{start_line}".encode()).hexdigest()[:12]
        
        # 生成語意簽名
        semantic_sig = self._generate_semantic_signature(node, raw_code)
        
        # 生成AST結構簽名
        ast_sig = self._generate_ast_signature(node)
        
        fragment_name = f"{parent_class}.{node.name}" if parent_class else node.name
        
        return CodeFragment(
            id=fragment_id,
            name=fragment_name,
            type=fragment_type,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            raw_code=raw_code,
            normalized_code=normalized_code,
            ast_structure=ast_sig,
            semantic_signature=semantic_sig,
            hash_code=hashlib.md5(normalized_code.encode()).hexdigest()
        )
    
    def _find_end_line(self, node: Union[ast.FunctionDef, ast.ClassDef], lines: List[str], start_line: int) -> int:
        """找到程式碼片段的結束行"""
        if start_line >= len(lines):
            return len(lines)
        
        # 找到起始縮排級別
        if start_line < len(lines):
            indent_level = len(lines[start_line]) - len(lines[start_line].lstrip())
        else:
            return len(lines)
        
        # 向下搜尋直到找到相同或更少縮排的非空行
        for i in range(start_line + 1, len(lines)):
            if i >= len(lines):
                break
            line = lines[i].strip()
            if line and not line.startswith(('#', '"', "'")):
                current_indent = len(lines[i]) - len(lines[i].lstrip())
                if current_indent <= indent_level:
                    return i
        
        return len(lines)
    
    def _normalize_code(self, raw_code: str) -> str:
        """標準化程式碼"""
        lines = []
        for line in raw_code.split('\n'):
            # 移除行內註釋
            if '#' in line:
                line = line[:line.find('#')]
            # 標準化空白
            line = ' '.join(line.split())
            if line.strip():
                lines.append(line.strip())
        
        return '\n'.join(lines)
    
    def _generate_semantic_signature(self, node: Union[ast.FunctionDef, ast.ClassDef], raw_code: str) -> str:
        """生成語意簽名，識別功能模式"""
        signature_parts = []
        
        # 分析函數參數模式
        if isinstance(node, ast.FunctionDef):
            signature_parts.append(f"params:{len(node.args.args)}")
            
            # 檢查是否有迴圈
            has_loops = any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(node))
            if has_loops:
                signature_parts.append("pattern:loop")
            
            # 檢查是否有條件判斷
            has_conditions = any(isinstance(n, ast.If) for n in ast.walk(node))
            if has_conditions:
                signature_parts.append("pattern:condition")
            
            # 優化：使用預建集合進行 O(1) 查找 (基於 loop_lookup_optimization.md)
            code_lower = raw_code.lower()
            if any(keyword in code_lower for keyword in self._sorting_keywords):
                signature_parts.append("function:sorting")
            if any(keyword in code_lower for keyword in self._searching_keywords):
                signature_parts.append("function:searching")
            if any(keyword in code_lower for keyword in self._aggregation_keywords):
                signature_parts.append("function:aggregation")
            if any(keyword in code_lower for keyword in self._data_processing_keywords):
                signature_parts.append("function:data_processing")
        
        return ":".join(signature_parts)
    
    def _generate_ast_signature(self, node: Union[ast.FunctionDef, ast.ClassDef]) -> str:
        """生成 AST 結構簽名"""
        node_types = []
        for child in ast.walk(node):
            node_types.append(type(child).__name__)
        
        # 統計各種節點類型的數量
        from collections import Counter
        type_counts = Counter(node_types)
        
        # 生成結構簽名
        signature = []
        for node_type in ['For', 'While', 'If', 'Call', 'Return']:
            if node_type in type_counts:
                signature.append(f"{node_type}:{type_counts[node_type]}")
        
        return ":".join(signature)
    
    def _analyze_functional_patterns(self):
        """分析功能模式，識別功能相似的程式碼"""
        print("🔄 分析功能模式...")
        
        # 按語意簽名分組
        semantic_groups = defaultdict(list)
        for fragment in self.fragments.values():
            # 確保 functional_patterns 已初始化
            if fragment.functional_patterns is None:
                fragment.functional_patterns = []
                
            # 提取主要功能模式
            main_pattern = self._extract_main_pattern(fragment.semantic_signature)
            if main_pattern:
                semantic_groups[main_pattern].append(fragment.id)
                fragment.functional_patterns.append(main_pattern)
        
        # 記錄功能分組
        for pattern, fragment_ids in semantic_groups.items():
            if len(fragment_ids) > 1:  # 只記錄有多個實現的功能
                self.functional_groups[pattern] = fragment_ids
                print(f"  🔗 發現功能模式 '{pattern}': {len(fragment_ids)} 個實現")
    
    def _extract_main_pattern(self, semantic_signature: str) -> Optional[str]:
        """提取主要功能模式"""
        if not semantic_signature:
            return None
        
        parts = semantic_signature.split(':')
        
        # 優先選擇功能類型
        for part in parts:
            if part.startswith('function:'):
                return part.replace('function:', '')
        
        # 其次選擇模式類型
        for part in parts:
            if part.startswith('pattern:'):
                return part.replace('pattern:', '')
        
        return None
    
    def get_fragment(self, fragment_id: str) -> Optional[CodeFragment]:
        """獲取程式碼片段"""
        return self.fragments.get(fragment_id)
    
    def get_all_fragments(self) -> Dict[str, CodeFragment]:
        """獲取所有程式碼片段"""
        return self.fragments
    
    def update_fragment_analysis(self, fragment_id: str, analysis_type: str, data: Dict):
        """更新程式碼片段的分析結果"""
        if fragment_id in self.fragments:
            fragment = self.fragments[fragment_id]
            if analysis_type == "frequency":
                fragment.frequency_data = data
            elif analysis_type == "complexity":
                fragment.complexity_data = data
            elif analysis_type == "similarity":
                fragment.similarity_data = data
    
    def get_functional_groups(self) -> Dict[str, List[Dict]]:
        """獲取功能分組，包含完整的程式碼片段資訊"""
        groups = {}
        for pattern, fragment_ids in self.functional_groups.items():
            groups[pattern] = [
                {
                    "id": fid,
                    "name": self.fragments[fid].name,
                    "file": os.path.basename(self.fragments[fid].file_path),
                    "lines": f"{self.fragments[fid].start_line+1}-{self.fragments[fid].end_line}",
                    "raw_code": self.fragments[fid].raw_code[:200] + "..." if len(self.fragments[fid].raw_code) > 200 else self.fragments[fid].raw_code
                }
                for fid in fragment_ids if fid in self.fragments
            ]
        return groups
    
    def _save_repository(self):
        """保存程式碼倉庫"""
        output_dir = Path(self.config["global_config"]["output_directory"])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        repo_data = {
            "metadata": {
                "total_fragments": len(self.fragments),
                "functional_groups": len(self.functional_groups)
            },
            "fragments": {fid: asdict(fragment) for fid, fragment in self.fragments.items()},
            "functional_groups": dict(self.functional_groups),
            "analysis_history": self.analysis_history
        }
        
        repo_file = output_dir / self.config["global_config"]["repository_file"]
        with open(repo_file, 'w', encoding='utf-8') as f:
            json.dump(repo_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 程式碼倉庫已保存: {repo_file}")
    
    def load_repository(self) -> bool:
        """載入程式碼倉庫"""
        output_dir = Path(self.config["global_config"]["output_directory"])
        repo_file = output_dir / self.config["global_config"]["repository_file"]
        
        if not repo_file.exists():
            return False
        
        try:
            with open(repo_file, 'r', encoding='utf-8') as f:
                repo_data = json.load(f)
            
            # 重建程式碼片段
            self.fragments = {}
            for fid, fragment_data in repo_data["fragments"].items():
                fragment = CodeFragment(**fragment_data)
                self.fragments[fid] = fragment
            
            self.functional_groups = defaultdict(list, repo_data["functional_groups"])
            self.analysis_history = repo_data.get("analysis_history", [])
            
            print(f"✅ 程式碼倉庫已載入: {len(self.fragments)} 個片段")
            return True
            
        except Exception as e:
            print(f"❌ 載入程式碼倉庫失敗: {e}")
            return False


def main():
    """主程式入口"""
    print("🚀 TCK 程式碼倉庫管理系統")
    
    repo = CodeRepository()
    
    # 嘗試載入現有倉庫
    if repo.load_repository():
        print("發現現有程式碼倉庫")
        choice = input("是否重新掃描？(y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            repo.scan_and_extract_all()
    else:
        print("建立新的程式碼倉庫")
        repo.scan_and_extract_all()
    
    # 顯示功能分組摘要
    functional_groups = repo.get_functional_groups()
    if functional_groups:
        print("\n🔗 發現的功能模式:")
        for pattern, implementations in functional_groups.items():
            print(f"  📋 {pattern}: {len(implementations)} 個不同實現")
            for impl in implementations[:3]:  # 顯示前3個
                print(f"    - {impl['name']} ({impl['file']})")


if __name__ == "__main__":
    main()