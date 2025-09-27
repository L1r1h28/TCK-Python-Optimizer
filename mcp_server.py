#!/usr/bin/env python3
"""
TurboCode Kit MCP Server
========================

將 TCK 優化案例轉換為可查詢的 Model Context Protocol Server
為 GitHub Copilot 提供即時優化建議

Author: TurboCode Kit (TCK)
Version: 1.0
"""

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
        """從現有程式碼中建立優化案例索引 (優化版本：預編譯索引)"""
        # 預編譯的優化數據，減少運行時解析
        performance_data = {
            "LIST_LOOKUP": ("O(n)", "O(1)", "32.5x-325.8x", "A"),
            "FOR_LOOP_VECTORIZATION": ("O(n)", "O(1)", "60.9x-120.5x", "A+"),
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

        # 預定義的關鍵字映射，減少動態生成
        keyword_mappings = {
            'list': ['list', 'lookup', 'search', '清單', '查找', '列表'],
            'cache': ['cache', 'memoization', '快取', '記憶', ' Memorization'],
            'loop': ['loop', 'for', 'iteration', '循環', '迴圈', 'lookup'],
            'string': ['string', 'concatenation', '字串', '串接', 'str'],
            'set': ['set', 'operations', '集合', '運算', 'Set'],
            'optimization': ['optimization', 'optimize', '效能', '優化', 'performance'],
        }

        index = {}

        # 快速索引建立
        for pattern_key, (before, after, perf, level) in performance_data.items():
            pattern_name = pattern_key.replace('_', ' ').title()

            # 建立基本模式
            base_pattern = OptimizationPattern(
                name=pattern_name,
                description=f"優化模式: {pattern_name}",
                complexity_before=before,
                complexity_after=after,
                performance_gain=perf,
                level=level,
                applicable_scenarios=["效能優化"],
                code_example="# 優化代碼範例",
                test_case_class=f"TestCase{pattern_key.split('_')[0]}"
            )

            # 為每個關鍵字創建索引
            for category, keywords in keyword_mappings.items():
                if category.upper() in pattern_key:
                    for keyword in keywords:
                        index[keyword] = base_pattern

        return index

    def query_optimization(self, pattern: str, context: Optional[str] = None) -> QueryResponse:
        """查詢優化建議 (優化版本：簡化邏輯)"""
        pattern_lower = pattern.lower()

        # 直接關鍵字匹配 (O(1) 查找)
        matches = []
        if pattern_lower in self.optimization_index:
            matches.append(self.optimization_index[pattern_lower])

        # 擴展搜索相關關鍵字
        for keyword in self.optimization_index.keys():
            if (pattern_lower in keyword and keyword != pattern_lower):
                pattern_obj = self.optimization_index[keyword]
                if pattern_obj not in matches:
                    matches.append(pattern_obj)
                    if len(matches) >= 3:  # 限制結果數量
                        break

        # 生成簡化建議
        suggestions = []
        if not matches:
            suggestions.append("未找到完全匹配的優化模式")
        else:
            suggestions.append(f"找到 {len(matches)} 個相關的優化模式")

        confidence = min(len(matches) * 0.3, 1.0) if matches else 0.0

        return QueryResponse(
            matches=matches[:3],  # 最多返回3個匹配
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