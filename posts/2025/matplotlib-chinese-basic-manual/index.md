---
title: "Matplotlib 基础使用指南：让图表支持中文显示"
slug: "matplotlib-chinese-basic-manual"
date: 2025-11-17T12:29:18+08:00
tags:
  - "python"
categories:
  - "programming"
description: "Matplotlib 基础使用指南：让图表支持中文显示 在数据可视化领域，Python 的 Matplotlib 是最经典、最广泛使用的绘图库之一。然而，许多初学者在使用 Matplotlib 绘制包含中文的图表时，常常会遇到中文显示为方框或乱码的问题。本文将带你从零开始，掌握 Matplotlib"
cover: "./0072Vf1pgy1fodqork5ayj31cq0ygx6q.webp"
---

# Matplotlib 基础使用指南：让图表支持中文显示

在数据可视化领域，Python 的 **Matplotlib** 是最经典、最广泛使用的绘图库之一。然而，许多初学者在使用 Matplotlib 绘制包含中文的图表时，常常会遇到中文显示为方框或乱码的问题。本文将带你从零开始，掌握 Matplotlib 的基本用法，并重点解决中文显示问题。

---

## 一、安装与导入

首先确保你已安装 Matplotlib：

```bash
pip install matplotlib
```

然后在 Python 脚本中导入：

```python
import matplotlib.pyplot as plt
```

---

## 二、解决中文显示问题

Matplotlib 默认使用英文字体（如 DejaVu Sans），不支持中文字符。要正确显示中文，我们需要手动指定一个系统中已安装的中文字体。

### 推荐配置方式

```python
# 配置 matplotlib 支持中文显示
plt.rcParams["font.sans-serif"] = [
    "Sarasa Gothic SC",        # 更纱黑体（开源、现代）
    "Noto Sans CJK SC",        # 思源黑体（Google & Adobe 合作）
    "Microsoft YaHei",         # 微软雅黑（Windows 常见）
    "WenQuanYi Micro Hei",     # 文泉驿微米黑（Linux 常见）
]
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号（如 -1）
```

> 💡 **说明**：
> - `font.sans-serif` 是一个字体列表，Matplotlib 会按顺序尝试加载，直到找到系统中可用的字体。
> - `axes.unicode_minus = False` 确保负号（如坐标轴上的 `-5`）能正常显示，而不是变成方框。

---

## 三、基础绘图示例

下面是一个简单的折线图，展示中文标题和标签的效果：

```python
import matplotlib.pyplot as plt

# 设置中文字体支持
plt.rcParams["font.sans-serif"] = ["Sarasa Gothic SC", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

# 示例数据
months = ["1月", "2月", "3月", "4月", "5月", "6月"]
sales = [120, 135, 150, 180, 210, 240]

# 绘图
plt.figure(figsize=(8, 5))
plt.plot(months, sales, marker='o', linestyle='-', color='teal')
plt.title("2025年上半年销售额趋势", fontsize=16)
plt.xlabel("月份")
plt.ylabel("销售额（万元）")
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.show()
```

### 效果图（示意）


![截图 2025-11-17 12-33-24.png](./%E6%88%AA%E5%9B%BE%202025-11-17%2012-33-24.webp)
> ✅ 图中标题、横纵坐标等中文均正常显示，无乱码。

---

## 四、如何查看系统中可用的中文字体？

如果你不确定系统里有哪些中文字体可用，可以运行以下代码列出所有支持中文的字体：

```python
from matplotlib.font_manager import FontManager
import subprocess

fm = FontManager()
fonts = [f.name for f in fm.ttflist if 'SimSun' in f.name or 'Hei' in f.name or 'Song' in f.name or 'Microsoft' in f.name or 'Noto' in f.name or 'Sarasa' in f.name]
print(set(fonts))
```

或者更简单的方式（适用于 Linux/macOS）：

```bash
fc-list :lang=zh
```

---

## 五、常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| 中文显示为方框 | 缺少中文字体或未正确配置 | 安装字体（如思源黑体），并设置 `rcParams` |
| 负号显示异常 | `unicode_minus` 未关闭 | 设置 `plt.rcParams["axes.unicode_minus"] = False` |
| 字体生效但样式丑 | 默认字体不美观 | 优先使用 Sarasa Gothic 或 Noto Sans CJK |

---

## 六、推荐中文字体清单

| 字体名称 | 特点 | 适用平台 |
|--------|------|--------|
| **Sarasa Gothic SC** | 开源、等宽/比例可选、现代感强 | 跨平台（需手动安装） |
| **Noto Sans CJK SC** | Google/Adobe 出品，覆盖全面 | 跨平台（多数 Linux 自带） |
| **Microsoft YaHei** | Windows 默认，清晰易读 | Windows |
| **WenQuanYi Micro Hei** | 开源，Linux 友好 | Linux |

> 📌 小技巧：将 `Sarasa Gothic SC` 放在字体列表首位，可获得最佳视觉效果！

---

## 七、结语

通过简单的配置，我们就能让 Matplotlib 完美支持中文显示，大幅提升数据报告的专业性和可读性。记住关键两行代码：

```python
plt.rcParams["font.sans-serif"] = ["你的中文字体"]
plt.rcParams["axes.unicode_minus"] = False
```

从此告别乱码，轻松绘制中文图表！

---

**延伸阅读**：
- [Matplotlib 官方文档](https://matplotlib.org/)
- [更纱黑体 GitHub 项目](https://github.com/be5invis/Sarasa-Gothic)
- [思源黑体下载地址](https://github.com/adobe-fonts/source-han-sans)

---
希望这篇指南对你有帮助！欢迎点赞、收藏、转发～
