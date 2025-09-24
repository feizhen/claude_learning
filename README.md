# 个人学习日记系统

这是一个基于 Claude Code 自定义命令框架构建的**个人学习和日记系统**。项目通过自动化的 markdown 文件生成和组织，为日常学习、笔记记录和反思提供结构化方法。

## 快速开始

### 基本工作流程

```bash
/week-start → /daily-start → [日常记录] → /daily-review → /week-review
```

1. **开始新的一周**: 运行 `/week-start` 创建周文件夹
2. **开始每日记录**: 运行 `/daily-start` 创建当日日记模板
3. **填写学习内容**: 在日记文件中记录学习活动
4. **每日总结**: 运行 `/daily-review` 添加当日总结
5. **周度回顾**: 运行 `/week-review` 生成周总结

## 核心功能

### 自定义命令系统

项目包含八个核心自定义命令（位于 `.claude/commands/`）：

- **`/week-start`**: 创建周文件夹结构 (`weeks/YYYY_MMDD-MMDD/`)
- **`/daily-start`**: 创建每日日记文件，包含预设模板
- **`/daily-review`**: 添加每日总结部分（可配合 AI 分析）
- **`/week-review`**: 汇总整周内容，生成周度回顾
- **`/milestone`**: 生成学习进度和习惯分析报告
- **`/insight`**: 从学习记录中提取灵感，生成社交媒体创作内容建议
- **`/newsletter-fetch`**: 获取和整理新闻通讯内容
- **`/git-push`**: 自动化 git 提交和推送流程

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

## review
[每日总结 - 由 /daily-review 命令添加]
```

## 文件结构与组织

### 目录结构

```
claude_learning/
├── .claude/commands/          # 自定义命令定义
│   ├── daily-start.md        # 每日开始命令
│   ├── daily-review.md       # 每日总结命令
│   ├── week-start.md         # 周开始命令
│   └── week-review.md        # 周总结命令
├── weeks/                    # 按周组织的日记内容
│   └── YYYY_MMDD-MMDD/      # 周文件夹 (周一-周日)
│       ├── YYYY_MM_DD.md    # 每日日记文件
│       └── week_review.md   # 周总结文件
├── CLAUDE.md                 # Claude Code 指导文档
└── README.md                 # 项目说明文档
```

### 命名规范

- **周文件夹**: `YYYY_MMDD-MMDD` (例: `2025_0915-0921`)
- **日记文件**: `YYYY_MM_DD.md` (例: `2025_09_16.md`)
- **周总结**: `week_review.md`

## 系统特点

- **🤖 自动化**: 最少的手动文件管理
- **📋 结构化**: 一致的组织和模板
- **🔄 反思驱动**: 内置回顾和总结流程
- **🧠 AI 集成**: 利用 Claude 进行内容分析
- **📝 可移植性**: 纯 markdown 文件格式

## 技术说明

### 日期处理注意事项

所有自定义命令都使用 macOS BSD 风格的 `date` 命令。如果遇到中文日期格式问题，确保在脚本中设置：

```bash
export LC_ALL=C
```

### 修改自定义命令

1. 编辑 `.claude/commands/` 中的相应 `.md` 文件
2. 修改其中的 bash 脚本部分
3. 命令会自动在 Claude Code 中生效

### 内容聚合逻辑

- **周总结** 自动提取每日文件中各部分内容
- 使用正则表达式和 `sed` 命令解析 markdown 部分
- 支持多日内容的结构化汇总

## 开始使用

1. 确保已安装 [Claude Code](https://claude.ai/code)
2. 克隆此仓库到本地
3. 运行 `/week-start` 开始第一周的记录
4. 运行 `/daily-start` 创建今日的学习日记

---

*这个系统设计用于支持持续学习和反思的个人工作流程。通过结构化的记录和定期回顾，帮助建立有效的学习习惯。*