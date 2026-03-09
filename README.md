# 天国神算

基于 `FastAPI + React + TypeScript` 的前后端分离占卜系统。  
后端负责起卦、卦象校验、AI 解读、元气系统与限流；前端负责交互式起卦、结果展示与状态提示。

## 功能概览

- 六爻卦象生成：后端统一生成本卦、变卦、爻值，避免前后端结果不一致
- AI 解读：通过 OpenAI 兼容接口生成卦象说明
- 元气系统：按用户维度限制高频调用，防止滥用
- 限流保护：对高成本接口做滑动窗口限流
- 前后端分离：前端可独立部署，后端对外提供标准 API

## 技术栈

### 后端

- `FastAPI`
- `Uvicorn`
- `Pydantic`
- `python-dotenv`
- `openai`

### 前端

- `React 19`
- `TypeScript`
- `Vite`

## 目录结构

```text
.
├─ backend/
│  ├─ api_main.py
│  ├─ start_server.py
│  ├─ requirements.txt
│  ├─ test_api.py
│  └─ app/
│     ├─ core/
│     ├─ routers/
│     ├─ services/
│     └─ utils/
├─ frontend/
│  ├─ App.tsx
│  ├─ package.json
│  ├─ components/
│  └─ services/
└─ README.md
```

## 快速启动

### 1. 启动后端

```bash
cd backend
python -m pip install -r requirements.txt
python start_server.py
```

后端默认地址：

- `http://localhost:8000`
- Swagger：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

也可以直接使用：

```bash
cd backend
uvicorn api_main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认地址通常为：

- `http://localhost:5173`

## 环境变量

### 后端 `backend/.env`

```env
# 三选一即可，优先级依次为 DEEPSEEK_API_KEY -> OPENAI_API_KEY -> API_KEY
DEEPSEEK_API_KEY=your_api_key

# 可选：如果接入其他 OpenAI 兼容服务，请改成对应地址
API_BASE_URL=https://api.deepseek.com

# 可选：如果更换供应商，通常也要同步调整模型名
AI_MODEL=deepseek-reasoner

DEBUG_MODE=True
FRONTEND_URL=http://localhost:5173
```

说明：

- `DEEPSEEK_API_KEY` / `OPENAI_API_KEY` / `API_KEY`：任意设置一个即可
- `API_BASE_URL`：OpenAI 兼容服务地址，默认是 DeepSeek
- `AI_MODEL`：调用的模型名称，默认是 `deepseek-reasoner`
- `DEBUG_MODE`：开发模式下会放宽跨域限制
- `FRONTEND_URL`：生产环境建议显式配置允许访问的前端地址，可用逗号分隔多个来源

### 前端 `.env` / `.env.local`

```env
VITE_API_BASE_URL=http://localhost:8000
```

未配置时，前端会优先使用相对路径或本地默认地址。

## API 概览

- `POST /api/divination/generate-line`：生成单个爻
- `POST /api/divination/generate`：生成完整卦象
- `POST /api/divination/interpret`：提交问题并获取 AI 解读
- `GET /api/divination/karma-status`：查询元气状态
- `POST /api/divination/recharge`：恢复元气
- `GET /api/divination/rate-limit-status`：查询限流状态
- `GET /`：服务存活检查
- `GET /health`：健康检查

## 开发与验证

### 后端测试

```bash
cd backend
python -m pytest -q
```

### 前端类型检查

```bash
cd frontend
npm run typecheck
```

### 前端构建

```bash
cd frontend
npm run build
```

### 乱码排查

项目源码统一使用 UTF-8。若 PowerShell 中看到中文显示异常，优先检查终端编码，而不是直接认定文件损坏：

```powershell
chcp 65001
```

也可以使用仓库内的编码扫描方式：

```bash
python C:/Users/64426/.codex/skills/encoding-garbled-check/scripts/scan_encoding.py --path .
```


如果本地有未提交改动，先提交或暂存后再执行 `git pull --rebase`。

## 常见问题

### 1. 前端无法连接后端

请检查：

- 后端是否已经启动
- `VITE_API_BASE_URL` 是否正确
- 浏览器请求是否命中 `http://localhost:8000`

### 2. AI 解读失败

请检查：

- 是否配置了 `DEEPSEEK_API_KEY`、`OPENAI_API_KEY` 或 `API_KEY`
- 如果不是 DeepSeek，`API_BASE_URL` 和 `AI_MODEL` 是否匹配
- 后端日志中是否有上游接口报错

### 3. 跨域访问失败

请检查：

- 开发环境是否启用了 `DEBUG_MODE=True`
- 生产环境是否正确设置了 `FRONTEND_URL`

## 部署说明

- `frontend/` 目录可单独部署为静态站点
- `backend/` 目录可独立部署到支持 Python 的平台
- 仓库中已包含部分部署相关文件，如 `render.yaml`、`railway.json`、`fly.toml`
- 生产环境请务必配置真实可用的前端来源与 API 密钥
