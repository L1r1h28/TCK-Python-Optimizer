"""
TurboCode Kit Core Engine
=========================

TCK 核心分析引擎包，包含所有程式碼分析和優化模組。

模組列表:
- code_repository: 程式碼倉庫管理
- frequency_analyzer: 頻率分析器
- complexity_calculator: 複雜度計算器
- similarity_detector: 相似度檢測器
- report_generator: 報告生成器

Author: TurboCode Kit (TCK)
Version: 2.0
"""

__version__ = "2.0"
__author__ = "TurboCode Kit (TCK)"

# Public API: 將核心常用類別與函式在此暴露，方便第三方以 `import tck_core` 使用
# Minimal guidance: 若需更多 API 文件，請參見根目錄 README
__all__ = [
	"__version__",
	"__author__",
	"CodeRepository",
	"CodeFrequencyAnalyzer",
	"ComplexityCalculator",
	"SimilarityDetector",
	"OptimizationReportGenerator",
]

# 延遲導入（import toplevel names for convenience）
try:
	from .code_repository import CodeRepository  # type: ignore
	from .frequency_analyzer import CodeFrequencyAnalyzer  # type: ignore
	from .complexity_calculator import ComplexityCalculator  # type: ignore
	from .similarity_detector import SimilarityDetector  # type: ignore
	from .report_generator import OptimizationReportGenerator  # type: ignore
except Exception:
	# 在某些開發環境下（例如未安裝相依套件）避免導入失敗阻斷包匯入
	pass