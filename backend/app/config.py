# app/config.py
import os
from dotenv import load_dotenv

# 核心：加载 .env 文件中的变量到系统环境变量中
load_dotenv()

class Config:
    # 从环境变量读取，兼容多种常见命名
    API_KEY = (
        os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("API_KEY")
    )
    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.deepseek.com")
    AI_MODEL = os.getenv("AI_MODEL", "deepseek-reasoner")
    
    # 进行类型转换（环境变量读出来全是字符串）
    DEBUG = os.getenv("DEBUG_MODE", "False").lower() == "true"

# 实例化，方便其他模块调用
settings = Config()
