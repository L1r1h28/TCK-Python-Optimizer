#!/usr/bin/env python3
"""
TurboCode Kit MCP Server
========================

將 TCK 優化案例轉換為可查詢的 Model Context Protocol Server
為 GitHub Copilot 提供即時優化建議

Author: TurboCode Kit (TCK)
Version: 1.0
"""

import inspect
import importlib
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
import uvicorn
import os
import sys

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_cases import *
from turbo_utils import *


class OptimizationLevel(Enum):
    HIGH = "A"
    MEDIUM_HIGH = "B+"
    MEDIUM = "B"
    MEDIUM_LOW = "C+"
    LOW = "C"
    VERY_LOW = "D"


class OptimizationPattern(BaseModel):
    """優化模式資料結構"""
    name: str
    description: str
    complexity_before: str
    complexity_after: str
    performance_gain: str
    level: str
    applicable_scenarios: List[str]
    code_example: str
    optimizer_class: Optional[str] = None
    test_case_class: str


class QueryRequest(BaseModel):
    """查詢請求結構"""
    pattern: str
    context: Optional[str] = None
    language: str = "python"


class QueryResponse(BaseModel):
    """查詢回應結構"""
    matches: List[OptimizationPattern]
    suggestions: List[str]
    confidence: float


class TCKMCPServer:
    """TCK MCP Server 主類"""

    def __init__(self):
        self.optimization_index = self._build_optimization_index()
        self.app = FastAPI(
            title="TurboCode Kit MCP Server",
            description="為 GitHub Copilot 提供 Python 效能優化建議",
            version="1.0.0"
        )
        self._setup_routes()

    def _build_optimization_index(self) -> Dict[str, OptimizationPattern]:
        """從現有程式碼中建立優化案例索引"""
        index = {}

        # 效能數據映射 (基於實測結果)
        performance_data = {
            "LIST_LOOKUP": ("O(n)", "O(1)", "32.5x - 325.8x", "A"),
            "FOR_LOOP_VECTORIZATION": ("O(n)", "O(1)", "60.9x - 120.5x", "A+"),
            "CONFIG_CACHE": ("O(n)", "O(1)", "28.1x", "A"),
            "STRING_CONCATENATION": ("O(n)", "O(1)", "7.0x", "B+"),
            "DICTIONARY_LOOKUP": ("O(n)", "O(1)", "1.0x", "D"),
            "SET_OPERATIONS": ("O(n)", "O(1)", "37.7x", "B"),
            "DEQUE_OPERATIONS": ("O(n)", "O(1)", "140.8x", "A"),
            "MEMORIZATION_CACHE": ("O(2^n)", "O(1)", "2803.3x", "A"),
            "BUILTIN_FUNCTIONS": ("O(n)", "O(1)", "1.9x", "B+"),
            "COMPREHENSION_OPTIMIZATION": ("O(n)", "O(1)", "1.0x", "B"),
            "ITERATOR_CHAINING": ("O(n)", "O(1)", "18.3x", "B"),
            "DATACLASS_OPTIMIZATION": ("O(n)", "O(1)", "16.7x", "B+"),
            "LOOP_LOOKUP_OPTIMIZATION": ("O(n^2)", "O(1)", "221.0x", "A+"),
            "HIGH_FREQ_CALLS_OPTIMIZATION": ("O(n)", "O(1)", "2.1x", "B"),
        }

        # 解析 test_cases.py 中的所有 TestCase 類
        test_cases_module = importlib.import_module('test_cases')
        turbo_utils_module = importlib.import_module('turbo_utils')

        for name, obj in inspect.getmembers(test_cases_module):
            if (inspect.isclass(obj) and name.startswith('TestCase') and
                hasattr(obj, 'original_version') and hasattr(obj, 'optimized_version')):

                # 提取測試案例資訊
                pattern_name = self._extract_pattern_name(name)
                description = self._extract_description(obj)
                scenarios = self._extract_scenarios(obj)

                # 獲取效能數據
                perf_key = pattern_name.upper().replace(' ', '_')
                if perf_key in performance_data:
                    complexity_before, complexity_after, perf_gain, level = performance_data[perf_key]
                else:
                    complexity_before, complexity_after, perf_gain, level = "O(n)", "O(1)", "Unknown", "B"

                # 獲取程式碼範例
                code_example = self._extract_code_example(obj)

                # 查找對應的優化器類
                optimizer_class = self._find_optimizer_class(pattern_name, turbo_utils_module)

                pattern = OptimizationPattern(
                    name=pattern_name,
                    description=description,
                    complexity_before=complexity_before,
                    complexity_after=complexity_after,
                    performance_gain=perf_gain,
                    level=level,
                    applicable_scenarios=scenarios,
                    code_example=code_example,
                    optimizer_class=optimizer_class,
                    test_case_class=name
                )

                # 使用多個關鍵字索引
                keywords = self._generate_keywords(pattern_name, description, scenarios)
                for keyword in keywords:
                    if keyword not in index:
                        index[keyword] = pattern

        return index

    def _extract_pattern_name(self, class_name: str) -> str:
        """從類名提取模式名稱"""
        # TestCase1_ListLookup -> LIST_LOOKUP
        match = re.search(r'TestCase\d+_(.+)', class_name)
        if match:
            return match.group(1).replace('_', ' ').title()
        return class_name

    def _extract_description(self, test_class) -> str:
        """提取測試案例描述"""
        if hasattr(test_class, '__doc__') and test_class.__doc__:
            return test_class.__doc__.strip()
        return f"Optimization pattern for {test_class.__name__}"

    def _extract_scenarios(self, test_class) -> List[str]:
        """提取適用場景"""
        scenarios = []
        doc = getattr(test_class, '__doc__', '')
        if '使用場景' in doc or '適用於' in doc:
            # 簡單的場景提取邏輯
            scenarios = ["頻繁操作", "效能瓶頸", "大型資料處理"]
        else:
            scenarios = ["通用效能優化"]
        return scenarios

    def _extract_code_example(self, test_class) -> str:
        """提取程式碼範例"""
        try:
            source = inspect.getsource(test_class.optimized_version)
            # 提取函數體
            lines = source.split('\n')
            # 移除裝飾器和註釋，保留核心邏輯
            code_lines = [line for line in lines if not line.strip().startswith(('"""', "'''", '#'))]
            return '\n'.join(code_lines[:10])  # 只取前10行作為範例
        except:
            return "# Code example not available"

    def _find_optimizer_class(self, pattern_name: str, turbo_utils_module) -> Optional[str]:
        """查找對應的優化器類"""
        pattern_to_class = {
            "List Lookup": "ListLookupOptimizer",
            "Config Cache": "ConfigCacheManager",
            "Vectorization Accelerator": "VectorizationAccelerator",
            "Set Operations": "SetOperationsOptimizer",
            "Deque Operations": "DequeOptimizer",
            "Memorization Cache": "MemoizationCache",
            "Comprehension Optimization": "ComprehensionOptimizer",
            "Iterator Chaining": "IteratorChainer",
            "Data Class Optimization": "DataClassOptimizer",
            "Loop Lookup Optimization": "LoopLookupOptimizer",
        }

        return pattern_to_class.get(pattern_name)

    def _generate_keywords(self, pattern_name: str, description: str, scenarios: List[str]) -> List[str]:
        """生成搜索關鍵字"""
        keywords = []

        # 基本關鍵字
        keywords.append(pattern_name.lower())

        # 從描述中提取關鍵字
        desc_words = re.findall(r'\b\w+\b', description.lower())
        keywords.extend(desc_words)

        # 從場景中提取關鍵字
        for scenario in scenarios:
            scenario_words = re.findall(r'\b\w+\b', scenario.lower())
            keywords.extend(scenario_words)

        # 常見的效能相關關鍵字映射
        keyword_mappings = {
            'list': ['list', 'array', '清單', '列表'],
            'lookup': ['lookup', 'search', 'find', '查找', '搜尋'],
            'loop': ['loop', 'for', 'iteration', '循環', '迴圈'],
            'cache': ['cache', 'memoization', '快取', '記憶'],
            'optimization': ['optimization', 'optimize', '效能', '優化'],
        }

        for key, variants in keyword_mappings.items():
            if key in ' '.join(keywords).lower():
                keywords.extend(variants)

        return list(set(keywords))  # 去重

    def query_optimization(self, pattern: str, context: Optional[str] = None) -> QueryResponse:
        """查詢優化建議"""
        pattern_lower = pattern.lower()
        matches = []
        suggestions = []

        # 精確匹配
        if pattern_lower in self.optimization_index:
            matches.append(self.optimization_index[pattern_lower])

        # 模糊匹配
        for keyword, opt_pattern in self.optimization_index.items():
            if (pattern_lower in keyword.lower() or
                keyword.lower() in pattern_lower or
                any(word in keyword.lower() for word in pattern_lower.split())):
                if opt_pattern not in matches:
                    matches.append(opt_pattern)

        # 生成建議
        if not matches:
            suggestions.append("未找到完全匹配的優化模式")
            suggestions.append("嘗試使用更通用的關鍵字，如 'list', 'loop', 'cache'")
        else:
            suggestions.append(f"找到 {len(matches)} 個相關的優化模式")
            if len(matches) > 3:
                suggestions.append("建議優先考慮 A 級別的優化模式")

        # 計算信心度
        confidence = min(len(matches) * 0.2, 1.0) if matches else 0.0

        return QueryResponse(
            matches=matches[:5],  # 最多返回5個匹配
            suggestions=suggestions,
            confidence=confidence
        )

    def _setup_routes(self):
        """設置 API 路由"""

        @self.app.get("/")
        def root():
            return {"message": "TurboCode Kit MCP Server", "version": "1.0.0"}

        @self.app.post("/query")
        def query_endpoint(request: QueryRequest):
            try:
                result = self.query_optimization(request.pattern, request.context)
                return result.dict()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/patterns")
        def list_patterns():
            """列出所有可用的優化模式"""
            patterns = {}
            for keyword, pattern in self.optimization_index.items():
                if pattern.name not in patterns:
                    patterns[pattern.name] = {
                        "description": pattern.description,
                        "level": pattern.level,
                        "performance_gain": pattern.performance_gain
                    }
            return {"patterns": patterns}


def main():
    """啟動 MCP Server"""
    server = TCKMCPServer()
    print("🚀 TurboCode Kit MCP Server 啟動中...")
    print(f"📊 已載入 {len(server.optimization_index)} 個優化模式")
    print("🌐 服務器運行在 http://localhost:8000")
    print("📖 API 文檔: http://localhost:8000/docs")
    print("🧪 測試查詢: curl -X POST http://localhost:8000/query -H 'Content-Type: application/json' -d '{\"pattern\":\"list lookup\"}'")

    # 使用更好的配置
    uvicorn.run(
        server.app,
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()