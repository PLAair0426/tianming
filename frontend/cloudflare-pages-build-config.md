# Cloudflare Pages 构建配置

## 构建设置

如果通过 Git 连接部署，在 Cloudflare Pages 项目设置中配置：

- **Build command**: `cd frontend && npm install && npm run build`
- **Build output directory**: `frontend/dist`
- **Root directory**: `/`（项目根目录）
- **Node version**: `18` 或 `20`

## 环境变量

在 Cloudflare Pages 项目设置 → Environment variables 中添加：

```
VITE_API_BASE_URL = https://your-backend-url.com
```

⚠️ **重要**：Vite 环境变量必须以 `VITE_` 开头，且需要在构建时设置。

## 自定义域名

可以在 Cloudflare Pages 项目设置中绑定自定义域名。
