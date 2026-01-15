from app.core.constants import eight_hexagram, sixty_four_hexagrams_index
from app.core.generator import get_hexagram_result
from app.core.validator import validate_hexagram_data, log_validation_result

def get_hexagram_info(upper_bin, lower_bin):
    # 1. 获取基础信息
    upper_info = eight_hexagram.get(tuple(upper_bin), {"name": "未知", "symbol": "?", "nature": "未知"})
    lower_info = eight_hexagram.get(tuple(lower_bin), {"name": "未知", "symbol": "?", "nature": "未知"})
    
    # 2. 查找全名
    name = sixty_four_hexagrams_index.get((upper_info["name"], lower_info["name"]), "未知卦")
    
    # 3. 拼接符号
    symbol = f"{upper_info['symbol']}\n{lower_info['symbol']}"
    
    # 4. 拼接属性
    nature = f"{upper_info['nature']}\n{lower_info['nature']}"
    
    return name, symbol, nature

def output_hexagram_results(original_hexagram_values=None):
    """
    生成卦象数据
    
    这是系统中唯一生成卦象数据的地方。
    所有卦象数据（包括本卦和变卦）都由此函数生成，确保数据一致性。
    
    Args:
        original_hexagram_values: 可选的六爻原始数值列表 [6,7,8,9]
                                  如果提供，则使用这些值生成卦象；否则生成新的
    
    Returns:
        dict: 包含完整卦象数据的字典
    """
    results = get_hexagram_result(original_hexagram_values)
    
    # 验证：确保返回的 original_hexagram 与传入的值一致
    if original_hexagram_values and len(original_hexagram_values) == 6:
        if results["original_hexagram"] != original_hexagram_values:
            print(f"WARNING: 传入的爻值与返回的爻值不一致!")
            print(f"  传入: {original_hexagram_values}")
            print(f"  返回: {results['original_hexagram']}")
            # 强制使用传入的值
            results["original_hexagram"] = original_hexagram_values
            # 重新计算 binary
            results["original_binary"] = [1 if v in [7, 9] else 0 for v in original_hexagram_values]
    
    # 验证：根据 original_binary 重新计算上下卦，确保一致性
    orig_bin = results["original_binary"]
    lower_bin_verify = tuple(orig_bin[:3])  # 下卦：初、二、三爻
    upper_bin_verify = tuple(orig_bin[3:])  # 上卦：四、五、上爻
    
    # 确保使用的上下卦与 binary 一致
    original_name, original_symbol, original_nature = get_hexagram_info(
        upper_bin_verify, lower_bin_verify
    )
    
    # 验证变卦
    chan_bin = results["changed_binary"]
    changed_lower_bin_verify = tuple(chan_bin[:3])
    changed_upper_bin_verify = tuple(chan_bin[3:])
    
    changed_name, changed_symbol, changed_nature = get_hexagram_info(
        changed_upper_bin_verify, changed_lower_bin_verify
    )
    
    hexagram_data = {
        "original_name": original_name,
        "changed_name": changed_name,
        "original_binary": results["original_binary"],  # 从下往上：[初爻, 二爻, 三爻, 四爻, 五爻, 上爻]
        "changed_binary": results["changed_binary"],  # 从下往上：[初爻, 二爻, 三爻, 四爻, 五爻, 上爻]
        "original_symbol": original_symbol,
        "changed_symbol": changed_symbol,
        "original_nature": original_nature,
        "changed_nature": changed_nature,
        "original_hexagram": results["original_hexagram"],  # 从下往上：[初爻值, 二爻值, 三爻值, 四爻值, 五爻值, 上爻值]
        "changed_hexagram": results["changed_hexagram"],  # 从下往上：[初爻值, 二爻值, 三爻值, 四爻值, 五爻值, 上爻值]
    }
    
    # 验证数据正确性
    validation_result = validate_hexagram_data(hexagram_data)
    
    # 如果有错误，记录并抛出异常
    if not validation_result["valid"]:
        error_msg = "卦象数据验证失败:\n" + "\n".join(validation_result["errors"])
        print(f"ERROR: {error_msg}")
        # 如果数据可以修复，使用修复后的数据
        if validation_result.get("fixed"):
            print("WARNING: 使用修复后的数据")
            hexagram_data.update(validation_result["fixed"])
        else:
            # 如果无法修复，抛出异常
            raise ValueError(error_msg)
    
    # 如果有警告，记录警告
    if validation_result["warnings"]:
        for warning in validation_result["warnings"]:
            print(f"WARNING: {warning}")
    
    return hexagram_data