# 天国神算 - 前后端分离占卜系统

<div align="center">
  <h3>基于 FastAPI + React 的现代化占卜应用</h3>
</div>

## 📋 目录

- [项目简介](#项目简介)
- [技术栈](#技术栈)
- [快速启动](#快速启动)
- [项目结构](#项目结构)
- [API 文档](#api-文档)
- [开发指南](#开发指南)
- [故障排查](#故障排查)
- [部署说明](#部署说明)

---

## 项目简介

**天国神算** 是一个前后端分离的占卜系统，采用现代化的技术栈构建。系统通过《易经》六十四卦进行占卜，并使用 AI 进行智能解读。

### 主要特性

- ✅ **前后端分离架构** - 独立开发、部署和维护
- ✅ **安全性** - API 密钥仅在后端使用，不暴露给前端
- ✅ **AI 智能解读** - 基于 DeepSeek API 的占卜解读
- ✅ **现代化 UI** - 赛博朋克风格的交互界面
- ✅ **实时卦象生成** - 支持手动摇卦和自动生成
- ✅ **完整卦象信息** - 显示本卦、变卦及其详细说明

---

## 技术栈

### 后端技术栈

| 技术 | 说明 |
|------|------|
| **FastAPI** | 现代、快速的 Python Web 框架，支持异步操作 |
| **Uvicorn** | ASGI 服务器，高性能异步支持 |
| **Pydantic** | 数据验证和序列化 |
| **httpx** | 异步 HTTP 客户端，用于调用 AI API |
| **python-dotenv** | 环境变量管理 |

**为什么选择 FastAPI？**
- ✅ 高性能：基于 Starlette 和 Pydantic，性能接近 Node.js
- ✅ 自动文档：自动生成 OpenAPI/Swagger 文档
- ✅ 类型安全：基于 Python 类型提示，自动数据验证
- ✅ 现代语法：支持 async/await，适合 AI API 调用
- ✅ 轻量级：依赖少，启动快

### 前端技术栈

| 技术 | 说明 |
|------|------|
| **React** | UI 框架，组件化开发 |
| **TypeScript** | 类型安全，减少错误 |
| **Vite** | 极速热更新，构建速度快 |
| **Tailwind CSS** | 实用优先的 CSS 框架 |
| **Fetch API** | 原生 HTTP 请求（无需额外依赖） |

---

## 快速启动

### 前置要求

- **后端**: Python 3.8+
- **前端**: Node.js 16+

### 1. 启动后端服务

#### 方式一：使用启动脚本（推荐）

```bash
cd backend
python start_server.py
```

#### 方式二：使用 uvicorn 直接启动

```bash
cd backend
uvicorn api_main:app --reload --host 0.0.0.0 --port 8000
```

#### 方式三：Windows 批处理脚本

```bash
cd backend
start_server.bat
```

**后端服务将在 `http://localhost:8000` 启动**

#### 配置环境变量

在 `backend/` 目录下创建 `.env` 文件：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEBUG_MODE=False
```

#### 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. 启动前端服务

```bash
cd frontend
npm install  # 首次运行需要安装依赖
npm run dev
```

**前端服务将在 `http://localhost:3000` 启动**

#### 配置环境变量（可选）

如果后端不在默认地址，在 `frontend/` 目录下创建 `.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## 项目结构

```
天国神算/
├── backend/                    # 后端API服务
│   ├── api_main.py            # FastAPI主应用入口
│   ├── start_server.py        # Python启动脚本
│   ├── start_server.bat        # Windows启动脚本
│   ├── requirements.txt       # Python依赖
│   ├── .env                   # 环境变量配置（需创建）
│   └── app/
│       ├── routers/           # API路由
│       │   └── divination.py  # 占卜相关API
│       ├── services/          # 业务逻辑服务
│       │   └── ai_agent.py    # AI代理服务
│       ├── core/              # 核心功能
│       │   ├── generator.py   # 卦象生成
│       │   ├── processor.py   # 卦象处理
│       │   └── constants.py   # 常量定义
│       └── config.py          # 配置管理
│
└── frontend/                   # 前端React应用
    ├── src/
    │   ├── App.tsx           # 主应用组件
    │   ├── services/
    │   │   └── apiService.ts  # 后端API调用封装
    │   └── types.ts           # TypeScript类型定义
    ├── package.json           # 前端依赖
    └── vite.config.ts         # Vite配置
```

---

## API 文档

### POST /api/divination/generate

生成卦象数据

**响应示例:**
```json
{
  "original_name": "乾为天",
  "changed_name": "天风姤",
  "original_binary": [1, 1, 1, 1, 1, 1],
  "changed_binary": [1, 1, 1, 1, 1, 0],
  "original_symbol": "☰\n☰",
  "changed_symbol": "☰\n☴",
  "original_nature": "天\n天",
  "changed_nature": "天\n风",
  "original_hexagram": [9, 9, 9, 9, 9, 9]
}
```

### POST /api/divination/interpret

获取 AI 占卜解读

**请求体:**
```json
{
  "question": "我什么时候能暴富？",
  "hex_lines": [1, 0, 1, 1, 0, 1]  // 可选，六爻数据
}
```

**响应示例:**
```json
{
  "hexagram_data": {
    "original_name": "乾为天",
    "changed_name": "天风姤",
    "original_binary": [1, 1, 1, 1, 1, 1],
    "changed_binary": [1, 1, 1, 1, 1, 0],
    ...
  },
  "interpretation": "【技师在思考】...\n\n【正式解读】...",
  "technician_id": 18,
  "original_info": {
    "composition": "乾上乾下",
    "meaning": "卦象说明...",
    "quote": "经典名言..."
  },
  "changed_info": {
    "composition": "乾上巽下",
    "meaning": "卦象说明...",
    "quote": "经典名言..."
  }
}
```

---

## 开发指南

### 启动检查清单

#### 后端检查
- [ ] Python 3.8+ 已安装
- [ ] 已安装依赖：`pip install -r requirements.txt`
- [ ] `.env` 文件已创建并配置 `DEEPSEEK_API_KEY`
- [ ] 端口 8000 未被占用
- [ ] 后端服务成功启动，能看到 "Uvicorn running on http://0.0.0.0:8000"

#### 前端检查
- [ ] Node.js 已安装
- [ ] 已安装依赖：`npm install`
- [ ] 端口 3000 未被占用
- [ ] 前端服务成功启动，能看到 "Local: http://localhost:3000"

#### 连接检查
- [ ] 打开浏览器访问 http://localhost:3000
- [ ] 打开开发者工具（F12）查看 Network 标签
- [ ] 输入问题并提交，检查是否有 API 请求发送到后端
- [ ] 如果后端未启动，前端会显示降级响应（模拟数据）

### 测试流程

1. **启动后端**
   ```bash
   cd backend
   python start_server.py
   ```

2. **启动前端**
   ```bash
   cd frontend
   npm run dev
   ```

3. **测试功能**
   - 打开 http://localhost:3000
   - 输入问题（如："我什么时候能暴富？"）
   - 点击"启动天机引擎"
   - 摇卦（点击6次按钮）
   - 等待 AI 解读结果

4. **验证 API 调用**
   - 打开浏览器开发者工具（F12）
   - 查看 Network 标签
   - 应该能看到对 `/api/divination/interpret` 的请求

---

## 故障排查

### 后端无法启动

1. **检查 Python 版本**
   ```bash
   python --version  # 需要 3.8+
   ```

2. **检查依赖是否安装完整**
   ```bash
   pip install -r requirements.txt
   ```

3. **检查 .env 文件**
   - 确保文件在 `backend/` 目录下
   - 确保 `DEEPSEEK_API_KEY` 已配置

4. **检查端口占用**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

### 前端无法连接后端

1. **检查后端是否运行**
   - 访问 http://localhost:8000/docs 查看是否正常

2. **检查 CORS 配置**
   - 确保前端地址在 `backend/api_main.py` 的 `allow_origins` 列表中

3. **检查浏览器控制台**
   - 打开 F12 查看 Network 和 Console 标签
   - 查看是否有 CORS 错误或连接错误

4. **检查环境变量**
   - 确保 `VITE_API_BASE_URL` 配置正确（如果使用）

### API 调用失败

1. **检查 API Key**
   - 确保 `DEEPSEEK_API_KEY` 有效
   - 检查后端日志是否有 API Key 相关错误

2. **查看后端日志**
   - 后端控制台会显示详细的错误信息

3. **使用降级响应**
   - 如果后端连接失败，前端会自动使用模拟数据

---

## 部署说明

### 📋 部署方案

推荐使用 **Cloudflare Pages（前端）+ Render（后端）** 的混合部署方案：

- ✅ **前端**：Cloudflare Pages（免费、全球 CDN、自动部署）
- ✅ **后端**：Render（支持 Python/FastAPI、免费计划可用）

---

### 🚀 快速部署步骤

#### 第一步：上传代码到 GitHub

1. **初始化 Git 仓库**（如果还没有）
   ```bash
   git init
   git add .
   git commit -m "初始提交：天国神算项目"
   ```

2. **在 GitHub 创建仓库**
   - 访问 [GitHub](https://github.com)
   - 点击 **New repository**
   - 填写仓库信息，**不要**勾选 "Initialize with README"
   - 点击 **Create repository**

3. **连接并推送代码**
```bash
   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
   git branch -M main
   git push -u origin main
   ```
   > 如果提示认证失败，使用 Personal Access Token 作为密码

---

#### 第二步：部署后端到 Render

1. **注册并登录 Render**
   - 访问 [Render](https://render.com/)
   - 使用 GitHub 账号登录

2. **创建 Web Service**
   - 点击 **New +** → **Web Service**
   - 选择 **Connect GitHub**，授权并选择仓库
   - 选择仓库和分支（通常是 `main`）

3. **配置服务**
   - **Name**: `celestial-divination-api`（或自定义）
   - **Region**: 选择离你最近的区域
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     cd backend && pip install -r requirements.txt
     ```
   - **Start Command**: 
```bash
     cd backend && uvicorn api_main:app --host 0.0.0.0 --port $PORT
     ```

4. **配置环境变量**
   - `DEEPSEEK_API_KEY` = 你的 DeepSeek API Key（**必需**）
   - `DEBUG_MODE` = `False`
   - `FRONTEND_URL` = （先留空，等前端部署后再更新）

5. **选择计划并部署**
   - 选择 **Free Plan**（测试用）或 **Starter Plan**（$7/月，无冷启动）
   - 点击 **Create Web Service**
   - 等待部署完成（5-10 分钟）
   - **复制后端 URL**（例如：`https://your-api.onrender.com`）

6. **测试后端**
   - 访问 `https://your-api.onrender.com/health`
   - 应该返回 `{"status": "ok"}`

---

#### 第三步：部署前端到 Cloudflare Pages

1. **登录 Cloudflare**
   - 访问 [Cloudflare Dashboard](https://dash.cloudflare.com/)
   - 登录你的账号

2. **创建 Pages 项目**
   - 点击左侧菜单 **Pages**
   - 点击 **Create a project**
   - 选择 **Connect to Git**
   - 授权 Cloudflare 访问 GitHub
   - 选择仓库和分支

3. **配置构建设置**
   - **Project name**: `celestial-divination`（或自定义）
   - **Framework preset**: `React (Vite)`
   - **Build command**: 
```bash
     cd frontend && npm install && npm run build
```
   - **Build output directory**: `frontend/dist`
   - **Root directory**: 留空

4. **配置环境变量**
   - 展开 **Environment variables (Advanced)**
   - 添加变量：
     - Key: `VITE_API_BASE_URL`
     - Value: `https://your-api.onrender.com`（使用第二步的后端 URL）

5. **保存并部署**
   - 点击 **Save and Deploy**
   - 等待构建完成（2-5 分钟）
   - **复制前端 URL**（例如：`https://your-app.pages.dev`）

---

#### 第四步：连接前后端

1. **更新后端 CORS 配置**
   - 回到 Render Dashboard
   - 进入你的后端服务
   - 点击 **Environment** 标签
   - 更新 `FRONTEND_URL` 为你的前端 URL：
     ```
     https://your-app.pages.dev
     ```
   - 点击 **Save Changes**
   - 等待自动重新部署（2-3 分钟）

2. **测试连接**
   - 访问前端网站
   - 打开浏览器开发者工具（F12）
   - 尝试使用占卜功能
   - 检查 Network 标签，确认 API 请求成功

---

### ⚙️ 环境变量配置

#### 前端（Cloudflare Pages）

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `VITE_API_BASE_URL` | `https://your-api.onrender.com` | **必需**，后端 API 地址 |

⚠️ **重要**：前端**不应该**配置以下变量（这些是后端的）：
- ❌ `DEBUG_MODE`
- ❌ `DEEPSEEK_API_KEY`（敏感信息，不应暴露）
- ❌ `FRONTEND_URL`

#### 后端（Render）

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `DEEPSEEK_API_KEY` | `sk-...` | **必需**，DeepSeek API 密钥 |
| `DEBUG_MODE` | `False` | 生产环境设为 False |
| `FRONTEND_URL` | `https://your-app.pages.dev` | **必需**，前端域名（用于 CORS） |

---

### 🔧 常见部署问题

#### 1. CORS 错误

**错误信息**：
```
Access-Control-Allow-Origin header is not present
```

**解决方案**：
1. 检查 Render 的 `FRONTEND_URL` 环境变量是否正确
2. 确保 `DEBUG_MODE` = `False`
3. 确保 URL 格式正确（包含 `https://`，没有末尾斜杠）
4. 等待 Render 重新部署完成
5. 清除浏览器缓存后重试

#### 2. 构建失败

**前端构建失败**：
- 检查 Node.js 版本（Cloudflare Pages 支持 Node 18/20）
- 查看构建日志中的具体错误
- 确认 `frontend/dist` 目录路径正确

**后端构建失败**：
- 检查 `requirements.txt` 是否包含所有依赖
- 查看 Render Logs 中的错误信息
- 确认 Python 版本兼容

#### 3. 服务休眠（Render Free Plan）

**症状**：首次请求需要等待 30-60 秒

**原因**：Free Plan 的服务在 15 分钟无活动后会休眠

**解决方案**：
- 等待冷启动完成（30-60 秒）
- 或升级到 Starter Plan（$7/月），服务常驻

#### 4. 环境变量不生效

**前端环境变量**：
- Vite 环境变量必须以 `VITE_` 开头
- 环境变量在构建时注入，修改后需要重新构建

**后端环境变量**：
- 修改后需要等待重新部署
- 检查环境变量值是否正确（没有多余空格）

---

### ✅ 部署检查清单

#### 后端（Render）
- [ ] 服务已成功部署
- [ ] `/health` 端点返回 `{"status": "ok"}`
- [ ] 环境变量已配置：
  - [ ] `DEEPSEEK_API_KEY`（必需）
  - [ ] `DEBUG_MODE=False`
  - [ ] `FRONTEND_URL`（前端 URL）

#### 前端（Cloudflare Pages）
- [ ] 项目已成功部署
- [ ] 环境变量已配置：
  - [ ] `VITE_API_BASE_URL`（后端 URL）
- [ ] 网站可以正常访问

#### 连接测试
- [ ] 前端可以成功调用后端 API
- [ ] 没有 CORS 错误
- [ ] 占卜功能正常工作

---

### 📚 其他部署选项

#### 后端部署选项

- **Railway**: 简单易用，自动部署（参考 `backend/railway.json`）
- **Fly.io**: 支持全球部署（参考 `backend/fly.toml`）
- **Vercel**: 支持 Serverless Functions
- **AWS/GCP/Azure**: 企业级部署

#### 前端部署选项

- **Vercel**: 免费、自动部署、全球 CDN
- **Netlify**: 类似 Vercel
- **GitHub Pages**: 免费静态托管

---

## 主要改动记录

### 后端改造
1. ✅ 创建 FastAPI 应用 (`backend/api_main.py`)
   - 配置 CORS 支持跨域
   - 添加健康检查端点
   - 自动生成 API 文档（Swagger UI）

2. ✅ 创建 API 路由 (`backend/app/routers/divination.py`)
   - `POST /api/divination/generate` - 生成卦象
   - `POST /api/divination/interpret` - AI 解读占卜
   - 使用 Pydantic 进行数据验证

3. ✅ 更新依赖 (`backend/requirements.txt`)
   - 添加 FastAPI、Uvicorn、Pydantic、httpx

4. ✅ 创建启动脚本
   - `start_server.py` - Python 启动脚本
   - `start_server.bat` - Windows 批处理脚本

### 前端改造
1. ✅ 创建 API 服务 (`frontend/services/apiService.ts`)
   - 封装后端 API 调用
   - 处理错误和降级响应
   - 数据格式转换

2. ✅ 更新主应用 (`frontend/App.tsx`)
   - 移除直接调用 Gemini API
   - 改为调用后端 API 服务
   - 传递六爻数据给后端

3. ✅ 更新配置 (`frontend/vite.config.ts`)
   - 支持环境变量配置 API 地址

### 安全改进
1. ✅ **API 密钥保护**: DeepSeek API 密钥现在只在后端使用，不再暴露给前端
2. ✅ **CORS 配置**: 限制允许的源，防止未授权访问
3. ✅ **数据验证**: 使用 Pydantic 验证请求数据，防止恶意输入

---

## 下一步优化建议

1. **流式输出**: 使用 WebSocket 或 SSE 实现 AI 流式输出，提升用户体验
2. **认证授权**: 添加 JWT 认证（如需要）
3. **数据持久化**: 添加数据库存储占卜历史
4. **缓存**: 使用 Redis 缓存常用数据
5. **限流**: 添加 API 限流保护
6. **监控**: 添加日志和监控系统
7. **单元测试**: 为 API 端点添加测试

---

## 技术栈详细分析

### 为什么选择这些技术？

#### 后端：FastAPI vs Flask vs Django

| 特性 | FastAPI | Flask | Django |
|------|---------|-------|--------|
| 性能 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 异步支持 | ✅ 原生 | ⚠️ 需配置 | ⚠️ 需配置 |
| 自动文档 | ✅ | ❌ | ⚠️ DRF |
| 学习曲线 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| 适用场景 | API 服务 | 小型项目 | 大型项目 |

**FastAPI 优势**:
- 高性能异步操作，适合 AI API 调用
- 自动生成 API 文档，开发效率高
- 类型安全，减少错误

#### 前端：原生 Fetch vs Axios

| 特性 | Fetch API | Axios |
|------|-----------|-------|
| 依赖 | ✅ 原生 | ❌ 需安装 |
| 拦截器 | ❌ | ✅ |
| 取消请求 | ⚠️ AbortController | ✅ 简单 |
| 自动 JSON | ⚠️ 需手动 | ✅ |
| 浏览器支持 | ✅ 现代浏览器 | ✅ 所有浏览器 |

**当前使用 Fetch API**:
- 项目简单，无需额外依赖
- 现代浏览器原生支持
- 代码更简洁

---

## 改造优势

1. **安全性提升**: API 密钥不再暴露在前端
2. **可维护性**: 前后端分离，独立开发和部署
3. **可扩展性**: 后端可服务多个客户端（Web、移动端等）
4. **性能优化**: 后端可做缓存、限流等优化
5. **团队协作**: 前后端可并行开发

---

## 许可证

本项目仅供学习和研究使用。

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

<div align="center">
  <p>Made with ❤️ using FastAPI + React</p>
</div>
