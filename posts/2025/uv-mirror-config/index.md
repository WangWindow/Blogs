---
title: "uv 配置国内镜像加速"
slug: "uv-mirror-config"
date: 2025-11-27T13:06:34+08:00
tags:
  - "python"
  - "settings"
categories:
  - "tool"
description: "使用 uv 配置国内镜像加速：Python 解释器下载 + PyPI 包安装双提速 🚀 uv 是由 Astral 开发的新一代超快 Python 工具链，集成了虚拟环境创建、依赖解析、包安装甚至 Python 解释器自动下载功能。但在国内直接使用默认源时，无论是下载 Python 还是安装包，速度"
cover: "./0072Vf1pgy1foxk6ybqjfj31hc0u047b.webp"
---

---

# 使用 uv 配置国内镜像加速：Python 解释器下载 + PyPI 包安装双提速

> 🚀 **uv** 是由 Astral 开发的新一代超快 Python 工具链，集成了虚拟环境创建、依赖解析、包安装甚至 Python 解释器自动下载功能。但在国内直接使用默认源时，无论是下载 Python 还是安装包，速度都极其缓慢。  
> 本文将手把手教你通过 **全局配置** 或 **项目级配置**，结合 **USTC 镜像站** 和 **npmmirror 镜像**，实现 `uv` 全流程加速！

---

## 命令行快速写入（使用 python 确保通用性）
```shell
python -c "
import os, pathlib
cfg = '''
# Python 解释器镜像
python-install-mirror = \"https://registry.npmmirror.com/-/binary/python-build-standalone\"

# PyPI 包索引（USTC）
[[index]]
url = \"https://mirrors.ustc.edu.cn/pypi/simple\"
default = true
'''
path = pathlib.Path.home() / '.config' / 'uv' / 'uv.toml'
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(cfg)
"
```

## 一、为什么需要配置镜像？

`uv` 在以下场景会访问国外服务器：

- 执行 `uv init --python 3.12` → 从 GitHub 下载 [python-build-standalone](https://github.com/astral-sh/python-build-standalone)
- 执行 `uv add torch` → 从 `pypi.org` 下载包

由于网络限制，这些操作在国内往往卡顿甚至失败。  
**解决方案：替换为国内镜像源！**

---

## 二、加速 Python 解释器下载

### ✅ 推荐镜像源

使用 **npmmirror（淘宝 NPM 镜像站）** 提供的 Python 构建镜像：

```
https://registry.npmmirror.com/-/binary/python-build-standalone
```

该镜像完整同步了官方静态构建版本，完全兼容 `uv`。

### 🔧 配置方式

#### 1. 全局配置（用户级）

- **Linux / macOS**：
  ```bash
  mkdir -p ~/.config/uv
  cat > ~/.config/uv/uv.toml <<EOF
  python-install-mirror = "https://registry.npmmirror.com/-/binary/python-build-standalone"
  EOF
  ```

- **Windows（PowerShell）**：
  ```powershell
  New-Item -Path "$env:APPDATA\uv" -ItemType Directory -Force
  Set-Content -Path "$env:APPDATA\uv\uv.toml" -Value 'python-install-mirror = "https://registry.npmmirror.com/-/binary/python-build-standalone"'
  ```

#### 2. 项目级配置

在项目根目录的 `pyproject.toml` 中添加：

```toml
[tool.uv]
python-install-mirror = "https://registry.npmmirror.com/-/binary/python-build-standalone"
```

#### 3. 临时环境变量（调试用）

```bash
UV_PYTHON_INSTALL_MIRROR="https://registry.npmmirror.com/-/binary/python-build-standalone" uv venv --python 3.12
```

---

## 三、加速 PyPI 包安装

### ✅ 推荐镜像源

**中国科学技术大学（USTC）PyPI 镜像**（稳定、同步及时）：

```
https://mirrors.ustc.edu.cn/pypi/simple
```

> 💡 其他可选：清华 `https://pypi.tuna.tsinghua.edu.cn/simple`、阿里云 `https://mirrors.aliyun.com/pypi/simple`

### 🔧 配置方式

#### 1. 全局配置（~/.config/uv/uv.toml）

编辑或创建 `~/.config/uv/uv.toml`，内容如下：

```toml
# 加速 Python 解释器下载
python-install-mirror = "https://registry.npmmirror.com/-/binary/python-build-standalone"

# 加速 PyPI 包安装（USTC 镜像）
[[index]]
url = "https://mirrors.ustc.edu.cn/pypi/simple"
default = true
```

> ✅ 这是 **标准且推荐的写法**，兼容 `uv` 的多仓库机制。

#### 2. 项目级配置（pyproject.toml）

```toml
[tool.uv]
python-install-mirror = "https://registry.npmmirror.com/-/binary/python-build-standalone"

[[tool.uv.index]]
url = "https://mirrors.ustc.edu.cn/pypi/simple"
default = true
```

#### 3. 环境变量（仅限单源，不推荐长期使用）

```bash
export UV_DEFAULT_INDEX="https://mirrors.ustc.edu.cn/pypi/simple"
```

> ⚠️ 注意：环境变量无法表达 `default = true` 或多源逻辑，仅作临时测试。

---

## 四、完整配置示例汇总

### 全局配置文件：`~/.config/uv/uv.toml` 或 `/etc/uv/uv.toml`

```toml
# ~/.config/uv/uv.toml

# Python 解释器镜像
python-install-mirror = "https://registry.npmmirror.com/-/binary/python-build-standalone"

# PyPI 包索引（USTC）
[[index]]
url = "https://mirrors.ustc.edu.cn/pypi/simple"
default = true
```

### 项目配置文件：`pyproject.toml`

```toml
[tool.uv]
python-install-mirror = "https://registry.npmmirror.com/-/binary/python-build-standalone"

[[tool.uv.index]]
url = "https://mirrors.ustc.edu.cn/pypi/simple"
default = true
```

---

## 五、参考资料

- [USTC Mirror Help - uv](https://mirrors.ustc.edu.cn/help/uv.html)
- [uv 官方文档 - Settings](https://docs.astral.sh/uv/reference/settings/)
- [python-build-standalone 镜像说明](https://npmmirror.com/mirrors/python-build-standalone/)

---

配置完成后，你将体验到 `uv` 真正的“极速”魅力——秒建环境、秒装依赖，开发效率大幅提升！🎉
