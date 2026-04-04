---
title: "RPG Maker 游戏文本批量翻译脚本"
slug: "translate-rpg-maker-games-with-script"
date: 2025-12-07T15:52:54+08:00
tags:
  - "python"
categories:
  - "programming"
description: "RPG Maker 游戏文本批量翻译脚本 RPG Maker 系列游戏的文本大多存储在 JSON 或 CSV 文件中，手动翻译效率极低。如果使用 MTool 进行挂载翻译不够优雅，优先考虑内嵌汉化（即直接替换原来的文本内容）。 本文将介绍如何用 Python 脚本批量翻译 RPG Maker 游戏文"
cover: "./1094870.webp"
---

# RPG Maker 游戏文本批量翻译脚本

RPG Maker 系列游戏的文本大多存储在 JSON 或 CSV 文件中，手动翻译效率极低。如果使用 MTool 进行挂载翻译不够优雅，优先考虑内嵌汉化（即直接替换原来的文本内容）。
本文将介绍如何用 Python 脚本批量翻译 RPG Maker 游戏文本，并分享实战经验和常见坑点。

## 1. 脚本功能简介

本脚本支持：
- 读取翻译字典（如 `translation.json`）（建议使用 MTool 生成，通常需要 MTool 挂载汉化的也自带翻译文件）
- 遍历原始数据文件夹（如 `data-jp`），批量翻译所有 JSON/CSV 文件
- 递归处理嵌套结构，智能替换所有文本
- 自动处理插件参数中的嵌套 JSON 字符串，避免转义错误
- 输出到新文件夹（如 `data-cn`），不破坏原始数据

> **💡 小贴士**
> - 建议先备份源文件，确认无误后再批量替换。

## 2. 脚本核心代码

👇👇👇

<details>
<summary>rpg游戏翻译文本替换.py（点击展开查看）</summary>
    
```python
import json
import csv
from pathlib import Path

# 配置
TRANSLATION_FILE = "translation.json"
DATA_DIR = "data-jp"
OUTPUT_DIR = "data-cn"


def load_translation(file_path):
    """加载翻译JSON文件。"""
    print(f"加载翻译文件: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载翻译文件出错: {e}")
        return {}


def build_lookup_table(translation_map):
    """
    构建查找表以加速子串替换。
    返回一个字典：字符 -> (key, value)元组列表，按key长度降序排列。
    """
    print("正在构建查找表...")
    lookup = {}
    for key, value in translation_map.items():
        if not key:
            continue
        first_char = key[0]
        if first_char not in lookup:
            lookup[first_char] = []
        lookup[first_char].append((key, value))

    # 每个列表按key长度降序排列，确保最长优先匹配
    for char in lookup:
        lookup[char].sort(key=lambda x: len(x[0]), reverse=True)

    return lookup


def translate_text(text, lookup_table):
    """
    使用查找表翻译文本。
    替换文本中出现的所有key。
    """
    if not isinstance(text, str):
        return text

    # 尝试解析嵌套的JSON字符串 (针对插件参数)
    try:
        stripped = text.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            parsed = json.loads(text)
            if isinstance(parsed, (dict, list)):

                def recursive_helper(obj):
                    if isinstance(obj, dict):
                        return {k: recursive_helper(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [recursive_helper(v) for v in obj]
                    elif isinstance(obj, str):
                        return translate_text(obj, lookup_table)
                    else:
                        return obj

                translated_parsed = recursive_helper(parsed)
                return json.dumps(
                    translated_parsed, ensure_ascii=False, separators=(",", ":")
                )
    except Exception:
        pass

    result = []
    i = 0
    n = len(text)

    while i < n:
        char = text[i]
        match = None

        if char in lookup_table:
            for key, value in lookup_table[char]:
                if text.startswith(key, i):
                    match = (key, value)
                    break

        if match:
            result.append(match[1])
            i += len(match[0])
        else:
            result.append(char)
            i += 1

    return "".join(result)


def process_json_file(file_path, output_path, lookup_table):
    """处理JSON文件。"""
    print(f"处理JSON文件: {file_path} -> {output_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        def recursive_translate(obj):
            if isinstance(obj, dict):
                return {k: recursive_translate(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [recursive_translate(v) for v in obj]
            elif isinstance(obj, str):
                return translate_text(obj, lookup_table)
            else:
                return obj

        translated_data = recursive_translate(data)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"处理JSON文件出错 {file_path}: {e}")


def process_csv_file(file_path, output_path, lookup_table):
    """处理CSV文件。"""
    print(f"处理CSV文件: {file_path} -> {output_path}")
    try:
        rows = []
        fieldnames = None

        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                rows.append(row)

        if not fieldnames:
            print(f"警告: 未找到字段 {file_path}")
            return

        translated_rows = []
        for row in rows:
            new_row = {}
            for k, v in row.items():
                if k == "Message":
                    new_row[k] = translate_text(v, lookup_table)
                else:
                    new_row[k] = v
            translated_rows.append(new_row)

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(translated_rows)

    except Exception as e:
        print(f"处理CSV文件出错 {file_path}: {e}")


def main():
    translation_file = Path(TRANSLATION_FILE)
    data_dir = Path(DATA_DIR)
    output_dir = Path(OUTPUT_DIR)

    if not translation_file.exists():
        print(f"未找到翻译文件: {translation_file}")
        return

    translation_map = load_translation(translation_file)
    if not translation_map:
        print("未找到任何翻译内容。")
        return

    lookup_table = build_lookup_table(translation_map)

    for file_path in data_dir.rglob("*"):
        if file_path.is_file():
            # 计算相对路径并构建输出路径
            relative_path = file_path.relative_to(data_dir)
            output_path = output_dir / relative_path

            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if file_path.suffix.lower() == ".json":
                process_json_file(file_path, output_path, lookup_table)
            elif file_path.suffix.lower() == ".csv":
                process_csv_file(file_path, output_path, lookup_table)


if __name__ == "__main__":
    main()

```
</details>
    
<details>
<summary>rpg游戏翻译文本替换2.0.py（提高替换速度、优化了多行匹配）（点击展开查看）</summary>
    
```python
import json
import csv
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field
from collections import OrderedDict

# 配置
TRANSLATION_FILE = "A翻译.json"
DATA_DIR = "www/data-jp"
OUTPUT_DIR = "www/data-cn"


@dataclass
class TranslationMatcher:
    """纯 Python 翻译匹配器：Trie 最长匹配 + 简单 LRU 缓存。

    - trie: 前缀树，按字符逐步匹配，避免每个位置遍历大量 key。
    - cache: 限制大小的 LRU，提升重复文本/重复行的翻译速度。
    """

    trie: dict
    cache_max: int = 50_000
    cache: "OrderedDict[str, str]" = field(default_factory=OrderedDict)

    def cache_get(self, key: str) -> str | None:
        val = self.cache.get(key)
        if val is not None:
            self.cache.move_to_end(key)
        return val

    def cache_put(self, key: str, val: str) -> None:
        self.cache[key] = val
        self.cache.move_to_end(key)
        if len(self.cache) > self.cache_max:
            self.cache.popitem(last=False)


def load_translation(file_path):
    """加载翻译JSON文件。"""
    print(f"加载翻译文件: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载翻译文件出错: {e}")
        return {}


def build_lookup_table(translation_map) -> TranslationMatcher:
    """构建匹配器（Trie + LRU），用于大文件的高速替换。"""
    print("正在构建查找表(Trie)...")

    trie: dict = {}
    terminal = "\0"  # 作为终止标记；正常文本中几乎不会出现

    for key, value in translation_map.items():
        if not key:
            continue

        node = trie
        for ch in key:
            node = node.setdefault(ch, {})
        node[terminal] = value

    # 把 terminal 标记也塞进 matcher 里（避免全局变量/闭包开销）
    matcher = TranslationMatcher(trie={"_root": trie, "_terminal": terminal})
    return matcher


def translate_text(text, lookup_table: TranslationMatcher):
    """
    使用查找表翻译文本。
    替换文本中出现的所有key。
    """
    if not isinstance(text, str):
        return text

    # LRU 命中直接返回
    cached = lookup_table.cache_get(text)
    if cached is not None:
        return cached

    # 尝试解析嵌套的JSON字符串 (针对插件参数)
    try:
        stripped = text.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            parsed = json.loads(text)
            if isinstance(parsed, (dict, list)):

                def recursive_helper(obj):
                    if isinstance(obj, dict):
                        return {k: recursive_helper(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [recursive_helper(v) for v in obj]
                    elif isinstance(obj, str):
                        return translate_text(obj, lookup_table)
                    else:
                        return obj

                translated_parsed = recursive_helper(parsed)
                return json.dumps(
                    translated_parsed, ensure_ascii=False, separators=(",", ":")
                )
    except Exception:
        pass

    root = lookup_table.trie["_root"]
    terminal = lookup_table.trie["_terminal"]

    result: list[str] = []
    i = 0
    n = len(text)

    while i < n:
        node = root
        j = i
        last_val: str | None = None
        last_j = i

        # Trie 向前走，记录“最长的终止匹配”
        while j < n:
            ch = text[j]
            nxt = node.get(ch)
            if nxt is None:
                break
            node = nxt
            j += 1
            val = node.get(terminal)
            if val is not None:
                last_val = val
                last_j = j

        if last_val is not None:
            result.append(last_val)
            i = last_j
        else:
            result.append(text[i])
            i += 1

    translated = "".join(result)
    lookup_table.cache_put(text, translated)
    return translated


def _is_event_command_dict(obj: Any) -> bool:
    return (
        isinstance(obj, dict)
        and "code" in obj
        and "indent" in obj
        and "parameters" in obj
        and isinstance(obj.get("code"), int)
        and isinstance(obj.get("indent"), int)
        and isinstance(obj.get("parameters"), list)
    )


def _process_event_command_list(commands: list[dict], lookup_table) -> list[dict]:
    """对RPG Maker事件命令列表做更贴近引擎的翻译处理。

    关键点：
    - Show Text: code=101 后面会跟若干 code=401 行，这些 401 共同组成一个多行文本。
      翻译表里经常用 "A\nB" 作为一个 key；若逐行翻译就无法命中。
    - Show Scrolling Text: code=105 后面会跟若干 code=405 行，同理。
    """

    def translate_any(value: Any) -> Any:
        if isinstance(value, str):
            return translate_text(value, lookup_table)
        if isinstance(value, list):
            return [translate_any(v) for v in value]
        if isinstance(value, dict):
            return {k: translate_any(v) for k, v in value.items()}
        return value

    out: list[dict] = []
    i = 0

    while i < len(commands):
        cmd = commands[i]
        if not _is_event_command_dict(cmd):
            out.append(cmd)
            i += 1
            continue

        code = cmd["code"]

        # 101: Show Text + 401 continuations
        if code == 101:
            out.append(
                {
                    "code": cmd["code"],
                    "indent": cmd.get("indent", 0),
                    "parameters": translate_any(cmd.get("parameters", [])),
                }
            )
            j = i + 1
            lines: list[str] = []
            indent_for_401 = cmd.get("indent", 0)
            while (
                j < len(commands)
                and _is_event_command_dict(commands[j])
                and commands[j]["code"] == 401
            ):
                if commands[j].get("parameters"):
                    lines.append(commands[j]["parameters"][0])
                else:
                    lines.append("")
                indent_for_401 = commands[j].get("indent", indent_for_401)
                j += 1

            if lines:
                combined = "\n".join(lines)
                translated = translate_text(combined, lookup_table)
                for line in translated.split("\n"):
                    out.append(
                        {"code": 401, "indent": indent_for_401, "parameters": [line]}
                    )

            i = j
            continue

        # 105: Show Scrolling Text + 405 continuations
        if code == 105:
            out.append(
                {
                    "code": cmd["code"],
                    "indent": cmd.get("indent", 0),
                    "parameters": translate_any(cmd.get("parameters", [])),
                }
            )
            j = i + 1
            lines: list[str] = []
            indent_for_405 = cmd.get("indent", 0)
            while (
                j < len(commands)
                and _is_event_command_dict(commands[j])
                and commands[j]["code"] == 405
            ):
                if commands[j].get("parameters"):
                    lines.append(commands[j]["parameters"][0])
                else:
                    lines.append("")
                indent_for_405 = commands[j].get("indent", indent_for_405)
                j += 1

            if lines:
                combined = "\n".join(lines)
                translated = translate_text(combined, lookup_table)
                for line in translated.split("\n"):
                    out.append(
                        {"code": 405, "indent": indent_for_405, "parameters": [line]}
                    )

            i = j
            continue

        # 其它事件命令：沿用旧行为，递归翻译 parameters 中的字符串
        out.append(
            {
                "code": cmd["code"],
                "indent": cmd.get("indent", 0),
                "parameters": translate_any(cmd.get("parameters", [])),
            }
        )
        i += 1

    return out


def process_json_file(file_path, output_path, lookup_table):
    """处理JSON文件。"""
    print(f"处理JSON文件: {file_path} -> {output_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        def recursive_translate(obj):
            if isinstance(obj, dict):
                # 事件页 / 公共事件等结构：{ ..., "list": [ {code, indent, parameters}, ... ] }
                if "list" in obj and isinstance(obj.get("list"), list) and obj["list"]:
                    list_val = obj["list"]
                    if all(_is_event_command_dict(x) for x in list_val):
                        new_obj = {
                            k: recursive_translate(v)
                            for k, v in obj.items()
                            if k != "list"
                        }
                        new_obj["list"] = _process_event_command_list(
                            list_val, lookup_table
                        )
                        return new_obj

                return {k: recursive_translate(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                # 兼容某些文件顶层就是事件命令数组
                if obj and all(_is_event_command_dict(x) for x in obj):
                    return _process_event_command_list(obj, lookup_table)
                return [recursive_translate(v) for v in obj]
            elif isinstance(obj, str):
                return translate_text(obj, lookup_table)
            else:
                return obj

        translated_data = recursive_translate(data)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"处理JSON文件出错 {file_path}: {e}")


def process_csv_file(file_path, output_path, lookup_table):
    """处理CSV文件。"""
    print(f"处理CSV文件: {file_path} -> {output_path}")
    try:
        rows = []
        fieldnames = None

        with open(file_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                rows.append(row)

        if not fieldnames:
            print(f"警告: 未找到字段 {file_path}")
            return

        translated_rows = []
        for row in rows:
            new_row = {}
            for k, v in row.items():
                if k == "Message":
                    new_row[k] = translate_text(v, lookup_table)
                else:
                    new_row[k] = v
            translated_rows.append(new_row)

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(translated_rows)

    except Exception as e:
        print(f"处理CSV文件出错 {file_path}: {e}")


def main():
    translation_file = Path(TRANSLATION_FILE)
    data_dir = Path(DATA_DIR)
    output_dir = Path(OUTPUT_DIR)

    if not translation_file.exists():
        print(f"未找到翻译文件: {translation_file}")
        return

    translation_map = load_translation(translation_file)
    if not translation_map:
        print("未找到任何翻译内容。")
        return

    lookup_table = build_lookup_table(translation_map)

    for file_path in data_dir.rglob("*"):
        if file_path.is_file():
            # 计算相对路径并构建输出路径
            relative_path = file_path.relative_to(data_dir)
            output_path = output_dir / relative_path

            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if file_path.suffix.lower() == ".json":
                process_json_file(file_path, output_path, lookup_table)
            elif file_path.suffix.lower() == ".csv":
                process_csv_file(file_path, output_path, lookup_table)


if __name__ == "__main__":
    main()
```
</details>

## 3. 使用方法

1. 准备好翻译字典（如 `translation.json`），格式为：
   ```json
   { "原文": "译文", ... }
   ```
2. 将原始游戏数据（如 `data-jp` 文件夹）和脚本放在同一目录
3. 运行脚本：
   ```bash
   python rpg游戏翻译文本替换.py
   ```
4. 翻译结果会输出到 `data-cn` 文件夹

## 4. 关键实现与注意事项

### 4.1 转义字符与嵌套 JSON

**插件参数、对话选项等常用嵌套 JSON 字符串存储。直接替换会破坏转义，导致游戏报错。**

- 脚本会自动检测字符串是否为 JSON，并递归翻译后重新序列化，保证所有引号、特殊字符都被正确转义。
- 这样可避免 `SyntaxError: Unexpected token ... in JSON` 等常见报错。

### 4.2 字体适配与显示问题

**中文字体未适配会导致游戏内文字粗细不一、乱码或显示异常。**
- 建议在 `data/System.json` 中将 `mainFontFilename`、`numberFontFilename` 设置为支持中文的字体（如 `NotoSansSC-VariableFont_wght.ttf`、`Microsoft YaHei` 等）。
- 可在 CSS 或 System.json 里设置 `fallbackFonts`。
- 若字体文件较大，注意 RPG Maker 对字体格式的兼容性（如 ttf/otf/woff）。

### 4.3 翻译字典的维护

**翻译字典建议用 MTool 导出，文本编辑器维护，注意避免重复、空 key。**

- 优先匹配最长 key，避免短词误替换。
- 可用正则或脚本辅助去重。

---

# 附录
    

![莉可的奇妙外卖任务-zh.png](./%E8%8E%89%E5%8F%AF%E7%9A%84%E5%A5%87%E5%A6%99%E5%A4%96%E5%8D%96%E4%BB%BB%E5%8A%A1-zh.webp)
    
如有疑问，欢迎留言交流！
