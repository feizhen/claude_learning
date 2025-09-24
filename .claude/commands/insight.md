# Insight Command

从学习记录中提取灵感，生成适用于社交媒体创作的内容建议。分析学习内容的主题趋势、产品体验、技术洞察，为内容创作提供素材和灵感。

```bash
#!/bin/bash

# Set locale to avoid date formatting issues
export LC_ALL=C

# Default values
DAYS=""
WEEKS=""
ALL_CONTENT=false
TOPIC=""
PLATFORM=""
OUTPUT_FORMAT="markdown"
SAVE_TO_FILE=""
VERBOSE=false
AI_ANALYSIS=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --days)
            DAYS="$2"
            shift 2
            ;;
        --weeks)
            WEEKS="$2"
            shift 2
            ;;
        --all)
            ALL_CONTENT=true
            shift
            ;;
        --topic)
            TOPIC="$2"
            shift 2
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --save)
            SAVE_TO_FILE="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --ai-analysis)
            AI_ANALYSIS=true
            shift
            ;;
        -h|--help)
            echo "Usage: /insight [OPTIONS]"
            echo ""
            echo "从学习记录中提取灵感，生成社交媒体创作内容建议"
            echo ""
            echo "Options:"
            echo "  --days N         分析最近N天的内容 (默认7天)"
            echo "  --weeks N        分析最近N周的内容"
            echo "  --all            分析所有历史内容"
            echo "  --topic TOPIC    聚焦特定主题分析"
            echo "  --platform PLAT  为特定平台优化 (xiaohongshu|weibo|linkedin|twitter)"
            echo "  --format FORMAT  输出格式 (markdown|json|html)"
            echo "  --save FILE      保存结果到文件"
            echo "  --verbose        显示详细分析过程"
            echo "  --ai-analysis    启用AI深度分析(需要联网)"
            echo "  -h, --help       显示帮助信息"
            echo ""
            echo "Examples:"
            echo "  /insight                           # 分析最近7天的内容"
            echo "  /insight --weeks 2                 # 分析最近2周的内容"
            echo "  /insight --topic AI --platform xiaohongshu  # 分析AI相关内容并为小红书优化"
            echo "  /insight --all --save insights.md  # 分析所有内容并保存到文件"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Set default analysis period if none specified
if [ -z "$DAYS" ] && [ -z "$WEEKS" ] && [ "$ALL_CONTENT" = false ]; then
    DAYS=7
fi

# Function to get current date
get_current_date() {
    date +"%Y-%m-%d"
}

# Function to get date N days ago
get_date_n_days_ago() {
    local n_days=$1
    local current_date=$(get_current_date)

    if date -j -f "%Y-%m-%d" "$current_date" -v-${n_days}d +%Y-%m-%d >/dev/null 2>&1; then
        # BSD date (macOS)
        date -j -f "%Y-%m-%d" "$current_date" -v-${n_days}d +%Y-%m-%d
    else
        # GNU date (Linux)
        date -d "$current_date - $n_days days" +%Y-%m-%d
    fi
}

# Function to get date N weeks ago
get_date_n_weeks_ago() {
    local n_weeks=$1
    local n_days=$((n_weeks * 7))
    get_date_n_days_ago $n_days
}

# Function to check if a date is within the analysis period
is_date_in_period() {
    local file_date=$1
    local current_date=$(get_current_date)

    if [ "$ALL_CONTENT" = true ]; then
        return 0
    fi

    local cutoff_date=""
    if [ ! -z "$DAYS" ]; then
        cutoff_date=$(get_date_n_days_ago $DAYS)
    elif [ ! -z "$WEEKS" ]; then
        cutoff_date=$(get_date_n_weeks_ago $WEEKS)
    fi

    if [ ! -z "$cutoff_date" ]; then
        # Compare dates using arithmetic comparison (removes dashes)
        local file_date_num=$(echo "$file_date" | tr -d '-')
        local cutoff_date_num=$(echo "$cutoff_date" | tr -d '-')

        if [ "$file_date_num" -ge "$cutoff_date_num" ] 2>/dev/null; then
            return 0
        else
            return 1
        fi
    fi

    return 0
}

# Function to extract content from daily files within the specified period
extract_learning_content() {
    local temp_dir=$(mktemp -d)
    local content_file="$temp_dir/content.txt"
    local video_file="$temp_dir/videos.txt"
    local newsletter_file="$temp_dir/newsletters.txt"
    local braindump_file="$temp_dir/braindumps.txt"
    local output_file="$temp_dir/outputs.txt"
    local review_file="$temp_dir/reviews.txt"

    echo "📊 正在扫描学习记录..." >&2

    # Find all daily files
    local daily_files=$(find weeks/ -name "????_??_??.md" -type f | sort)
    local total_files=0
    local analyzed_files=0

    for file in $daily_files; do
        total_files=$((total_files + 1))

        # Extract date from filename (YYYY_MM_DD.md)
        local filename=$(basename "$file" .md)
        local file_date=$(echo "$filename" | sed 's/_/-/g')

        # Check if file is within analysis period
        if is_date_in_period "$file_date"; then
            analyzed_files=$((analyzed_files + 1))

            [ "$VERBOSE" = true ] && echo "  分析文件: $file" >&2

            # Extract content from each section
            if grep -q "## video" "$file"; then
                local video_content=$(sed -n '/## video/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d')
                if [ ! -z "$video_content" ]; then
                    echo "=== $file_date ===" >> "$video_file"
                    echo "$video_content" >> "$video_file"
                    echo "" >> "$video_file"
                fi
            fi

            if grep -q "## newsletter" "$file"; then
                local newsletter_content=$(sed -n '/## newsletter/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d')
                if [ ! -z "$newsletter_content" ]; then
                    echo "=== $file_date ===" >> "$newsletter_file"
                    echo "$newsletter_content" >> "$newsletter_file"
                    echo "" >> "$newsletter_file"
                fi
            fi

            if grep -q "## braindump" "$file"; then
                local braindump_content=$(sed -n '/## braindump/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d')
                if [ ! -z "$braindump_content" ]; then
                    echo "=== $file_date ===" >> "$braindump_file"
                    echo "$braindump_content" >> "$braindump_file"
                    echo "" >> "$braindump_file"
                fi
            fi

            if grep -q "## output" "$file"; then
                local output_content=$(sed -n '/## output/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d')
                if [ ! -z "$output_content" ]; then
                    echo "=== $file_date ===" >> "$output_file"
                    echo "$output_content" >> "$output_file"
                    echo "" >> "$output_file"
                fi
            fi

            if grep -q "## review" "$file"; then
                local review_content=$(sed -n '/## review/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d' | grep -v "<!-- Review will be added")
                if [ ! -z "$review_content" ]; then
                    echo "=== $file_date ===" >> "$review_file"
                    echo "$review_content" >> "$review_file"
                    echo "" >> "$review_file"
                fi
            fi
        fi
    done

    echo "📈 扫描完成: 分析了 $analyzed_files/$total_files 个文件" >&2

    # Store file paths for later use
    echo "$video_file" > "$temp_dir/video_path"
    echo "$newsletter_file" > "$temp_dir/newsletter_path"
    echo "$braindump_file" > "$temp_dir/braindump_path"
    echo "$output_file" > "$temp_dir/output_path"
    echo "$review_file" > "$temp_dir/review_path"
    echo "$analyzed_files" > "$temp_dir/analyzed_count"

    echo "$temp_dir"
}

# Function to analyze content and extract keywords/themes
analyze_content_themes() {
    local content_dir=$1
    local themes_file=$(mktemp)
    local keywords_file=$(mktemp)

    echo "🔍 正在分析内容主题..." >&2

    # Define keyword categories for Chinese content
    cat > "$themes_file" << 'EOF'
# 技术关键词
AI|人工智能|大模型|LLM|GPT|Claude|ChatGPT|机器学习|深度学习|神经网络
编程|代码|开发|程序|软件|产品|设计|用户体验|UX|UI
Python|JavaScript|React|Vue|Node|后端|前端|全栈|数据库|API
云计算|AWS|阿里云|腾讯云|Docker|Kubernetes|微服务|架构

# 产品工具
Replit|HeyGen|Figma|Notion|Slack|GitHub|GitLab|VSCode|Jupyter
小红书|微博|LinkedIn|Twitter|抖音|B站|YouTube|TikTok
数字人|视频生成|图像处理|自动化|效率工具|生产力

# 行业动态
创业|投资|融资|IPO|独角兽|估值|商业模式|变现|增长|用户|流量
SaaS|B2B|B2C|C端|B端|ToB|ToC|平台|生态|社区|开源

# 学习发展
目标管理|时间管理|效率|习惯|成长|学习|技能|能力|经验|总结|反思
面试|求职|跳槽|职业发展|转岗|晋升|领导力|沟通|协作|团队
EOF

    # Extract and count keywords from all content files
    for content_type in video newsletter braindump output review; do
        local content_file=$(cat "$content_dir/${content_type}_path" 2>/dev/null)
        if [ -f "$content_file" ] && [ -s "$content_file" ]; then
            echo "分析 $content_type 内容..." >&2

            # Extract keywords based on predefined patterns
            while IFS='|' read -r keyword_line; do
                if [[ ! "$keyword_line" =~ ^# ]] && [ ! -z "$keyword_line" ]; then
                    echo "$keyword_line" | tr '|' '\n' | while read -r keyword; do
                        if [ ! -z "$keyword" ]; then
                            local count=$(grep -i -o "$keyword" "$content_file" | wc -l | tr -d ' ')
                            if [ "$count" -gt 0 ]; then
                                echo "$keyword:$count:$content_type" >> "$keywords_file"
                            fi
                        fi
                    done
                fi
            done < "$themes_file"
        fi
    done

    # Sort and deduplicate keywords
    local final_keywords=$(mktemp)
    if [ -s "$keywords_file" ]; then
        sort "$keywords_file" | uniq > "$final_keywords"
    fi

    echo "$final_keywords"

    # Cleanup
    rm -f "$themes_file" "$keywords_file"
}

# Function to identify high-value content for social media
identify_valuable_content() {
    local content_dir=$1
    local valuable_content=$(mktemp)

    echo "💎 正在识别高价值内容..." >&2

    # Look for content with social media indicators
    echo "## 🌟 高价值内容片段" > "$valuable_content"
    echo "" >> "$valuable_content"

    # Check braindump for insights and opinions
    local braindump_file=$(cat "$content_dir/braindump_path" 2>/dev/null)
    if [ -f "$braindump_file" ] && [ -s "$braindump_file" ]; then
        echo "### 💡 深度思考与洞察" >> "$valuable_content"
        echo "" >> "$valuable_content"

        # Extract lines with strong opinions or insights
        grep -E "(思考|洞察|发现|体验|感受|总结|建议|推荐|不错|很棒|有趣|惊喜|问题|缺点|优点)" "$braindump_file" | head -10 | while read -r line; do
            if [ ! -z "$line" ] && [[ ! "$line" =~ ^=== ]]; then
                echo "- $line" >> "$valuable_content"
            fi
        done
        echo "" >> "$valuable_content"
    fi

    # Check output for achievements and creations
    local output_file=$(cat "$content_dir/output_path" 2>/dev/null)
    if [ -f "$output_file" ] && [ -s "$output_file" ]; then
        echo "### 🎯 学习成果与产出" >> "$valuable_content"
        echo "" >> "$valuable_content"

        # Extract achievement-related content
        grep -E "(完成|发布|创建|实现|搭建|上线|demo|项目|产品|文章|视频)" "$output_file" | head -8 | while read -r line; do
            if [ ! -z "$line" ] && [[ ! "$line" =~ ^=== ]]; then
                echo "- $line" >> "$valuable_content"
            fi
        done
        echo "" >> "$valuable_content"
    fi

    # Check newsletter for trending topics
    local newsletter_file=$(cat "$content_dir/newsletter_path" 2>/dev/null)
    if [ -f "$newsletter_file" ] && [ -s "$newsletter_file" ]; then
        echo "### 📰 行业动态与趋势" >> "$valuable_content"
        echo "" >> "$valuable_content"

        # Extract newsletter insights
        grep -v "^===" "$newsletter_file" | grep -E "(.{10,})" | head -5 | while read -r line; do
            if [ ! -z "$line" ]; then
                echo "- $line" >> "$valuable_content"
            fi
        done
        echo "" >> "$valuable_content"
    fi

    echo "$valuable_content"
}

# Function to generate social media content suggestions
generate_social_media_suggestions() {
    local content_dir=$1
    local keywords_file=$2
    local valuable_content_file=$3
    local suggestions=$(mktemp)

    echo "📱 正在生成社交媒体内容建议..." >&2

    echo "## 🚀 社交媒体内容建议" > "$suggestions"
    echo "" >> "$suggestions"

    # Top keywords for hashtags
    if [ -f "$keywords_file" ] && [ -s "$keywords_file" ]; then
        echo "### 🏷️ 推荐话题标签" >> "$suggestions"
        echo "" >> "$suggestions"

        # Get top keywords by frequency
        local top_keywords=$(sort -t':' -k2 -nr "$keywords_file" | head -10 | cut -d':' -f1)
        echo "$top_keywords" | while read -r keyword; do
            if [ ! -z "$keyword" ]; then
                echo "- #$keyword" >> "$suggestions"
            fi
        done
        echo "" >> "$suggestions"
    fi

    # Platform-specific suggestions based on PLATFORM parameter
    if [ ! -z "$PLATFORM" ]; then
        echo "### 📲 $PLATFORM 专属建议" >> "$suggestions"
        echo "" >> "$suggestions"

        case "$PLATFORM" in
            "xiaohongshu")
                echo "**小红书内容特点:**" >> "$suggestions"
                echo "- 标题要吸引眼球，使用数字和情绪词汇" >> "$suggestions"
                echo "- 多用表情符号增加视觉吸引力" >> "$suggestions"
                echo "- 分享个人体验和真实感受" >> "$suggestions"
                echo "- 包含实用的教程或建议" >> "$suggestions"
                ;;
            "weibo")
                echo "**微博内容特点:**" >> "$suggestions"
                echo "- 简洁明了，突出重点" >> "$suggestions"
                echo "- 结合时事热点" >> "$suggestions"
                echo "- 使用相关的超话标签" >> "$suggestions"
                echo "- 鼓励转发和互动" >> "$suggestions"
                ;;
            "linkedin")
                echo "**LinkedIn 内容特点:**" >> "$suggestions"
                echo "- 专业性强，展示专业见解" >> "$suggestions"
                echo "- 分享职业经验和学习心得" >> "$suggestions"
                echo "- 英文内容为主" >> "$suggestions"
                echo "- 适合技术深度分享" >> "$suggestions"
                ;;
            "twitter")
                echo "**Twitter 内容特点:**" >> "$suggestions"
                echo "- 简短精炼，一针见血" >> "$suggestions"
                echo "- 使用 thread 展开复杂话题" >> "$suggestions"
                echo "- 及时性强，追求viral传播" >> "$suggestions"
                echo "- 多使用相关 hashtag" >> "$suggestions"
                ;;
        esac
        echo "" >> "$suggestions"
    fi

    # Content format suggestions
    echo "### 📝 内容格式建议" >> "$suggestions"
    echo "" >> "$suggestions"
    echo "**推荐内容类型:**" >> "$suggestions"
    echo "- 📊 学习总结 - 将本周/本月学习内容制作成图表" >> "$suggestions"
    echo "- 🔧 工具分享 - 介绍使用过的优秀工具和体验" >> "$suggestions"
    echo "- 💡 思考感悟 - 分享学习过程中的洞察和思考" >> "$suggestions"
    echo "- 🎯 成果展示 - 展示学习成果和项目进展" >> "$suggestions"
    echo "- 📚 资源推荐 - 推荐优质的学习资源和文章" >> "$suggestions"
    echo "" >> "$suggestions"

    # Timing suggestions
    echo "### ⏰ 发布时机建议" >> "$suggestions"
    echo "" >> "$suggestions"
    echo "**最佳发布时间:**" >> "$suggestions"
    echo "- 工作日早上 8-9 点（上班路上）" >> "$suggestions"
    echo "- 午休时间 12-13 点" >> "$suggestions"
    echo "- 晚上 20-22 点（休息时间）" >> "$suggestions"
    echo "- 周末下午 14-17 点" >> "$suggestions"
    echo "" >> "$suggestions"

    echo "$suggestions"
}

# Function to generate platform-specific content examples
generate_platform_content_examples() {
    local content_dir=$1
    local valuable_content_file=$2
    local platform_examples=$(mktemp)

    echo "📱 正在生成平台专属内容示例..." >&2

    echo "## 📲 平台专属内容示例" > "$platform_examples"
    echo "" >> "$platform_examples"

    # Extract a sample insight from valuable content for examples
    local sample_insight=""
    if [ -f "$valuable_content_file" ] && [ -s "$valuable_content_file" ]; then
        sample_insight=$(grep -E "^- " "$valuable_content_file" | head -1 | sed 's/^- //')
    fi

    if [ -z "$sample_insight" ]; then
        sample_insight="今天体验了一个AI工具，发现它的用户体验设计非常出色，特别是在引导新用户方面的处理"
    fi

    # Xiaohongshu version
    echo "### 🍃 小红书版本" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo '```' >> "$platform_examples"
    echo "🚀 又发现一个宝藏AI工具！" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "姐妹们，今天必须要分享这个发现！" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "✨ $sample_insight" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "🔥 最让我惊喜的几个点：" >> "$platform_examples"
    echo "1️⃣ 界面设计超级简洁好看" >> "$platform_examples"
    echo "2️⃣ 新手引导做得特别贴心" >> "$platform_examples"
    echo "3️⃣ 功能强大但不会让人觉得复杂" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "💡 适合人群：" >> "$platform_examples"
    echo "• 想要提升工作效率的打工人" >> "$platform_examples"
    echo "• 对AI工具感兴趣的小伙伴" >> "$platform_examples"
    echo "• 追求美感和实用性的完美主义者" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "评分：⭐⭐⭐⭐⭐" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "你们还有什么好用的AI工具推荐吗？评论区见👇" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "#AI工具 #效率神器 #产品体验 #科技分享 #学习笔记" >> "$platform_examples"
    echo '```' >> "$platform_examples"
    echo "" >> "$platform_examples"

    # Weibo version
    echo "### 🐦 微博版本" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo '```' >> "$platform_examples"
    echo "💡 产品观察：$sample_insight" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "作为一个产品爱好者，今天深度体验了这个AI工具，几个值得思考的点：" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "1. 用户引导的力量：好的引导能让复杂功能变得易懂" >> "$platform_examples"
    echo "2. 设计的温度感：技术产品也需要人文关怀" >> "$platform_examples"
    echo "3. 功能与简洁的平衡：克制比堆砌更需要智慧" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "这让我想到，AI时代的产品设计，除了技术领先，用户体验的细节往往决定成败。" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "你觉得一个AI产品最重要的是什么？技术还是体验？" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "#产品思考 #AI工具 #用户体验 #产品设计 #科技观察" >> "$platform_examples"
    echo '```' >> "$platform_examples"
    echo "" >> "$platform_examples"

    # LinkedIn version
    echo "### 💼 LinkedIn版本" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo '```' >> "$platform_examples"
    echo "🎯 Product Insights: What Makes AI Tools Truly User-Friendly?" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "After spending time with a new AI tool today, I was struck by how thoughtful user onboarding can transform the entire experience." >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "Key observations:" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "🔸 Progressive Disclosure: Complex features introduced gradually" >> "$platform_examples"
    echo "🔸 Contextual Guidance: Help appears exactly when and where needed" >> "$platform_examples"
    echo "🔸 Emotional Design: The interface feels approachable, not intimidating" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "This reinforces something I've been thinking about: In the AI era, technical capability is just table stakes. The real differentiator is how seamlessly we can integrate these powerful tools into human workflows." >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "For product teams building in this space:" >> "$platform_examples"
    echo "• Invest heavily in onboarding design" >> "$platform_examples"
    echo "• Test with real users, not just tech-savvy early adopters" >> "$platform_examples"
    echo "• Remember that complexity should be hidden, not eliminated" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "What's your experience with AI tool adoption in your organization? What barriers have you encountered?" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "#ProductManagement #AITools #UserExperience #TechInnovation #ProductDesign" >> "$platform_examples"
    echo '```' >> "$platform_examples"
    echo "" >> "$platform_examples"

    # Twitter version
    echo "### 🐦 Twitter版本" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo '```' >> "$platform_examples"
    echo "🧵 Thread: Why this AI tool's onboarding is chef's kiss 👨‍🍳💋" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "1/ Just experienced something rare in AI tools: actually good UX design" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "2/ The onboarding didn't dump 50 features on me at once. Instead, it showed me one thing, let me succeed, then gradually revealed more" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "3/ The UI feels warm and approachable. No intimidating command lines or dense feature grids. Just clean, intuitive design that gets out of your way" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "4/ Hot take: We're in an AI tool bubble where everyone's competing on features, but the real winners will be those who nail the human experience" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "5/ For builders: Your AI can be GPT-5 level, but if users bounce in the first 30 seconds, none of that matters" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "What's the best-designed AI tool you've used? 👇" >> "$platform_examples"
    echo "" >> "$platform_examples"
    echo "#AI #ProductDesign #UX #BuildInPublic" >> "$platform_examples"
    echo '```' >> "$platform_examples"
    echo "" >> "$platform_examples"

    echo "$platform_examples"
}

# Function to create content templates
create_content_templates() {
    local valuable_content_file=$1
    local templates=$(mktemp)

    echo "📋 正在创建内容模板..." >&2

    echo "## 📄 内容创作模板" > "$templates"
    echo "" >> "$templates"

    # Learning summary template
    echo "### 📊 学习总结模板" >> "$templates"
    echo "" >> "$templates"
    echo '```' >> "$templates"
    echo "📚 这周的学习收获 #学习记录 #AI学习" >> "$templates"
    echo "" >> "$templates"
    echo "本周重点学习了：" >> "$templates"
    echo "🔸 [技术/工具名称] - [简短描述]" >> "$templates"
    echo "🔸 [重要概念] - [个人理解]" >> "$templates"
    echo "🔸 [实践项目] - [具体成果]" >> "$templates"
    echo "" >> "$templates"
    echo "💡 最大的收获：" >> "$templates"
    echo "[写出最有价值的洞察或体验]" >> "$templates"
    echo "" >> "$templates"
    echo "🎯 下周计划：" >> "$templates"
    echo "[简述下周学习重点]" >> "$templates"
    echo "" >> "$templates"
    echo "#持续学习 #技术成长 #个人发展" >> "$templates"
    echo '```' >> "$templates"
    echo "" >> "$templates"

    # Tool review template
    echo "### 🔧 工具体验模板" >> "$templates"
    echo "" >> "$templates"
    echo '```' >> "$templates"
    echo "🛠️ [工具名称]体验分享 #工具推荐" >> "$templates"
    echo "" >> "$templates"
    echo "✨ 亮点功能：" >> "$templates"
    echo "• [功能1] - [具体体验]" >> "$templates"
    echo "• [功能2] - [使用感受]" >> "$templates"
    echo "• [功能3] - [实际价值]" >> "$templates"
    echo "" >> "$templates"
    echo "👍 推荐指数：⭐⭐⭐⭐⭐" >> "$templates"
    echo "💰 付费情况：[免费/付费]" >> "$templates"
    echo "🎯 适用场景：[具体应用场景]" >> "$templates"
    echo "" >> "$templates"
    echo "总结：[一句话总结工具价值]" >> "$templates"
    echo "" >> "$templates"
    echo "#效率工具 #产品体验 #生产力" >> "$templates"
    echo '```' >> "$templates"
    echo "" >> "$templates"

    # Insight sharing template
    echo "### 💡 思考分享模板" >> "$templates"
    echo "" >> "$templates"
    echo '```' >> "$templates"
    echo "🤔 关于[话题]的一些思考" >> "$templates"
    echo "" >> "$templates"
    echo "最近在学习/使用[具体内容]的过程中，有一个有趣的发现：" >> "$templates"
    echo "" >> "$templates"
    echo "[核心观点或洞察]" >> "$templates"
    echo "" >> "$templates"
    echo "这让我想到：" >> "$templates"
    echo "• [延伸思考1]" >> "$templates"
    echo "• [延伸思考2]" >> "$templates"
    echo "• [实际应用]" >> "$templates"
    echo "" >> "$templates"
    echo "你们怎么看？欢迎在评论区分享你的想法👇" >> "$templates"
    echo "" >> "$templates"
    echo "#深度思考 #行业洞察 #互动讨论" >> "$templates"
    echo '```' >> "$templates"
    echo "" >> "$templates"

    echo "$templates"
}

# Function to perform AI-powered content analysis using Claude Code
ai_enhanced_analysis() {
    local content_dir=$1
    local ai_insights=$(mktemp)

    echo "🤖 正在进行AI深度分析..." >&2

    # Combine all content for AI analysis
    local combined_content=$(mktemp)
    echo "## 学习内容汇总" > "$combined_content"
    echo "" >> "$combined_content"

    for content_type in braindump output newsletter video review; do
        local content_file=$(cat "$content_dir/${content_type}_path" 2>/dev/null)
        if [ -f "$content_file" ] && [ -s "$content_file" ]; then
            echo "### ${content_type} 内容" >> "$combined_content"
            echo "" >> "$combined_content"
            cat "$content_file" >> "$combined_content"
            echo "" >> "$combined_content"
        fi
    done

    # Create AI analysis prompt
    local ai_prompt=$(mktemp)
    cat > "$ai_prompt" << 'EOF'
请分析以下学习记录内容，为社交媒体创作提供深度洞察和建议。

分析要求：
1. 识别最具传播价值的观点和经验
2. 提取可以引起共鸣的话题和痛点
3. 发现独特的见解和有趣的角度
4. 评估内容的病毒传播潜力
5. 提供具体的创作建议和标题示例

请从以下维度进行分析：
- 内容价值度（1-10分）
- 传播潜力（1-10分）
- 目标受众分析
- 推荐的发布平台
- 具体的文案建议（提供3个不同风格的版本）
- 配图建议
- 发布时机建议

学习内容：
EOF

    # Append content to prompt
    cat "$combined_content" >> "$ai_prompt"

    echo "## 🧠 AI 深度分析报告" > "$ai_insights"
    echo "" >> "$ai_insights"

    # Check if Claude Code environment allows AI analysis
    if command -v claude >/dev/null 2>&1; then
        echo "🔄 调用AI分析引擎..." >&2

        # Use Claude Code's AI capabilities
        local ai_response=$(claude analyze "$(cat "$ai_prompt")" 2>/dev/null || echo "AI分析服务暂时不可用")

        if [ "$ai_response" = "AI分析服务暂时不可用" ]; then
            echo "⚠️ AI分析功能需要在Claude Code环境中使用" >&2
            echo "### ⚠️ AI分析说明" >> "$ai_insights"
            echo "" >> "$ai_insights"
            echo "AI深度分析功能需要在Claude Code环境中使用。请在Claude Code中运行此命令以获得：" >> "$ai_insights"
            echo "" >> "$ai_insights"
            echo "- 🎯 内容价值评估和传播潜力分析" >> "$ai_insights"
            echo "- 👥 目标受众画像和平台推荐" >> "$ai_insights"
            echo "- ✍️ 多风格文案建议和标题优化" >> "$ai_insights"
            echo "- 🖼️ 配图方向和视觉呈现建议" >> "$ai_insights"
            echo "- ⏰ 最佳发布时机和策略建议" >> "$ai_insights"
            echo "" >> "$ai_insights"
        else
            echo "$ai_response" >> "$ai_insights"
        fi
    else
        # Fallback: provide structured analysis framework
        echo "### 📊 AI分析框架（手动填写）" >> "$ai_insights"
        echo "" >> "$ai_insights"
        echo "**内容价值评估：**" >> "$ai_insights"
        echo "- 🎯 核心价值点：[待分析]" >> "$ai_insights"
        echo "- 💡 独特见解：[待分析]" >> "$ai_insights"
        echo "- 🔥 传播潜力：[1-10分]" >> "$ai_insights"
        echo "" >> "$ai_insights"

        echo "**目标受众分析：**" >> "$ai_insights"
        echo "- 👨‍💼 主要受众：[群体描述]" >> "$ai_insights"
        echo "- 📱 推荐平台：[平台选择+理由]" >> "$ai_insights"
        echo "- 🎨 内容风格：[风格建议]" >> "$ai_insights"
        echo "" >> "$ai_insights"

        echo "**创作建议：**" >> "$ai_insights"
        echo "- 📝 标题方向：" >> "$ai_insights"
        echo "  1. [吸引眼球版本]" >> "$ai_insights"
        echo "  2. [专业深度版本]" >> "$ai_insights"
        echo "  3. [互动讨论版本]" >> "$ai_insights"
        echo "- 🖼️ 配图建议：[视觉方向]" >> "$ai_insights"
        echo "- ⏰ 发布时机：[具体时间+理由]" >> "$ai_insights"
        echo "" >> "$ai_insights"

        echo "💡 **使用提示**: 在Claude Code环境中运行 \`/insight --ai-analysis\` 可获得自动化AI分析" >> "$ai_insights"
    fi

    # Cleanup
    rm -f "$combined_content" "$ai_prompt"
    echo "$ai_insights"
}

# Function to generate the final insight report
generate_insight_report() {
    local content_dir=$1
    local keywords_file=$2
    local valuable_content_file=$3
    local suggestions_file=$4
    local templates_file=$5
    local ai_insights_file=$6
    local platform_examples_file=$7

    local analyzed_count=$(cat "$content_dir/analyzed_count" 2>/dev/null || echo "0")
    local current_date=$(date +"%Y年%m月%d日")

    echo "# 🎯 Insight Report - $current_date"
    echo ""

    # Analysis summary
    echo "## 📈 分析摘要"
    echo ""
    echo "- **分析范围**: "
    if [ "$ALL_CONTENT" = true ]; then
        echo "所有历史内容"
    elif [ ! -z "$DAYS" ]; then
        echo "最近 $DAYS 天"
    elif [ ! -z "$WEEKS" ]; then
        echo "最近 $WEEKS 周"
    fi
    echo "- **分析文件数**: $analyzed_count 个学习记录"
    echo "- **主题焦点**: ${TOPIC:-"全部主题"}"
    echo "- **目标平台**: ${PLATFORM:-"通用平台"}"
    echo ""

    # Include AI insights if available
    if [ -f "$ai_insights_file" ] && [ -s "$ai_insights_file" ]; then
        cat "$ai_insights_file"
        echo ""
    fi

    # Include valuable content
    if [ -f "$valuable_content_file" ] && [ -s "$valuable_content_file" ]; then
        cat "$valuable_content_file"
        echo ""
    fi

    # Include social media suggestions
    if [ -f "$suggestions_file" ] && [ -s "$suggestions_file" ]; then
        cat "$suggestions_file"
        echo ""
    fi

    # Include content templates
    if [ -f "$templates_file" ] && [ -s "$templates_file" ]; then
        cat "$templates_file"
        echo ""
    fi

    # Include platform-specific examples
    if [ -f "$platform_examples_file" ] && [ -s "$platform_examples_file" ]; then
        cat "$platform_examples_file"
        echo ""
    fi

    # Keyword analysis
    if [ -f "$keywords_file" ] && [ -s "$keywords_file" ]; then
        echo "## 📊 关键词分析"
        echo ""
        echo "### 🔥 热门关键词排行"
        echo ""

        # Top 15 keywords
        sort -t':' -k2 -nr "$keywords_file" | head -15 | while IFS=':' read -r keyword count source; do
            echo "- **$keyword** (出现 $count 次，来源: $source)"
        done
        echo ""

        # Keywords by category
        echo "### 📂 分类关键词统计"
        echo ""

        for category in video newsletter braindump output review; do
            local category_count=$(grep ":$category$" "$keywords_file" | wc -l | tr -d ' ')
            if [ "$category_count" -gt 0 ]; then
                echo "**${category} 相关关键词 ($category_count 个):**"
                grep ":$category$" "$keywords_file" | sort -t':' -k2 -nr | head -5 | while IFS=':' read -r keyword count source; do
                    echo "- $keyword ($count)"
                done
                echo ""
            fi
        done
    fi

    # Next steps
    echo "## 🎯 下一步行动建议"
    echo ""
    echo "### 📅 内容创作计划"
    echo ""
    echo "- **本周重点**: 选择1-2个高价值内容片段，制作成社交媒体帖子"
    echo "- **内容日程**: "
    echo "  - 周一：发布学习总结类内容"
    echo "  - 周三：分享工具体验或产品评测"
    echo "  - 周五：发布思考洞察类内容"
    echo "- **互动策略**: 在帖子中加入问题，鼓励读者评论和分享"
    echo "- **内容优化**: 根据不同平台特点调整内容格式和长度"
    echo ""

    echo "### 🔄 持续改进"
    echo ""
    echo "- 定期使用 \`/insight\` 命令分析学习内容（建议每周一次）"
    echo "- 跟踪发布内容的反馈和互动数据"
    echo "- 根据受众反应调整内容主题和风格"
    echo "- 建立内容素材库，积累可复用的观点和金句"
    echo ""

    # Footer
    echo "---"
    echo "*本报告由 /insight 命令自动生成，基于您的学习记录分析*"
}

# Main function
main() {
    echo "🎯 启动内容洞察分析..." >&2

    # Extract learning content
    local content_dir=$(extract_learning_content)

    # Analyze themes and keywords
    local keywords_file=$(analyze_content_themes "$content_dir")

    # Identify valuable content
    local valuable_content_file=$(identify_valuable_content "$content_dir")

    # Generate social media suggestions
    local suggestions_file=$(generate_social_media_suggestions "$content_dir" "$keywords_file" "$valuable_content_file")

    # Create content templates
    local templates_file=$(create_content_templates "$valuable_content_file")

    # Generate platform-specific content examples
    local platform_examples_file=$(generate_platform_content_examples "$content_dir" "$valuable_content_file")

    # Perform AI analysis if requested
    local ai_insights_file=""
    if [ "$AI_ANALYSIS" = true ]; then
        ai_insights_file=$(ai_enhanced_analysis "$content_dir")
    fi

    # Generate final report
    echo "📝 正在生成最终报告..." >&2
    local report_content=$(generate_insight_report "$content_dir" "$keywords_file" "$valuable_content_file" "$suggestions_file" "$templates_file" "$ai_insights_file" "$platform_examples_file")

    # Output the report
    if [ ! -z "$SAVE_TO_FILE" ]; then
        echo "$report_content" > "$SAVE_TO_FILE"
        echo "✅ 洞察报告已保存到: $SAVE_TO_FILE" >&2
    else
        echo "$report_content"
    fi

    echo "🎉 分析完成！" >&2

    # Cleanup temporary files
    rm -rf "$content_dir"
    [ -f "$keywords_file" ] && rm -f "$keywords_file"
    [ -f "$valuable_content_file" ] && rm -f "$valuable_content_file"
    [ -f "$suggestions_file" ] && rm -f "$suggestions_file"
    [ -f "$templates_file" ] && rm -f "$templates_file"
    [ -f "$platform_examples_file" ] && rm -f "$platform_examples_file"
    [ -f "$ai_insights_file" ] && rm -f "$ai_insights_file"
}

# Execute main function
main
```