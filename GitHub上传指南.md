# GitHub 上传指南

## 📋 准备工作

### 1. 安装 Git

如果还没有安装 Git，请先下载安装：
- 下载地址：https://git-scm.com/download/win
- 安装后重启命令行工具

### 2. 配置 Git（首次使用）

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

---

## 🚀 上传步骤

### 方法一：通过命令行（推荐）

#### 步骤 1：在项目目录打开命令行

1. 在文件资源管理器中，进入项目目录：`H:\天国神算`
2. 在地址栏输入 `cmd` 并回车，或右键选择"在此处打开 PowerShell 窗口"

#### 步骤 2：初始化 Git 仓库

```bash
git init
```

#### 步骤 3：添加所有文件

```bash
git add .
```

#### 步骤 4：提交代码

```bash
git commit -m "初始提交：天国神算项目"
```

#### 步骤 5：在 GitHub 创建仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角 **+** → **New repository**
3. 填写仓库信息：
   - **Repository name**: `celestial-divination`（或自定义名称）
   - **Description**: 天国神算 - 易经占卜系统
   - **Visibility**: 选择 Public（公开）或 Private（私有）
   - ⚠️ **不要**勾选 "Initialize this repository with a README"（因为本地已有代码）
4. 点击 **Create repository**

#### 步骤 6：连接远程仓库并推送

GitHub 创建仓库后会显示命令，复制并执行：

```bash
# 添加远程仓库（将 YOUR_USERNAME 替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/celestial-divination.git

# 或者使用 SSH（如果已配置 SSH 密钥）
# git remote add origin git@github.com:YOUR_USERNAME/celestial-divination.git

# 推送代码到 GitHub
git branch -M main
git push -u origin main
```

如果提示输入用户名和密码：
- **用户名**：你的 GitHub 用户名
- **密码**：使用 Personal Access Token（不是 GitHub 密码）
  - 生成 Token：GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
  - 勾选 `repo` 权限
  - 复制生成的 Token 作为密码使用

---

### 方法二：使用 GitHub Desktop（图形界面，更简单）

#### 步骤 1：下载安装 GitHub Desktop

- 下载地址：https://desktop.github.com/

#### 步骤 2：登录 GitHub 账号

打开 GitHub Desktop，使用你的 GitHub 账号登录

#### 步骤 3：添加本地仓库

1. 点击 **File** → **Add Local Repository**
2. 点击 **Choose...**，选择项目目录：`H:\天国神算`
3. 如果提示"这不是一个 Git 仓库"，点击 **create a repository**
   - Name: `celestial-divination`
   - Local path: `H:\天国神算`
   - 勾选 "Initialize this repository with a README"（可选）

#### 步骤 4：提交代码

1. 在左侧会显示所有更改的文件
2. 在底部填写提交信息：`初始提交：天国神算项目`
3. 点击 **Commit to main**

#### 步骤 5：发布到 GitHub

1. 点击 **Publish repository**
2. 填写仓库信息：
   - **Name**: `celestial-divination`
   - **Description**: 天国神算 - 易经占卜系统
   - 选择 **Public** 或 **Private**
3. 点击 **Publish Repository**

---

## ✅ 验证上传成功

1. 打开浏览器，访问你的 GitHub 仓库页面
2. 应该能看到所有项目文件
3. 检查是否有敏感文件（如 `.env`）被上传
   - 如果有，需要删除并更新 `.gitignore`

---

## 🔄 后续更新代码

### 使用命令行

```bash
# 1. 查看更改
git status

# 2. 添加更改的文件
git add .

# 3. 提交更改
git commit -m "描述你的更改"

# 4. 推送到 GitHub
git push
```

### 使用 GitHub Desktop

1. 在 GitHub Desktop 中查看更改
2. 填写提交信息
3. 点击 **Commit to main**
4. 点击 **Push origin** 推送到 GitHub

---

## ⚠️ 注意事项

### 1. 不要上传敏感信息

以下文件已被 `.gitignore` 忽略，不会上传：
- `.env` 文件（包含 API 密钥）
- `__pycache__/`（Python 缓存）
- `node_modules/`（Node.js 依赖）
- `dist/`（构建产物）

### 2. 如果误上传了敏感文件

```bash
# 从 Git 历史中删除文件（但保留本地文件）
git rm --cached .env

# 提交更改
git commit -m "移除敏感文件"

# 推送到 GitHub
git push
```

### 3. 大文件处理

如果项目中有大文件（>100MB），考虑使用：
- [Git LFS](https://git-lfs.github.com/)
- 或者将大文件存储在云存储服务

---

## 🆘 常见问题

### Q: 提示 "fatal: not a git repository"
A: 需要在项目目录中先执行 `git init`

### Q: 提示 "remote origin already exists"
A: 如果已添加过远程仓库，可以：
```bash
# 查看现有远程仓库
git remote -v

# 删除后重新添加
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/celestial-divination.git
```

### Q: 推送时提示认证失败
A: 
- 使用 Personal Access Token 而不是密码
- 或配置 SSH 密钥：https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### Q: 如何添加多个远程仓库？
A:
```bash
git remote add origin https://github.com/USERNAME/REPO.git
git remote add backup https://github.com/USERNAME/BACKUP-REPO.git
```

---

## 📚 相关资源

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub 帮助文档](https://docs.github.com/)
- [Git 中文教程](https://www.liaoxuefeng.com/wiki/896043488029600)
