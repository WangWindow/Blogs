---
title: "从网页自动提取题库"
date: 2025-11-21T15:02:32+08:00
tags:
  - "python"
categories:
  - "programming"
description: "从网页自动提取「形势与政策」题库 摘要：本文分享一个高效提取“形势与政策”在线自测题库的方法——通过保存网页为HTML文件，再用Python脚本自动解析题目、选项与正确答案，最终生成整洁的文本题库。适用于学生复习、资料整理或二次开发。 背景 “形势与政策”是高校思想政治教育的重要组成部分，许多学校通"
cover: "./0072Vf1pgy1foxliaky92j31kw0w0b16.webp"
---

# 从网页自动提取「形势与政策」题库

> **摘要**：本文分享一个高效提取“形势与政策”在线自测题库的方法——通过保存网页为HTML文件，再用Python脚本自动解析题目、选项与正确答案，最终生成整洁的文本题库。适用于学生复习、资料整理或二次开发。

## 背景

“形势与政策”是高校思想政治教育的重要组成部分，许多学校通过在线学习平台（如超星、智慧树等）布置自测任务。这些平台通常会在提交后显示所有题目的正确答案，但**不提供导出功能**。手动搜题费时费力，还容易出错。

有没有办法自动化这一过程？答案是肯定的！

本文将手把手教你：
1. 如何保存包含题目的网页；
2. 如何用一段Python脚本自动提取题目和答案；
3. 脚本原理与关键代码解析。


> 🔧 **环境要求**：Python 3.x，无需额外安装库。


---

## 第一步：保存网页为HTML文件

1. 进入课程的“自测”界面；
2. 创建一套自测题并**直接提交**（无需答题）；
3. 提交后页面会显示所有题目及正确答案；
4. 在浏览器中按下 `Ctrl + S`（Windows）或 `Cmd + S`（Mac），将页面**保存为完整网页**（即 `xxxx.html` 的 html 文件）；
5. 确保保存的是包含题目的完整HTML，而非仅链接。

> 💡提示：部分平台可能有反爬机制，若无法正常保存，可尝试使用浏览器开发者工具（F12）复制 `<body>` 内容，手动构建HTML文件。

---

## 第二步：运行Python脚本提取题库

将以下代码保存为 `extract.py`，与 `查看详情.html` 放在同一目录下，运行即可生成 `形势与政策7.txt` 文件。

```python
import re
import html
import os

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)          # 去除HTML标签
    text = html.unescape(text)                   # 解码HTML实体（如 &nbsp;）
    text = re.sub(r"\s+", " ", text).strip()     # 合并多余空白
    return text

def main():
    input_file = "查看详情.html"
    output_file = "形势与政策7.txt"

    if not os.path.exists(input_file):
        print(f"错误：未找到文件 {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 定位主容器（含所有题目的区域）
    start_match = re.search(r'<div[^>]*id="fanyaMarking"[^>]*>', content)
    if start_match:
        content = content[start_match.start():]
    else:
        print("警告：未找到主容器 'fanyaMarking'，将处理整个文件。")

    # 按题型标题分割（如“单选题”、“多选题”）
    parts = re.split(r'(<h2[^>]*class="type_tit"[^>]*>.*?</h2>)', content, flags=re.S)

    results = []
    for part in parts:
        if not part.strip():
            continue

        # 如果是题型标题
        if 'type_tit' in part:
            header = clean_text(part)
            results.append(f"\n{header}\n")
        else:
            # 分割每一道题
            questions = re.split(r'<div class="marBom60 questionLi', part)
            for q_block in questions:
                if "<h3" not in q_block:  # 跳过无效块
                    continue

                # 提取题目
                q_match = re.search(r"<h3[^>]*>(.*?)</h3>", q_block, re.S)
                if not q_match:
                    continue
                q_text = clean_text(q_match.group(1))

                # 提取选项
                options = ""
                ul_match = re.search(r'<ul[^>]*class="mark_letter colorDeep qtDetail"[^>]*>(.*?)</ul>', q_block, re.S)
                if ul_match:
                    lis = re.findall(r"<li[^>]*>(.*?)</li>", ul_match.group(1), re.S)
                    for li in lis:
                        options += clean_text(li) + "\n"

                # 提取正确答案
                ans_match = re.search(r'<span[^>]*class="rightAnswerContent"[^>]*>(.*?)</span>', q_block, re.S)
                answer = clean_text(ans_match.group(1)) if ans_match else ""

                # 格式化输出
                results.append(f"{q_text}\n{options}答案：{answer}\n")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(results))

    print(f"✅ 提取完成！题库已保存至：{output_file}")

if __name__ == "__main__":
    main()
```

### 运行效果示例

生成的 `形势与政策7.txt` 内容如下：

```
一. 单选题（共 223 题）

1. (单选题)“十四五”时期，我们坚持以人民为中心的发展思想，在高质 量发展中持续加大民生投入，着力解决人民群众急难愁盼问题，不断书写温暖人心的民生答卷。下列关于我国民生福祉的说法错误的是（ ）。
A. 实施重大专项支持一批托育综合服务中心、公办托育机构和普 惠性托位建设
B. 全国城镇新增就业人口连续 4 年保持在 1200 万人以上
C. 全国劳动年龄人口平均受教育年限从 2020 年的 10.8 年提升至 2024 年的 11.3 年，已超过高收入国家水平
D. 国产创新药数量和质量齐升，国产创新药获批上市数量是 “十三五”时期的 2.8 倍
答案：C

2. (单选题)2024年10月16日，习近平总书记给中国国际大学生创新大赛（2024）总决赛参赛学生代表回信，充分肯定大赛在促进学生创新实践、增进中外青年友谊方面的重要作用，勉励广大青年学生要弘扬科学精神，积极投身科技创新，为促进中外科技交流、推动科技进步贡献青春力量。中国国际大学生创新大赛质量再创新高，凸显人才培养模式向（）转变。
A. “政治素养培养为先”
B. “道德素养培养为先”
C. “能力素质培养为先”
D. “知识素养培养为先”
答案：C
。。。。

二. 多选题（共 182 题）

1. (多选题)市场是最稀缺的资源，无论国际风云如何变幻，（）、（）、（）、（）的国内市场始终是我们应对各种风险挑战的有力保障。
A. 规模庞大
B. 层次多样
C. 外向依存
D. 潜力巨大
E. 统一开放
答案：ABDE

2. (多选题)2025年4月29日，习近平总书记在上海考察时强调，“发展人工只能前景广阔，要加强（）和（）。
A. 政策支持
B. 技术支持
C. 资金支持
D. 人才培养
E. 队伍建设
答案：AD
。。。。

三. 判断题（共 95 题）

1. (判断题)今年3月22日是第三十三届“世界水日”。
A. 对
B. 错
答案：对

2. (判断题)七七事变是全民族抗战的开始。
A. 对
B. 错
答案：对
。。。。
```

---

## 技术解析：脚本是如何工作的？

1. **HTML清洗**：`clean_text()` 函数去除标签、解码特殊字符、清理空格，确保文本干净；
2. **定位内容区域**：通过 `id="fanyaMarking"` 找到题目所在的主容器，避免处理无关内容；
3. **按题型分组**：利用 `<h2 class="type_tit">` 分割“单选题”“多选题”等板块；
4. **逐题解析**：
   - 题目在 `<h3>` 标签内；
   - 选项在 `<ul class="mark_letter ...">` 的 `<li>` 中；
   - 正确答案在 `<span class="rightAnswerContent">` 中；
5. **结构化输出**：按人类可读格式组织题目、选项与答案。

---

## 注意事项与扩展建议

- **平台差异**：不同学校的平台HTML结构可能略有不同，若脚本失效，可检查类名（如 `questionLi`、`rightAnswerContent`）是否变化，并相应调整正则表达式。
- **尊重版权**：提取内容仅限个人学习使用，请勿用于商业传播。

---

## 结语

通过简单的网页保存 + Python正则解析，我们就能将封闭的在线题库转化为开放、可编辑的文本资源。这不仅提升了学习效率，也体现了“用技术解决实际问题”的乐趣。

如果你觉得这个脚本有用，欢迎收藏、转发，或在评论区分享你的改进版本！

---
