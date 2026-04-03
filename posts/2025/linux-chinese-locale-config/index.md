---
title: "Linux 中文设置"
date: 2025-11-01T16:07:41+08:00
tags:
  - "settings"
categories:
  - "linux"
description: "如果想把 Linux 作为日常使用的话，配置中文显然是不可少的。本文结合了我个人的使用习惯，给出一些配置步骤和注意事项，内容较为基础，可供初学者或遇到类似问题时进行参考。 - 使用环境 Header Content Linux 发行版 ArchLinux Linux 内核版本 6.12-LTS 桌面"
---

> 如果想把 Linux 作为日常使用的话，配置中文显然是不可少的。本文结合了我个人的使用习惯，给出一些配置步骤和注意事项，内容较为基础，可供初学者或遇到类似问题时进行参考。

# \- 使用环境

| Header | Content |
| --- | --- |
| Linux 发行版 | ArchLinux |
| Linux 内核版本 | 6.12-LTS |
| 桌面环境 | Gnome 49 (Wayland) |

# 1\. 中文字体

## 1.1 字体推荐

字体方面，推荐使用 `Sarasa Gothic SC`（更纱黑体）作为显示的中文字体，使用 `JetbrainsMono Nerd Font` 作为等线字体。

<注：以前我一般用"Noto Fonts CJK"或者"文泉驿"系列作为中文字体，不过发现有的字体不太美观 >

字体可以在网上搜索下载

更纱黑体：[Releases · be5invis/Sarasa-Gothic](https://github.com/be5invis/Sarasa-Gothic/releases)

JetbainsMono Nerd Font ：[Releases · ryanoasis/nerd-fonts](https://github.com/ryanoasis/nerd-fonts/releases)

Nerd Fonts ：[Nerd Fonts - Iconic font aggregator, glyphs/icons collection, & fonts patcher](https://www.nerdfonts.com/font-downloads)

## 1.2 安装字体

将字体文件（或最好是包含一类字体的整个文件夹）复制到系统字体文件夹 `/usr/share/fonts` 下：

```shellscript
sudo cp -r <字体文件夹> /usr/share/fonts
```

然后更新一下字体缓存：

```shellscript
fc-cache -fv
```

然后就可以在 KDE 设置 / Gnome Tweaks 中通过 UI 设置界面，设置界面字体为上述字体。

如果系统中**只有一种中文字体**的话，其实到这里中文字体部分就可以说完成了。

！！！然而，如果要使用 WPS Office 等软件时，往往又会安装其他中文字体（如：宋体SimSun，微软雅黑Microsoft Yahei 等），当多种中文字体共存时，可能会出现一段文字中同时包含多种字体样式，非常不规整、不美观。

## 1.3 多种中文字体的情况

为了解决上面的问题，需要编辑`字体配置文件`，手动指定一种字体（和回滚字体）。

为了避免有时使用管理员权限运行程序时，不加载用户字体配置，个人使用的话建议创建全局字体配置文件。  
<这里字体配置文件的格式参考了 ArchWiki 中的 [字体配置 - Arch Linux 中文维基](https://wiki.archlinuxcn.org/wiki/%E5%AD%97%E4%BD%93%E9%85%8D%E7%BD%AE)\>

创建 `/etc/fonts/local.conf` 文件，简单配置如下（设置 `Sarasa Gothic SC` 作为主字体 ）：  

```xml
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>

<!-- settings go here -->

<!-- 这块区域是"衬线字体" -->
<match target="pattern">
  <test qual="any" name="family">
    <string>serif</string>
  </test>
  <edit name="family" mode="append" binding="strong">
    <string>Sarasa Gothic SC</string>
    <string>Microsoft Yahei</string>
  </edit>
</match>

<!-- 这块区域是"无衬线字体" -->
<match target="pattern">
  <test qual="any" name="family">
    <string>sans-serif</string>
  </test>
  <edit name="family" mode="append" binding="strong">
    <string>Sarasa Gothic SC</string>
    <string>Microsoft Yahei</string>
  </edit>
</match>

<!-- 这块区域是"等宽字体" -->
<match target="pattern">
  <test qual="any" name="family">
  <string>monospace</string>
  </test>
  <edit name="family" mode="append" binding="strong">
    <string>JetbrainsMono Nerd Font</string>
    <string>Adwaita Mono</string>
  </edit>
</match>

</fontconfig>
```

到这里，字体问题基本就解决了🥰。

# 2\. 中文语言

## 2.1 启用中文区域支持

编辑 `/etc/locale.gen` 文件，添加一行 `zh_CN.UTF-8`。

然后，在终端输入执行下面的命令生成中文区域支持：

```shellscript
sudo locale-gen
```

## 2.2 将系统语言设置为中文

编辑 `/etc/locale.conf` 文件，将其中的 `LANG=en_US.UTF-8` 改为 `LANG=zh_CN.UTF-8`

然后重启电脑，即可看到效果：文件管理器、设置等软件中的显示语言变成中文。

## 2.3 换成中文后恢复 Home 目录下文件夹为英文

将系统语言改为中文后，使用 `ls` 命令，发现 Home 目录下的文件夹也变成中文了。  
考虑到编程时讨厌的"中文路径“问题，所以需要更新一下目录的名称，但是请不要直接修改文件名。采用以下方法解决：

```shellscript
export LANG=en_US
xdg-user-dirs-gtk-update
```

# 3\. 中文输入法

Linux 下主流的输入法框架是 `Ibus` 和 `Fcitx` 。

-   Gnome 与 Ibus 的集成更好，因此 Gnome 桌面环境下推荐使用 Ibus。
    
-   KDE、XFCE 等桌面环境推荐使用 Fcitx，兼容性更好。
    

## 3.1 `Gnome + Ibus` 的组合

**安装 ibus 和 libpinyin （中文输入法）**

以 ArchLinux 为例：

```shellscript
sudo pacman -S ibus ibus-libpinyin
```

在 `/etc/environment` 中，添加环境变量：

    GTK_IM_MODULE=ibus
    XMODIFIERS=@im=ibus
    QT_IM_MODULE=ibus

然后重启，使得环境变量生效。

-   安装并启用 `Input Panel` 插件，这样在任务栏区域就能显示和切换输入法状态了。
    

[Input Method Panel - GNOME Shell Extensions](https://extensions.gnome.org/extension/261/kimpanel/)

-   安装并启用 `Clipboard Indicator` 插件，可以使用剪切板。
    

[Clipboard Indicator - GNOME Shell Extensions](https://extensions.gnome.org/extension/779/clipboard-indicator/)

## 3.2 `KDE + Fcitx` 的组合

**安装 fcitx 和 chinese-addons**

同样以 ArchLinux 为例：

```shellscript
sudo pacman -S fcitx5-im fcitx5-chinese-addons fcitx5-configtool
```

如果添加了 ArchLinuxCN 源，可以再安装中文词库（来自中文维基和萌娘百科）：

```shellscript
sudo pacman -S fcitx5-pinyin-zhwiki fcitx5-pinyin-moegirl
```

在 `/etc/environment` 中，添加环境变量：

    GTK_IM_MODULE=fcitx
    XMODIFIERS=@im=fcitx
    QT_IM_MODULE=fcitx

然后重启，使得环境变量生效。

<虽然 Fcitx 不建议添加这几个环境变量，但是实测没有任何坏处，并且对 x11/xwayland 应用程序中文输入法兼容性更好>

KDE 自带了"输入法状态栏"和"剪切板工具"，无需自己安装。

# 4\. 结语

至此，Linux 上的中文配置基本完成，可以开心的玩耍啦✌️。

以上的配置较为简单，步骤可能有所省略，如有疑问可以在评论区中提出 (👉ﾟヮﾟ)👉。

# \* 附录

我的一些配置文件：[WangWindow/dotfiles: my config for some things.](https://github.com/WangWindow/dotfiles)
