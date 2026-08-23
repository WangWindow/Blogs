---
slug: icoextract-rust-port
title: 把 Python 的 icoextract 移植成 Rust 库
date: 2026-08-16T20:40:00+08:00
description: 为给游戏管理器提取 exe 图标，我把一个 Python 工具移植成了 Rust 库并发布到 crates.io，过程中踩了一个 2GB 样本的 PE 解析兼容坑，还在迭代过程中内存占用优化了 700 多倍（相对我自己之前的版本）。
cover: ./2026-08-23_17-58-39.webp
categories:
  - project
tags:
  - lib
  - rust
draft: false
sticky: false
---

## 前言

GameManager 需要给游戏卡片显示封面图，Windows 游戏的封面图标就嵌在 .exe 的 PE 资源里。当时我在做 Tauri 到 Iced 的迁移，后端的图标提取能力正好需要重写。先看了现成的 Rust 库，都不太满意：

- **exeico**：专门做图标提取的库，底层用 pelite，但 API 不够灵活，不方便做枚举和按资源 ID 查询。
- **pelite**：PE 解析库，功能最全，可以自己控制资源解析流程，但要写不少胶水代码。
- **windows-icons**：Windows-only，调用系统 API，我在 Linux 上用不了。

转头发现 Python 生态有个现成工具 [icoextract](https://github.com/jplew/icoextract)，功能正好是我们要的：枚举组图标、按序号或资源 ID 提取、输出 ICO、生成缩略图，还带 `icoextract` / `icolist` / `exe-thumbnailer` 三个命令行工具。既然没有合适的 Rust 库，干脆把它移植成 Rust 库自己用，顺便发布到 crates.io 造福其他人。

## 项目设计

移植前先和上游做了逐项盘点，列了个范围矩阵，确保不重复、不遗漏。结论是完整覆盖 Python 项目的 PE 侧全部能力，唯一排除 NE/Win16（太老的 16 位格式，没必要支持，检测到就返回明确的 `UnsupportedExecutableType::Ne` 错误）。

PE 解析选型上，我最初犹豫过要不要手写。资源目录的 RVA 遍历、语言回退、字符串资源 ID 这些细节很易错，最后决定用 pelite 做唯一 PE 解析后端，但在库层隔离它的类型，不让依赖细节泄漏到公开 API。

架构上分成几个模块，功能用 feature 开关：

```plain
pe          # PE/资源目录解析（内部使用 pelite）
extractor   # IconExtractor：按索引或资源 ID 提取、列出
ico         # 生成标准 ICO 字节
thumbnail   # 可选 feature：解码最高质量帧，输出 PNG
cli         # 可选 feature：icoextract / icolist / exe-thumbnailer 三个二进制
```

公共 API 完全按 Rust 习惯设计，覆盖 Python 库的所有语义：

```rust
let extractor = icoextract_rs::IconExtractor::from_path("shell32.dll")?;

for group in extractor.list_group_icons()? {
    println!("{}: {} images", group.resource_id(), group.images().len());
}

let icon = extractor.icon_by_resource_id(32512_u16)?;
icon.write_ico(std::fs::File::create("app.ico")?)?;
```

默认只启用库的 PE 提取能力，缩略图和 CLI 都要按 feature 开启，避免只想提取 ICO 的使用者背上图像编解码依赖。

## 出现的问题：2GB 样本提取失败

库写完后，拿真实游戏测试。小文件 `geek.exe`（7.2 MiB PE32）一次通过，17 个图标组正常枚举。但大文件 `Goodbye Eternity.exe` 直接报 `corrupt PE data: bounds check failed`——这是个 2.0 GiB 的 PE32+。

有意思的是，同一个文件用 Python 上游跑，一切正常：1 个组图标、6 个帧、138 KiB 的 ICO 顺利生成。于是对着 Python 的实现逐步排查，最后定位到根因：

| 项目 | `Goodbye Eternity.exe` |
| --- | --- |
| 资源目录 RVA | `0x040e5000` |
| 正确的 `.rsrc` 文件偏移 | `0x03f08600` |
| 异常 `pck` 节起始 RVA | `0x040e3000` |
| `pck` 声明的原始大小 | `0x785d4010`（异常巨大） |

这个游戏把数据打包成了 `.pck` 节，节表里它声明的 `SizeOfRawData` 异常巨大，RVA 范围和真正的 `.rsrc` 资源节重叠了。pelite 用 `max(VirtualSize, SizeOfRawData)` 判断节的覆盖范围，并优先取第一个命中的节，于是把资源 RVA 错误映射到了游戏数据上，解析自然失败。

Python 用的 pefile 则会把一个节的有效 RVA 范围截断到下一个节的起点，`.pck` 只覆盖到下一个节前，不会遮蔽后面的 `.rsrc`，所以它能正确映射。

修复方案是保留 pelite 的 PE 头解析，但资源目录的 RVA→文件偏移映射改成 pefile 同款行为：按下一个节起点截断重叠范围，显式选中 `.rsrc`。修完后 Rust 输出和 Python 输出逐字节一致，分毫不差。这个 bug 也让我学到了：拿真实样本做回归测试很重要，很多时候仅靠 mock 的测试用例是不够的。

> [!NOTE]
> >
> 在测试排错过程中，我还想起了之前看**左程云**的 LeetCode 教学视频时教过的一个概念：对数器
> 
>  一个简单的示例如下（Java 实现）：
> 
> \`\`\`java
> for (int i = 0; i < testTime; i++) {
>     int[] arr1 = generateRandomArray();
>     int[] arr2 = copyArray(arr1);
> 
>     mySort(arr1);
>     Arrays.sort(arr2);
> >
>     if (!isEqual(arr1, arr2)) {
>         System.out.println("出错了！");
>         printArray(arr1);
>         printArray(arr2);
>         break;
>     }
> }
> \`\`\`
> >
> 实际上在开发中常被称作 “差分测试”，核心思想是比较两个实现的结果。
> 其中拿来比较的正确程序就是 reference implementation / oracle

## 性能优化

2GB 样本还暴露了第二个问题。初始实现里 `IconExtractor::from_path` 会 `std::fs::read` 把整个文件读进内存，再复制到 `Arc<[u8]>`——处理这个 2GB 的文件，峰值内存可能接近 4GB，而最终提取出的 ICO 只有 138 KiB。

修复很直接：`from_path` 改用 pelite 的 `FileMap` 做内存映射，文件只按需调页，不会整份载入；`from_bytes` 保持原来的独立拷贝语义不变。顺手还处理了一个细节：内存映射后文件长度要保存真实的，避免页对齐的填充字节被当成 PE 数据。

优化后的实测结果：

| 输入 | 结果 |
| --- | --- |
| `Goodbye Eternity.exe`（约 2GB） | 成功提取 ICO，140,799 B；峰值 RSS **5,384 KiB** |
| `geek.exe` | 成功提取 ICO，154,056 B |

峰值 RSS 从接近 4GB 降到 5.4 MiB，约 700 倍，代价只是内存映射会占用与文件大小相当的虚拟地址空间。

## 发布

crates.io 的发布经历了几次迭代：0.1.0 缺 repository 元数据，补上发 0.1.1；性能优化发 0.1.2。期间还补了 docs.rs 的 crate 首页文档，三个 CLI 的 `--help`/`--version` 测试也改成从 `CARGO_PKG_VERSION` 读版本，不再硬编码字符串。

这个库最终在 crates.io 上叫 [icoextract_rs](https://crates.io/crates/icoextract_rs)，源码在 [WangWindow/icoextract-rs](https://github.com/WangWindow/icoextract-rs)，GameManager 的图标提取直接依赖它。一次移植换来了三个收获：一个可复用的 PE 图标提取库、一次对 PE 格式边角情况的深入理解、以及一次的 Rust 库发布体验。
