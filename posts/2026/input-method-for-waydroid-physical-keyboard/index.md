---
slug: input-method-for-waydroid-physical-keyboard
title: waydroid物理键盘的输入法推荐
date: 2026-05-29T20:56:00+08:00
description: 我突然想用电脑玩安卓游戏（主要是想用悟饭模拟器玩宝可梦），于是又安装了一次 waydroid，并且这次我搞了谷歌服务，但是自带的AOSP键盘不支持中文输入，Gboard 不支持键盘快捷切换输入法。遂寻找好用的输入法。
cover: ./截图 2026-05-29 20-56-28.webp
categories:
  - linux
tags:
  - settings
  - waydroid
draft: false
sticky: false
---

于是，我尝试了一下几种输入法：

1.  [SwiftKey](https://www.microsoft.com/en-us/swiftkey)（微软的 Android 输入法）
2. [小企鹅输入法](https://github.com/fcitx5-android/fcitx5-android)（Fcitx5 框架的 Android 输入法）
3. [Trime](https://github.com/osfans/trime)（RIME 框架的 Android 输入法）

然后我发现，SwiftKey 与 Gboard 一样不支持快捷键切换。

而小企鹅输入法虽然支持快捷键切换，但是不发隐藏虚拟键盘，导致每次输入的时候会遮挡视线，所以也不考虑使用。

最后测试的是 Trime 输入法，它不仅支持输入法语言快捷切换，而且经过配置后可以隐藏虚拟键盘，然后我配置了一下主题，使得与深色主题适配，体验下来效果很不错，跟桌面输入法差不多。

Trime 默认使用的是 Lunar Pinyin 方案，我在 Linux 下使用的是 Rime Ice 方案，其实也可以直接迁移过去，配置就在安卓主目录下的 rime 文件夹中。不过我比较懒，就没搞了😙。

![](./20260529-211719.webp)
