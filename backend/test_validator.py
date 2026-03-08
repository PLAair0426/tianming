#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试验证模块
"""
from app.core.processor import output_hexagram_results
from app.core.validator import validate_hexagram_data, log_validation_result

def test_validation():
    """测试验证功能"""
    print("=" * 60)
    print("测试卦象数据验证模块")
    print("=" * 60)
    
    # 生成卦象数据
    print("\n1. 生成卦象数据...")
    hexagram_data = output_hexagram_results()
    
    print(f"\n生成的数据:")
    print(f"  本卦名称: {hexagram_data['original_name']}")
    print(f"  本卦二进制: {hexagram_data['original_binary']}")
    print(f"  本卦数值: {hexagram_data['original_hexagram']}")
    print(f"  变卦名称: {hexagram_data['changed_name']}")
    print(f"  变卦二进制: {hexagram_data['changed_binary']}")
    print(f"  变卦数值: {hexagram_data['changed_hexagram']}")
    
    # 验证数据
    print("\n2. 验证数据...")
    validation_result = validate_hexagram_data(hexagram_data)
    assert validation_result["valid"] is True
    assert validation_result["errors"] == []
    
    # 输出验证结果
    print("\n验证结果:")
    log_validation_result(validation_result)
    
    # 测试错误情况
    print("\n" + "=" * 60)
    print("测试错误情况")
    print("=" * 60)
    
    # 构造一个错误的卦象数据
    wrong_data = hexagram_data.copy()
    wrong_data["original_name"] = "错误的卦名"
    
    print("\n测试错误的卦名...")
    wrong_validation = validate_hexagram_data(wrong_data)
    assert wrong_validation["valid"] is False
    assert any("卦名不匹配" in error for error in wrong_validation["errors"])
    assert wrong_validation.get("fixed")
    assert wrong_validation["fixed"]["original_name"] == hexagram_data["original_name"]
    log_validation_result(wrong_validation)
    
    if wrong_validation.get("fixed"):
        print(f"\n修复后的卦名: {wrong_validation['fixed']['original_name']}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_validation()
