#!/usr/bin/env python3
"""
后端服务启动脚本
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式：代码变更自动重启
        log_level="info"
    )
