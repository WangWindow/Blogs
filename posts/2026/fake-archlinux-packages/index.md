---
slug: fake-archlinux-packages
title: 使用 provides 避免 pacman 重复安装依赖
date: 2026-08-01T17:40:00+08:00
description: ''
cover: ./2026-08-01_17-44-20.webp
categories:
  - note
  - linux
tags:
  - aur
draft: false
sticky: false
---

有时我们已经通过官方压缩包、SDK 管理器或其他方式，在用户目录中安装了某个运行环境，但 pacman 并不知道它的存在。

例如，我已经手动安装了 Java，并将其加入了 `PATH`。此时 Java 命令可以正常使用，但在安装 Minecraft 启动器时，pacman 仍可能要求安装仓库中的 Java 软件包。

这是因为 pacman 判断依赖是否满足时，主要检查的是自己的本地软件包数据库，而不是扫描 `PATH`，也不会检查用户目录中是否存在对应程序。

一种解决方法是创建一个只包含软件包元数据的空包，通过 PKGBUILD 中的 `provides` 字段，告诉 pacman：

> 当前系统已经通过其他方式提供了这些依赖。

例如：

```bash
pkgname=facman
pkgver=1.0.0
pkgrel=1
pkgdesc='Virtual package providers for pacman dependency resolution'
arch=('any')
license=('MIT')

provides=(
    'dotnet-sdk'
    'netcat'
    'nodejs=26.5.0'
    'npm'
)

package() {
    :
}
```

其中，`provides` 用来声明这个软件包能够提供哪些其他软件包或虚拟组件。安装 `facman` 后，当其他软件包依赖 `dotnet-sdk`、`netcat`、`npm` 或符合版本要求的 `nodejs` 时，pacman 会认为这些依赖已经得到满足。`provides` 正是 PKGBUILD 官方支持的虚拟依赖机制。

`package()` 中只有一个 `:`，表示不安装任何实际文件。因此，`facman` 本质上只是一个元数据包：它不会安装 Node.js、.NET SDK 或其他运行环境，只会将 `provides` 信息注册到 pacman 的本地数据库中。

将上述内容保存为 `PKGBUILD` 后，可以执行：

```bash
makepkg -si
```

`makepkg` 会根据当前目录中的 `PKGBUILD` 生成 Arch 软件包，`-i` 会在构建完成后安装该软件包。

安装后，可以使用以下命令查看注册的虚拟依赖：

```bash
pacman -Qi facman
```

也可以检查某个依赖是否已经得到满足：

```bash
pacman -T dotnet-sdk npm netcat 'nodejs>=18'
```

如果没有任何输出，说明这些依赖在 pacman 看来均已满足。

### 关于版本

如果目标软件包只依赖包名：

```bash
depends=('npm')
```

那么下面的声明就足够了：

```bash
provides=('npm')
```

但如果目标软件包带有版本限制：

```bash
depends=('nodejs>=18')
```

那么 `provides` 也应声明一个具体版本：

```bash
provides=('nodejs=26.5.0')
```

`provides` 中应描述“当前提供的具体版本”，不能写成 `nodejs>=18`。依赖方会使用这个具体版本进行比较。

### 注意事项

这种方法只会改变 pacman 的依赖判断，不会真正提供对应的命令、动态链接库或运行环境。

因此，它适合下面这种情况：

* 已经通过官方压缩包安装了 Java 或 .NET SDK；
* 已经通过语言版本管理器安装了对应运行环境；
* 系统中确实存在与目标软件兼容的替代实现；
* 只是希望避免 pacman 再安装一份重复环境。

不建议为了减少下载量而随意伪造原生动态库依赖。假如软件运行时需要 `libexample.so`，仅仅添加：

```bash
provides=('example')
```

并不会创建这个动态链接库，软件仍然可能无法启动。

另外，这个包只需要在本地通过 `makepkg` 构建和安装，并不一定要上传到 AUR。AUR 主要用于共享用户维护的 PKGBUILD；其中的软件仍然需要由用户使用 `makepkg` 构建，再通过 pacman 安装。

### 参考资料

* 参考实现: https://github.com/WangWindow/facman
* [ArchWiki：PKGBUILD](https://wiki.archlinux.org/title/PKGBUILD)
* [ArchWiki：Creating packages](https://wiki.archlinux.org/title/Creating_packages)
* [ArchWiki：makepkg](https://wiki.archlinux.org/title/Makepkg)
* [Arch 官方手册：PKGBUILD(5)](https://man.archlinux.org/man/PKGBUILD.5)
* [Arch 官方手册：makepkg(8)](https://man.archlinux.org/man/makepkg.8)
* [Arch 官方手册：pacman(8)](https://man.archlinux.org/man/pacman.8)
