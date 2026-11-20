# Blogs

共享博客内容仓库，作为 [Pages](https://github.com/WangWindow/Pages) 和 [wangwindow.github.io](https://github.com/WangWindow/wangwindow.github.io) 的 Git 子模块。

## 目录结构

```
Blogs/
├── posts/
│   ├── 2025/           # 2025 年文章
│   └── 2026/           # 2026 年文章
│       └── article-slug/
│           ├── index.md
│           └── cover.webp
├── data/
│   └── taxonomy/
│       ├── categories/ # 分类词表（CMS relation 使用）
│       └── tags/       # 标签词表（CMS relation 使用）
├── uploads/            # 公共上传资源（历史遗留）
└── README.md
```

## Frontmatter 格式

```yaml
---
title: "文章标题"
slug: "url-slug"              # 可选，默认使用目录名
date: 2025-12-28T17:51:27+08:00
updated: 2025-12-29T10:00:00+08:00  # 可选
author: "wangwindow"          # 可选
draft: false                  # 可选；仅用于“已合并但暂时隐藏”
categories:
  - "tool"                    # 对应 data/taxonomy/categories/tool.yml
tags:
  - "tag1"                    # 对应 data/taxonomy/tags/tag1.yml
  - "tag2"
description: "文章描述"
cover: "./cover.webp"         # 可选，相对路径
---
```

## 使用方式

### 作为子模块添加

```bash
# Pages 项目
git submodule add https://github.com/WangWindow/Blogs.git src/content/blog

# wangwindow.github.io 项目
git submodule add https://github.com/WangWindow/Blogs.git src/data/blog
```

### 更新子模块

```bash
git submodule update --remote --merge
```

## 自动同步

当 `main` 的 `posts/**` 或 `uploads/**` 有变更时，会通过 GitHub Actions 触发 Pages 和 wangwindow.github.io 的自动构建。`data/taxonomy/**` 只供 CMS 使用，不会触发前端重建。

## 架构设计

```text
CMS（Sveltia Preview Workflow）
  → 保存到 cms/<collection>/<slug>
  → Draft PR
  → Publish：squash merge 到 main
  → notify-update.yml
  → Pages / wangwindow.github.io 更新子模块并重建
```

图片在 CMS 上传时于浏览器内转 WebP / 缩放，不再由 CI 在保存后重命名或删除原图。不再使用 `cms/sveltia` 中转分支，`cms-process.yml` 已删除。
