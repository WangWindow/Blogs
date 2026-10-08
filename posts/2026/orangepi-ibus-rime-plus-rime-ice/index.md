---
slug: orangepi-ibus-rime-plus-rime-ice
title: Armbian/Ubuntu 下安装 IBus Rime + 雾凇拼音
date: 2026-10-08T09:19:00+08:00
description: |-
  最近在 Orange Pi 5B 的 Armbian 上配置中文输入法，准备继续使用 ibus-rime + 雾凇拼音。
  不过直接通过 APT 安装时，会附带安装不少其他 Rime 输入方案。另外，雾凇拼音本身不由 APT 管理，后续更新需要单独处理。
  最终决定使用 APT 管理输入法引擎，Git 管理雾凇拼音配置，不需要自行编译。
cover: ./rime.png
categories:
  - tool
tags:
  - rime
  - ibus
draft: false
sticky: false
---

最近在 Orange Pi 5B 的 Armbian 上配置中文输入法，准备继续使用 `ibus-rime` + [雾凇拼音](https://github.com/iDvel/rime-ice)。

不过直接通过 APT 安装时，会附带安装不少其他 Rime 输入方案。另外，雾凇拼音本身不由 APT 管理，后续更新需要单独处理。

最终决定使用 **APT 管理输入法引擎，Git 管理雾凇拼音配置**，不需要自行编译。

## 安装 IBus Rime

通过 `--no-install-recommends` 跳过非必要的推荐依赖：

```plain
sudo apt update
sudo apt install --no-install-recommends ibus-rime
```

这个参数不会排除硬依赖，例如 `librime-data`，但能减少额外安装的预置输入方案。

## 安装雾凇拼音

IBus Rime 的用户配置目录为 `~/.config/ibus/rime/`。

如果已经使用过 Rime，先备份原有配置：

```plain
mkdir -p ~/.config/ibus
if test -e ~/.config/ibus/rime
    mv ~/.config/ibus/rime ~/.config/ibus/rime.backup-(date +%Y%m%d-%H%M%S)
end
```

然后直接克隆雾凇拼音仓库：

```plain
git clone --depth 1 https://github.com/iDvel/rime-ice.git ~/.config/ibus/rime
```

在 `~/.config/ibus/rime/default.custom.yaml` 中添加：

```plain
patch:
  __include: rime_ice_suggestion:/
```

这样就只启用雾凇拼音的默认输入方案，无需删除系统安装的其他 Rime 方案。

重新部署：

```plain
touch ~/.config/ibus/rime/
ibus restart
```

最后在 GNOME 的 **设置 → 键盘 → 输入源** 中添加中文（Rime）即可。

## 更新雾凇拼音

由于直接克隆到配置目录，更新只需要：

```plain
git -C ~/.config/ibus/rime pull --ff-only
touch ~/.config/ibus/rime/
ibus-daemon -rdx
```

使用 `*.custom.yaml` 保存个人配置，不直接修改仓库内的默认文件，能减少后续 Git 更新时发生冲突的可能性。

## 自动更新（可选）

如果不想手动更新，可以使用 systemd user timer，每周自动同步一次仓库。

创建 `~/.config/systemd/user/rime-ice-update.service`：

```plain
[Unit]
Description=Update Rime Ice

[Service]
Type=oneshot
ExecStart=/usr/bin/git -C %h/.config/ibus/rime pull --ff-only
ExecStartPost=/usr/bin/touch %h/.config/ibus/rime/
```

创建 `~/.config/systemd/user/rime-ice-update.timer`：

```plain
[Unit]
Description=Weekly Rime Ice Update

[Timer]
OnCalendar=weekly
Persistent=true

[Install]
WantedBy=timers.target
```

然后启用：

```plain
systemctl --user daemon-reload
systemctl --user enable --now rime-ice-update.timer
```

这样就会每周自动拉取更新，并标记 Rime 配置需要重新部署。下次重启 IBus 并触发部署后即可使用新配置。

这种方式将输入法引擎和配置的更新分开管理，比手动复制词库文件方便很多。

## 参考资料

- [雾凇拼音 GitHub](https://github.com/iDvel/rime-ice)
- [雾凇拼音安装指南](https://github.com/iDvel/rime-ice/blob/main/others/docs/Installation.md)
- [Rime 定制指南](https://github.com/rime/home/wiki/CustomizationGuide)
- [之前的 Rime 输入法配置存档](https://wangwindow.pages.dev/posts/rime-input-method-configuration-backup/)
