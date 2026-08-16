---
slug: rewrite-gamemanager-from-tauri-to-iced
title: 游戏管理器的原生重写（从 Tauri 迁移到 Iced）
date: 2026-08-16T20:30:00+08:00
description: 一次更换框架重写的实践。与其在 WebView 架构上反复打补丁，不如趁版本大更新把前端整个换掉。
cover: ./pasted-image-1786880584658.webp
categories:
  - project
tags:
  - rust
  - migration
draft: false
sticky: false
---

## 前言

GameManager 是我写的一个本地游戏管理器，主要功能是导入、扫描、启动游戏，还要管理运行时。这个项目最初是 React + Tauri v2 的技术栈（更早前用的是 Vue），前端用 Tailwind + shadcn/ui，后端是 Tauri 的 Rust 命令层，数据库用 Toasty + SQLite。

功能倒是都能用，但我总觉得不太称手：列表滚动不跟手、启动游戏时 UI 明显卡顿、扫描大目录时整个界面像死了一样。在 v0.10.0 的开发中，我做了一个大胆的决定——把前端从 React/WebView 整个换成纯 Rust 的 Iced 0.14。这篇文章记录一下迁移的原因、过程和一些库选型的对比。

## 为什么想换：

我让 Codex 对整个项目做了一次代码审查，卡顿感主要来自几处架构问题：

- **引擎/插件抽象没有贯通**。项目里用 TOML 文件定义各种引擎（Unreal、Electron、RPG Maker 等）的识别和启动规则，但入库时引擎 ID 会被硬编码枚举折叠成 `other`，等于插件能识别、不能保存、更不能按自己的策略启动。
- **扫描是阻塞式的**。扫描游戏目录时持有全局锁，同步遍历文件系统，每导入一个游戏还要全表查重、生成 profile key，批量导入接近 O(n²)。扫描期间列表、编辑、启动全部排队，而且不能取消。
- **前端没有做任何性能优化**。游戏卡片没有虚拟化，每张卡片都订阅引擎注册表，封面原图直接全量解码渲染，任何一次删除/刷新/启动后的同步都会让整个列表闪进 skeleton 状态。
- **细节竞态**。编辑弹窗没有请求序号保护，快速切换游戏时上一个游戏的异步设置可能写进下一个的表单；启动次数在进程真正创建之前就写库了。

这些问题的根源在于 WebView 架构下的两层模型（前端 JS 状态 + 后端 Rust 状态）之间靠 IPC 同步，状态一多，任何一方的变化都要走序列化、事件分发、订阅更新一整条链路。

## 打补丁不如重写

最初我并没有想重写，而是按审查结果逐项修补：把引擎配置改成 JSONC + JSON Schema（后来还是觉得 TOML 和 serde 更契合 Rust 生态，放弃了 JSONC 迁移）、重构插件系统、修扫描逻辑、加 mkxp-z 运行时支持……改了一周，效果不理想。当时的记录里我写了一句：

> 最近很多更改都是无效的，并且冗余的，很多功能不是说打补丁就能做好的。

正好我在刷到用 Rust 重写 Bun 的视频，并看了开发者的博客( [Rewriting Bun in Rust](https://bun.com/blog/bun-in-rust) )。其中有一[小节](https://bun.com/blog/bun-in-rust#claude-rewrite-bun-in-rust)，作者写道(以下是中文翻译)：

> 有很多方法可以做得很糟糕。例如，提示Claude“用Rust重写Bun。不要犯错。“然后祈祷它能奏效，这并不是我做的事。
> 
> 想想一个人会怎么做。第一个大问题是：
> 
> > 渐进式重写？还是说，所有东西同时出现？
> 
> 根据我从Bun初版（无LLM）将esbuild的Transpiler从Go移植到Zig的经验，一次性所有内容都做得更好。渐进式重写会添加临时代码，你希望最终会被删除，这在短中期内会很痛苦。

于是决定回退到 v0.9.0 基线，只保留托盘移除、文件选择器、主题初始化三处有用修改，然后向 Codex 提了一个新方案：v0.10.0 不用 Tauri 架构，换成纯 Rust 的 Iced 0.14，保持全部现有功能等价，顺便重构代码库、降低 IPC 损耗、提高性能、降低内存占用。

## 库选型对比

既然决定重写，前端生态里"哪个库更好"的问题就变成了实际决策。列一下我比较过的几组：

### UI 控件库：iced_aw / icondata / iced-shadcn-v2

- **iced_aw**：Iced 官方的组件扩展库，有日期选择、分页、卡片等，但风格偏基础，和原来 shadcn 那套视觉对不齐。
- **icondata** + **iced_aw**：图标库，但和 Iced 的集成体验一般。
- **iced-shadcn-v2**（shadcn-rs）：把 shadcn/ui 的组件用 Iced 重写的一套库，按钮、弹窗、下拉框、开关都有，正好能对上原来 React 版的视觉效果。最后选了它，配合 **lucide-icons**（带 `iced` feature）做图标。

最终依赖只有 `iced` + `iced-shadcn-v2` + `lucide-icons` 三个，没有引入 iced_aw 和 icondata。对比过程还发现一件事：之前评估时觉得"用 shadcn-rs 不如直接用 iced 原生组件"，实际对齐布局时才发现卡片、对话框这些复合组件还是用现成的省事。

### exe 图标提取：icoextract_rs

游戏卡片需要显示 Windows 游戏的封面图标，而图标嵌在 .exe 的 PE 资源里（RT_GROUP_ICON + RT_ICON 的层级结构）。市面上的 Rust 库都不太合适（exeico 的 API 不够灵活、pelite 要写大量胶水代码、windows-icons 是 Windows-only），最后我把 Python 的 [icoextract](https://github.com/jplew/icoextract) 移植成了 Rust 库 [icoextract_rs](https://crates.io/crates/icoextract_rs) 自用，发布到了 crates.io。

### 文件类型识别：infer

迁移后遇到一个很隐蔽的 bug：挂载盘（比如 NTFS 移动硬盘）会把普通文件统一暴露成 `0755` 权限，原来的检测逻辑只检查执行位，于是把 `.ico`、`.dll`、`.pck` 这些全当成原生程序。改用 [infer](https://docs.rs/infer) 按 magic bytes 识别 ELF/Mach-O，`@native` 只匹配真实二进制文件，问题解决。

### 文件选择器：rfd + xdg-portal

旧版用 tauri-plugin-dialog，默认走 GTK3 后端，弹出来的是老式文件选择器而不是 GNOME 的 Nautilus 风格。迁移到 Iced 后直接用 rfd，配置 `xdg-portal` feature，走 XDG Desktop Portal，视觉统一了，还顺便支持了 Wayland。

### 数据库：toasty 沿用

后端数据库一直用 toasty + SQLite，这次迁移把 v0.9 的数据库结构和 profile 数据完整保留了下来，用户升级无感。

## 迁移过程

### 项目结构：crates 拆分

参考了 [bottles-next](https://github.com/bottlesdevs/bottles-next) 的项目结构（不过我们不用 submodule），拆成两个 crate：

```
crates/
  gamemanager-core/      # 纯逻辑：路径、域模型、引擎注册表、扫描、导入、启动器
  gamemanager-desktop/   # Iced 界面：窗口框架、平台适配器、状态、视图、组件
```

core 只依赖纯 Rust 库，不碰 GUI；desktop 只负责渲染和事件。这样核心逻辑可以被独立测试，也方便以后加其他前端。

### UI 代码迁移实例

这是迁移前后最直观的对比。原来的 React 卡片组件：

```tsx
export default function GameCard({ game, isLaunching, onLaunch, onEdit, onDelete }) {
  const { getName, getIcon } = useEngineRegistry();
  const coverSrc = useMemo(() => {
    if (!game.coverPath) return "";
    return convertFileSrc(game.coverPath);
  }, [game.coverPath]);
  return (
    <div className="group relative flex items-center gap-3 rounded-xl border bg-card px-4 py-2.5">
      {/* 封面 */}
      <div className="h-12 w-12 shrink-0 overflow-hidden rounded-md bg-muted">
        <img src={coverSrc} className="h-full w-full object-cover" />
      </div>
      {/* ... */}
    </div>
  );
}
```

对应的 Iced 版本是一个纯函数，返回 `Element`，没有 hooks、没有闭包订阅：

```rust
pub fn view<'a>(
    game: &'a GameSummary,
    engine_name: String,
    played_time: Option<String>,
    launching: bool,
    theme: &'a Theme,
) -> Element<'a, Message> {
    let media: Element<'a, Message> = game
        .cover_path
        .as_deref()
        .map(|path| {
            image(image::Handle::from_path(path))
                .width(Length::Fixed(UiTokens::CARD_COVER_SIZE))
                .height(Length::Fixed(UiTokens::CARD_COVER_SIZE))
                .content_fit(iced::ContentFit::Cover)
                .border_radius(8.0)
                .into()
        })
        .unwrap_or_else(|| container(icons::engine(&game.engine_type)).into());

    row![media, column![text(&game.title), ...], actions].into()
}
```

Iced 是 Elm 架构（Model / Message / Update / View），所有状态集中在一个结构体里，视图函数是 `state -> Element` 的纯函数，不存在"每张卡片各自订阅"这种问题——列表重渲染是整棵视图树重新求值，没有虚拟 DOM diff，性能反而更好。

### 过程中遇到的一些小问题

- **无边框窗口的缩放热区**：`decorations: false` 之后系统不再提供边框拖拽缩放，需要在窗口四边和四角放 6-8px 的 `mouse_area` 调用 `window::drag_resize`，否则只能移动不能缩放。
- **文件拖放**：Iced 0.14 依赖的 winit 在 GNOME Wayland 下根本不投递文件拖放事件，只有 X11 路径生效。这不是补个事件回调能解决的，最后把拖放支持限制在 X11，Wayland 下没做。
- **设置弹窗高度**：之前固定 `60vh`，短表单也被撑高，底部一大片空白。改成按表单行数计算自然高度，超出才滚动。

### 扫描逻辑对齐

迁移后扫描行为必须和 0.9.3 对齐，这里也修了几个老问题：扫描识别到游戏后停止深入其资源/存档/插件子目录；`skip_scan` 引擎（比如 html）不应在扫描时命中；入口排除规则之前只检查通配符命中的第一个文件，如果第一个是辅助程序就直接放弃，改成在候选搜索内部排除。

## 结果

v0.10.0 发布后，最直观的变化是：启动更快、列表滚动流畅、扫描不再卡界面。内存占用也降了，毕竟没有 WebView 那一整套浏览器进程了。

当然 Iced 生态远没有 React 成熟，组件要自己调（不过很多组件有 shadcn-rs 已经做好了），拖放这类能力在 Wayland 下还受限；开发速度也比写 Web 套壳慢。但对于一个工具型桌面应用来说，换来的是确定的性能边界和更低的资源占用，我觉得很不错。

这次迁移给我的体会是：**当架构问题和需求不匹配时，打补丁的边际成本会越来越高，早点下定决心换框架，反而省时间。** 

> 注：旧的 Tauri 代码我没有删，留在了 `tauri-v2` 分支，随时可以回去。
