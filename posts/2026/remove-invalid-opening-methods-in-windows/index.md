---
slug: remove-invalid-opening-methods-in-windows
title: 移除windows中的失效的打开方式
date: 2026-09-01T18:18:00+08:00
description: 通过修改注册表，移除windows中的失效的打开方式
cover: ./2026-09-01_17-50-40.webp
categories:
  - note
tags:
  - windows
  - regedit
draft: false
sticky: false
---

Windows 的注册表是个 “好东西”，使用 **Geek Uninstaller** 卸载完软件之后，如果应用修改过文件启动方式，那么就会出现这样的 “幽灵” 条目：

![无效条目 potplayer](./2026-09-01_17-50-40.webp)

可以在注册表这里

```plain
计算机\HKEY_CLASSES_ROOT\Applications
```

删除对应软件条目即可解决

![找到注册表中的位置](./2026-09-01_18-14-55.webp)

然后在看一下打开方式，potplayer 的已经被清除了

![移除后的效果](./2026-09-01_18-12-32.webp)

参考链接：

[https://www.zhihu.com/question/515691937](https://www.zhihu.com/question/515691937)
