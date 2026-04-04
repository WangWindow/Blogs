---
title: "Flatpak 安装的 QQMusic 无法显示系统托盘的问题"
slug: "qqmusic-installed-via-flatpak-miss-the-tray-icon"
date: 2025-12-31T10:53:49+08:00
tags:
  - "settings"
categories:
  - "linux"
description: "flatpak 安装的 qqmusic 无法显示系统托盘 issue 无法显示系统托盘 是因为缺少了 org.kde.* 的权限 可以使用 flatseal 管理 flatpak 应用权限。 注意 需要杀死所有 qqmusic 进程后再重新启动，新的权限才能生效。"
cover: "./546081.webp"
---

flatpak 安装的 qqmusic 无法显示系统托盘

[issue: 无法显示系统托盘](https://github.com/flathub/com.qq.QQmusic/issues/25)

是因为缺少了 `org.kde.*` 的权限

可以使用 `flatseal` 管理 flatpak 应用权限。

![2025-12-31 10-39-20.png](./%E6%88%AA%E5%9B%BE%202025-12-31%2010-39-20.webp)

> 注意: 需要杀死所有 qqmusic 进程后再重新启动，新的权限才能生效。
