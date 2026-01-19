# LocalMind 技术指南
## 版本 1.2.0

---

**将音频转化为智能**

专业级转录，配备AI驱动的质量分析。
100%离线。零成本。完全隐私。

---

## 目录

1. [简介](#简介)
2. [系统要求](#系统要求)
3. [安装和首次启动](#安装和首次启动)
4. [A部分：转录（语音转文字）](#a部分-转录)
5. [B部分：LLM质量分析](#b部分-llm质量分析)
6. [导出选项](#导出选项)
7. [设置参考](#设置参考)
8. [故障排除](#故障排除)
9. [隐私和安全](#隐私和安全)

---

## 简介

LocalMind是一个执行两项独立AI任务的桌面应用程序：

| 任务 | 技术 | 目的 |
|------|------|------|
| **转录** | OpenAI Whisper | 将语音转换为文字 |
| **质量分析** | 本地/云端LLM | 评分和分析对话 |

这些是**独立的系统**，可以协同工作，也可以独立使用。

---

## 系统要求

### 最低要求

| 组件 | 要求 |
|------|------|
| 操作系统 | macOS 12 (Monterey) 或更高 |
| 内存 | 8 GB |
| 存储 | 10 GB 可用空间 |
| 处理器 | Intel 或 Apple Silicon |

### 推荐要求

| 组件 | 要求 |
|------|------|
| 操作系统 | macOS 14 (Sonoma) 或更高 |
| 内存 | 16 GB 或更多 |
| 存储 | 20 GB 可用空间 |
| 处理器 | Apple M1/M2/M3 芯片 |

### 首次下载

| 模型类型 | 大小 | 下载时机 |
|---------|------|---------|
| Whisper（转录） | 约1.5 GB | 首次转录时 |
| 本地LLM（分析） | 约4 GB | 首次质量分析时 |

**仅初始模型下载需要互联网连接。**

---

## 安装和首次启动

### 步骤1：下载

从以下位置下载 `LocalMind-1.2.0-macOS.dmg`：
[github.com/KaivalyaDeepTeam/LocalMind/releases](https://github.com/KaivalyaDeepTeam/LocalMind/releases)

### 步骤2：安装

1. 打开下载的DMG文件
2. 将LocalMind拖到应用程序文件夹
3. 弹出DMG

### 步骤3：首次启动

**重要：** macOS可能会阻止该应用，因为它不是来自App Store。

**打开LocalMind：**

1. 右键点击LocalMind.app
2. 从菜单选择"打开"
3. 在安全对话框中点击"打开"

---

# A部分：转录（语音转文字）

本部分介绍使用OpenAI的Whisper技术进行**音频到文字的转换**。

---

## 什么是转录？

转录将音频文件中的口语转换为书面文字。LocalMind使用**OpenAI Whisper**。

### 工作原理

```
Audio File → Whisper AI → Written Transcript
   (MP3)       (Local)        (Text)
```

### 主要功能

- 支持**50多种语言**
- **自动语言检测**
- **说话人识别**（分离化）
- 每个片段的**时间戳**
- 模型下载后**完全离线工作**

### 支持的音频格式

| 格式 | 扩展名 | 描述 |
|------|--------|------|
| MP3 | .mp3 | 最常见的格式 |
| WAV | .wav | 未压缩，高质量 |
| M4A | .m4a | Apple/iTunes格式 |
| FLAC | .flac | 无损压缩 |
| OGG | .ogg | 开源格式 |
| WebM | .webm | 网络音频格式 |

**最大文件大小：** 每个文件2 GB

---

## Whisper模型说明

| 模型 | 大小 | 精度 | 速度 | 最适合 |
|------|------|------|------|--------|
| **Large V3** | 1.5 GB | 97-99% | 慢 | 专业使用 |
| **Medium** | 750 MB | 95-97% | 中等 | 日常使用 |
| **Small** | 250 MB | 92-95% | 快 | 快速转录 |
| **Base** | 150 MB | 88-92% | 很快 | 测试 |
| **Tiny** | 75 MB | 80-88% | 最快 | 实时 |

---

## 转录语言支持

**欧洲语言：** English, Spanish, French, German, Italian, Portuguese, Dutch, Polish, Russian, Ukrainian

**亚洲语言：** Chinese (Mandarin), Japanese, Korean, Hindi, Bengali, Tamil, Telugu, Thai, Vietnamese

**中东语言：** Arabic, Hebrew, Turkish, Persian, Urdu

**还有更多...**

---

# B部分：LLM质量分析

本部分介绍使用大型语言模型进行的**AI驱动的对话分析**。

---

## 什么是LLM分析？

LLM分析读取您的转录并评估对话质量。它提供：

- **总体评分**（0-100%）
- **参数评分**（可自定义的标准）
- 在对话中识别的**优势**
- **改进领域**
- 每个参数的**详细反馈**

### 与转录的主要区别

| 方面 | 转录 | LLM分析 |
|------|------|---------|
| **输入** | 音频文件 | 文字转录 |
| **输出** | 书面文字 | 评分和反馈 |
| **技术** | Whisper | LLM (Phi/Qwen/GPT) |
| **目的** | 转换语音 | 评估质量 |
| **必需？** | 是 | 可选 |

---

## LLM提供商选项

### 1. 本地LLM（推荐）

| 优点 | 缺点 |
|------|------|
| 100%免费 | 比云端慢 |
| 完全隐私 | 需要8GB以上内存 |
| 不需要互联网 | 大型模型下载 |

### 2. OpenAI API

| 优点 | 缺点 |
|------|------|
| 非常快 | 需要付费 |
| 高质量 | 需要互联网 |

### 3. Anthropic API

| 优点 | 缺点 |
|------|------|
| 出色的推理 | 需要付费 |
| 适合分析 | 需要互联网 |

---

## 本地LLM模型

| 模型 | 大小 | 速度 | 质量 | 最适合 |
|------|------|------|------|--------|
| **Phi-3.5 Mini** | 2.4 GB | 快 | 良好 | 默认 |
| **Qwen 2.5 3B** | 2.0 GB | 很快 | 良好 | 快速分析 |
| **Qwen 2.5 7B** | 4.4 GB | 中等 | 优秀 | 专业使用 |
| **Mistral 7B** | 4.1 GB | 中等 | 优秀 | 详细反馈 |
| **Gemma 2 2B** | 1.6 GB | 最快 | 中等 | 速度优先 |

---

## 质量评分参数

| 参数 | 权重 | 测量内容 |
|------|------|----------|
| Greeting & Introduction | 1.0x | 专业开场 |
| Active Listening | 1.0x | 注意力和参与度 |
| Problem Identification | 1.0x | 问题理解 |
| Solution Provided | 1.0x | 有用的解决方案 |
| Product Knowledge | 1.0x | 信息准确性 |
| Communication Clarity | 1.0x | 清晰的解释 |
| Empathy & Rapport | 1.0x | 情感联系 |
| Call Control | 1.0x | 流程管理 |
| Call Closing | 1.0x | 专业结束 |
| Script Compliance | 1.0x | 遵循指南 |

---

## 导出选项

| 格式 | 快捷键 | 最适合 |
|------|--------|--------|
| **PDF** | Cmd + Shift + P | 管理层、客户 |
| **Markdown** | Cmd + Shift + M | 快速分享 |
| **JSON** | Cmd + Shift + J | 系统集成 |
| **Text** | Cmd + Shift + T | 简单存档 |

---

## 隐私和安全

### 数据处理

| 模式 | 音频数据 | 转录文本 |
|------|----------|----------|
| **Local LLM** | 保留在设备上 | 保留在设备上 |
| **OpenAI API** | 保留在设备上 | 发送到OpenAI |
| **Anthropic API** | 保留在设备上 | 发送到Anthropic |

**您的音频文件永远不会上传到云端。**

### LocalMind收集什么

**什么都不收集。**

- 无遥测
- 无分析
- 无崩溃报告
- 无需账户

---

## 键盘快捷键

| 操作 | 快捷键 |
|------|--------|
| 打开文件 | Cmd + O |
| 开始处理 | Cmd + Return |
| 停止 | Escape |
| 导出PDF | Cmd + Shift + P |
| 导出Markdown | Cmd + Shift + M |
| 导出JSON | Cmd + Shift + J |
| 导出转录 | Cmd + Shift + T |
| 评分参数 | Cmd + Shift + S |
| 设置 | Cmd + , |
| 退出 | Cmd + Q |

---

## 获取帮助

- **文档：** [github.com/KaivalyaDeepTeam/LocalMind](https://github.com/KaivalyaDeepTeam/LocalMind)
- **问题：** [github.com/KaivalyaDeepTeam/LocalMind/issues](https://github.com/KaivalyaDeepTeam/LocalMind/issues)

---

**版本：** 1.2.0
**最后更新：** 2026年1月
**许可证：** MIT

© 2026 LocalMind Team. 为所有重视隐私的人精心打造。
