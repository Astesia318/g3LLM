# Git 推送指南

## 📋 推送前准备

### 1. 检查要提交的文件

```bash
git status
```

### 2. 决定是否上传数据集

数据集文件可能很大（`multiturn_data_merged.json` 等），建议：

**选项 A：不上传数据集**（推荐，如果数据集很大）
- 数据集文件已在 `.gitignore` 中排除
- 在 README 中说明如何生成数据

**选项 B：使用 Git LFS 上传大文件**
```bash
# 安装 Git LFS
git lfs install

# 跟踪大文件
git lfs track "*.json"
git lfs track "*.jsonl"
git add .gitattributes
```

**选项 C：直接上传**（如果文件不大）
```bash
git add dataset/*.json dataset/*.jsonl
```

## 🚀 推送步骤

### 步骤 1: 在 GitHub 上创建仓库

1. 登录 GitHub
2. 点击右上角 "+" → "New repository"
3. 填写仓库信息：
   - Repository name: `g3LLM` (或你喜欢的名字)
   - Description: `心理健康助手微调项目`
   - 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"（我们已经有了）
4. 点击 "Create repository"

### 步骤 2: 配置 Git 用户信息（如果还没配置）

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 步骤 3: 提交代码

```bash
# 查看要提交的文件
git status

# 添加所有文件（.gitignore 会自动排除不需要的文件）
git add .

# 提交
git commit -m "Initial commit: g3LLM 心理健康助手微调项目"
```

### 步骤 4: 添加远程仓库并推送

```bash
# 添加远程仓库（替换为你的 GitHub 用户名和仓库名）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 或者使用 SSH（如果配置了 SSH key）
# git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO_NAME.git

# 重命名分支为 main（GitHub 默认使用 main）
git branch -M main

# 推送到 GitHub
git push -u origin main
```

## 🔐 认证方式

### 方式 1: Personal Access Token (HTTPS)

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 生成新 token，勾选 `repo` 权限
3. 推送时使用 token 作为密码

### 方式 2: SSH Key (推荐)

```bash
# 生成 SSH key（如果还没有）
ssh-keygen -t ed25519 -C "your.email@example.com"

# 复制公钥
cat ~/.ssh/id_ed25519.pub

# 在 GitHub → Settings → SSH and GPG keys 中添加公钥
```

## 📝 后续更新

```bash
# 修改文件后
git add .
git commit -m "描述你的更改"
git push
```

## ⚠️ 注意事项

1. **不要上传模型文件**：已在 `.gitignore` 中排除
2. **数据集文件**：如果很大，考虑使用 Git LFS 或不上传
3. **敏感信息**：不要提交 API keys、密码等敏感信息
4. **大文件**：GitHub 限制单个文件 100MB，仓库建议不超过 1GB

## 🛠️ 如果遇到问题

### 问题 1: 推送被拒绝（rejected）

```bash
# 如果远程仓库有内容，先拉取
git pull origin main --allow-unrelated-histories

# 解决冲突后再次推送
git push -u origin main
```

### 问题 2: 认证失败

- 检查用户名和密码/token
- 或使用 SSH 方式

### 问题 3: 文件太大

```bash
# 使用 Git LFS
git lfs install
git lfs track "*.json"
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

