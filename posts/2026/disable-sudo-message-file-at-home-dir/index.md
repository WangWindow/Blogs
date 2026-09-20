---
slug: disable-sudo-message-file-at-home-dir
title: 禁用在使用 sudo 时创建的 .sudo_as_admin_successful 文件
date: 2026-09-20T22:17:00+08:00
description: 这是个没用的提示文件，删除后使用 sudo 命令有会重新创建，这样很不好💥！
cover: ./54603466.png
categories:
  - linux
tags:
  - ubuntu
draft: false
sticky: false
---

`~/.sudo_as_admin_successful` 是 Ubuntu/Debian 系的 `sudo` 在首次成功执行时创建的 **admin flag**。单纯 `rm` 掉它，下次执行 `sudo` 时还可能再次生成。`sudo` 官方提供 `admin_flag` 配置项，可以直接关闭。

推荐这样永久禁用：

```plain
sudo visudo -f /etc/sudoers.d/disable-admin-flag
```

写入：

```plain
Defaults !admin_flag
```

参考文献：

- [Sudo installation instructions](https://github.com/sudo-project/sudo/blob/main/INSTALL.md)
- [Bug#1012276：sudo：Debian 中 --enable-admin-flag 配置选项的实用性](https://mail-archive.com/debian-bugs-dist%40lists.debian.org/msg1856590.html)
- [sudo-rs email about .sudo_as_admin_successful file](https://mail-archive.com/debian-bugs-dist%40lists.debian.org/msg1856590.html)
