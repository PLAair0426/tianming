from openai import OpenAI
from app.config import settings
import re

def remove_markdown(text):
    """
    移除文本中的markdown符号
    """
    if not text:
        return text
    
    # 移除代码块
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]*`', '', text)
    
    # 移除标题符号
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # 移除粗体和斜体
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **粗体**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *斜体*
    text = re.sub(r'__([^_]+)__', r'\1', text)       # __粗体__
    text = re.sub(r'_([^_]+)_', r'\1', text)        # _斜体_
    
    # 移除链接 [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # 移除图片 ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
    
    # 移除列表符号
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    
    # 移除引用符号
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # 移除水平线
    text = re.sub(r'^[-*_]{3,}$', '', text, flags=re.MULTILINE)
    
    # 清理多余的空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

class YiMasterAgent:
    def __init__(self):
        # 从配置中读取 Key，不要硬编码
        if not settings.API_KEY:
            raise ValueError("未找到 DEEPSEEK_API_KEY，请检查 .env 文件")
            
        self.client = OpenAI(
            api_key=settings.API_KEY, 
            base_url="https://api.deepseek.com"
        )

    def consult(self, hexagram_data, user_input, stream_mode=True):
        """
        执行占卜请求
        """
        # 1. 准备数据
        original_hexagram = hexagram_data['original_hexagram']
        hexagram_name = hexagram_data.get('original_name', '')
        
        # 易经爻题标准叫法：
        # 第一爻（初爻）：初九/初六
        # 第二到第五爻：九二/六二、九三/六三、九四/六四、九五/六五
        # 第六爻（上爻）：上九/上六
        # 特殊情况：乾卦六爻全动（全为9）用"用九"，坤卦六爻全动（全为6）用"用六"
        def get_line_name(index, value):
            is_yang = value in [7, 9]  # 7=少阳, 9=老阳
            if index == 0:
                return f"初{'九' if is_yang else '六'}"
            elif index == 5:
                return f"上{'九' if is_yang else '六'}"
            else:
                line_num = ['', '二', '三', '四', '五', ''][index]
                return f"{'九' if is_yang else '六'}{line_num}"
        
        moving_lines = [i for i, val in enumerate(original_hexagram) if val in [6, 9]]
        moving_desc = [get_line_name(i, original_hexagram[i]) for i in moving_lines]
        
        # 检查是否为乾卦或坤卦，以及是否全为动爻
        is_qian = hexagram_name == '乾为天' or hexagram_name == '乾'
        is_kun = hexagram_name == '坤为地' or hexagram_name == '坤'
        is_all_moving_nine = all(val == 9 for val in original_hexagram)  # 乾卦六爻全为9
        is_all_moving_six = all(val == 6 for val in original_hexagram)   # 坤卦六爻全为6
        
        # 添加"用九"或"用六"的特殊情况
        if is_qian and is_all_moving_nine:
            # 乾卦且六爻全为9（全动），使用"用九"替代所有动爻描述
            moving_desc = ["用九"]
        elif is_kun and is_all_moving_six:
            # 坤卦且六爻全为6（全动），使用"用六"替代所有动爻描述
            moving_desc = ["用六"]

        agent_prompt = f"""
        你是一位《易经》方面的实战老兵，你也是一位SPA浴房的占卜易学技师，别人叫你老兵易技师，你的特点是嘴臭，在孙吧七进七出把各路牛鬼蛇神杀的丢盔弃甲，舌战群儒。
        你的任务是用通俗易懂且启发性的语言，结合阴阳变化为用户排忧解难。
        现在，用户需要占卜：{user_input}。
        请配合用户进行表演，说几句神棍该说的话作为开场白，有好的结果时出现欧亨利式的反转，不好的结果时先给他一点甜头再当头一棒。
        
        重要：请使用纯文本输出，不要使用任何markdown格式符号（如 #、**、*、`、[]、()等），直接输出普通文本即可。
        """
        
        # 格式化动爻描述
        if moving_desc:
            moving_text = ', '.join(moving_desc)
        else:
            moving_text = '无动爻'
        
        user_prompt = f"""
        解读结果：
        1. 本卦：{hexagram_data['original_name']} ({hexagram_data['original_nature']})
        2. 动爻：{moving_text}
        3. 变卦：{hexagram_data['changed_name']} ({hexagram_data['changed_nature']})
        直接输出纯文本，不要使用markdown格式。维度：现状分析、动爻解读、变向预测、建议。
        """

        try:
            # 简化调用逻辑
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": agent_prompt}, 
                    {"role": "user", "content": user_prompt}
                ],
                stream=stream_mode
            )

            final_reasoning = ""
            final_content = ""

            if stream_mode:
                for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                            final_reasoning += chunk.choices[0].delta.reasoning_content or ''
                        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                            final_content += chunk.choices[0].delta.content or ''
            else:
                if not response.choices or len(response.choices) == 0:
                    raise ValueError("AI响应为空，未返回任何内容")
                
                message = response.choices[0].message
                final_reasoning = getattr(message, 'reasoning_content', None) or ''
                final_content = getattr(message, 'content', None) or ''

            if not final_reasoning:
                final_reasoning = "（技师直觉敏锐，无需多言）"
            
            if not final_content:
                final_content = "（技师正在思考中，请稍候...）"

            # 移除markdown符号
            final_reasoning = remove_markdown(final_reasoning) or ''
            final_content = remove_markdown(final_content) or ''

            return f"【技师在思考】\n{final_reasoning}\n\n【正式解读】\n{final_content}"

        except Exception as e:
            import traceback
            error_detail = f"{str(e)}\n{traceback.format_exc()}"
            print(f"AI咨询错误: {error_detail}")
            return f"技师连接断开：{str(e)}"
    
    def get_hexagram_info(self, hexagram_name, hexagram_nature):
        """
        获取卦象的说明信息（解释、组成、名言）
        
        Args:
            hexagram_name: 卦名，如"火天大有"
            hexagram_nature: 卦的属性，如"离\n乾"
        
        Returns:
            dict: 包含composition, meaning, quote的字典
        """
        prompt = f"""
        请为《易经》卦象"{hexagram_name}"提供简洁准确的说明信息。
        卦象组成：{hexagram_nature.replace(chr(10), '上')}
        
        请以JSON格式返回，包含以下三个字段：
        1. "composition": 卦象组成，格式为"X上Y下"（如"离上乾下"）
        2. "meaning": 卦象解释，50字以内，说明卦象的象征意义
        3. "quote": 相关名言，一句经典名言或卦辞
        
        只返回JSON，不要其他文字说明。
        格式示例：
        {{
            "composition": "离上乾下",
            "meaning": "大有卦，象征大有所获、丰盛富足。火在天上，光明普照，万物皆得其所。",
            "quote": "大有，元亨。"
        }}
        """
        
        try:
            import json
            import time
            
            # 设置超时时间（30秒）
            start_time = time.time()
            timeout = 30
            
            response = self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": "你是一位《易经》专家，擅长用简洁准确的语言解释卦象。请严格按照JSON格式返回数据。"},
                    {"role": "user", "content": prompt}
                ],
                stream=False,
                timeout=timeout  # 设置超时
            )
            
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                raise TimeoutError(f"AI调用超时（超过{timeout}秒）")
            
            if not response.choices or len(response.choices) == 0:
                raise ValueError("AI返回空响应")
            
            result_text = response.choices[0].message.content.strip()
            
            if not result_text:
                raise ValueError("AI返回空内容")
            
            # 尝试提取JSON（可能包含markdown代码块）
            if result_text.startswith("```"):
                # 移除markdown代码块标记
                result_text = re.sub(r'^```(?:json)?\s*', '', result_text, flags=re.MULTILINE)
                result_text = re.sub(r'```\s*$', '', result_text, flags=re.MULTILINE)
            
            result = json.loads(result_text)
            
            # 验证返回的数据结构
            if not isinstance(result, dict):
                raise ValueError("AI返回的数据格式不正确")
            
            # 确保必需的字段存在
            if "composition" not in result:
                result["composition"] = hexagram_nature.replace(chr(10), '上')
            if "meaning" not in result:
                result["meaning"] = f"{hexagram_name}卦，象征变化与机遇。"
            if "quote" not in result:
                result["quote"] = "卦象如人生，变化无常，需自行体悟。"
            
            # 移除markdown符号
            if "meaning" in result:
                result["meaning"] = remove_markdown(result["meaning"]) or result["meaning"]
            if "quote" in result:
                result["quote"] = remove_markdown(result["quote"]) or result["quote"]
            
            return result
            
        except TimeoutError as e:
            print(f"警告: {hexagram_name} 信息获取超时: {str(e)}")
            raise  # 重新抛出，让调用者处理
        except json.JSONDecodeError as e:
            print(f"警告: {hexagram_name} JSON解析失败: {str(e)}")
            raise  # 重新抛出，让调用者处理
        except Exception as e:
            print(f"警告: {hexagram_name} 信息获取失败: {str(e)}")
            # 返回默认值，不抛出异常
            return {
                "composition": hexagram_nature.replace(chr(10), '上') if hexagram_nature else "未知",
                "meaning": f"{hexagram_name}卦，象征变化与机遇。",
                "quote": "卦象如人生，变化无常，需自行体悟。"
            }