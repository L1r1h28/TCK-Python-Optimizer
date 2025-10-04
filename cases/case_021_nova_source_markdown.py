"""
Case 21: NOVA_SOURCE_MARKDOWN_OPTIMIZATION - 對應 021_NOVA_SOURCE_MARKDOWN_OPTIMIZATION.md
"""

import random
import re

# 測試案例名稱
name = "case_021_nova_source_markdown"
description = "Nova-Source Markdown 處理優化：正則表達式與高效字串操作。"


def setup_data():
    """準備大規模 Markdown 測試資料"""
    lines = []
    for i in range(10000):  # 10000 行複雜 Markdown
        line_type = random.choice(["header", "list", "link", "table", "normal"])

        if line_type == "header":
            level = random.randint(1, 6)
            lines.append("#" * level + f" Header Level {level} - Line {i}")
        elif line_type == "list":
            indent = "  " * random.randint(0, 3)
            marker = random.choice(["-", "*", "+"])
            lines.append(f"{indent}{marker} List item {i}")
        elif line_type == "link":
            lines.append(
                f"This is [link text {i}](https://example.com/{i}) in line {i}"
            )
        elif line_type == "table":
            lines.append(f"| Column 1 | Column 2 {i} | Column 3 |")
        else:
            lines.append(f"Regular text line {i} with some content")

    content = "\n".join(lines)
    return (content,)


def unoptimized_version(content):
    """❌ 原始版本：低效的字串處理和條件檢查"""
    lines = content.split("\n")
    processed_lines = []
    link_count = 0

    for line in lines:
        # 模擬一些處理
        processed_line = line.rstrip()

        # 標題檢查
        if line.strip().startswith("#"):
            processed_line += " [HEADER]"

        # 鏈接檢查 - 暴力字串查找
        if "[" in line and "]" in line and "(" in line and ")" in line:
            link_count += 1

        processed_lines.append(processed_line)

    return len(processed_lines), link_count


def optimized_version_regex(content):
    """✅ 優化版本：應用 TCK 優化技術"""
    # 使用 splitlines() 比 split("\n") 更高效
    lines = content.splitlines()

    # 預編譯正則表達式
    header_pattern = re.compile(r"^\s*#")
    link_pattern = re.compile(r"\[[^\]]+\]\([^)]+\)")

    processed_lines = []
    link_count = 0

    for line in lines:
        # 模擬一些處理
        processed_line = line  # rstrip 在 splitlines 模式下通常不是必須的

        # 標題檢查
        if header_pattern.match(line):
            processed_line += " [HEADER]"

        # 鏈接檢查
        if link_pattern.search(line):
            link_count += 1

        processed_lines.append(processed_line)

    return len(processed_lines), link_count


# 優化版本字典
optimized_versions = {"regex_and_splitlines": optimized_version_regex}
