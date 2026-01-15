# app/config.py
import os
from dotenv import load_dotenv

# 核心：加载 .env 文件中的变量到系统环境变量中
load_dotenv()

class Config:
    # 从环境变量读取，如果读取不到则默认为 None
    API_KEY = os.getenv("DEEPSEEK_API_KEY")
    
    # 进行类型转换（环境变量读出来全是字符串）
    DEBUG = os.getenv("DEBUG_MODE", "False").lower() == "true"

# 实例化，方便其他模块调用
settings = Config()