"""
TurboCode Kit (TCK) - 相似度檢測器
用於檢測程式碼中的重複和相似模式
"""

import ast
import hashlib
import json
import os
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Dict, List

from simhash import Simhash, SimhashIndex
from tqdm import tqdm


class SimilarityDetector:
    """程式碼相似度檢測器"""

    def __init__(self, config_path: str = "config.json"):
        """初始化相似度檢測器"""
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.code_blocks = []
        self.function_signatures = defaultdict(list)
        # 優化：預先將排除目錄轉換為集合，實現 O(1) 查找
        self.exclude_dirs_set = set(self.config["scan_settings"]["exclude_dirs"])

    def scan_directory(self, directory: str) -> List[Dict]:
        """掃描目錄中的所有 Python 檔案"""
        python_files = []

        print(f"🔍 正在掃描目錄: {directory}")

        for root, dirs, files in os.walk(directory):
            # 優化：使用預建集合進行 O(1) 查找而不是 O(n) 列表查找
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs_set]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    python_files.append(file_path)

        print(f"📁 找到 {len(python_files)} 個 Python 檔案")

        # 處理每個檔案
        all_blocks = []
        with tqdm(total=len(python_files), desc="分析檔案", unit="個") as pbar:
            for file_path in python_files:
                blocks = self._extract_code_blocks(file_path)
                all_blocks.extend(blocks)
                pbar.update(1)

        self.code_blocks = all_blocks
        print(f"📊 總共提取了 {len(all_blocks)} 個程式碼塊")

        return all_blocks

    def _extract_code_blocks(self, file_path: str) -> List[Dict]:
        """從檔案中提取程式碼塊"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                lines = content.split("\n")

            tree = ast.parse(content, filename=file_path)
            code_blocks = []

            for node in ast.walk(tree):
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ):
                    start_line = node.lineno
                    end_line = self._find_end_line(node, lines)

                    if (
                        end_line - start_line
                        < self.config["complexity_settings"]["min_lines"]
                    ):
                        continue

                    # 提取程式碼片段
                    code_lines = lines[start_line - 1 : end_line]
                    raw_code = "\n".join(code_lines)
                    normalized_code = self._normalize_code(code_lines)

                    if len(normalized_code.strip()) == 0:
                        continue

                    # 建立程式碼塊資訊
                    code_block = {
                        "file_path": file_path,
                        "start_line": start_line,
                        "end_line": end_line,
                        "raw_code": raw_code,
                        "normalized_code": normalized_code,
                        "type": type(node).__name__,
                        "name": getattr(node, "name", "unknown"),
                        "signature": self._get_function_signature(node)
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                        else None,
                    }

                    # 生成程式碼雜湊
                    code_block["hash"] = hashlib.md5(
                        code_block["normalized_code"].encode()
                    ).hexdigest()

                    # 生成 SimHash 指紋用於快速相似度檢測
                    code_block["simhash"] = Simhash(code_block["normalized_code"]).value

                    code_blocks.append(code_block)

                    # 記錄函數簽名
                    if code_block["signature"]:
                        self.function_signatures[code_block["signature"]].append(
                            code_block
                        )

        except Exception as e:
            print(f"⚠️ 無法處理檔案 {file_path}: {e}")
            return []

        return code_blocks

    def _find_end_line(self, node: ast.stmt, lines: List[str]) -> int:
        """找到 AST 節點的結束行"""
        # 簡單的啟發式方法：找到下一個同級定義或檔案結束
        start_line = node.lineno - 1

        # 找到函數的縮排級別
        if start_line < len(lines):
            indent_level = len(lines[start_line]) - len(lines[start_line].lstrip())
        else:
            return len(lines)

        # 向下搜尋，直到找到相同或更少縮排的非空行
        for i in range(start_line + 1, len(lines)):
            line = lines[i].strip()
            if line:  # 非空行
                current_indent = len(lines[i]) - len(lines[i].lstrip())
                if current_indent <= indent_level and not line.startswith(
                    ("#", '"', "'")
                ):
                    return i

        return len(lines)

    def _normalize_code(self, code_lines: List[str]) -> str:
        """標準化程式碼（移除註釋、空白等）"""
        normalized_lines = []

        for line in code_lines:
            # 移除註釋
            if self.config["similarity_settings"]["ignore_comments"]:
                if "#" in line:
                    line = line[: line.find("#")]

            # 標準化空白
            if self.config["similarity_settings"]["ignore_whitespace"]:
                line = " ".join(line.split())

            if line.strip():
                normalized_lines.append(line.strip())

        return "\n".join(normalized_lines)

    def _get_function_signature(
        self, func_node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> str:
        """提取函數簽名（參數類型和數量）"""
        params = []
        for arg in func_node.args.args:
            params.append(arg.arg)

        return f"{func_node.name}({len(params)})"

    def calculate_similarity(self, code1: str, code2: str) -> float:
        """計算兩段程式碼的相似度"""
        return SequenceMatcher(None, code1, code2).ratio()

    def find_similar_blocks_parallel(self) -> List[Dict]:
        """使用 SimHash 預過濾的高效相似度檢測 (接近 O(N) 複雜度)"""
        similar_groups = []
        processed_hashes = set()
        # 使用配置中的相似度閾值進行檢測
        config_threshold = self.config["similarity_settings"]["similarity_threshold"]
        simhash_threshold = 3  # Hamming 距離閾值，可調整

        print("🔄 正在使用 SimHash 預過濾進行程式碼相似度分析...")

        # 先按雜湊分組，處理完全重複的程式碼
        hash_groups = defaultdict(list)
        for block in self.code_blocks:
            hash_groups[block["hash"]].append(block)

        # 處理完全重複的程式碼（雜湊相同）
        exact_duplicates = []
        remaining_blocks = []

        for hash_code, blocks in hash_groups.items():
            if len(blocks) > 1:
                # 完全重複的程式碼
                group = {
                    "group_id": len(exact_duplicates) + 1,
                    "similarity_type": "exact",
                    "block_count": len(blocks),
                    "blocks": blocks,
                    "optimization_potential": self._calculate_optimization_potential(
                        blocks
                    ),
                }
                exact_duplicates.append(group)
                processed_hashes.add(hash_code)
            else:
                remaining_blocks.extend(blocks)

        similar_groups.extend(exact_duplicates)
        print(f"✅ 找到 {len(exact_duplicates)} 個完全重複的程式碼組")

        # 使用 SimHash 索引進行高效相似度檢測
        if remaining_blocks:
            try:
                print(
                    f"🔄 建立 SimHash 索引用於 {len(remaining_blocks)} 個程式碼塊的快速查找..."
                )

                # 建立 SimHash 索引（用於相似度檢測）
                simhash_objs = [
                    (block["hash"], Simhash(block["normalized_code"]))
                    for block in remaining_blocks
                ]
                index = SimhashIndex(simhash_objs, k=simhash_threshold)

                # 使用配置閾值進行相似度檢測
                for i, block in enumerate(remaining_blocks):
                    if block["hash"] not in processed_hashes:
                        similar_hashes = index.get_near_dups(
                            Simhash(block["normalized_code"])
                        )
                        if len(similar_hashes) > 1:  # 包含自己
                            group_blocks = [
                                b
                                for b in remaining_blocks
                                if b["hash"] in similar_hashes
                                and self.calculate_similarity(
                                    block["normalized_code"], b["normalized_code"]
                                )
                                >= config_threshold
                            ]
                            if len(group_blocks) > 1:
                                similar_groups.append(group_blocks)
                                processed_hashes.update(b["hash"] for b in group_blocks)

            except Exception as e:
                print(
                    f"⚠️ SimHash 索引失敗: {e}，跳過相似度檢測，只返回完全重複的結果..."
                )
                # 不進行序列相似度檢測，直接返回完全重複的結果
                pass

        print("🚀 SimHash 優化完成！從 O(N²) 降級為接近 O(N) 的查找效率")
        return similar_groups

    def _find_similar_blocks_sequential(
        self, blocks: List[Dict], processed_hashes: set
    ) -> List[Dict]:
        """序列方式找出相似的程式碼塊（優化版本）"""
        similar_groups = []
        similarity_threshold = self.config["similarity_settings"][
            "similarity_threshold"
        ]
        min_code_length = self.config["similarity_settings"]["min_code_length"]

        # 預過濾：只處理足夠長的程式碼塊
        filtered_blocks = [
            block
            for block in blocks
            if len(block["normalized_code"]) >= min_code_length
        ]
        print(f"🔍 過濾後剩餘 {len(filtered_blocks)} 個程式碼塊進行相似度分析")

        with tqdm(total=len(filtered_blocks), desc="序列相似度檢測", unit="個") as pbar:
            for i, block1 in enumerate(filtered_blocks):
                if block1["hash"] in processed_hashes:
                    pbar.update(1)
                    continue

                # 進一步過濾：長度相似的程式碼塊
                similar_candidates = []
                len1 = len(block1["normalized_code"])

                for block2 in filtered_blocks[i + 1 :]:
                    if block2["hash"] in processed_hashes:
                        continue

                    len2 = len(block2["normalized_code"])
                    # 長度相似度檢查（允許30%的差異）
                    if abs(len1 - len2) / max(len1, len2) <= 0.3:
                        similar_candidates.append(block2)

                # 只對候選者進行詳細相似度計算
                similar_blocks = []
                for block2 in similar_candidates:
                    if block2["hash"] in processed_hashes:
                        continue

                    similarity = self.calculate_similarity(
                        block1["normalized_code"], block2["normalized_code"]
                    )

                    if similarity >= similarity_threshold:
                        similar_blocks.append(block2)
                        processed_hashes.add(block2["hash"])

                if similar_blocks:
                    group = {
                        "group_id": len(similar_groups) + 1,
                        "similarity_type": "similar",
                        "block_count": len(similar_blocks) + 1,
                        "blocks": [block1] + similar_blocks,
                        "optimization_potential": self._calculate_optimization_potential(
                            [block1] + similar_blocks
                        ),
                    }
                    similar_groups.append(group)

                processed_hashes.add(block1["hash"])
                pbar.update(1)

        return similar_groups

    def _calculate_optimization_potential(self, blocks: List[Dict]) -> Dict:
        """計算優化潛力"""
        if not blocks:
            return {
                "duplicate_lines": 0,
                "potential_savings": "0 行程式碼",
                "refactor_suggestion": "無",
            }

        # 計算重複的行數
        first_block = blocks[0]
        total_lines = sum(block["end_line"] - block["start_line"] for block in blocks)
        duplicate_lines = total_lines - (
            first_block["end_line"] - first_block["start_line"]
        )

        # 生成建議
        if duplicate_lines > 20:
            suggestion = "強烈建議重構：建立共用函數或模組"
        elif duplicate_lines > 10:
            suggestion = "考慮重構：提取共同邏輯"
        elif duplicate_lines > 5:
            suggestion = "可以考慮合併相似程式碼"
        else:
            suggestion = "小量重複，可以保持現狀"

        return {
            "duplicate_lines": duplicate_lines,
            "potential_savings": f"{duplicate_lines} 行程式碼",
            "refactor_suggestion": suggestion,
        }

    def run_analysis(self) -> Dict:
        """執行相似度分析"""
        if not self.code_blocks:
            print("⚠️ 尚未掃描任何程式碼，請先執行 scan_directory()")
            return {}

        print("🚀 開始相似度分析...")

        # 使用並行處理找出相似的程式碼塊
        similar_groups = self.find_similar_blocks_parallel()

        # 統計結果
        total_duplicates = sum(group["block_count"] for group in similar_groups)
        total_savings = sum(
            group["optimization_potential"]["duplicate_lines"]
            for group in similar_groups
        )

        results = {
            "summary": {
                "total_code_blocks": len(self.code_blocks),
                "similar_groups": len(similar_groups),
                "total_duplicate_blocks": total_duplicates,
                "potential_line_savings": total_savings,
                "files_analyzed": len(
                    set(block["file_path"] for block in self.code_blocks)
                ),
            },
            "similar_groups": similar_groups,
        }

        print("✅ 分析完成！")
        print(f"   - 分析了 {results['summary']['total_code_blocks']} 個程式碼塊")
        print(f"   - 找到 {results['summary']['similar_groups']} 個相似群組")
        print(f"   - 可能節省 {results['summary']['potential_line_savings']} 行程式碼")

        return results

    def _analyze_function_patterns(self) -> Dict:
        """分析函數簽名模式"""
        patterns = {
            "most_common_signatures": [],
            "signature_distribution": {},
            "potential_overloads": [],
        }

        # 統計函數簽名
        signature_counts = defaultdict(int)
        for signature, blocks in self.function_signatures.items():
            signature_counts[signature] = len(blocks)

        # 找出最常見的簽名
        sorted_signatures = sorted(
            signature_counts.items(), key=lambda x: x[1], reverse=True
        )
        patterns["most_common_signatures"] = sorted_signatures[:10]
        patterns["signature_distribution"] = dict(signature_counts)

        # 找出可能的重載函數（相同函數名但不同參數數量）
        function_names = defaultdict(list)
        for signature in signature_counts:
            if "(" in signature:
                name = signature.split("(")[0]
                param_count = signature.split("(")[1].split(")")[0]
                function_names[name].append((signature, param_count))

        for name, signatures in function_names.items():
            if len(signatures) > 1:
                patterns["potential_overloads"].append(
                    {"function_name": name, "signatures": signatures}
                )

        return patterns

    def save_results(self, results: Dict, output_file: str = "similarity_results.json"):
        """儲存分析結果"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"💾 結果已儲存到 {output_file}")


if __name__ == "__main__":
    # 測試程式碼
    detector = SimilarityDetector()

    # 從設定檔讀取根目錄
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    root_dir = config["scan_settings"]["root_directory"]

    # 掃描並分析
    detector.scan_directory(root_dir)
    results = detector.run_analysis()
    detector.save_results(results)

    print("🎉 相似度檢測完成！")
