
"""
FastAPI 主应用入口
前后端分离架构 - 后端API服务
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import divination

# 创建FastAPI应用实例
app = FastAPI(
    title="天国神算 API",
    description="易经占卜服务后端API",
    version="1.0.0"
)

# 配置CORS - 允许前端跨域访问
# 前后端分离架构必须配置CORS，否则浏览器会阻止跨域请求
import os
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

# 从环境变量读取前端URL（支持多个，用逗号分隔）
FRONTEND_URL = os.getenv("FRONTEND_URL", "")
frontend_origins = []

if FRONTEND_URL:
    # 如果设置了环境变量，解析多个URL（用逗号分隔）
    frontend_origins = [url.strip() for url in FRONTEND_URL.split(",") if url.strip()]

if DEBUG_MODE:
    # 开发模式：允许所有来源（仅用于本地开发）
    # 注意：FastAPI不允许 allow_credentials=True 和 allow_origins=["*"] 同时使用
    # 解决方案：设置 allow_credentials=False 并使用 allow_origins=["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 开发模式允许所有来源
        allow_credentials=False,  # 必须设置为False才能使用 allow_origins=["*"]
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
else:
    # 生产模式：只允许特定域名
    # 默认包含本地开发地址（用于测试）
    default_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # 合并环境变量配置的前端URL和默认地址
    allowed_origins = list(set(default_origins + frontend_origins))
    
    # 如果 FRONTEND_URL 未设置，临时允许所有来源（防止配置错误导致无法访问）
    # 注意：这应该尽快通过环境变量配置正确的域名
    if not frontend_origins:
        print("⚠️ 警告: 生产环境未设置 FRONTEND_URL，临时允许所有来源访问")
        print("⚠️ 请在 Render Dashboard 设置 FRONTEND_URL 环境变量")
        allowed_origins = ["*"]
        allow_creds = False
    else:
        allow_creds = True
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_creds,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

# 注册路由
app.include_router(divination.router, prefix="/api", tags=["占卜"])


@app.get("/")
async def root():
    """根路径，健康检查"""
    return {
        "message": "天国神算 API 服务运行中",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok"}
