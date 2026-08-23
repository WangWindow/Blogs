---
slug: use-curl
title: 使用 curl
date: 2026-08-23T16:46:00+08:00
description: curl 是一个通用的网络请求客户端，支持 HTTP API、上传/下载、调试请求、认证、代理、多协议。功能十分强大，但是之前一般都是直接复制粘贴命令，没有仔细学习一下各个参数的具体含义，所以今天通过 GPT 帮我总结了一下
cover: ./curl.webp
categories:
  - tool
tags:
  - network
draft: false
sticky: false
---

## curl 与 wget 的比较

| 工具 | 类型 | 擅长 |
| --- | --- | --- |
| `curl` | 通用的网络请求客户端 | HTTP API、上传/下载、调试请求、认证、代理、多协议 |
| `wget` | 专门的下载器 | 下载文件、递归下载网站、断点续传、镜像站点 |

`curl` 的通用性主要体现在它不只是“下载文件”。例如：

```shell
# GET
curl https://example.com

# POST JSON
curl -X POST https://example.com/api \
  -H 'Content-Type: application/json' \
  -d '{"name":"test"}'

# 上传文件
curl -F 'file=@a.png' https://example.com/upload

# 带认证
curl -u user:password https://example.com

# SOCKS5 代理
curl --proxy socks5h://127.0.0.1:1080 https://example.com
```

日常使用上的差别：

```shell
wget https://example.com/a.zip
```

默认就会保存为 `a.zip`。

但是 curl 默认把文件内容**输出到终端**：

```shell
curl https://example.com/a.zip
```

需要：

```shell
# 按远程文件名保存
curl -O https://example.com/a.zip

# 手动指定保存位置
curl -o a.zip https://example.com/a.zip
```

<details> 
<summary> ⭐ curl 常用参数列表 ⭐ </summary>

| 参数 | 作用 | 示例 |
| --- | --- | --- |
| `-O` | 按远程文件名保存 | `curl -O https://example.com/a.zip` |
| `-o FILE` | 保存为指定文件名 | `curl -o app.zip URL` |
| `-L` | 跟随重定向 | `curl -L URL` |
| `-C -` | 断点续传 | `curl -C - -O URL` |
| `-s` | 静默，不显示进度 | `curl -s URL` |
| `-S` | 配合 `-s`，出错时仍显示错误 | `curl -sS URL` |
| `-f` | HTTP 4xx/5xx 时返回失败 | `curl -f URL` |
| `-I` | 只获取响应头 | `curl -I URL` |
| `-i` | 输出响应头 + 响应体 | `curl -i URL` |
| `-v` | 显示详细请求过程 | `curl -v URL` |
| `-X` | 指定 HTTP 方法 | `curl -X POST URL` |
| `-H` | 添加请求头 | `curl -H 'Authorization: Bearer xxx' URL` |
| `-d` | 发送请求数据 | `curl -d 'a=1&b=2' URL` |
| `--data-raw` | 原样发送数据 | `curl --data-raw '{"a":1}' URL` |
| `-F` | multipart/form-data，常用于上传文件 | `curl -F 'file=@a.png' URL` |
| `-u` | Basic Auth | `curl -u user:pass URL` |
| `-b` | 发送 Cookie | `curl -b 'token=abc' URL` |
| `-c` | 保存 Cookie | `curl -c cookies.txt URL` |
| `-A` | 指定 User-Agent | `curl -A 'Mozilla/5.0' URL` |
| `-e` | 指定 Referer | `curl -e 'https://google.com' URL` |
| `-x` / `--proxy` | 使用代理 | `curl -x http://127.0.0.1:7890 URL` |
| `--socks5` | SOCKS5 代理 | `curl --socks5 127.0.0.1:1080 URL` |
| `--socks5-hostname` | SOCKS5，DNS 也通过代理 | `curl --socks5-hostname 127.0.0.1:1080 URL` |
| `-k` | 忽略 HTTPS 证书错误 | `curl -k https://example.com` |
| `--connect-timeout` | 连接超时 | `curl --connect-timeout 5 URL` |
| `-m` | 整个请求最大时间 | `curl -m 30 URL` |
| `--retry` | 请求失败自动重试 | `curl --retry 5 URL` |
| `-w` | 输出请求统计信息 | \`curl -w '%{http_code}\n' URL\` |

</details>

## 下载功能说明

下载功能主要与 `-L` 参数有关，同时支持与一些其他参数组合使用。

通常使用：

```shell
curl -fsSL URL
```

因为如果服务器返回 `403`、`404`、`500`，`-f` 会让 curl 返回非 0 exit code。

<details>

- -f    HTTP 错误时失败
- -s    静默
- -S    静默模式下仍显示错误
- -L    跟随重定向
</details>

例如很多安装脚本都是：

```shell
curl -fsSL https://example.com/install.sh | sh
```

不过对于不熟悉的脚本，建议先查看：

```shell
curl -fsSL https://example.com/install.sh | less
```

确认内容后再执行。

> [!TIP]
> >
> 还支持断续传，添加 `-C` 参数以支持。

## 网络请求功能

主要与参数 `-X`、`-H`、`-d` 有关。

一下是个示例：

```shell
curl -X POST https://api.example.com/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alice","age":20}'
```

## 测试网络代理

通常完成环境变量设置后，使用：

```shell
export http_proxy=http://127.0.0.1:7890
export https_proxy=http://127.0.0.1:7890

curl https://www.google.com
```

如果正常获得输出，这说明网络代理配置工作正常。
