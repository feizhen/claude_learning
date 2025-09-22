# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# 沟通规范

- **语言要求**：使用英文思考，但是使用中文表达。

## 项目概述

这是一个基于 Claude Code 自定义命令框架构建的**个人学习和日记系统**。项目通过自动化的 markdown 文件生成和组织，为日常学习、笔记记录和反思提供结构化方法。

## 核心工作流程

### 自定义命令系统

项目包含六个核心自定义命令（位于 `.claude/commands/`）：

- **`/week-start`**: 创建周文件夹结构 (`weeks/YYYY_MMDD-MMDD/`)
- **`/daily-start`**: 创建每日日记文件，包含预设模板
- **`/daily-review`**: 添加每日总结部分（可配合 AI 分析）
- **`/week-review`**: 汇总整周内容，生成周度回顾
- **`/milestone`**: 生成学习进度和习惯分析报告
- **`/git-push`**: 自动化 git 提交和推送流程

### 推荐工作流程

```
/week-start → /daily-start → [日常记录] → /daily-review → /week-review
```

## 文件结构与命名规范

### 目录组织

- **`weeks/`**: 所有日记按周组织
- **`weeks/YYYY_MMDD-MMDD/`**: 周文件夹，MMDD 表示该周的周一和周日日期
- **日记文件**: `YYYY_MM_DD.md` 格式
- **周总结**: `week_review.md`

### 日记模板结构

每个日记文件包含以下标准化部分：

```markdown
# MMDD Journal

## video

[学习视频/教程内容]

## newsletter

[文章阅读/新闻通讯]

## braindump

[想法、思考、随记]

## output

[学习输出内容/项目成果]

## review

[每日总结 - 由 /daily-review 命令添加]
```

## 日期处理注意事项

**重要**: 所有自定义命令都使用 macOS BSD 风格的 `date` 命令。如果遇到中文日期格式问题，确保在脚本中设置：

```bash
export LC_ALL=C
```

## 开发和维护

### 修改自定义命令

1. 编辑 `.claude/commands/` 中的相应 `.md` 文件
2. 修改其中的 bash 脚本部分
3. 命令会自动在 Claude Code 中生效

### 内容聚合逻辑

- **周总结** 自动提取每日文件中各部分内容
- 使用正则表达式和 `sed` 命令解析 markdown 部分
- 支持多日内容的结构化汇总

### 文件管理

- 系统自动处理文件创建和组织
- 不需要手动管理目录结构
- 所有内容以纯 markdown 格式存储，确保长期可访问性

## 架构特点

- **自动化**: 最少的手动文件管理
- **结构化**: 一致的组织和模板
- **反思驱动**: 内置回顾和总结流程
- **AI 集成**: 利用 Claude 进行内容分析
- **可移植性**: 纯 markdown 文件格式

## 关键文件说明

### 学习规划文件
- **`objective.md`**: 详细的12个月学习计划和阶段性目标
- **`milestone.md`**: 学习进度跟踪和习惯分析报告

### 常用操作

#### 开始新的学习周期
```bash
/week-start    # 创建周文件夹
/daily-start   # 创建今日日记
```

#### 每日维护流程
```bash
/daily-review  # 添加每日总结
/git-push      # 提交更改（如需要）
```

#### 周期性回顾
```bash
/week-review   # 创建周总结
/milestone     # 生成学习进度报告
```

### 版本控制集成

项目支持自动 Git 操作：
- 使用 `/git-push` 命令自动提交和推送更改
- 所有学习文件都应纳入版本控制以便追踪进度
- 建议定期备份到远程仓库
