---
title: "游戏管理器前端框架迁移日志"
slug: "game-manager-frontend-migration-log"
date: 2026-02-25T11:50:54+08:00
tags:
  - "other"
categories:
  - "project"
description: "游戏管理器前端框架迁移日志 项目地址：https//github.com/WangWindow/GameManager 变更历史：https//github.com/WangWindow/GameManager/compare/v0.3.2...v0.4.2 1. 是什么 最近把前段时间写的 G"
cover: "./1060055.webp"
---

# 游戏管理器前端框架迁移日志

> 项目地址：https://github.com/WangWindow/GameManager
> 变更历史：https://github.com/WangWindow/GameManager/compare/v0.3.2...v0.4.2

## 1. 是什么

最近把前段时间写的 `GameManager` 的前端框架进行更新迁移 （由 `Vue -> React`）

## 2. 为什么

- `VSCode`、`Zed` 等开发工具默认支持 React (即 `tsx`、`jsx` 语法)，集成度更高，可以避免再安装第三方 Vue 插件。
- 代码格式化和代码诊断、代码提示支持更好。
- React 的生态更好，如 [shadcn-ui](https://github.com/shadcn-ui/ui) 等知名的组件库支持。
- 几周前在 Cloudflare Pages 上的博客网页使用的模板为 Astro + React 框架。

所以，我决定不再使用 Vue，转而使用 React。

而这个游戏管理器项目考虑到可能需要长期维护，所以进行迁移重构还是很重要的。

## 3. 怎么做

在本项目中，从 Vue 迁移到 React 的过程主要分为以下 3 步：

1. 将 vue 相关依赖移除，并替换为相应的 React 依赖；
2. 将 ts 文件中使用 vue 组件的地方进行替换；
3. 将 vue 文件重写为 tsx 文件：其中 shadcn 风格组件使用 init 命令进行初始化重建，其他自定义组件则对照着原本的 vue 文件尽可能 1:1 使用 tsx 还原。

这样就基本迁移的差不多了，然后就是对迁移后存在的 bug 和细节上的修复了。
