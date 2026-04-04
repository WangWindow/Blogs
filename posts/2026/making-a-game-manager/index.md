---
title: "制作了一个游戏管理器"
slug: "making-a-game-manager"
date: 2026-01-10T15:26:53+08:00
tags:
  - "rust"
categories:
  - "project"
description: "最近做了个游戏管理器（目前只实现了 RPG 游戏的支持，通过 NWjs 运行游戏） 使用的技术为：tauri + vue + tailwindcss 效果如下（移除了默认的系统标题栏，改为自绘制的按钮，通过 tauri 中的插件功能，获得窗口拖动、最小化、最大化、关闭权限） 项目地址为：https"
cover: "./159688.webp"
---

最近做了个游戏管理器（目前只实现了 RPG 游戏的支持，通过 NWjs 运行游戏）

使用的技术为：`tauri` + `vue` + `tailwindcss`

效果如下（移除了默认的系统标题栏，改为自绘制的按钮，通过 tauri 中的插件功能，获得窗口拖动、最小化、最大化、关闭权限）

![screenshot](./%E6%88%AA%E5%9B%BE%202026-01-10%2015-09-42.webp)

项目地址为：[https://github.com/WangWindow/GameManager](https://github.com/WangWindow/GameManager)


使用 tauri 库的 `tray-icon` feature，实现系统托盘菜单功能。

此外，文件访问、对话框等权限也是由 tauri 端进行控制。

----

目前的管理方案是，由 `sqlite` 数据库存储管理器数据，如软件设置、游戏容器路径等上层设置。

每个游戏容器中包含一个 `settings.toml` ，用于具体启动参数、游戏封面等细节设置。


利用 XDG 规范，重定向游戏的运行目录和缓存位置，避免“垃圾”的扩散。

[https://wiki.archlinux.org/title/XDG_Base_Directory](https://wiki.archlinux.org/title/XDG_Base_Directory)
