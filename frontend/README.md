# 前端说明

本目录是 `Vite + React + TypeScript` 前端，用于连接后端占卜 API。

## 当前结构

- `App.tsx`：主界面与交互状态
- `components/`：卦象展示、加载动画、背景和通用图标
- `services/apiService.ts`：统一的后端 API 调用封装
- `types.ts`：前端共享类型定义

## 启动

```bash
npm install
npm run dev
```

## 本地配置

在 `.env.local` 或 `.env` 中配置后端地址：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 可用脚本

- `npm run dev`：本地开发
- `npm run build`：生产构建
- `npm run preview`：预览构建结果
- `npm run typecheck`：TypeScript 类型检查

## 说明

- 当前前端默认通过 `frontend/services/apiService.ts` 调用后端
- 如未配置 `VITE_API_BASE_URL`，会优先尝试相对路径
- 已移除未使用的 Gemini/AI Studio 模板残留文件，当前前端只依赖后端 API
