---
title: "rime 输入法配置存档"
slug: "rime-input-method-configuration-backup"
date: 2025-12-30T12:41:27+08:00
tags:
  - "settings"
categories:
  - "linux"
description: "rime 输入法配置存档 目前使用 ibus + rime + rime-ice 的输入方案 rime/default.custom.yaml patch  # 仅使用「雾凇拼音」的默认配置，配置此行即可  __include rime_ice_suggestion/  # 以下根据自己"
cover: "./616556.webp"
---

`rime` 输入法配置存档

目前使用 `ibus + rime + rime-ice` 的输入方案

<details>
<summary> rime/default.custom.yaml </summary>
    
```yaml
patch:
  # 仅使用「雾凇拼音」的默认配置，配置此行即可
  __include: rime_ice_suggestion:/
  # 以下根据自己所需自行定义，仅做参考。
  # 针对对应处方的定制条目，请使用 <recipe>.custom.yaml 中配置，例如 rime_ice.custom.yaml
  __patch:

    menu:
      page_size: 6

    switcher:
      hotkeys:
        - Control+Shift+space     # 切换输入法的快捷键（可自定义）

    # key_binder/bindings/+:
      # 开启逗号句号翻页
      # - { when: paging, accept: comma, send: Page_Up }
      # - { when: has_menu, accept: period, send: Page_Down }     
```
</details>
    
<details>
<summary> rime/build/ibus_rime.yaml </summary>

```yaml
__build_info:
  rime_version: 1.14.0
  timestamps:
    ibus_rime: 1757706530
    ibus_rime.custom: 0
config_version: 1.0
style:
  cursor_type: insert
  horizontal: true      # 开启水平输入法布局
  inline_preedit: false # 关闭预编辑（即开启双行显示）
  preedit_style: composition
```
</details>
