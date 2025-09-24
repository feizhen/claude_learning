# Daily Review Command

Reviews the current day's markdown file content and updates the `## review` section with a comprehensive summary including learning habits analysis and content insights.

```bash
#!/bin/bash

# Set locale to avoid Chinese date format issues
export LC_ALL=C

# Get day of week (1=Monday, 7=Sunday)
dow=$(date +%u)

# Calculate days to Monday (if today is Monday, days_to_monday=0)
days_to_monday=$((dow - 1))

# Get Monday's date using simple date arithmetic
monday_formatted=$(date -v-${days_to_monday}d +%m%d)
monday_year=$(date -v-${days_to_monday}d +%Y)

# Get Sunday's date (6 days after Monday)
sunday_days=$((6 - days_to_monday))
sunday_formatted=$(date -v+${sunday_days}d +%m%d)

folder_name="${monday_year}_${monday_formatted}-${sunday_formatted}"

# Format daily file name: YYYY_MM_DD.md
daily_file="weeks/$folder_name/$(date +%Y_%m_%d).md"

# Check if daily file exists
if [ ! -f "$daily_file" ]; then
    echo "Daily file does not exist: $daily_file"
    echo "Please run /daily-start first to create the daily file."
    exit 1
fi

echo "Reading and analyzing content from: $daily_file"

# Read current file content and extract sections
video_content=$(sed -n '/^## video$/,/^## /p' "$daily_file" | sed '$d' | tail -n +2)
newsletter_content=$(sed -n '/^## newsletter$/,/^## /p' "$daily_file" | sed '$d' | tail -n +2)
braindump_content=$(sed -n '/^## braindump$/,/^## /p' "$daily_file" | sed '$d' | tail -n +2)
output_content=$(sed -n '/^## output$/,/^## /p' "$daily_file" | sed '$d' | tail -n +2)
todo_content=$(sed -n '/^## TODO$/,/^## /p' "$daily_file" | sed '$d' | tail -n +2)
waytoace_content=$(sed -n '/^## WayToAce$/,/^## /p' "$daily_file" | sed '$d' | tail -n +2)

# Function to analyze learning habits
analyze_learning_habits() {
    local habits_score=0
    local habits_details=""
    local content_diversity=0

    # Check content diversity and completeness
    if [ -n "$video_content" ]; then
        content_diversity=$((content_diversity + 1))
        habits_details="${habits_details}- ✅ 视频学习：包含实用的学习视频内容\n"
    else
        habits_details="${habits_details}- ⚪ 视频学习：今日未观看学习视频\n"
    fi

    if [ -n "$newsletter_content" ]; then
        content_diversity=$((content_diversity + 1))
        habits_details="${habits_details}- ✅ 阅读输入：关注行业动态和知识更新\n"
    else
        habits_details="${habits_details}- ⚪ 阅读输入：今日未进行阅读学习\n"
    fi

    if [ -n "$braindump_content" ]; then
        content_diversity=$((content_diversity + 1))
        local braindump_lines=$(echo "$braindump_content" | grep -c '^-' || echo "0")
        if [ "$braindump_lines" -ge 3 ]; then
            habits_details="${habits_details}- ✅ 深度思考：记录了丰富的思考和洞察 ($braindump_lines 条)\n"
        else
            habits_details="${habits_details}- ⚠️ 深度思考：有思考记录但相对较少 ($braindump_lines 条)\n"
        fi
    else
        habits_details="${habits_details}- ⚪ 深度思考：今日缺少思考和洞察记录\n"
    fi

    if [ -n "$output_content" ]; then
        content_diversity=$((content_diversity + 1))
        habits_details="${habits_details}- ✅ 学习输出：有实际的学习成果产出\n"
    else
        habits_details="${habits_details}- ⚪ 学习输出：今日未产生学习输出\n"
    fi

    # Calculate overall score
    habits_score=$((content_diversity * 25))

    echo "学习习惯评估 (${habits_score}/100分):"
    echo -e "$habits_details"

    # Add learning habit insights
    if [ "$content_diversity" -ge 3 ]; then
        echo "🎯 **学习状态**: 今日学习内容均衡，输入输出兼备，学习习惯良好"
    elif [ "$content_diversity" -ge 2 ]; then
        echo "📈 **学习状态**: 今日学习有一定成效，建议补充缺失的学习维度"
    else
        echo "🔄 **学习状态**: 今日学习内容较少，建议明日加强学习投入"
    fi

    return $content_diversity
}

# Function to extract key insights from content
extract_content_insights() {
    local insights=""

    # Extract video learning insights
    if [ -n "$video_content" ]; then
        local video_titles=$(echo "$video_content" | grep -E "^\s*-\s*\[.*\]" | sed 's/^\s*-\s*\[\(.*\)\].*/\1/' | head -3)
        if [ -n "$video_titles" ]; then
            insights="${insights}**视频学习重点:**\n"
            echo "$video_titles" | while read -r title; do
                [ -n "$title" ] && insights="${insights}- $title\n"
            done
            insights="${insights}\n"
        fi
    fi

    # Extract braindump insights
    if [ -n "$braindump_content" ]; then
        local key_insights=$(echo "$braindump_content" | grep -i "insights:" -A 10 | tail -n +2 | head -5)
        if [ -n "$key_insights" ]; then
            insights="${insights}**关键洞察:**\n$key_insights\n\n"
        fi

        # Extract product thoughts
        local product_thoughts=$(echo "$braindump_content" | grep -E "(产品|体验|用户|功能)" | head -3)
        if [ -n "$product_thoughts" ]; then
            insights="${insights}**产品思考:**\n$product_thoughts\n\n"
        fi
    fi

    # Extract project progress
    if [ -n "$waytoace_content" ]; then
        insights="${insights}**WayToAce 项目进展:**\n$waytoace_content\n\n"
    fi

    # Extract completed todos
    if [ -n "$todo_content" ]; then
        local completed_todos=$(echo "$todo_content" | grep "\[x\]" | head -3)
        if [ -n "$completed_todos" ]; then
            insights="${insights}**今日完成:**\n$completed_todos\n\n"
        fi
    fi

    echo -e "$insights"
}

# Function to generate learning recommendations
generate_recommendations() {
    local diversity=$1
    local recommendations=""

    recommendations="**明日建议:**\n"

    if [ -z "$video_content" ]; then
        recommendations="${recommendations}- 📹 考虑观看1-2个技术相关视频或教程\n"
    fi

    if [ -z "$newsletter_content" ]; then
        recommendations="${recommendations}- 📰 阅读行业newsletter或技术文章\n"
    fi

    if [ -z "$braindump_content" ] || [ $(echo "$braindump_content" | wc -l) -lt 3 ]; then
        recommendations="${recommendations}- 💭 增加深度思考，记录更多洞察和想法\n"
    fi

    if [ -z "$output_content" ]; then
        recommendations="${recommendations}- 📝 尝试将学习内容转化为具体输出\n"
    fi

    # General recommendations based on patterns
    if [ -n "$braindump_content" ] && echo "$braindump_content" | grep -q "产品"; then
        recommendations="${recommendations}- 🚀 继续深化产品思维和用户体验思考\n"
    fi

    if [ -n "$waytoace_content" ]; then
        recommendations="${recommendations}- 🎯 持续推进 WayToAce 项目关键功能开发\n"
    fi

    echo -e "$recommendations"
}

# Check if review section already exists
if grep -q "## review" "$daily_file"; then
    echo "Review section already exists in $daily_file"
    echo "Would you like to regenerate it? (Current content shown below)"
    sed -n '/## review/,$p' "$daily_file"

    # Ask user if they want to regenerate
    read -p "Regenerate review section? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing review section and regenerate
        sed -i '' '/^## review$/,$d' "$daily_file"
        echo "Removed existing review section. Generating new one..."
    else
        echo "Keeping existing review section."
        exit 0
    fi
fi

# Generate comprehensive review
echo "" >> "$daily_file"
echo "## review" >> "$daily_file"
echo "" >> "$daily_file"

# Check if there's any content to analyze
if [ -n "$video_content" ] || [ -n "$newsletter_content" ] || [ -n "$braindump_content" ] || [ -n "$output_content" ] || [ -n "$todo_content" ] || [ -n "$waytoace_content" ]; then

    echo "**今日学习活动总结:**" >> "$daily_file"
    echo "" >> "$daily_file"

    # Add basic activity summary
    activity_count=0

    if [ -n "$video_content" ]; then
        video_count=$(echo "$video_content" | grep -c "^\s*-" || echo "0")
        echo "- **视频学习**: 观看了技术相关视频和教程内容" >> "$daily_file"
        activity_count=$((activity_count + 1))
    fi

    if [ -n "$newsletter_content" ]; then
        newsletter_items=$(echo "$newsletter_content" | grep -c "\[x\]" || echo "0")
        echo "- **文章阅读**: 完成了 $newsletter_items 项阅读任务" >> "$daily_file"
        activity_count=$((activity_count + 1))
    fi

    if [ -n "$braindump_content" ]; then
        braindump_items=$(echo "$braindump_content" | grep -c "^-" || echo "0")
        echo "- **深度思考**: 记录了 $braindump_items 条思考和洞察" >> "$daily_file"
        activity_count=$((activity_count + 1))
    fi

    if [ -n "$output_content" ]; then
        echo "- **学习输出**: 产生了具体的学习成果和项目进展" >> "$daily_file"
        activity_count=$((activity_count + 1))
    fi

    if [ -n "$waytoace_content" ]; then
        echo "- **项目推进**: WayToAce 项目取得新进展" >> "$daily_file"
        activity_count=$((activity_count + 1))
    fi

    if [ -n "$todo_content" ]; then
        completed_count=$(echo "$todo_content" | grep -c "\[x\]" || echo "0")
        if [ "$completed_count" -gt 0 ]; then
            echo "- **任务完成**: 完成了 $completed_count 项计划任务" >> "$daily_file"
        fi
    fi

    echo "" >> "$daily_file"

    # Add learning habits analysis
    analyze_learning_habits >> "$daily_file"
    echo "" >> "$daily_file"

    # Add content insights
    insights=$(extract_content_insights)
    if [ -n "$insights" ]; then
        echo "**主要收获:**" >> "$daily_file"
        echo "$insights" >> "$daily_file"
    fi

    # Add recommendations
    diversity_score=0
    [ -n "$video_content" ] && diversity_score=$((diversity_score + 1))
    [ -n "$newsletter_content" ] && diversity_score=$((diversity_score + 1))
    [ -n "$braindump_content" ] && diversity_score=$((diversity_score + 1))
    [ -n "$output_content" ] && diversity_score=$((diversity_score + 1))

    generate_recommendations $diversity_score >> "$daily_file"

else
    echo "**今日学习记录为空**" >> "$daily_file"
    echo "" >> "$daily_file"
    echo "建议明日开始记录学习内容，包括：" >> "$daily_file"
    echo "- 📹 观看的学习视频" >> "$daily_file"
    echo "- 📰 阅读的文章和资讯" >> "$daily_file"
    echo "- 💭 思考和洞察记录" >> "$daily_file"
    echo "- 📝 学习输出和项目进展" >> "$daily_file"
fi

echo ""
echo "✅ Successfully added comprehensive daily review to $daily_file"
echo ""
echo "Review includes:"
echo "- 📊 Learning habits analysis with scoring"
echo "- 🧠 Key insights extraction from content"
echo "- 📈 Personalized recommendations for tomorrow"
echo "- 🎯 Project progress tracking"
```