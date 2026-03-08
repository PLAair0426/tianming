# 天国神算

基于 `FastAPI + React + TypeScript` 的前后端分离占卜系统。  
后端负责卦象生成、AI 解读、元气系统与限流控制；前端负责交互式起卦、结果展示与状态提示。

## 功能概览

- 六爻卦象生成：后端统一生成本卦、变卦和爻值，避免前后端结果不一致
- AI 解读：基于 `DeepSeek` 接口生成占卜说明
- 元气系统：按用户维度维护使用状态，防止频繁滥用
- 限流保护：对高成本接口做滑动窗口限流
- 前后端分离：前端可独立部署，后端提供标准 API

## 技术栈

### 后端

- `FastAPI`
- `Uvicorn`
- `Pydantic`
- `httpx`
- `python-dotenv`

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
DEEPSEEK_API_KEY=your_deepseek_api_key
DEBUG_MODE=True
FRONTEND_URL=http://localhost:5173
```

说明：

- `DEEPSEEK_API_KEY`：AI 解读所需
- `DEBUG_MODE`：开发模式下会放宽跨域限制
- `FRONTEND_URL`：生产环境建议显式配置允许访问的前端地址

### 前端

前端可通过 `.env` 或 `.env.local` 配置后端地址：

```env
VITE_API_BASE_URL=http://localhost:8000
```

未配置时，代码会优先使用相对路径或本地默认地址。

## API 概览

当前核心接口：

- `POST /api/divination/generate-line`：生成单个爻
- `POST /api/divination/generate`：生成完整卦象
- `POST /api/divination/interpret`：提交问题并获取 AI 解读
- `GET /api/divination/karma-status`：查询元气状态
- `POST /api/divination/recharge`：恢复元气
- `GET /api/divination/rate-limit-status`：查询限流状态
- `GET /health`：健康检查

## 用户隔离与限流

后端按用户维度维护状态：

- 优先使用前端传入的 `X-Device-ID`
- 其次使用 `user_id` Cookie
- 否则回退为 `IP + User-Agent` 生成的稳定标识

高成本接口使用滑动窗口限流，避免单个用户持续占满资源。

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

## 常见问题

### 1. 前端提示无法连接后端

检查：

- 后端是否已经启动
- `VITE_API_BASE_URL` 是否正确
- 浏览器请求是否命中 `http://localhost:8000`

### 2. AI 解读失败

检查：

- `backend/.env` 中是否配置了 `DEEPSEEK_API_KEY`
- 后端日志中是否出现上游接口错误

### 3. 跨域访问失败

检查：

- 开发环境是否启用了 `DEBUG_MODE=True`
- 生产环境是否正确设置了 `FRONTEND_URL`

## 部署说明

- 前端目录包含 `render`/静态站点部署所需文件，可单独托管
- 后端目录包含 `render`、`fly.io` 等部署配置示例
- 生产环境请务必配置真实的前端来源和 API Key

## 当前状态

截至 `2026-03-08`，项目已验证：

- 后端基础接口可启动并响应
- 前端可通过 `Vite` 成功构建
- 根文档已恢复为 UTF-8 正常内容
