#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试后端API端点
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(method, path, data=None):
    """测试API端点"""
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        else:
            return False, f"不支持的方法: {method}"
        
        return response.status_code == 200, {
            "status": response.status_code,
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except requests.exceptions.ConnectionError:
        return False, "无法连接到后端服务，请确保后端服务已启动"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    print("=" * 60)
    print("测试后端API端点")
    print("=" * 60)
    
    # 1. 测试健康检查
    print("\n1. 测试健康检查端点...")
    success, result = test_endpoint("GET", "/health")
    if success:
        print(f"   ✓ /health: {result}")
    else:
        print(f"   ✗ /health: {result}")
    
    # 2. 测试生成单个爻
    print("\n2. 测试生成单个爻端点...")
    success, result = test_endpoint("POST", "/api/divination/generate-line")
    if success:
        print(f"   ✓ /api/divination/generate-line: {result}")
    else:
        print(f"   ✗ /api/divination/generate-line: {result}")
        if isinstance(result, str) and "无法连接" in result:
            print("\n   请启动后端服务：")
            print("   cd backend")
            print("   python start_server.py")
    
    # 3. 测试根路径
    print("\n3. 测试根路径...")
    success, result = test_endpoint("GET", "/")
    if success:
        print(f"   ✓ /: {result}")
    else:
        print(f"   ✗ /: {result}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
