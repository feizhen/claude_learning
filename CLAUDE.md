# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# 沟通规范

- **语言要求**：使用英文思考，但是使用中文表达。

## 项目概述

这是一个基于 Claude Code 自定义命令框架构建的**个人学习和日记系统**。项目通过自动化的 markdown 文件生成和组织，为日常学习、笔记记录和反思提供结构化方法。

## 常用命令

### 核心学习流程
```bash
/week-start    # 创建周文件夹结构
/daily-start   # 创建每日日记文件
/daily-review  # 添加每日总结
/week-review   # 生成周度回顾
```

### 分析和报告
```bash
/milestone     # 生成学习进度和习惯分析报告
/insight       # 生成社交媒体创作内容建议
```

### 版本控制
```bash
/git-push      # 自动化 git 提交和推送
```

## 自定义命令系统

项目包含八个核心自定义命令（位于 `.claude/commands/`）：

- **`/week-start`**: 创建周文件夹结构 (`weeks/YYYY_MMDD-MMDD/`)
- **`/daily-start`**: 创建每日日记文件，包含预设模板
- **`/daily-review`**: 添加每日总结部分（可配合 AI 分析）
- **`/week-review`**: 汇总整周内容，生成周度回顾
- **`/milestone`**: 生成学习进度和习惯分析报告
- **`/insight`**: 从学习记录中提取灵感，生成社交媒体创作内容建议
- **`/newsletter-fetch`**: 获取和整理新闻通讯内容
- **`/git-push`**: 自动化 git 提交和推送流程

### 推荐工作流程

```
/week-start → /daily-start → [日常记录] → /daily-review → /week-review
```

### 周期性分析工作流程

```
每周: /week-review → /insight
每月: /milestone
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

### 命令实现架构

每个自定义命令都是一个独立的 markdown 文件，包含：
- **命令描述**：功能说明和用途
- **Bash 脚本实现**：包装在 markdown 代码块中
- **参数处理**：支持各种命令行选项

**关键设计模式**：
- 所有命令使用 BSD 风格的 `date` 命令（macOS 兼容）
- 错误处理和用户反馈机制
- 临时文件管理和清理
- 内容聚合使用 `sed` 和正则表达式解析 markdown

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
/insight       # 生成社交媒体创作灵感报告
```

## 内容解析架构

### Markdown 内容分区

系统通过特定的 markdown 标题来组织内容：

```markdown
## video     - 学习视频/教程内容
## newsletter - 文章阅读/新闻通讯
## braindump - 想法、思考、随记
## output    - 学习输出内容/项目成果
## review    - 每日总结
```

### 内容聚合机制

命令使用以下技术栈进行内容处理：
- **`sed`** 用于提取特定 markdown 部分
- **`grep`** 用于内容搜索和过滤
- **正则表达式** 用于解析和匹配模式
- **临时文件** 用于中间数据处理

### 内容创作支持

#### `/insight` 命令详解

**功能**: 从学习记录中提取灵感，分析内容价值，生成适用于社交媒体创作的内容建议。

**核心特性**:
- 🔍 智能内容分析 - 自动识别高价值内容片段和深度思考
- 🏷️ 关键词提取 - 基于学习内容生成话题标签
- 📱 多平台优化 - 为小红书、微博、LinkedIn、Twitter 定制内容格式
- 🤖 AI 增强分析 - 可选的深度内容价值评估
- 📊 趋势识别 - 从学习记录中发现技术和行业趋势

**使用方法**:
```bash
/insight                    # 分析最近7天内容
/insight --weeks 2          # 分析最近2周内容
/insight --all              # 分析所有历史内容
/insight --platform xiaohongshu  # 为小红书优化
/insight --ai-analysis      # 启用AI深度分析
/insight --save report.md   # 保存报告到文件
```

**报告内容**:
- 高价值内容片段识别
- 社交媒体内容建议和模板
- 平台专属内容示例
- 关键词分析和话题标签
- 内容创作计划和时机建议

### 版本控制集成

项目支持自动 Git 操作：
- 使用 `/git-push` 命令自动提交和推送更改
- 所有学习文件都应纳入版本控制以便追踪进度
- 建议定期备份到远程仓库

## 开发和扩展

### 修改现有命令

1. 编辑 `.claude/commands/` 中的相应 `.md` 文件
2. 修改 markdown 代码块中的 bash 脚本
3. 保存后命令会自动在 Claude Code 中生效

### 添加新命令

1. 在 `.claude/commands/` 中创建新的 `.md` 文件
2. 遵循现有命令的结构模式：
   ```markdown
   # 命令名称和描述

   ```bash
   #!/bin/bash
   # 脚本实现
   ```
   ```
3. 确保脚本包含适当的错误处理和用户反馈

### 关键技术约束

- **平台兼容性**: 脚本必须兼容 macOS BSD 工具
- **日期处理**: 使用 `export LC_ALL=C` 避免本地化问题
- **文件路径**: 所有路径操作必须考虑文件名中的特殊字符
- **临时文件**: 使用 `mktemp` 创建临时文件，确保适当清理
