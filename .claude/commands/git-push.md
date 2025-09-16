# /git-push

提交当前修改并推送到远端 main 分支

```bash
#!/bin/bash

# 设置环境变量避免中文日期问题
export LC_ALL=C

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 检查当前 git 状态...${NC}"

# 检查是否有未暂存的修改
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo -e "${YELLOW}📋 发现以下修改：${NC}"
    git status --short
    echo ""

    # 显示详细修改内容
    echo -e "${BLUE}📖 详细修改内容：${NC}"
    git diff --name-status
    echo ""

    # 添加所有修改到暂存区
    echo -e "${BLUE}➕ 添加所有修改到暂存区...${NC}"
    git add -A

    # 生成提交信息
    current_date=$(date '+%Y-%m-%d')
    commit_message="更新学习日记和命令配置 - ${current_date}

🤖 通过 Claude Code 自定义命令生成

Co-Authored-By: Claude <noreply@anthropic.com>"

    # 提交修改
    echo -e "${BLUE}💾 提交修改...${NC}"
    if git commit -m "$(cat <<EOF
$commit_message
EOF
)"; then
        echo -e "${GREEN}✅ 提交成功${NC}"

        # 推送到远端
        echo -e "${BLUE}🚀 推送到远端 main 分支...${NC}"
        if git push origin main; then
            echo -e "${GREEN}🎉 成功推送到远端！${NC}"
            echo ""
            echo -e "${BLUE}📊 最新提交信息：${NC}"
            git log --oneline -1
        else
            echo -e "${RED}❌ 推送失败，请检查网络连接和权限${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ 提交失败${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}ℹ️  没有需要提交的修改${NC}"

    # 检查本地是否领先远端
    if git log origin/main..HEAD --oneline | grep -q .; then
        echo -e "${BLUE}🔄 发现本地领先远端的提交，正在推送...${NC}"
        if git push origin main; then
            echo -e "${GREEN}🎉 成功推送到远端！${NC}"
        else
            echo -e "${RED}❌ 推送失败${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ 本地与远端保持同步${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🔗 远端仓库状态已更新${NC}"
```