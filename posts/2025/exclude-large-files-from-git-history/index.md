---
title: "在 Git 仓库中排除历史记录中的大文件"
date: 2025-11-17T19:32:28+08:00
tags:
  - "settings"
categories:
  - "programming"
description: "在 Git 仓库中排除历史记录中的大文件（仅仅在 .gitignore 中忽略是不够的） 适用场景：误将模型权重（如 .pth、.pt、.h5）、数据集、日志等大文件提交到 Git，导致仓库体积膨胀、克隆缓慢。 🚨 问题背景 Git 的设计初衷是管理代码，而非二进制大文件。一旦你不小心将 .pth"
cover: "./a15b4afegy1fmvjnab7dhj21hc0u0nem.webp"
---

# 在 Git 仓库中排除历史记录中的大文件（仅仅在 .gitignore 中忽略是不够的）

> **适用场景**：误将模型权重（如 `.pth`、`.pt`、`.h5`）、数据集、日志等大文件提交到 Git，导致仓库体积膨胀、克隆缓慢。

---

## 🚨 问题背景

Git 的设计初衷是管理**代码**，而非二进制大文件。一旦你不小心将 `.pth` 模型文件、训练数据或日志提交进仓库，即使后续用 `git rm` 删除并提交，这些文件仍会**永久保留在历史记录中**，导致：

- 仓库体积持续膨胀（`.git` 目录可能达 GB 级）
- 克隆速度极慢
- CI/CD 流水线效率下降
- 协作体验变差

**仅仅在 `.gitignore` 中忽略是不够的！必须重写历史记录才能真正“瘦身”。**

---

## ✅ 解决方案：使用 `git-filter-repo` 彻底清除

目前最推荐的工具是 **`git-filter-repo`** —— 它由 Git 官方社区维护，比旧工具（如 `BFG Repo-Cleaner` 或 `git filter-branch`）更安全、高效、易用。

### 第一步：备份你的仓库！

```bash
cp -r your-project your-project-backup
```

> ⚠️ 重写历史是**不可逆操作**！务必先备份整个目录。

---

### 第二步：安装 `git-filter-repo`

你可以通过多种方式安装：

#### 方式 1：使用 `pip`（推荐）
```bash
pip install git-filter-repo
```

#### 方式 2：使用 `uv`（超快 Python 包安装器）
```bash
uv pip install git-filter-repo
```

#### 方式 3：系统包管理器
- Ubuntu/Debian: `sudo apt install git-filter-repo`
- macOS (Homebrew): `brew install git-filter-repo`

> 安装后确保 `git-filter-repo` 命令可用。

---

### 第三步：删除所有 `.pth` 文件（包括历史）

进入你的 Git 仓库根目录，执行：

```bash
git filter-repo --path-glob '*.pth' --invert-paths
```

- `--path-glob '*.pth'`：匹配所有扩展名为 `.pth` 的文件
- `--invert-paths`：表示“排除这些路径”，即从历史中彻底删除

💡 **其他常见用法示例**：
```bash
# 删除多个类型
git filter-repo --path-glob '*.pth' --path-glob '*.pt' --path-glob '*.h5' --invert-paths

# 删除特定目录下的大文件
git filter-repo --path data/ --invert-paths

# 删除单个文件
git filter-repo --path model_weights.pth --invert-paths
```

---

### 第四步：清理本地 Git 缓存

```bash
# 清除 filter-repo 自动生成的备份引用
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d

# 清理 reflog 和垃圾回收
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

此时你的 `.git` 目录应该显著缩小。

---

### 第五步：强制推送到远程仓库

⚠️ 此操作会**改写远程历史**，影响所有协作者！

```bash
git push origin --force --all
git push origin --force --tags
```

> 📢 **重要提醒**：通知团队成员不要再基于旧历史提交代码，建议他们重新 `git clone` 仓库。

---

## 🔍 验证是否删除成功

检查是否还有 `.pth` 文件残留在历史中：

```bash
git log --all --full-history -- '**/*.pth'
```

若无输出，说明已彻底清除。

查看仓库体积变化：

```bash
du -sh .git
```

通常可减少几十 MB 到数 GB 不等。

---

## 🛡️ 预防措施：避免再次提交大文件

1. **更新 `.gitignore`**：
   ```gitignore
   # 忽略模型和数据文件
   *.pth
   *.pt
   *.h5
   *.bin
   data/
   logs/
   ```

2. **使用 Git LFS（Large File Storage）管理必要大文件**：
   ```bash
   git lfs install
   git lfs track "*.pth"
   git add .gitattributes
   ```

3. **设置 pre-commit 钩子**（可选）：
   使用 [pre-commit](https://pre-commit.com/) 插件阻止大文件提交。

---


## ✅ 总结

| 步骤 | 操作 |
|------|------|
| 1 | **备份仓库** |
| 2 | 安装 `git-filter-repo`（`pip` 或 `uv`） |
| 3 | 执行 `git filter-repo --path-glob '*.pth' --invert-paths` |
| 4 | 清理本地缓存 |
| 5 | 强制推送（谨慎！） |
| 6 | 更新 `.gitignore` 并教育团队 |

通过以上步骤，你可以彻底从 Git 历史中移除大文件，让仓库“轻装上阵”。

---

> 🌟 **小贴士**：定期检查仓库大小，防患于未然。一个健康的 Git 仓库，`.git` 目录应远小于工作区代码本身。

> git 自带的 gc 命令（即执行：`git gc`）也可以很好的帮助整理 .git 文件中的空间。

如有疑问，欢迎留言讨论！
