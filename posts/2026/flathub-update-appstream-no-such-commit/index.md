---
slug: flathub-update-appstream-no-such-commit
title: flathub 更新遇到 "appstream ... no such commit"
date: 2026-06-11T09:26:00+08:00
description: |-
  我每天打开电脑之后，就会更新一下软件，最近使用 `flatpak update` 时出现以下报错：
  正在为远程仓库 flathub 更新 appstream 数据
  更新时出错: 从远程仓库 flathub 提取 appstream2/x86_64 时：No such metadata object
cover: ''
categories:
  - linux
  - note
tags:
  - flatpak
draft: false
sticky: false
---

我每天打开电脑之后，就会更新一下软件，最近使用 `flatpak update` 时出现以下报错：

```sh
正在为远程仓库 flathub 更新 appstream 数据
更新时出错: 从远程仓库 flathub 提取 appstream2/x86_64 时：No such metadata object 6b2e0ca48f381b94d09e497197506653c5541d532b3e2de10b6f6cbc05cfc391.commit
```

一开始觉得是镜像源的问题，所以切换回 flathub 的官方源，重新更新以及使用 `flatpak repair` 均没有效果。

之后在 ChatGPT 的帮助下找到这个 [issue](https://status.flathub.org/issues/2026-03-24-appstream2/) ，按照上面的方法解决了问题。

```sh
sudo ostree --repo=/var/lib/flatpak/repo refs --delete flathub:appstream2/x86_64

ostree --repo=$HOME/.local/share/flatpak/repo refs --delete flathub:appstream2/x86_64

flatpak update --appstream
正在为远程仓库 flathub 更新 appstream 数据

flatpak update
正在查找更新…
没有更新。
```

原文内容：
># appstream2 分支引用过时的提交
>
>
> appstream2 分支与增量索引不匹配，导致本地 Flatpak 客户端无法更新 appstream 数据。重新生成分支和索引后，此问题已解决。
> 
> 如果问题仍然存在，请尝试以下步骤清除 appstream2 分支的本地副本。 
> 
> ```sh
> # For system-wide installation 
> sudo ostree --repo=/var/lib/flatpak/repo refs --delete flathub:appstream2/x86_64
> 
> # For user installation
> ostree --repo=$HOME/.local/share/flatpak/repo refs --delete flathub:appstream2/x86_64
> 
> # Update the appstream data
> flatpak update --appstream
> ```
> 
> 此外，部分客户端在获取已从服务器移除的增量索引时遇到超时问题。这是由于 CDN 未缓存 404 响应，导致请求在 nginx 的缓存锁后排队等待。我们已部署修复程序来缓存 404 响应，使客户端能够优雅地回退到完整下载。
