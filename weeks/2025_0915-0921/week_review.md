# Weekly Review: 2025_0915-0921

Week of September 15 - September 21, 2025

## Summary

本周主要专注于个人学习系统的搭建和学习内容的产出。完成了 claude_learning 项目的基础架构，学习了 RAG 技术和 Claude Code 的使用，并开始了新的产品开发项目 WayToAce。

## Daily Summaries

### September 16

**Ideas/Thoughts:**
- 初步完成了 claude_learning 目录的搭建，支持 /week-* 和 /daily-_ 命令，用来 by 天、by 周维度进行记录和 review
- 接下来需要持续迭代 claude learning 系统，需要导入整体的目标，让 claude code 或者 gpt 来做具体的目标拆解，并进一步细化实践目标

**Daily Review:**
- **Project work**: 初步完成了 claude_learning 目录的搭建，支持 /week-* 和 /daily-_ 命令，用来 by 天、by 周维度进行记录和 review
- **Development milestone**: 成功设置了个人学习和日记系统的基础架构，包括自动化的文件管理和模板系统

---

### September 17

**Videos/Learning:**
- [Claude Code Tutorial: Build a YouTube Research Agent in 15 Minutes](https://www.youtube.com/watch?v=iW0lMW-Ff5I)
教你如何使用 claude 搭建一个 agent：
1. 使用 claude 的 plan mode
2. 根据你的目的，先让 claude 规划可行的方案，然后确定采用的方案
3. 先让 claude 写一个自定义 command 的概要（spec），然后 review 这份概要
4. 让 calude 按照 review 过的 spec 开始 coding
5. 最后测试和迭代

整体算是一个比较好的使用 claude code 搭建功能的实践，后续可以用这种方式持续迭代当前的项目

**Daily Review:**
- **Video learning**: Watched content related to project setup and development tools

---

### September 20

**Newsletter/Reading:**
- AI Vally
- The Keyword

**Ideas/Thoughts:**
- 初步完成了 /milestone 命令，可以查看当前的 milestone，进一步优化了功能，增加了学习习惯的评估
- 目前这套流程，目标的拆解，回顾是否有产品化的能力

**Learning Output:**
- 发布了第一个[小红书笔记](https://www.xiaohongshu.com/explore/68ce79a10000000013019913?xsec_token=YByhfracJkx9wfWo5NXk2u6QkLyeEvSvyOAwyuIQNOq6E%3D&xsec_source=pc_creatormng)，简单记录了使用这个项目的搭建和使用

**Daily Review:**
- **项目开发**: 初步完成了 /milestone 命令，可以查看当前的 milestone，进一步优化了功能，增加了学习习惯的评估
- **内容输出**: 发布了第一个小红书笔记，分享了项目的搭建和使用经验

---

### September 21

**Videos/Learning:**
- [RAG 工作机制详解——一个高质量知识库背后的技术全流程](https://www.youtube.com/watch?v=WWdlme1EAGI)
  - 大量的上下文导致的结果：
  1. 内容无法读取
  2. 推理成本过高
  3. 推理速度变慢

  现在的大模型的上下文窗口都是越来越大的，容量的问题不用担心，主要还是推理成本和推理速度的问题

  Rag 基本原理：分片 -> 索引 -> 召回 -> 重排 -> 生成

  分片通常需要按照特定的规则，像助手就是按照问题答案来做分片的，每一个答案是一个分片，然后需要 embedding 将这些分片转换成向量存储到向量数据库里
  召回：指的是查询和用户问题相关的内容的过程，主要涉及到对用户问题进行 embedding 得到向量，然后对向量数据库进行查询，然后得到几个相关回答
  重排：对召回的回答进行排序，获取 topX 的回答发送给模型，重排可以进一步提升准确率。召回：成本低、耗时短、_准确率低_，重排：成本高、耗时长、_准确率高_

**Ideas/Thoughts:**
- 将当前这一套学习记录做成一款 app 目前看是有很大潜力的，可以尽快行动起来，先起一个名字就叫 WayToAce

**Learning Output:**
- [将 Claude Code 当做产品 MVP 来用](https://www.xiaohongshu.com/explore/68cf5439000000001300bdb7?xsec_token=GB81a3fpBuCK6eYnCDk_HCn1UxGfeScjzsudQRwCCcsqc=&xsec_source=pc_creatormng)

**WayToAce:**
- 初步实现了注册和登陆功能，界面的交互流程还不是我想要的，得着重设计一下界面交互

**Daily Review:**
- **Video learning**: Watched content related to project setup and development tools
- **Reading**: Consumed newsletter and article content
- **Project work**:
- **Learning output**: Created and shared learning content

---

## Weekly Insights

### 技术学习成果
- **Claude Code 使用**: 深入学习了如何使用 Claude Code 构建自动化工具和 agent，掌握了 plan mode 的使用流程
- **RAG 技术**: 系统学习了 RAG 工作机制，理解了分片、索引、召回、重排、生成的完整流程，以及成本和准确率的权衡

### 项目开发进展
- **claude_learning 系统**: 成功搭建了个人学习记录和回顾系统，实现了自动化的文件管理和模板化记录
- **WayToAce 产品**: 开始了新的产品开发，初步实现了用户注册和登录功能

### 内容产出
- 开始在小红书平台分享学习心得，发布了两篇关于 Claude Code 使用的笔记
- 建立了定期的内容输出习惯

### 关键洞察
- 个人学习系统具有产品化的潜力，可以帮助更多人建立结构化的学习习惯
- Claude Code 可以作为快速 MVP 开发工具，验证产品概念的可行性

## Action Items for Next Week

### 技术深化
- [ ] 继续优化 claude_learning 系统，添加更多自动化功能
- [ ] 深入研究 RAG 技术的实际应用场景和实现方案

### 产品开发
- [ ] 完善 WayToAce 的界面交互设计
- [ ] 制定 WayToAce 的产品发展路线图
- [ ] 调研类似产品的市场情况

### 内容产出
- [ ] 继续保持小红书内容更新频率
- [ ] 考虑增加更多平台的内容分发
- [ ] 准备技术分享相关的深度内容

### 学习目标
- [ ] 深入学习产品设计相关知识
- [ ] 研究用户体验设计最佳实践
- [ ] 学习移动应用开发技术栈
