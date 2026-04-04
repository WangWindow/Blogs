---
title: "使用 fisher 管理 fish shell 插件拓展"
slug: "fisher-manage-fish"
date: 2025-12-13T23:38:04+08:00
tags:
  - "settings"
categories:
  - "linux"
description: "使用 fisher 管理 fish shell 插件拓展 fish 是一个功能很强大的 shell，但是没有插件的话只有默认的补全功能，虽然比 bash 好用，但是不支持 posix 标准的 sh 脚本，难免心里感到有些不爽。 不过幸好有 fisher [github link] 这个管理工具 Ar"
cover: "./1154991.webp"
---

# 使用 fisher 管理 fish shell 插件拓展

> `fish` 是一个功能很强大的 shell，但是没有插件的话只有默认的补全功能，虽然比 `bash` 好用，但是不支持 posix 标准的 sh 脚本，难免心里感到有些不爽。

不过幸好有 `fisher` [[github link]](https://github.com/jorgebucaran/fisher) 这个管理工具

Arch 的官方仓库就有收录，因此直接使用 `pacman` 完成安装
```shell
sudo pacman -S fisher
```

插件可以在这里搜索到：
https://github.com/topics/fish-plugin

1. 安装插件
```shell
fisher install xxx/xxx
```

2. 列出插件
```shell
fisher list
```

3. 移除插件
```shell
fisher remove xxx/xxx
```

常用插件：

- z 跳转插件： [jethrokuan/z](https://github.com/jethrokuan/z)
- bash 环境变量复用插件：[edc/bass](https://github.com/edc/bass)
- catppuccin 配色主题： [catppuccin/fish](https://github.com/catppuccin/fish)
- extract 解压插件： [shoriminimoe/fish-extract](https://github.com/shoriminimoe/fish-extract)
