"""
TCK Case 012: 資料類別優化

對應藍圖：dataclass_optimization.md
優化策略：手動 __init__ → @dataclass 自動生成
效能提升：程式碼簡潔度 + 執行效率
"""

from dataclasses import dataclass

# 測試案例名稱
name = "case_012_dataclass"
description = "資料類別優化：手動實現 → @dataclass 自動生成，提升效率與維護性。"


def setup_data():
    """準備測試資料"""
    # 大量物件建立測試
    count = 10000
    names = [f"user_{i}" for i in range(count)]
    ages = list(range(18, 18 + count))
    emails = [f"user_{i}@example.com" for i in range(count)]
    return names, ages, emails


# --- 未優化版本 ---
class ManualUser:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email

    def __repr__(self):
        return f"ManualUser(name='{self.name}', age={self.age}, email='{self.email}')"

    def __eq__(self, other):
        if not isinstance(other, ManualUser):
            return False
        return (
            self.name == other.name
            and self.age == other.age
            and self.email == other.email
        )


def unoptimized_version(names, ages, emails):
    """❌ 原始版本：手動實現類別

    效能問題：
    - 手動實現 __init__, __repr__, __eq__
    - Python 層級的方法調用
    - 大量樣板程式碼
    """
    users = [
        ManualUser(name, age, email) for name, age, email in zip(names, ages, emails)
    ]
    # 返回創建的物件數量
    return len(users)


# --- 優化版本 ---
@dataclass
class DataUser:
    name: str
    age: int
    email: str


def optimized_version_dataclass(names, ages, emails):
    """✅ 優化版本：@dataclass 自動生成

    優化策略：
    - 使用 @dataclass 自動生成方法
    - C 層級實現，效率更高
    - 程式碼簡潔，維護性佳
    """
    users = [
        DataUser(name, age, email) for name, age, email in zip(names, ages, emails)
    ]
    # 返回創建的物件數量
    return len(users)


# 優化版本字典
optimized_versions = {"dataclass_generated": optimized_version_dataclass}
