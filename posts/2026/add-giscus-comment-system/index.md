---
slug: add-giscus-comment-system
title: 在文章底部添加 Giscus 评论系统
date: 2026-05-27T08:03:00+08:00
description: 测试 😀
cover: ./2026-05-27_08-26-08.webp
categories:
  - tool
tags:
  - settings
draft: false
sticky: false
---

感觉没有评论的话，只能单向交流，正好博客模板中预留了评论系统，考虑到应该类似帖子一样的回复，Github Discussion 就是个很不错的选择，可以进行自由交流对话。

因此选择了 [Giscus](https://giscus.app/)。

首先需要在博客仓库中安装 [Gisuss App](https://github.com/apps/giscus) 并完成授权，然后进入 https://giscus.app 输入 `用户名/仓库`，并进行一些个性化设置，它会生成相应的模板，然后放在博客模板的合适位置中（主要是需要 `data-repo-id` 和 `data-category-id`）。我生成的配置如下：

```html
<script src="https://giscus.app/client.js"
        data-repo="WangWindow/Blogs"
        data-repo-id="R_kgDORoITkg"
        data-category="Comments"
        data-category-id="DIC_kwDORoITks4C96YC"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="bottom"
        data-theme="preferred_color_scheme"
        data-lang="zh-CN"
        data-loading="lazy"
        crossorigin="anonymous"
        async>
</script>
```

# 具体的步骤参考

## Step 1 — 在 WangWindow/Blogs 仓库启用 Discussions：

Settings → Features → Discussions → 勾选启用。创建一个 Discussion 分类（建议叫 "Comments" 或 "General"，不要用 "Announcements" — 那个分类有限制）。

## Step 2 — 安装 giscus GitHub App：

https://github.com/apps/giscus → 授权到 WangWindow/Blogs。

## Step 3 — 获取配置参数：

打开 https://giscus.app，填入 WangWindow/Blogs，选择刚创建的分类，复制生成的 repoId 和 categoryId。
