<div align="center">

# 🔄 CodeContext-Bridge

**Seamlessly migrate and sync project context across AI coding assistants**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-39%20passed-brightgreen.svg)]()

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Introduction

**CodeContext-Bridge** is a lightweight CLI tool that solves a real pain point for developers: **when switching between AI coding assistants (Claude Code, Codex, Cursor, GitHub Copilot, etc.), you have to re-explain your entire project structure every time.**

This tool automatically scans your project, creates a comprehensive context snapshot, and exports it in the exact format your favorite AI assistant understands — so you can pick up right where you left off, no matter which tool you're using.

**Key Differentiators:**
- 🚀 **Zero-config setup** — works out of the box with sensible defaults
- 🔐 **Privacy-first** — automatically redacts API keys, passwords, and secrets
- 📦 **Snapshot management** — save and compare project states over time
- 🎯 **Multi-format export** — native support for Claude, Codex, Cursor, and generic Markdown

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔍 **Smart Project Scanning** | Automatically detects project structure, dependencies, and key files while respecting `.gitignore` |
| 💾 **Context Snapshots** | Save compressed snapshots of your project context and compare changes between versions |
| 🔄 **Multi-Format Export** | Export to **Claude Code** (CLAUDE.md), **Codex CLI**, **Cursor** (.cursorrules), or generic Markdown |
| 🔐 **Privacy Protection** | Built-in redaction of API keys, passwords, tokens, and private keys |
| 🎨 **Beautiful CLI** | Rich terminal output with progress indicators and color-coded results |
| 📊 **Token Estimation** | Know exactly how much context you're sending to avoid hitting limits |

### 🚀 Quick Start

#### Requirements
- **Python** 3.9 or higher
- **pip** or **uv** for package management

#### Installation

```bash
# Using pip
pip install codecontext-bridge

# Using uv (recommended)
uv pip install codecontext-bridge

# Or install from source
git clone https://github.com/gitstq/CodeContext-Bridge.git
cd CodeContext-Bridge
pip install -e ".[dev]"
```

#### Basic Usage

```bash
# Scan your project and see its structure
ccb scan

# Export context for Claude Code
ccb export claude

# Export context for all supported formats at once
ccb export-all

# Create a snapshot for later comparison
ccb snapshot create --name "before-refactor"

# List all snapshots
ccb snapshot list

# Compare two snapshots
ccb snapshot diff --name "before-refactor" --compare "after-refactor"
```

### 📖 Detailed Usage Guide

#### Scanning a Project

```bash
# Scan current directory
ccb scan

# Scan a specific project
ccb scan /path/to/your/project

# Scan without redacting sensitive data
ccb scan --no-redact

# Limit file size to read
ccb scan --max-size 524288  # 512KB
```

#### Exporting Context

```bash
# Export for Claude Code (creates CLAUDE.md)
ccb export claude

# Export for OpenAI Codex CLI
ccb export codex

# Export for Cursor AI Editor (creates .cursorrules)
ccb export cursor

# Export as generic Markdown
ccb export generic

# Export to a specific directory
ccb export claude --output ./exports/

# Limit tokens in export
ccb export claude --max-tokens 50000

# Copy output to clipboard
ccb export claude --clipboard
```

#### Snapshot Management

```bash
# Create a snapshot
ccb snapshot create --name "v1.0"

# List all snapshots
ccb snapshot list

# Load a snapshot
ccb snapshot load --name "v1.0"

# Delete a snapshot
ccb snapshot delete --name "v1.0"

# Compare two snapshots
ccb snapshot diff --name "v1.0" --compare "v1.1"
```

#### Export All Formats at Once

```bash
# Export to all formats
ccb export-all

# Export all with custom output directory
ccb export-all --output ./context-exports/
```

### 💡 Design Philosophy & Roadmap

**Design Principles:**
1. **Developer-first** — every feature should save time, not add complexity
2. **Privacy by default** — sensitive data is redacted automatically, never sent to AI
3. **Tool agnostic** — support all major AI coding assistants, not just one
4. **Composable** — works as a standalone tool or integrated into CI/CD pipelines

**Technology Choices:**
- **Python 3.9+** for broad compatibility
- **Typer** for elegant CLI design with type hints
- **Rich** for beautiful terminal output
- **Pydantic** for robust data validation
- **GitPython** for repository metadata extraction

**Roadmap:**
- [ ] VS Code extension for one-click context export
- [ ] Support for more AI assistants (Windsurf, Continue, etc.)
- [ ] Incremental sync (only export changed files)
- [ ] Team sharing with encrypted context snapshots
- [ ] Web dashboard for visualizing project context

### 📦 Packaging & Deployment

This is a **Python CLI tool/library**. No executable packaging needed.

```bash
# Install from PyPI (when published)
pip install codecontext-bridge

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
ruff check src/
black src/
mypy src/
```

### 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository and create a feature branch
2. **Write tests** for new functionality
3. **Follow PEP 8** style guidelines
4. **Submit a PR** with a clear description

**Commit Convention:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test updates

### 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

**CodeContext-Bridge** 是一款轻量级 CLI 工具，专门解决开发者的真实痛点：**在切换 AI 编程助手（Claude Code、Codex、Cursor、GitHub Copilot 等）时，每次都要重新解释整个项目结构。**

本工具自动扫描您的项目，创建全面的上下文快照，并以您喜爱的 AI 助手能理解的精确格式导出——让您无论使用哪个工具，都能无缝衔接、继续工作。

**核心差异化亮点：**
- 🚀 **零配置开箱即用** — 合理的默认设置，无需繁琐配置
- 🔐 **隐私优先** — 自动脱敏 API 密钥、密码和机密信息
- 📦 **快照管理** — 保存并对比项目不同时间点的状态
- 🎯 **多格式导出** — 原生支持 Claude、Codex、Cursor 和通用 Markdown

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **智能项目扫描** | 自动检测项目结构、依赖关系和关键文件，同时尊重 `.gitignore` |
| 💾 **上下文快照** | 保存项目上下文的压缩快照，并对比不同版本间的变更 |
| 🔄 **多格式导出** | 导出为 **Claude Code** (CLAUDE.md)、**Codex CLI**、**Cursor** (.cursorrules) 或通用 Markdown |
| 🔐 **隐私保护** | 内置 API 密钥、密码、令牌和私钥的自动脱敏功能 |
| 🎨 **精美 CLI** | 带有进度指示器和彩色结果的丰富终端输出 |
| 📊 **Token 估算** | 精确了解发送的上下文量，避免超出限制 |

### 🚀 快速开始

#### 环境要求
- **Python** 3.9 或更高版本
- **pip** 或 **uv** 包管理器

#### 安装

```bash
# 使用 pip
pip install codecontext-bridge

# 使用 uv（推荐）
uv pip install codecontext-bridge

# 或从源码安装
git clone https://github.com/gitstq/CodeContext-Bridge.git
cd CodeContext-Bridge
pip install -e ".[dev]"
```

#### 基本用法

```bash
# 扫描项目并查看结构
ccb scan

# 导出 Claude Code 上下文
ccb export claude

# 一次性导出所有支持的格式
ccb export-all

# 创建快照供后续对比
ccb snapshot create --name "重构前"

# 列出所有快照
ccb snapshot list

# 对比两个快照
ccb snapshot diff --name "重构前" --compare "重构后"
```

### 📖 详细使用指南

#### 扫描项目

```bash
# 扫描当前目录
ccb scan

# 扫描指定项目
ccb scan /path/to/your/project

# 扫描时不脱敏敏感数据
ccb scan --no-redact

# 限制读取的文件大小
ccb scan --max-size 524288  # 512KB
```

#### 导出上下文

```bash
# 导出为 Claude Code 格式（创建 CLAUDE.md）
ccb export claude

# 导出为 OpenAI Codex CLI 格式
ccb export codex

# 导出为 Cursor AI 编辑器格式（创建 .cursorrules）
ccb export cursor

# 导出为通用 Markdown
ccb export generic

# 导出到指定目录
ccb export claude --output ./exports/

# 限制导出 token 数量
ccb export claude --max-tokens 50000

# 复制输出到剪贴板
ccb export claude --clipboard
```

#### 快照管理

```bash
# 创建快照
ccb snapshot create --name "v1.0"

# 列出所有快照
ccb snapshot list

# 加载快照
ccb snapshot load --name "v1.0"

# 删除快照
ccb snapshot delete --name "v1.0"

# 对比两个快照
ccb snapshot diff --name "v1.0" --compare "v1.1"
```

#### 一次性导出所有格式

```bash
# 导出所有格式
ccb export-all

# 导出到自定义目录
ccb export-all --output ./context-exports/
```

### 💡 设计思路与迭代规划

**设计原则：**
1. **开发者优先** — 每个功能都应该节省时间，而非增加复杂度
2. **默认隐私保护** — 敏感数据自动脱敏，绝不发送到 AI
3. **工具无关** — 支持所有主流 AI 编程助手，不局限于单一工具
4. **可组合** — 既可作为独立工具使用，也可集成到 CI/CD 流水线

**技术选型：**
- **Python 3.9+** — 广泛的兼容性
- **Typer** — 基于类型提示的优雅 CLI 设计
- **Rich** — 精美的终端输出
- **Pydantic** — 健壮的数据验证
- **GitPython** — 仓库元数据提取

**迭代计划：**
- [ ] VS Code 扩展，支持一键导出上下文
- [ ] 支持更多 AI 助手（Windsurf、Continue 等）
- [ ] 增量同步（仅导出变更文件）
- [ ] 团队共享，支持加密上下文快照
- [ ] Web 仪表板，可视化项目上下文

### 📦 打包与部署

这是一个 **Python CLI 工具/库**，无需打包为可执行文件。

```bash
# 从 PyPI 安装（发布时）
pip install codecontext-bridge

# 开发模式安装
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v

# 运行代码检查
ruff check src/
black src/
mypy src/
```

### 🤝 贡献指南

欢迎贡献！请遵循以下规范：

1. **Fork** 仓库并创建功能分支
2. 为新功能**编写测试**
3. 遵循 **PEP 8** 代码风格
4. 提交 **PR** 并附上清晰的描述

**提交规范：**
- `feat:` 新增功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试更新

### 📄 开源协议

本项目采用 [MIT 协议](LICENSE) 开源。

---

<a name="繁體中文"></a>
## 🇹🇼 繁體中文

### 🎉 專案介紹

**CodeContext-Bridge** 是一款輕量級 CLI 工具，專門解決開發者的真實痛點：**在切換 AI 編程助手（Claude Code、Codex、Cursor、GitHub Copilot 等）時，每次都要重新解釋整個專案結構。**

本工具自動掃描您的專案，創建全面的上下文快照，並以您喜愛的 AI 助手能理解的精確格式匯出——讓您無論使用哪個工具，都能無縫銜接、繼續工作。

**核心差異化亮點：**
- 🚀 **零配置開箱即用** — 合理的預設設定，無需繁瑣配置
- 🔐 **隱私優先** — 自動脫敏 API 金鑰、密碼和機密資訊
- 📦 **快照管理** — 儲存並對比專案不同時間點的狀態
- 🎯 **多格式匯出** — 原生支援 Claude、Codex、Cursor 和通用 Markdown

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **智慧專案掃描** | 自動檢測專案結構、依賴關係和關鍵檔案，同時尊重 `.gitignore` |
| 💾 **上下文快照** | 儲存專案上下文的壓縮快照，並對比不同版本間的變更 |
| 🔄 **多格式匯出** | 匯出為 **Claude Code** (CLAUDE.md)、**Codex CLI**、**Cursor** (.cursorrules) 或通用 Markdown |
| 🔐 **隱私保護** | 內建 API 金鑰、密碼、令牌和私鑰的自動脫敏功能 |
| 🎨 **精美 CLI** | 帶有進度指示器和彩色結果的豐富終端輸出 |
| 📊 **Token 估算** | 精確瞭解傳送的上下文量，避免超出限制 |

### 🚀 快速開始

#### 環境要求
- **Python** 3.9 或更高版本
- **pip** 或 **uv** 套件管理器

#### 安裝

```bash
# 使用 pip
pip install codecontext-bridge

# 使用 uv（推薦）
uv pip install codecontext-bridge

# 或從原始碼安裝
git clone https://github.com/gitstq/CodeContext-Bridge.git
cd CodeContext-Bridge
pip install -e ".[dev]"
```

#### 基本用法

```bash
# 掃描專案並檢視結構
ccb scan

# 匯出 Claude Code 上下文
ccb export claude

# 一次性匯出所有支援的格式
ccb export-all

# 建立快照供後續對比
ccb snapshot create --name "重構前"

# 列出所有快照
ccb snapshot list

# 對比兩個快照
ccb snapshot diff --name "重構前" --compare "重構後"
```

### 📖 詳細使用指南

#### 掃描專案

```bash
# 掃描目前目錄
ccb scan

# 掃描指定專案
ccb scan /path/to/your/project

# 掃描時不脫敏敏感資料
ccb scan --no-redact

# 限制讀取的檔案大小
ccb scan --max-size 524288  # 512KB
```

#### 匯出上下文

```bash
# 匯出為 Claude Code 格式（建立 CLAUDE.md）
ccb export claude

# 匯出為 OpenAI Codex CLI 格式
ccb export codex

# 匯出為 Cursor AI 編輯器格式（建立 .cursorrules）
ccb export cursor

# 匯出為通用 Markdown
ccb export generic

# 匯出到指定目錄
ccb export claude --output ./exports/

# 限制匯出 token 數量
ccb export claude --max-tokens 50000

# 複製輸出到剪貼簿
ccb export claude --clipboard
```

#### 快照管理

```bash
# 建立快照
ccb snapshot create --name "v1.0"

# 列出所有快照
ccb snapshot list

# 載入快照
ccb snapshot load --name "v1.0"

# 刪除快照
ccb snapshot delete --name "v1.0"

# 對比兩個快照
ccb snapshot diff --name "v1.0" --compare "v1.1"
```

#### 一次性匯出所有格式

```bash
# 匯出所有格式
ccb export-all

# 匯出到自訂目錄
ccb export-all --output ./context-exports/
```

### 💡 設計思路與迭代規劃

**設計原則：**
1. **開發者優先** — 每個功能都應該節省時間，而非增加複雜度
2. **預設隱私保護** — 敏感資料自動脫敏，絕不傳送到 AI
3. **工具無關** — 支援所有主流 AI 編程助手，不侷限於單一工具
4. **可組合** — 既可作為獨立工具使用，也可整合到 CI/CD 流水線

**技術選型：**
- **Python 3.9+** — 廣泛的相容性
- **Typer** — 基於型別提示的優雅 CLI 設計
- **Rich** — 精美的終端輸出
- **Pydantic** — 健壯的資料驗證
- **GitPython** — 倉庫元資料提取

**迭代計劃：**
- [ ] VS Code 擴充套件，支援一鍵匯出上下文
- [ ] 支援更多 AI 助手（Windsurf、Continue 等）
- [ ] 增量同步（僅匯出變更檔案）
- [ ] 團隊共享，支援加密上下文快照
- [ ] Web 儀表板，視覺化專案上下文

### 📦 打包與部署

這是一個 **Python CLI 工具/庫**，無需打包為可執行檔案。

```bash
# 從 PyPI 安裝（發布時）
pip install codecontext-bridge

# 開發模式安裝
pip install -e ".[dev]"

# 執行測試
pytest tests/ -v

# 執行程式碼檢查
ruff check src/
black src/
mypy src/
```

### 🤝 貢獻指南

歡迎貢獻！請遵循以下規範：

1. **Fork** 倉庫並建立功能分支
2. 為新功能**編寫測試**
3. 遵循 **PEP 8** 程式碼風格
4. 提交 **PR** 並附上清晰的描述

**提交規範：**
- `feat:` 新增功能
- `fix:` 修復問題
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `test:` 測試更新

### 📄 開源協議

本專案採用 [MIT 協議](LICENSE) 開源。
