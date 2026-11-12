---
slug: zed-extension-godotfiles
title: 开发了一个 zed 的 godot 插件
date: 2026-11-12T14:35:00+08:00
description: 我做了一个 Godot Files for Zed，把 Godot 项目里常见文件的编辑体验补进 Zed。
cover: ./2026-11-12_14-40-24.png
categories:
  - program
tags:
  - zed
  - godot
  - extension
draft: false
sticky: false
---

我做了一个 [Godot Files for Zed](https://github.com/WangWindow/zed-extension-godotfiles)，把 Godot 项目里常见文件的编辑体验补进 Zed。

扩展为 GDScript、GDShader、场景、资源和 UID 文件提供语法支持。打开场景或资源时，res://、uid://、ExtResource 和 SubResource 引用可以跳转；悬浮信息会显示解析到的资源路径、类型和图片预览。资源服务用 Rust 编写，索引项目中的 UID 和导入信息。

> GDScript 的补全和诊断通过 Godot 编辑器自带的 Language Server 提供，因此使用时需要让 Godot 打开对应项目。GDScript 调试连接 Godot 的调试端口。

> C# 语言支持交给 [Zed 官方 C# 扩展](https://github.com/zed-extensions/csharp)，调试使用 [zed-netcoredbg](https://github.com/qwadrox/zed-netcoredbg)。GDShader 也可以选择启用独立的 [gdshader-lsp-cpp](https://github.com/Dead-Shrimp-Studio/gdshader-lsp-cpp)，提供诊断、补全等功能；它默认关闭，避免没有安装后端时影响其他文件支持。

不同服务各自负责擅长的部分：

- Tree-sitter 提供语法解析和高亮
- [gdfiles-lsp](https://github.com/WangWindow/zed-extension-godotfiles/tree/main/crates/gdfiles-lsp) 负责 Godot 资源导航
- 外部语言服务（C#、 GDScript）负责代码智能

## Thanks

- [zed-gdscript](https://github.com/grndctrl/zed-gdscript) — original extension.
- [zed-csharp](https://github.com/zed-extensions/csharp) and [zed-netcoredbg](https://github.com/qwadrox/zed-netcoredbg) — C# language features and .NET debugging.
- [Godot Files for VS Code](https://github.com/AlfishSoftware/godot-files-vscode) — resource navigation and preview reference.
- [tree-sitter-gdscript](https://github.com/PrestonKnopp/tree-sitter-gdscript) and [tree-sitter-godot-resource](https://github.com/PrestonKnopp/tree-sitter-godot-resource) — Godot grammars.
- [tree-sitter-gdshader](https://github.com/airblast-dev/tree-sitter-gdshader) — GDShader grammar and highlight queries.
- [gdshader-lsp-cpp](https://github.com/Dead-Shrimp-Studio/gdshader-lsp-cpp) — optional GDShader language server.
- [Zed extension API](https://github.com/zed-industries/zed/tree/main/crates/extension_api) and [lsp-server](https://github.com/rust-lang/rust-analyzer/tree/master/lib/lsp-server) — editor integration and LSP transport.
- [image](https://github.com/image-rs/image) and [resvg](https://github.com/linebender/resvg) — image decoding and SVG rendering.
