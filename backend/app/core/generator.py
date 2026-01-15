import random

# 卦象生成函数
def yarrow_hexagram():
    stalks = 49 
    for _ in range(3):
        tian = random.randint(1, stalks - 2) # 留出地和人的位置
        ren = 1
        di = stalks - tian - ren
        
        ren_num = tian % 4 or 4
        di_num = di % 4 or 4

        num_changed = ren_num + di_num + ren 
        stalks -= num_changed 
    
    # 蓍草法映射逻辑
    mapping = {36: 9, 32: 8, 28: 7, 24: 6}
    return mapping.get(stalks, 7) # 添加默认值防止异常

def get_hexagram_result(original_hexagram_values=None):
    """
    生成卦象结果
    
    Args:
        original_hexagram_values: 可选的六爻原始数值列表 [6,7,8,9]
                                  如果提供，则使用这些值生成卦象；否则生成新的
    
    Returns:
        dict: 包含卦象数据的字典
    """
    # 1. 生成或使用提供的六爻原始数值
    if original_hexagram_values and len(original_hexagram_values) == 6:
        # 验证所有值都在有效范围内
        if all(v in [6, 7, 8, 9] for v in original_hexagram_values):
            original_hexagram = original_hexagram_values
        else:
            # 如果值无效，生成新的
            original_hexagram = [yarrow_hexagram() for _ in range(6)]
    else:
        # 如果没有提供或长度不对，生成新的
        original_hexagram = [yarrow_hexagram() for _ in range(6)]

    # 2. 计算变卦
    changed_hexagram = []
    for num in original_hexagram:
        if num == 6: changed_hexagram.append(7)
        elif num == 9: changed_hexagram.append(8)
        else: changed_hexagram.append(num)
    
    # 3. 转换为二进制 (1代表阳爻, 0代表阴爻)
    to_bin = lambda nums: [1 if n in [7, 9] else 0 for n in nums]

    orig_bin = to_bin(original_hexagram)
    chan_bin = to_bin(changed_hexagram)

    return {
        "original_hexagram": original_hexagram,
        "original_binary": orig_bin,
        "upper_hexagram": orig_bin[3:],
        "lower_hexagram": orig_bin[:3],
        "changed_hexagram": changed_hexagram, 
        "changed_binary": chan_bin,
        "changed_upper_hexagram": chan_bin[3:],
        "changed_lower_hexagram": chan_bin[:3],
    }