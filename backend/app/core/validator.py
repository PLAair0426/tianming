"""
卦象数据验证模块
用于验证生成的卦象数据是否正确
"""
from app.core.constants import eight_hexagram, sixty_four_hexagrams_index


def validate_hexagram_data(hexagram_data: dict) -> dict:
    """
    验证卦象数据是否正确
    
    Args:
        hexagram_data: 包含卦象数据的字典
        
    Returns:
        dict: 包含验证结果的字典
        {
            "valid": bool,  # 是否通过验证
            "errors": list,  # 错误列表
            "warnings": list,  # 警告列表
            "fixed": dict  # 修复后的数据（如果有修复）
        }
    """
    errors = []
    warnings = []
    fixed_data = hexagram_data.copy()
    
    # 1. 验证本卦
    original_validation = _validate_single_hexagram(
        hexagram_data.get("original_binary", []),
        hexagram_data.get("original_hexagram", []),
        hexagram_data.get("original_name", ""),
        "本卦"
    )
    errors.extend(original_validation["errors"])
    warnings.extend(original_validation["warnings"])
    if original_validation.get("fixed_name"):
        fixed_data["original_name"] = original_validation["fixed_name"]
        warnings.append(f"本卦名称已自动修复: {hexagram_data.get('original_name')} -> {original_validation['fixed_name']}")
    
    # 2. 验证变卦
    changed_validation = _validate_single_hexagram(
        hexagram_data.get("changed_binary", []),
        hexagram_data.get("changed_hexagram", []),
        hexagram_data.get("changed_name", ""),
        "变卦"
    )
    errors.extend(changed_validation["errors"])
    warnings.extend(changed_validation["warnings"])
    if changed_validation.get("fixed_name"):
        fixed_data["changed_name"] = changed_validation["fixed_name"]
        warnings.append(f"变卦名称已自动修复: {hexagram_data.get('changed_name')} -> {changed_validation['fixed_name']}")
    
    # 3. 验证变卦计算逻辑
    change_logic_errors = _validate_change_logic(
        hexagram_data.get("original_hexagram", []),
        hexagram_data.get("changed_hexagram", []),
        hexagram_data.get("original_binary", []),
        hexagram_data.get("changed_binary", [])
    )
    errors.extend(change_logic_errors)
    
    # 4. 验证数据完整性
    completeness_errors = _validate_completeness(hexagram_data)
    errors.extend(completeness_errors)
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "fixed": fixed_data if warnings else None
    }


def _validate_single_hexagram(binary: list, hexagram_values: list, name: str, label: str) -> dict:
    """
    验证单个卦象（本卦或变卦）
    
    Args:
        binary: 二进制数组 [0,1,0,1,1,0] 从下往上
        hexagram_values: 原始数值数组 [6,7,8,9] 从下往上
        name: 卦名
        label: 标签（"本卦"或"变卦"）
        
    Returns:
        dict: 验证结果
    """
    errors = []
    warnings = []
    fixed_name = None
    
    # 检查数组长度
    if len(binary) != 6:
        errors.append(f"{label}: binary数组长度不正确，应为6，实际为{len(binary)}")
        return {"errors": errors, "warnings": warnings}
    
    if len(hexagram_values) != 6:
        errors.append(f"{label}: hexagram_values数组长度不正确，应为6，实际为{len(hexagram_values)}")
        return {"errors": errors, "warnings": warnings}
    
    # 验证 binary 和 hexagram_values 的一致性
    for i in range(6):
        expected_binary = 1 if hexagram_values[i] in [7, 9] else 0
        if binary[i] != expected_binary:
            errors.append(
                f"{label}: 第{i+1}爻（从下往上）数据不一致 - "
                f"hexagram_values[{i}]={hexagram_values[i]} 应为binary={expected_binary}，实际binary={binary[i]}"
            )
    
    # 验证卦名是否正确
    lower_bin = tuple(binary[:3])  # 下卦：初、二、三爻
    upper_bin = tuple(binary[3:])  # 上卦：四、五、上爻
    
    lower_info = eight_hexagram.get(lower_bin, None)
    upper_info = eight_hexagram.get(upper_bin, None)
    
    if not lower_info:
        errors.append(f"{label}: 下卦二进制 {lower_bin} 无法识别")
        return {"errors": errors, "warnings": warnings}
    
    if not upper_info:
        errors.append(f"{label}: 上卦二进制 {upper_bin} 无法识别")
        return {"errors": errors, "warnings": warnings}
    
    # 查找正确的卦名
    correct_name = sixty_four_hexagrams_index.get(
        (upper_info["name"], lower_info["name"]), 
        None
    )
    
    if not correct_name:
        errors.append(
            f"{label}: 无法找到对应的卦名 - "
            f"上卦: {upper_info['name']}({upper_info['nature']}), "
            f"下卦: {lower_info['name']}({lower_info['nature']})"
        )
        return {"errors": errors, "warnings": warnings}
    
    # 检查卦名是否匹配
    if name != correct_name:
        errors.append(
            f"{label}: 卦名不匹配 - "
            f"实际: {name}, 应为: {correct_name} "
            f"(上{upper_info['name']}下{lower_info['name']})"
        )
        fixed_name = correct_name
    
    return {
        "errors": errors,
        "warnings": warnings,
        "fixed_name": fixed_name
    }


def _validate_change_logic(
    original_hexagram: list,
    changed_hexagram: list,
    original_binary: list,
    changed_binary: list
) -> list:
    """
    验证变卦计算逻辑是否正确
    
    规则：
    - 6 (老阴) -> 7 (少阳)
    - 9 (老阳) -> 8 (少阴)
    - 7 (少阳) -> 7 (不变)
    - 8 (少阴) -> 8 (不变)
    """
    errors = []
    
    if len(original_hexagram) != 6 or len(changed_hexagram) != 6:
        errors.append("变卦计算验证: 数组长度不正确")
        return errors
    
    for i in range(6):
        orig_val = original_hexagram[i]
        changed_val = changed_hexagram[i]
        
        # 验证变卦规则
        if orig_val == 6:
            if changed_val != 7:
                errors.append(
                    f"变卦计算错误: 第{i+1}爻（从下往上）"
                    f"老阴(6)应变为少阳(7)，实际变为{changed_val}"
                )
        elif orig_val == 9:
            if changed_val != 8:
                errors.append(
                    f"变卦计算错误: 第{i+1}爻（从下往上）"
                    f"老阳(9)应变为少阴(8)，实际变为{changed_val}"
                )
        elif orig_val in [7, 8]:
            if changed_val != orig_val:
                errors.append(
                    f"变卦计算错误: 第{i+1}爻（从下往上）"
                    f"少阳/少阴({orig_val})应保持不变，实际变为{changed_val}"
                )
        else:
            errors.append(
                f"变卦计算错误: 第{i+1}爻（从下往上）"
                f"原始值{orig_val}不在有效范围内(6,7,8,9)"
            )
        
        # 验证 binary 转换
        orig_bin = 1 if orig_val in [7, 9] else 0
        changed_bin = 1 if changed_val in [7, 9] else 0
        
        if original_binary[i] != orig_bin:
            errors.append(
                f"本卦binary转换错误: 第{i+1}爻 "
                f"hexagram_values={orig_val} 应为binary={orig_bin}，实际={original_binary[i]}"
            )
        
        if changed_binary[i] != changed_bin:
            errors.append(
                f"变卦binary转换错误: 第{i+1}爻 "
                f"hexagram_values={changed_val} 应为binary={changed_bin}，实际={changed_binary[i]}"
            )
    
    return errors


def _validate_completeness(hexagram_data: dict) -> list:
    """
    验证数据完整性
    """
    errors = []
    required_fields = [
        "original_name",
        "changed_name",
        "original_binary",
        "changed_binary",
        "original_hexagram",
        "changed_hexagram",
        "original_symbol",
        "changed_symbol",
        "original_nature",
        "changed_nature"
    ]
    
    for field in required_fields:
        if field not in hexagram_data:
            errors.append(f"缺少必需字段: {field}")
        elif hexagram_data[field] is None:
            errors.append(f"字段为空: {field}")
        elif isinstance(hexagram_data[field], list) and len(hexagram_data[field]) == 0:
            errors.append(f"字段为空数组: {field}")
    
    return errors


def log_validation_result(validation_result: dict, logger=None):
    """
    记录验证结果
    
    Args:
        validation_result: validate_hexagram_data 返回的结果
        logger: 日志记录器（可选）
    """
    if logger is None:
        import sys
        logger = sys.stdout
    
    if validation_result["valid"]:
        if validation_result["warnings"]:
            logger.write("✓ 验证通过（有警告）\n")
            for warning in validation_result["warnings"]:
                logger.write(f"  警告: {warning}\n")
        else:
            logger.write("✓ 验证通过\n")
    else:
        logger.write("✗ 验证失败\n")
        for error in validation_result["errors"]:
            logger.write(f"  错误: {error}\n")
        if validation_result["warnings"]:
            for warning in validation_result["warnings"]:
                logger.write(f"  警告: {warning}\n")
