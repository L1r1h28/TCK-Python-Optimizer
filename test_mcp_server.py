#!/usr/bin/env python3
"""
TCK MCP Server 測試腳本
測試各項查詢功能
"""

import requests
import json
import subprocess
import sys
import time

def test_server():
    """測試 MCP Server 功能"""

    # 啟動 server（在背景運行）
    print("🚀 啟動 MCP Server...")
    server_process = subprocess.Popen([
        sys.executable, "mcp_server.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)

    # 等待 server 啟動
    print("⏳ 等待服務器啟動...")
    time.sleep(3)

    try:
        # 測試根端點
        print("📡 測試根端點...")
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ 根端點回應: {response.json()}")

        # 測試列出所有模式
        print("📋 測試列出優化模式...")
        response = requests.get("http://localhost:8000/patterns", timeout=5)
        patterns = response.json()["patterns"]
        print(f"✅ 找到 {len(patterns)} 個優化模式")

        # 測試查詢功能
        test_queries = [
            "list lookup",
            "cache",
            "loop",
            "optimization"
        ]

        for query in test_queries:
            print(f"🔍 測試查詢: '{query}'")
            response = requests.post(
                "http://localhost:8000/query",
                json={"pattern": query},
                headers={"Content-Type": "application/json"},
                timeout=5
            )

            result = response.json()
            matches = result["matches"]
            print(f"   📊 找到 {len(matches)} 個匹配")

            if matches:
                first_match = matches[0]
                print(f"   🏆 第一個匹配: {first_match['name']}")
                print(f"   ⚡ 效能提升: {first_match['performance_gain']}")

        print("✅ 所有測試通過！")

    except requests.exceptions.RequestException as e:
        print(f"❌ 網路請求失敗: {e}")
        print("💡 請確保 MCP Server 正在運行")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
    finally:
        # 停止 server
        print("🛑 停止 MCP Server...")
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except:
            server_process.kill()

if __name__ == "__main__":
    test_server()