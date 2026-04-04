---
title: "记一次 Arch Linux 下声音调整“左右漂移”的修复指南"
slug: "strange-sound-problem-in-archlinux-matebooke"
date: 2026-03-19T21:32:00+08:00
tags:
  - "settings"
categories:
  - "linux"
description: "最近在使用 Arch Linux 时遇到了一个非常诡异的音频问题。如果你也使用的是搭载 4 扬声器阵列的轻薄本（比如华为等基于 Intel 11代 Tiger Lake 平台的机型），并且遇到类似症状，这篇记录或许能帮你彻底跳出泥坑"
---

# 记一次 Arch Linux 下声音调整“左右漂移”的修复指南

最近在使用 Arch Linux 时遇到了一个非常诡异的音频问题。如果你也使用的是搭载 4 扬声器阵列的轻薄本（比如华为等基于 Intel 11代 Tiger Lake 平台的机型），并且遇到类似症状，这篇记录或许能帮你彻底跳出泥坑。

## 🐛 诡异的症状表现

1. **音量变化问题：** 系统音量开到 100%，听起来跟开了 20% 左右时音量大小无明显增大。
2. **声场撕裂（左右漂移）：** 增大系统音量时，感觉声音是从右到左发生变化的，就像是有两个扬声器，增大音量实际上是新开了一个左扬声器，整体听感极其撕裂，只是稍微“立体”了一点。

**我的运行环境：**
* **Hardware** Huawei MateBook E 2022
* **OS:** Arch Linux x86_64
* **DE:** GNOME (Wayland)
* **Audio Server:** PipeWire + WirePlumber
* **CPU:** Intel 11th Gen i5-1130G7 (Tiger Lake-LP)
* **Audio Codec:** Conexant CX11970 (Smart Sound Technology)

---

## 🕵️ 排错踩坑记录（What didn't work）

为了揪出这个“幽灵扬声器”，我尝试了几个常见的修复方向，但都以失败告终：

1. **引脚重新映射 (Jack Retasking)：** 怀疑是 Linux 内核丢失了右侧和低音扬声器的引脚定义。使用 `hdajackretask` 工具强制覆盖 `0x17` 引脚为内部扬声器并写入启动引导，重启后毫无改善。
2. **强制回退传统 HDA 驱动：** 既然 Intel 最新的 SOF (Sound Open Firmware) 驱动搞不定 4 扬声器拓扑，我尝试通过写入 `options snd-intel-dspcfg dsp_driver=1` 强制内核使用传统的 Legacy HDA 驱动。**结果：** 扬声器问题没解决，反而导致依赖 SOF 驱动的内置阵列麦克风直接罢工消失。此路不通。

---

## 💡 真正的病因 (Root Cause)

经过反复测试，最终定位了问题核心：**PipeWire 的硬件混音器控制逻辑与 Conexant 多扬声器阵列的底层 dB（分贝）缩放不匹配。**

当我们拖动 GNOME 的系统音量条时，WirePlumber 试图直接去拉动底层硬件（ALSA）的多个滑块（`Speaker` 和 `Bass Speaker`）。但由于驱动对分贝值的理解有误，导致它拉动高音和低音滑块的比例彻底错乱——左声道的信号大得快，右声道和低音的信号大得慢，从而产生了“声音从右往左跑”的撕裂感。同时，因为这种错乱的控制，硬件真实的输出功率根本没有被推满，导致最大音量极其微小。

---

## 🛠️ 终极解决方案：开启全局软混音并拉满底层硬件音量

既然让系统去控制硬件滑块会导致错乱，我们的终极方案就是：**没收 WirePlumber 控制底层硬件音量的权力，强制硬件保持满功率输出，完全由软件层来均匀地放大或缩小总音量。**

### 第一步：创建 WirePlumber 全局软混音配置

打开终端，在系统目录下创建 WirePlumber 的配置文件：

```bash
# 创建配置目录
sudo mkdir -p /etc/wireplumber/wireplumber.conf.d/

# 编辑配置文件
sudo nano /etc/wireplumber/wireplumber.conf.d/50-alsa-soft-mixer.conf
```

将以下 JSON 配置完整粘贴进去并保存：

```json
monitor.alsa.rules = [
  {
    matches = [
      {
        device.name = "~alsa_card.*"
      }
    ]
    actions = {
      update-props = {
        api.alsa.soft-mixer = true
        api.alsa.ignore-dB = true
      }
    }
  }
]
```
*这行配置的作用是让所有的 ALSA 声卡都使用软件混音，并忽略硬件自身的 dB 缩放。*

### 第二步：重启系统

保存配置后，重启电脑让 WirePlumber 加载新规则：

```bash
reboot
```

### 第三步：使用 alsamixer 将 Speaker 和 Bass 硬件音量推至最大

重启进入系统后，我们需要去底层把所有喇叭的“水龙头”彻底拧到最大：

1. 打开终端，运行 `alsamixer`。
2. 按 `F6` 选择你的真实声卡（例如 `sof-hda-dsp` 或 `Tiger Lake` 相关的选项）。
3. **关键操作：** 使用左右方向键选中 **Speaker**（高音）和 **Bass Speaker**（低音），然后用向上方向键将它们的音量柱 **全部推到最高（显示为 100 / 00）**。同时也确保 **Master** 处于最大值。
4. 如果柱子底部显示 `MM`（静音状态），选中它并按键盘上的 **`M`** 键解除静音（变成绿色的 `00`）。
5. 按 `Esc` 退出。

### 第四步：持久化保存 ALSA 最大音量状态

为了防止下次开机时底层音量又掉下去恢复到之前极小的状态，**必须**执行以下命令，将刚才设置的最大满功率状态永久保存：

```bash
sudo alsactl store
```

## 🎉 最终结果

此时再次拖动 GNOME 右上角的系统音量条，声音的变大变小变得极其平滑。那个“从右往左跑”的幽灵结像彻底消失了，4 个扬声器正常协同工作！
