---
title: "Linux 应用程序缩放问题解决方案"
slug: "scaling-issues-in-linux"
date: 2025-11-08T18:53:23+08:00
tags:
  - "settings"
categories:
  - "linux"
description: "现在大部分桌面默认是 wayland 协议，对于 wayland 应用程序与桌面环境通常有较好的缩放支持，而对 xwayland/x11 应用有时缩放会明显不起作用，需要一些额外设置（通常是设置一些环境变量），本文对多种框架的处理情况进行总结。 1. QT 缩放（WeChat等应用） 环境变量： Q"
cover: "./0072Vf1pgy1foxkd1pxk2j31hc0u0tqe.webp"
---

> 现在大部分桌面默认是 `wayland` 协议，对于 `wayland` 应用程序与桌面环境通常有较好的缩放支持，而对 `xwayland/x11` 应用有时缩放会明显不起作用，需要一些额外设置（通常是设置一些环境变量），本文对多种框架的处理情况进行总结。

#   
1\. QT 缩放（WeChat等应用）

环境变量：

```shellscript
QT_SCREEN_SCALE_FACTOR=2 #强制2倍缩放

QT_AUTO_SCREEN_SCALE_FACTOR=1 #自动缩放

```

# 2\. Avalonia 强制全局缩放（Ryujinx等应用）

环境变量：

```shellscript
AVALONIA_GLOBAL_SCALE_FACTOR=2 #强制2倍缩放
```

[https://github.com/AvaloniaUI/Avalonia/issues/9390](https://github.com/AvaloniaUI/Avalonia/issues/9390)  

# 3\. Chrome/Electron wayland支持

添加启动参数（编辑 `xxx.desktop` 或者 `~/.config/xxx-flags.conf`）：

    --enable-features=UseOzonePlatform --ozone-platform=wayland --enable-wayland-ime
    

[https://jishuzhan.net/article/1951523354925641730](https://jishuzhan.net/article/1951523354925641730)  

# 4\. Gnome 缩放

```shellscript
gsettings set org.gnome.mutter experimental-features '["scale-monitor-framebuffer", "xwayland-native-scaling"]'
```
