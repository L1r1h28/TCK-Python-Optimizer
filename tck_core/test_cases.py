"""
TCK 測試案例自動載入器 - 從 cases/ 目錄動態載入所有測試案例

藍圖對應架構：
- 每個 case_*.py 檔案對應一個 optimization_blueprints/ 下的 .md 檔案
- 保持 tck_enhanced_analyzer.py 相容性，提供 TEST_CASES 和 TEST_CASE_DICT
- 一個藍圖對應一個 case，不佔用根目錄，模組化組織
"""

import importlib.util
from pathlib import Path
from typing import List, Any

def load_cases_from_directory(cases_dir: str = "cases") -> List[Any]:
    """
    從指定目錄自動載入所有測試案例
    
    Args:
        cases_dir: 案例目錄路徑，預設為 "cases"
    
    Returns:
        載入的測試案例類別列表
    """
    cases = []
    cases_path = Path(cases_dir)
    
    if not cases_path.exists():
        print(f"⚠️  警告：cases 目錄不存在: {cases_dir}")
        return []
    
    # 載入所有 case_*.py 檔案，按數字順序排序
    for case_file in sorted(cases_path.glob("case_*.py")):
        try:
            # 動態載入模組
            spec = importlib.util.spec_from_file_location(
                case_file.stem, case_file
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 尋找 TestCase 類別
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        attr_name.startswith('TestCase') and 
                        hasattr(attr, 'name')):
                        cases.append(attr)
                        blueprint_ref = getattr(attr, 'blueprint_file', 'N/A')
                        print(f"✅ 載入案例: {attr.name} ({case_file.name}) -> {blueprint_ref}")
                        
        except Exception as e:
            print(f"❌ 載入失敗: {case_file.name} - {e}")
    
    return cases

# 🚀 自動載入所有測試案例
print("🔄 正在自動載入測試案例...")
TEST_CASES = load_cases_from_directory()

# 📊 效能最佳化：O(1) 名稱查找字典 (基於 list_lookup_accelerator.md)
TEST_CASE_DICT = {test_case.name: test_case for test_case in TEST_CASES}

# 別名保持向後相容性
ALL_TEST_CASES = TEST_CASES

print(f"✅ 載入完成：共 {len(TEST_CASES)} 個測試案例")
print(f"📋 可用案例：{[tc.name for tc in TEST_CASES]}")