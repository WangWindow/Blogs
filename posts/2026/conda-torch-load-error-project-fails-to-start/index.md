---
slug: conda-torch-load-error-project-fails-to-start
title: conda 环境加载 torch 问题导致项目启动失败
date: 2026-05-26T21:32:00+08:00
description: I hate conda 👿
cover: ''
categories:
  - program
tags:
  - python
draft: false
sticky: false
---

我在维护实验室的一个子课题项目仓库，当我综合整理好代码，运行脚本进行测试时出现以下报错：

```bash
(soh-model) ➜  SoH-Model git:(dev/wangwindow) ✗ ./temp/train/CPTransformer.sh
Bus error (core dumped)
```

也就是刚启动就出现这个严重的错误（通常 core dumped 都是比较严重的软件问题）。

之后发现是 pytorch 的 c 拓展部分加载出了问题，在查下去发现因为使用了 miniconda 环境的 python 导致 torch 加载的问题（之前为了减小磁盘占用，清理了 conda 环境中的一些包，因为我一直用的是 uv 来进行 python 包管理，很久都不用 conda 环境了）。

然后我将 conda 彻底删除，换用 uv python，并使用 uv sync 重新安装依赖。再次启动，问题被解决 🥴。
