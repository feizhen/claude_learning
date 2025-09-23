# /git-push

提交当前修改并推送到远端 main 分支

```bash
#!/bin/bash

# 设置环境变量避免中文日期问题
export LC_ALL=C

echo "🔍 检查当前 git 状态..."

# 获取当前状态
git_status=$(git status --porcelain)

# 检查是否有任何修改（包括新文件、修改的文件、删除的文件）
if [ -n "$git_status" ]; then
    echo "📋 发现以下修改："
    git status --short
    echo ""

    # 显示未跟踪的文件
    untracked_files=$(git ls-files --others --exclude-standard)
    if [ -n "$untracked_files" ]; then
        echo "📁 未跟踪的文件："
        echo "$untracked_files"
        echo ""
    fi

    # 显示已修改文件的详细内容
    modified_files=$(git diff --name-only)
    if [ -n "$modified_files" ]; then
        echo "📖 已修改文件的详细变更："
        git diff --name-status
        echo ""
    fi

    # 显示已暂存文件
    staged_files=$(git diff --cached --name-only)
    if [ -n "$staged_files" ]; then
        echo "📋 已暂存的文件："
        git diff --cached --name-status
        echo ""
    fi

    # 添加所有修改到暂存区
    echo "➕ 添加所有修改到暂存区..."
    git add -A

    # 生成提交信息
    current_date=$(date '+%Y-%m-%d')
    commit_message="更新学习日记和命令配置 - ${current_date}

🤖 通过 Claude Code 自定义命令生成

Co-Authored-By: Claude <noreply@anthropic.com>"

    # 提交修改
    echo "💾 提交修改..."
    if git commit -m "$(cat <<EOF
$commit_message
EOF
)"; then
        echo "✅ 提交成功"

        # 推送到远端
        echo "🚀 推送到远端 main 分支..."
        if git push origin main; then
            echo "🎉 成功推送到远端！"
            echo ""
            echo "📊 最新提交信息："
            git log --oneline -1
        else
            echo "❌ 推送失败，请检查网络连接和权限"
            exit 1
        fi
    else
        echo "❌ 提交失败"
        exit 1
    fi
else
    echo "ℹ️  没有需要提交的修改"

    # 检查本地是否领先远端
    if git log origin/main..HEAD --oneline | grep -q .; then
        echo "🔄 发现本地领先远端的提交，正在推送..."
        if git push origin main; then
            echo "🎉 成功推送到远端！"
        else
            echo "❌ 推送失败"
            exit 1
        fi
    else
        echo "✅ 本地与远端保持同步"
    fi
fi

echo ""
echo "🔗 远端仓库状态已更新"
```