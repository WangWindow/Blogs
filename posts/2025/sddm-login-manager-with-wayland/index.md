---
title: "SDDM登陆界面缩放及卡顿问题（Wayland）"
date: 2025-10-30T00:26:07+08:00
tags:
  - "csdn"
categories:
  - "linux"
description: "最近装了Arch+KDE（默认使用SDDM）+ Wayland，在登陆过后缩放什么的都一切正常，而在登陆界面不仅有缩放问题（字和图标太小），而且鼠标移动时还会卡顿。于是我怀疑是SDDM使用的是X11的缘故，换成Wayland果然解决。"
cover: "./470327.webp"
---

最近装了Arch+KDE（默认使用SDDM）+ Wayland，在登陆过后缩放什么的都一切正常，而在登陆界面不仅有缩放问题（字和图标太小），而且鼠标移动时还会卡顿。于是我怀疑是SDDM使用的是X11的缘故，换成Wayland果然解决。

[https://blog.csdn.net/Modest\_WANG/article/details/140643298](https://blog.csdn.net/Modest_WANG/article/details/140643298)
