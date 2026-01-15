import sys
import os
import random
import time

# 确保能导入 app 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.processor import output_hexagram_results
from app.services.ai_agent import YiMasterAgent
from app.utils.ui_effects import rpg_typewriter, LoadingContext

def main():
    # 1. 初始化服务
    try:
        agent = YiMasterAgent()
    except Exception as e:
        print(f"错误：{e}")
        return

    # 2. 获取用户输入
    user_question = input("请输入您需要占卜的问题：")
    
    # 3. 算卦（数学逻辑）
    hexagram_data = output_hexagram_results()
    
    print("-" * 30)
    print(f"您起卦的内容为：{user_question}")
    print(f"本卦：{hexagram_data['original_name']} -> 变卦：{hexagram_data['changed_name']}")
    print(f"正在为您联系【天国推搡】高级会所的 {random.randint(1, 100)} 号技师...")
    print("\n")

    # 4. 调用AI进行解读（带动画上下文）
    full_text = ""
    # 使用 with 语句自动管理 Loading 动画的开始和结束
    with LoadingContext():
        # use_stream=False 在这里比较合适，因为我们在等完整的回复再打印
        full_text = agent.consult(hexagram_data, user_question, stream_mode=False)
    
    # 5. 结果展示 (RPG 模式)
    print("【技师为您解读】")
    print("-" * 30)
    
    if "【正式解读】" in full_text:
        parts = full_text.split("【正式解读】")
        thinking_part = parts[0]
        speaking_part = "【正式解读】" + parts[1]
        
        # 内心戏（快）
        rpg_typewriter(thinking_part, speed=0.01) 
        print("\n" + "="*15 + " 服务开始 " + "="*15 + "\n")
        time.sleep(1)
        # 正文（慢）
        rpg_typewriter(speaking_part, speed=0.05)
    else:
        rpg_typewriter(full_text, speed=0.04)

if __name__ == "__main__":
    main()