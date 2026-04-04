# Blogs

共享博客内容仓库，作为 [Pages](https://github.com/WangWindow/Pages) 和 [wangwindow.github.io](https://github.com/WangWindow/wangwindow.github.io) 的 Git 子模块。

## 目录结构

```
Blogs/
├── posts/
│   ├── 2025/           # 2024年文章
│   └── 2026/           # 2026年文章
│       └── article-slug/
│           ├── index.md
│           └── cover.jpg
├── uploads/            # 公共上传资源
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
draft: false                  # 可选，默认 false
tags:
  - "tag1"
  - "tag2"
description: "文章描述"
cover: "./cover.jpg"          # 可选，相对路径
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

当此仓库有新提交时，会通过 GitHub Actions 触发 Pages 和 wangwindow.github.io 的自动构建。

## 架构设计

```
CMS → cms/sveltia → [优化图片] → 合并到 main → 同步回 cms/sveltia
                                      ↓
                              通知 Pages + wangwindow.github.io 重建
```
