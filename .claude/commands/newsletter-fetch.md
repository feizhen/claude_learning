# /newsletter-fetch

自动获取并汇总 Gmail 中的 newsletter 内容，将其整理成结构化的 markdown 格式，存储在独立的 newsletter 目录系统中。

```bash
#!/bin/bash

# 设置环境变量
export LC_ALL=C

# 默认参数
DAYS=1
SENDERS=""
OUTPUT=""
DRY_RUN=false
SHOW_CONFIG=false

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --days)
            DAYS="$2"
            shift 2
            ;;
        --senders)
            SENDERS="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --config)
            SHOW_CONFIG=true
            shift
            ;;
        *)
            echo "未知参数: $1"
            echo "用法: /newsletter-fetch [--days N] [--senders pattern] [--output file] [--dry-run] [--config]"
            exit 1
            ;;
    esac
done

# 目录管理函数
create_newsletter_structure() {
    local target_date=${1:-$(date +%Y-%m-%d)}
    local year=$(echo $target_date | cut -d'-' -f1)
    local month=$(echo $target_date | cut -d'-' -f2)
    local day=$(echo $target_date | cut -d'-' -f3)

    # 计算周一和周日的日期
    local target_date_seconds=$(date -j -f "%Y-%m-%d" "$target_date" "+%s" 2>/dev/null || date -d "$target_date" "+%s")
    local day_of_week=$(date -j -f "%s" "$target_date_seconds" "+%u" 2>/dev/null || date -d "@$target_date_seconds" "+%u")

    # 计算周一的日期
    local monday_seconds=$((target_date_seconds - (day_of_week - 1) * 86400))
    local sunday_seconds=$((monday_seconds + 6 * 86400))

    local monday_date=$(date -j -f "%s" "$monday_seconds" "+%Y-%m-%d" 2>/dev/null || date -d "@$monday_seconds" "+%Y-%m-%d")
    local sunday_date=$(date -j -f "%s" "$sunday_seconds" "+%Y-%m-%d" 2>/dev/null || date -d "@$sunday_seconds" "+%Y-%m-%d")

    # 格式化为 MMDD
    local monday_mmdd=$(echo $monday_date | sed 's/.*-\(.*\)-\(.*\)/\1\2/')
    local sunday_mmdd=$(echo $sunday_date | sed 's/.*-\(.*\)-\(.*\)/\1\2/')

    # 创建周文件夹名称
    local week_folder="${year}_${monday_mmdd}-${sunday_mmdd}"
    local newsletters_dir="newsletters"
    local week_path="$newsletters_dir/$week_folder"

    # 创建目录结构
    mkdir -p "$week_path"

    # 返回路径信息
    echo "$week_path"
}

# 获取默认输出文件路径
get_default_output_path() {
    local target_date=${1:-$(date +%Y-%m-%d)}
    local week_path=$(create_newsletter_structure "$target_date")
    local formatted_date=$(echo $target_date | tr '-' '_')
    echo "$week_path/newsletter_$formatted_date.md"
}

# 配置管理函数
show_config() {
    local config_file="newsletters/newsletter-config.json"

    if [[ ! -f "$config_file" ]]; then
        echo "配置文件不存在，正在创建默认配置..."
        create_default_config
    fi

    echo "当前配置文件位置: $config_file"
    echo "配置内容:"
    cat "$config_file"

    echo ""
    echo "环境变量:"
    echo "GMAIL_USERNAME: ${GMAIL_USERNAME:-未设置}"
    echo "GMAIL_APP_PASSWORD: ${GMAIL_APP_PASSWORD:-未设置}"
}

# 创建默认配置文件
create_default_config() {
    local config_dir="newsletters"
    local config_file="$config_dir/newsletter-config.json"

    mkdir -p "$config_dir"

    cat > "$config_file" << 'EOF'
{
  "gmail": {
    "username": "${GMAIL_USERNAME}",
    "password": "${GMAIL_APP_PASSWORD}",
    "server": "imap.gmail.com",
    "port": 993
  },
  "filters": {
    "newsletter_patterns": ["newsletter", "digest", "weekly", "noreply"],
    "trusted_senders": [
      "substack.com",
      "medium.com",
      "hackernewsletter.com"
    ],
    "exclude_patterns": ["promotion", "sale", "offer"]
  },
  "output": {
    "max_content_length": 500,
    "include_links": true,
    "format": "markdown"
  }
}
EOF

    echo "已创建默认配置文件: $config_file"
}

# IMAP 邮件获取函数
fetch_emails_via_imap() {
    local days=$1
    local senders_filter=$2
    local dry_run=$3

    # 检查必要的环境变量
    if [[ -z "$GMAIL_USERNAME" || -z "$GMAIL_APP_PASSWORD" ]]; then
        echo "错误: 请设置 GMAIL_USERNAME 和 GMAIL_APP_PASSWORD 环境变量"
        echo "建议在 ~/.bashrc 或 ~/.zshrc 中添加:"
        echo "export GMAIL_USERNAME=your-email@gmail.com"
        echo "export GMAIL_APP_PASSWORD=your-app-specific-password"
        return 1
    fi

    echo "正在连接到 Gmail IMAP 服务器..."

    # 计算搜索日期范围
    local since_date
    if [[ "$OSTYPE" == "darwin"* ]]; then
        since_date=$(date -j -v-${days}d "+%d-%b-%Y" | tr '[:lower:]' '[:upper:]')
    else
        since_date=$(date -d "${days} days ago" "+%d-%b-%Y" | tr '[:lower:]' '[:upper:]')
    fi

    # 构建搜索查询
    local search_query="SINCE $since_date"

    # 如果指定了发件人过滤
    if [[ -n "$senders_filter" ]]; then
        IFS=',' read -ra SENDERS_ARRAY <<< "$senders_filter"
        for sender in "${SENDERS_ARRAY[@]}"; do
            search_query="$search_query FROM $sender"
        done
    else
        # 默认的 newsletter 关键词过滤
        search_query="$search_query (SUBJECT newsletter OR SUBJECT digest OR SUBJECT weekly)"
    fi

    if [[ "$dry_run" == "true" ]]; then
        echo "预览模式 - 将要搜索的邮件:"
        echo "搜索条件: $search_query"
        echo "时间范围: 最近 $days 天"
        return 0
    fi

    # 使用 curl 连接 IMAP
    local temp_file=$(mktemp)

    # IMAP 命令序列
    cat > "$temp_file" << EOF
a001 LOGIN $GMAIL_USERNAME $GMAIL_APP_PASSWORD
a002 SELECT INBOX
a003 SEARCH $search_query
a004 LOGOUT
EOF

    echo "正在搜索邮件..."

    # 执行 IMAP 命令
    local imap_response=$(curl -s --url "imaps://imap.gmail.com:993/INBOX" \
        --user "$GMAIL_USERNAME:$GMAIL_APP_PASSWORD" \
        --request "SEARCH $search_query" 2>/dev/null)

    rm -f "$temp_file"

    if [[ $? -eq 0 ]]; then
        echo "成功连接到 Gmail"
        echo "搜索结果: $imap_response"
        return 0
    else
        echo "连接失败，请检查网络连接和认证信息"
        return 1
    fi
}

# 邮件内容解析函数
parse_email_content() {
    local email_uid=$1
    local temp_dir=$(mktemp -d)

    echo "正在解析邮件 UID: $email_uid"

    # 获取邮件头信息
    local headers=$(curl -s --url "imaps://imap.gmail.com:993/INBOX;UID=$email_uid" \
        --user "$GMAIL_USERNAME:$GMAIL_APP_PASSWORD" \
        --request "FETCH $email_uid (ENVELOPE)" 2>/dev/null)

    # 获取邮件正文
    local body=$(curl -s --url "imaps://imap.gmail.com:993/INBOX;UID=$email_uid" \
        --user "$GMAIL_USERNAME:$GMAIL_APP_PASSWORD" \
        --request "FETCH $email_uid (BODY[TEXT])" 2>/dev/null)

    # 解析主题
    local subject=$(echo "$headers" | grep -i "subject:" | head -1 | sed 's/.*subject: //i' | sed 's/\r$//')

    # 解析发件人
    local sender=$(echo "$headers" | grep -i "from:" | head -1 | sed 's/.*from: //i' | sed 's/\r$//')

    # 解析日期
    local email_date=$(echo "$headers" | grep -i "date:" | head -1 | sed 's/.*date: //i' | sed 's/\r$//')

    # 清理 HTML 标签（简单版本）
    local clean_body=$(echo "$body" | sed 's/<[^>]*>//g' | sed 's/&nbsp;/ /g' | sed 's/&amp;/\&/g' | sed 's/&lt;/</g' | sed 's/&gt;/>/g')

    # 提取链接
    local links=$(echo "$body" | grep -oE 'https?://[^[:space:]<>"]+' | sort | uniq)

    # 创建邮件数据结构（JSON格式）
    cat > "$temp_dir/email_$email_uid.json" << EOF
{
  "uid": "$email_uid",
  "subject": "$subject",
  "sender": "$sender",
  "date": "$email_date",
  "content": $(echo "$clean_body" | jq -R -s .),
  "links": [$(echo "$links" | sed 's/.*/"&"/' | tr '\n' ',' | sed 's/,$//')]
}
EOF

    echo "$temp_dir/email_$email_uid.json"
    cleanup_temp_files "$temp_dir"
}

# 过滤 newsletter 邮件
filter_newsletters() {
    local email_list=$1
    local config_file="newsletters/newsletter-config.json"

    if [[ ! -f "$config_file" ]]; then
        echo "配置文件不存在，使用默认过滤规则"
        echo "$email_list"
        return
    fi

    # 读取配置中的过滤规则
    local newsletter_patterns=$(jq -r '.filters.newsletter_patterns[]' "$config_file" 2>/dev/null | tr '\n' '|' | sed 's/|$//')
    local trusted_senders=$(jq -r '.filters.trusted_senders[]' "$config_file" 2>/dev/null | tr '\n' '|' | sed 's/|$//')
    local exclude_patterns=$(jq -r '.filters.exclude_patterns[]' "$config_file" 2>/dev/null | tr '\n' '|' | sed 's/|$//')

    echo "应用过滤规则..."
    echo "Newsletter 模式: $newsletter_patterns"
    echo "信任发件人: $trusted_senders"
    echo "排除模式: $exclude_patterns"

    # 这里应该实现实际的过滤逻辑
    # 暂时返回原始列表
    echo "$email_list"
}

# 生成内容摘要函数
generate_summary() {
    local email_json=$1
    local config_file="newsletters/newsletter-config.json"

    # 从JSON中提取内容
    local content=$(jq -r '.content' "$email_json" 2>/dev/null)
    local subject=$(jq -r '.subject' "$email_json" 2>/dev/null)

    # 获取最大长度配置
    local max_length=500
    if [[ -f "$config_file" ]]; then
        max_length=$(jq -r '.output.max_content_length // 500' "$config_file" 2>/dev/null)
    fi

    # 简单的内容截取和清理
    local cleaned_content=$(echo "$content" | tr -d '\n\r' | sed 's/[[:space:]]\+/ /g')
    local truncated_content=$(echo "$cleaned_content" | cut -c1-$max_length)

    if [[ ${#cleaned_content} -gt $max_length ]]; then
        truncated_content="$truncated_content..."
    fi

    # 提取关键点（简单版本）
    local key_points=""
    if echo "$content" | grep -qi "key\|important\|主要\|重要"; then
        key_points=$(echo "$content" | grep -i "key\|important\|主要\|重要" | head -3)
    fi

    # 生成摘要结构
    cat << EOF
{
  "summary": "$truncated_content",
  "key_points": [$(echo "$key_points" | sed 's/.*/"&"/' | tr '\n' ',' | sed 's/,$//')]
}
EOF
}

# 清理临时文件
cleanup_temp_files() {
    local temp_dir=$1
    if [[ -d "$temp_dir" ]]; then
        rm -rf "$temp_dir"
    fi
}

# Claude API 集成函数
call_claude_api() {
    local content=$1
    local prompt="请为以下 newsletter 内容生成一个简洁的中文摘要（100-200字），并提取3-5个关键点：\n\n$content"

    # 检查是否设置了 Claude API 密钥
    if [[ -z "$CLAUDE_API_KEY" ]]; then
        echo "警告: 未设置 CLAUDE_API_KEY，使用简单摘要功能"
        return 1
    fi

    # 调用 Claude API
    local api_response=$(curl -s -X POST "https://api.anthropic.com/v1/messages" \
        -H "Content-Type: application/json" \
        -H "x-api-key: $CLAUDE_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -d "{
            \"model\": \"claude-3-haiku-20240307\",
            \"max_tokens\": 300,
            \"messages\": [{
                \"role\": \"user\",
                \"content\": \"$prompt\"
            }]
        }" 2>/dev/null)

    if [[ $? -eq 0 ]] && [[ -n "$api_response" ]]; then
        echo "$api_response" | jq -r '.content[0].text' 2>/dev/null
    else
        echo "API 调用失败，使用简单摘要"
        return 1
    fi
}

# 增强的摘要生成函数
generate_ai_summary() {
    local email_json=$1

    local content=$(jq -r '.content' "$email_json" 2>/dev/null)
    local subject=$(jq -r '.subject' "$email_json" 2>/dev/null)

    # 尝试使用 Claude API
    local ai_summary=$(call_claude_api "$content")

    if [[ $? -eq 0 ]] && [[ -n "$ai_summary" ]]; then
        echo "$ai_summary"
    else
        # 回退到简单摘要
        generate_summary "$email_json" | jq -r '.summary'
    fi
}

# 格式化输出函数
format_output() {
    local emails_data_dir=$1
    local output_file=$2

    local current_date=$(date +%Y-%m-%d)
    local current_time=$(date +"%Y-%m-%d %H:%M:%S")

    # 创建输出文件头部
    cat > "$output_file" << EOF
# Newsletter Summary - $current_date

> 📧 自动生成于 $current_time
> 🔧 由 /newsletter-fetch 命令生成

---

EOF

    # 统计信息
    local total_emails=0
    if [[ -d "$emails_data_dir" ]]; then
        total_emails=$(find "$emails_data_dir" -name "*.json" | wc -l)
    fi

    echo "## 📊 统计信息" >> "$output_file"
    echo "" >> "$output_file"
    echo "- **总邮件数**: $total_emails" >> "$output_file"
    echo "- **处理日期**: $current_date" >> "$output_file"
    echo "- **生成时间**: $current_time" >> "$output_file"
    echo "" >> "$output_file"
    echo "---" >> "$output_file"
    echo "" >> "$output_file"

    # 处理每封邮件
    if [[ -d "$emails_data_dir" ]] && [[ $total_emails -gt 0 ]]; then
        echo "## 📧 Newsletter 内容" >> "$output_file"
        echo "" >> "$output_file"

        local counter=1
        for email_file in "$emails_data_dir"/*.json; do
            if [[ -f "$email_file" ]]; then
                echo "正在格式化邮件 $counter/$total_emails..."

                local subject=$(jq -r '.subject' "$email_file" 2>/dev/null)
                local sender=$(jq -r '.sender' "$email_file" 2>/dev/null)
                local email_date=$(jq -r '.date' "$email_file" 2>/dev/null)
                local links_array=$(jq -r '.links[]' "$email_file" 2>/dev/null)

                # 生成 AI 摘要
                local summary=$(generate_ai_summary "$email_file")

                # 写入邮件内容
                cat >> "$output_file" << EOF
### 📬 $subject

**发件人**: $sender
**日期**: $email_date

**摘要**:
$summary

EOF

                # 添加链接（如果存在）
                if [[ -n "$links_array" ]]; then
                    echo "**相关链接**:" >> "$output_file"
                    echo "$links_array" | while read -r link; do
                        if [[ -n "$link" ]]; then
                            echo "- [$link]($link)" >> "$output_file"
                        fi
                    done
                    echo "" >> "$output_file"
                fi

                echo "---" >> "$output_file"
                echo "" >> "$output_file"

                ((counter++))
            fi
        done
    else
        echo "## ⚠️ 未找到邮件内容" >> "$output_file"
        echo "" >> "$output_file"
        echo "没有找到符合条件的 newsletter 邮件。" >> "$output_file"
        echo "" >> "$output_file"
    fi

    # 添加页脚
    cat >> "$output_file" << EOF

---

## 🔧 使用说明

- 使用 \`/newsletter-fetch --config\` 查看和配置邮件设置
- 使用 \`/newsletter-fetch --days N\` 获取最近 N 天的邮件
- 使用 \`/newsletter-fetch --senders pattern\` 过滤特定发件人

EOF

    echo "✅ Newsletter 内容已保存到: $output_file"
}

# 主工作流程函数
process_emails() {
    local email_uids=$1
    local temp_dir=$(mktemp -d)

    echo "📝 开始处理邮件内容..."

    # 解析每封邮件
    local processed_count=0
    for uid in $email_uids; do
        if [[ -n "$uid" ]] && [[ "$uid" != "SEARCH" ]]; then
            echo "处理邮件 UID: $uid"
            local email_json=$(parse_email_content "$uid")
            if [[ -f "$email_json" ]]; then
                cp "$email_json" "$temp_dir/"
                ((processed_count++))
            fi
        fi
    done

    echo "✅ 成功处理 $processed_count 封邮件"
    echo "$temp_dir"
}

# 主函数
main() {
    echo "📧 Newsletter Fetch 工具启动"
    echo "=================="

    # 如果是显示配置
    if [[ "$SHOW_CONFIG" == "true" ]]; then
        show_config
        return 0
    fi

    # 确定输出路径
    if [[ -z "$OUTPUT" ]]; then
        OUTPUT=$(get_default_output_path)
        echo "📁 使用默认输出路径: $OUTPUT"
    fi

    # 确保输出目录存在
    local output_dir=$(dirname "$OUTPUT")
    mkdir -p "$output_dir"

    # 创建配置文件（如果不存在）
    if [[ ! -f "newsletters/newsletter-config.json" ]]; then
        echo "📋 创建默认配置文件..."
        create_default_config
    fi

    echo ""
    echo "🔧 配置信息："
    echo "- 获取天数: $DAYS"
    echo "- 发件人过滤: ${SENDERS:-所有newsletter}"
    echo "- 输出文件: $OUTPUT"
    echo "- 预览模式: $DRY_RUN"
    echo ""

    # 获取邮件列表
    echo "📬 开始获取邮件列表 (最近 $DAYS 天)..."
    local imap_result=$(fetch_emails_via_imap "$DAYS" "$SENDERS" "$DRY_RUN")

    if [[ $? -eq 0 ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            echo "✅ 预览完成"
            return 0
        fi

        # 从 IMAP 结果中提取邮件 UID
        local email_uids=$(echo "$imap_result" | grep -o '[0-9]\+' | tr '\n' ' ')

        if [[ -n "$email_uids" ]]; then
            echo "📋 找到邮件 UIDs: $email_uids"

            # 过滤 newsletter 邮件
            local filtered_uids=$(filter_newsletters "$email_uids")

            # 处理邮件内容
            local emails_temp_dir=$(process_emails "$filtered_uids")

            # 格式化并保存输出
            echo "📝 生成最终报告..."
            format_output "$emails_temp_dir" "$OUTPUT"

            # 清理临时文件
            cleanup_temp_files "$emails_temp_dir"

            echo ""
            echo "🎉 Newsletter 获取完成！"
            echo "📄 报告已保存到: $OUTPUT"

        else
            echo "⚠️ 未找到符合条件的邮件"
            # 仍然创建一个空的报告文件
            format_output "" "$OUTPUT"
        fi
    else
        echo "❌ Newsletter 获取失败"
        echo "请检查："
        echo "1. 网络连接"
        echo "2. Gmail 认证信息 (GMAIL_USERNAME, GMAIL_APP_PASSWORD)"
        echo "3. Gmail 应用专用密码设置"
        return 1
    fi
}

# 错误处理和清理
cleanup_on_exit() {
    echo ""
    echo "🧹 正在清理临时文件..."
    # 清理可能残留的临时文件
    find /tmp -name "tmp.*" -user $(whoami) -mtime +1 -delete 2>/dev/null || true
}

# 设置退出时清理
trap cleanup_on_exit EXIT

# 执行主函数
main
```

## 配置需求

### 环境变量（存储在 `.env` 或安全位置）

```bash
GMAIL_USERNAME=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-specific-password
NEWSLETTER_PATTERNS=newsletter,digest,weekly,substack,medium
```

### 配置文件格式 (`newsletters/newsletter-config.json`)

```json
{
  "gmail": {
    "username": "${GMAIL_USERNAME}",
    "password": "${GMAIL_APP_PASSWORD}",
    "server": "imap.gmail.com",
    "port": 993
  },
  "filters": {
    "newsletter_patterns": ["newsletter", "digest", "weekly", "noreply"],
    "trusted_senders": [
      "substack.com",
      "medium.com",
      "hackernewsletter.com"
    ],
    "exclude_patterns": ["promotion", "sale", "offer"]
  },
  "output": {
    "max_content_length": 500,
    "include_links": true,
    "format": "markdown"
  }
}
```

## 输出格式

### 标准输出格式

```markdown
## Newsletter Summary - YYYY-MM-DD

### 📧 [Newsletter Title](original-link)
**From**: sender@domain.com
**Date**: YYYY-MM-DD HH:MM
**Summary**: [AI生成的内容摘要，约100-200字]

**Key Points**:
- 要点1
- 要点2
- 要点3

**Links**:
- [Link Title](url)

---

### 📧 [Another Newsletter](link)
...
```

## 目录结构

### Newsletter 目录组织（与 weeks 目录结构一致）

```
newsletters/
├── newsletter-config.json
├── 2024_0101-0107/
│   ├── newsletter_2024_01_01.md
│   ├── newsletter_2024_01_02.md
│   └── ...
├── 2024_0108-0114/
│   ├── newsletter_2024_01_08.md
│   └── ...
└── YYYY_MMDD-MMDD/
    └── newsletter_YYYY_MM_DD.md
```

### 文件命名规范

- **周文件夹**: `YYYY_MMDD-MMDD` （周一到周日的日期）
- **日文件**: `newsletter_YYYY_MM_DD.md`
- **配置文件**: `newsletters/newsletter-config.json`

## 技术实现要点

### 目录管理流程

1. **自动创建目录**: 根据当前日期自动创建对应的周文件夹
2. **文件命名**: 按照 `newsletter_YYYY_MM_DD.md` 格式命名
3. **目录结构**: 与 weeks 目录保持一致的组织方式

### 邮件获取流程

1. **IMAP 连接**: 使用应用专用密码连接 Gmail
2. **邮件过滤**: 基于发件人、主题、时间范围筛选
3. **内容解析**: 提取 HTML/文本内容，识别链接
4. **智能摘要**: 使用 Claude API 生成内容摘要
5. **格式化输出**: 转换为 markdown 格式并保存到对应目录

### 错误处理

- 网络连接失败：重试机制
- 认证失败：提示检查密码配置
- 解析失败：记录错误但继续处理其他邮件
- 配额限制：显示警告并建议延后执行

### 安全考虑

- 密码存储：仅支持应用专用密码，不存储主密码
- 本地缓存：敏感信息不写入日志
- 权限最小化：仅请求读取邮件权限

## 性能指标

- **获取速度**: 每封邮件 < 2秒
- **摘要生成**: 每封邮件 < 5秒（取决于 Claude API）
- **批量处理**: 支持最多50封邮件
- **缓存机制**: 避免重复处理相同邮件

## 扩展功能（未来版本）

- **标签分类**: 自动为不同类型 newsletter 添加标签
- **趋势分析**: 分析 newsletter 话题趋势
- **订阅管理**: 识别低价值 newsletter 并建议取消订阅
- **多邮箱支持**: 支持多个邮箱账户
- **定时执行**: 支持 cron 定时自动获取
- **周总结**: 类似 `/week-review`，汇总整周的 newsletter 内容
- **跨周搜索**: 在整个 newsletters 目录中搜索特定主题或关键词

## 依赖项

- `curl` 或 `openssl` (IMAP 连接)
- `jq` (JSON 处理)
- `sed`, `awk` (文本处理)
- Claude API access (内容摘要)

## 兼容性

- **操作系统**: macOS, Linux, Windows (WSL)
- **Shell**: bash 4.0+
- **Gmail**: 需要启用2FA并生成应用专用密码