# Milestone Report Command

Generates a comprehensive milestone report based on learning progress, comparing objectives from `objective.md` with actual learning records from `weeks/` directory.

```bash
#!/bin/bash

# Set locale to avoid date formatting issues
export LC_ALL=C

# Default values
SAVE_TO_FILE=""
TARGET_MONTH=""
OUTPUT_FORMAT="markdown"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --save)
            SAVE_TO_FILE="$2"
            shift 2
            ;;
        --month)
            TARGET_MONTH="$2"
            shift 2
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: /milestone [--save filename] [--month X] [--format markdown|json]"
            exit 1
            ;;
    esac
done

# Function to get current date in various formats
get_current_date() {
    date +"%Y-%m-%d"
}

get_formatted_date() {
    date +"%Y年%m月%d日"
}

# Function to calculate learning start date (from earliest file in weeks/)
get_learning_start_date() {
    local earliest_file=$(find weeks/ -name "????_??_??.md" -type f | sort | head -1)
    if [ -z "$earliest_file" ]; then
        echo "2025-09-15"  # Default start date if no files found
        return
    fi

    # Extract date from filename (YYYY_MM_DD.md)
    local filename=$(basename "$earliest_file" .md)
    local year=$(echo "$filename" | cut -d'_' -f1)
    local month=$(echo "$filename" | cut -d'_' -f2)
    local day=$(echo "$filename" | cut -d'_' -f3)

    echo "$year-$month-$day"
}

# Function to calculate months since start
calculate_current_month() {
    local start_date=$(get_learning_start_date)
    local current_date=$(get_current_date)

    local start_year=$(echo "$start_date" | cut -d'-' -f1)
    local start_month=$(echo "$start_date" | cut -d'-' -f2 | sed 's/^0*//')
    local current_year=$(echo "$current_date" | cut -d'-' -f1)
    local current_month=$(echo "$current_date" | cut -d'-' -f2 | sed 's/^0*//')

    local months_diff=$(( (current_year - start_year) * 12 + current_month - start_month ))

    # Return month number (0-based, so month 1 in plan = 0 months passed)
    echo $((months_diff + 1))
}

# Function to extract monthly goals from objective.md
extract_monthly_goals() {
    local month_num=$1

    if [ ! -f "objective.md" ]; then
        echo "目标文件 objective.md 未找到"
        return 1
    fi

    # Extract goals for specific month range based on current progress
    if [ "$month_num" -le 3 ]; then
        # Months 1-3: 基础巩固 + 快速产出
        sed -n '/月 1–3（基础巩固 + 快速产出）/,/月 4–6/p' objective.md | sed '$d' | tail -n +2
    elif [ "$month_num" -le 6 ]; then
        # Months 4-6: 进阶能力 + 用户/业务理解
        sed -n '/月 4–6（进阶能力 + 用户/,/月 7–9/p' objective.md | sed '$d' | tail -n +2
    elif [ "$month_num" -le 9 ]; then
        # Months 7-9: 扩大影响 + 学术/行业深度
        sed -n '/月 7–9（扩大影响 + 学术/,/月 10–12/p' objective.md | sed '$d' | tail -n +2
    else
        # Months 10-12: 包装、面试准备、跳槽/转岗
        sed -n '/月 10–12（包装、面试准备/,/四、每月/p' objective.md | sed '$d' | tail -n +2
    fi
}

# Function to aggregate learning content from weeks/
aggregate_learning_content() {
    local temp_file=$(mktemp)
    local video_count=0
    local newsletter_count=0
    local braindump_entries=0
    local active_learning_days=0
    local project_outputs=0

    echo "## 学习内容汇总" > "$temp_file"
    echo "" >> "$temp_file"

    # Find all daily files and process them
    local daily_files=$(find weeks/ -name "????_??_??.md" -type f | sort)

    if [ -z "$daily_files" ]; then
        echo "未找到学习记录文件" >> "$temp_file"
        echo "$temp_file"
        return
    fi

    # Track days with actual learning content (using space-separated list for bash 3.2 compatibility)
    local learning_days_list=""

    echo "### 视频学习" >> "$temp_file"
    for file in $daily_files; do
        if grep -q "## video" "$file"; then
            local video_content=$(sed -n '/## video/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d')
            if [ ! -z "$video_content" ]; then
                local file_date=$(basename "$file" .md | sed 's/_/-/g')
                echo "**$file_date:**" >> "$temp_file"
                echo "$video_content" >> "$temp_file"
                echo "" >> "$temp_file"
                video_count=$((video_count + 1))
                learning_days_list="$learning_days_list $file_date"
            fi
        fi
    done

    echo "### 文章阅读" >> "$temp_file"
    for file in $daily_files; do
        if grep -q "## newsletter" "$file"; then
            local newsletter_content=$(sed -n '/## newsletter/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d')
            if [ ! -z "$newsletter_content" ]; then
                local file_date=$(basename "$file" .md | sed 's/_/-/g')
                echo "**$file_date:**" >> "$temp_file"
                echo "$newsletter_content" >> "$temp_file"
                echo "" >> "$temp_file"
                newsletter_count=$((newsletter_count + 1))
                learning_days_list="$learning_days_list $file_date"
            fi
        fi
    done

    echo "### 思考与想法" >> "$temp_file"
    for file in $daily_files; do
        if grep -q "## braindump" "$file"; then
            local braindump_content=$(sed -n '/## braindump/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d')
            if [ ! -z "$braindump_content" ]; then
                local file_date=$(basename "$file" .md | sed 's/_/-/g')
                echo "**$file_date:**" >> "$temp_file"
                echo "$braindump_content" >> "$temp_file"
                echo "" >> "$temp_file"
                braindump_entries=$((braindump_entries + 1))
                learning_days_list="$learning_days_list $file_date"
            fi
        fi
    done

    # Count actual learning days (count unique days from the list)
    active_learning_days=$(echo "$learning_days_list" | tr ' ' '\n' | sort -u | grep -v '^$' | wc -l | tr -d ' ')

    # Count project outputs (look for keywords like "项目", "产品", "案例", "demo", "MVP" etc.)
    project_outputs=$(grep -r -i -E "(项目|产品|案例|demo|mvp|实现|开发|搭建)" weeks/ --include="*.md" | wc -l | tr -d ' ')

    # Store statistics in temporary variables for later use
    echo "$video_count" > /tmp/milestone_video_count
    echo "$newsletter_count" > /tmp/milestone_newsletter_count
    echo "$braindump_entries" > /tmp/milestone_braindump_count
    echo "$active_learning_days" > /tmp/milestone_total_days
    echo "$project_outputs" > /tmp/milestone_project_count

    echo "$temp_file"
}

# Function to evaluate learning habits
evaluate_learning_habits() {
    local temp_file=$(mktemp)
    echo "## 📈 学习习惯评估" > "$temp_file"
    echo "" >> "$temp_file"

    # Get statistics
    local video_count=$(cat /tmp/milestone_video_count 2>/dev/null || echo "0")
    local newsletter_count=$(cat /tmp/milestone_newsletter_count 2>/dev/null || echo "0")
    local braindump_count=$(cat /tmp/milestone_braindump_count 2>/dev/null || echo "0")
    local total_days=$(cat /tmp/milestone_total_days 2>/dev/null || echo "0")
    local project_count=$(cat /tmp/milestone_project_count 2>/dev/null || echo "0")

    # Calculate time since start
    local start_date=$(get_learning_start_date)
    local current_date=$(get_current_date)
    # Calculate days since start (compatible with both BSD and GNU date)
    local current_epoch start_epoch days_since_start
    if date -j -f "%Y-%m-%d" "$current_date" +%s >/dev/null 2>&1; then
        # BSD date (macOS)
        current_epoch=$(date -j -f "%Y-%m-%d" "$current_date" +%s)
        start_epoch=$(date -j -f "%Y-%m-%d" "$start_date" +%s)
    else
        # GNU date (Linux)
        current_epoch=$(date -d "$current_date" +%s)
        start_epoch=$(date -d "$start_date" +%s)
    fi
    days_since_start=$(( ( current_epoch - start_epoch ) / 86400 + 1 ))

    # 1. 一致性指标
    echo "### 一致性评估" >> "$temp_file"
    echo "" >> "$temp_file"

    local learning_frequency_pct=0
    if [ "$days_since_start" -gt 0 ]; then
        learning_frequency_pct=$(( total_days * 100 / days_since_start ))
    fi

    echo "- **学习频率**: ${learning_frequency_pct}% (${total_days}/${days_since_start} 天)" >> "$temp_file"

    if [ "$learning_frequency_pct" -ge 80 ]; then
        echo "  - ✅ 学习频率很高，保持良好习惯" >> "$temp_file"
    elif [ "$learning_frequency_pct" -ge 60 ]; then
        echo "  - ⚠️ 学习频率中等，可以进一步提升" >> "$temp_file"
    else
        echo "  - ❌ 学习频率偏低，需要建立更规律的学习习惯" >> "$temp_file"
    fi

    # Content balance assessment
    local total_content_entries=$((video_count + newsletter_count + braindump_count))
    echo "- **内容平衡度**:" >> "$temp_file"

    if [ "$total_content_entries" -gt 0 ]; then
        local video_pct=$((video_count * 100 / total_content_entries))
        local newsletter_pct=$((newsletter_count * 100 / total_content_entries))
        local braindump_pct=$((braindump_count * 100 / total_content_entries))

        echo "  - 视频学习: ${video_pct}% (${video_count})" >> "$temp_file"
        echo "  - 文章阅读: ${newsletter_pct}% (${newsletter_count})" >> "$temp_file"
        echo "  - 思考记录: ${braindump_pct}% (${braindump_count})" >> "$temp_file"

        # Check if any category is severely lacking
        if [ "$video_count" -eq 0 ]; then
            echo "  - ⚠️ 缺少视频学习，建议增加实践教程观看" >> "$temp_file"
        fi
        if [ "$newsletter_count" -eq 0 ]; then
            echo "  - ⚠️ 缺少文章阅读，建议关注行业动态" >> "$temp_file"
        fi
        if [ "$braindump_count" -eq 0 ]; then
            echo "  - ⚠️ 缺少思考记录，建议增加反思和总结" >> "$temp_file"
        fi

        # Check for good balance
        if [ "$video_count" -gt 0 ] && [ "$newsletter_count" -gt 0 ] && [ "$braindump_count" -gt 0 ]; then
            echo "  - ✅ 内容类型分布均衡" >> "$temp_file"
        fi
    else
        echo "  - ❌ 缺少学习内容记录" >> "$temp_file"
    fi

    echo "" >> "$temp_file"

    # 2. 质量指标
    echo "### 质量评估" >> "$temp_file"
    echo "" >> "$temp_file"

    # Review completion rate
    local daily_files=$(find weeks/ -name "????_??_??.md" -type f)
    local files_with_review=0
    local total_files=0

    for file in $daily_files; do
        total_files=$((total_files + 1))
        if grep -q "## review" "$file" && [ -n "$(sed -n '/## review/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d')" ]; then
            files_with_review=$((files_with_review + 1))
        fi
    done

    local review_completion_pct=0
    if [ "$total_files" -gt 0 ]; then
        review_completion_pct=$(( files_with_review * 100 / total_files ))
    fi

    echo "- **总结习惯**: ${review_completion_pct}% (${files_with_review}/${total_files} 天)" >> "$temp_file"

    if [ "$review_completion_pct" -ge 80 ]; then
        echo "  - ✅ 每日总结习惯很好" >> "$temp_file"
    elif [ "$review_completion_pct" -ge 50 ]; then
        echo "  - ⚠️ 总结习惯需要加强" >> "$temp_file"
    else
        echo "  - ❌ 缺少每日总结，建议使用 /daily-review 命令" >> "$temp_file"
    fi

    # Deep thinking assessment
    echo "- **深度思考**: " >> "$temp_file"
    if [ "$braindump_count" -ge "$total_days" ]; then
        echo "思考记录丰富，平均每学习日都有思考输出" >> "$temp_file"
        echo "  - ✅ 深度思考习惯良好" >> "$temp_file"
    elif [ "$braindump_count" -gt 0 ]; then
        echo "有一定的思考记录，但可以更加频繁" >> "$temp_file"
        echo "  - ⚠️ 建议增加每日思考和反思" >> "$temp_file"
    else
        echo "缺少思考记录" >> "$temp_file"
        echo "  - ❌ 建议在 braindump 部分记录更多想法和思考" >> "$temp_file"
    fi

    # Practical application
    echo "- **实践转化**: " >> "$temp_file"
    if [ "$project_count" -ge 5 ]; then
        echo "项目实践活动丰富" >> "$temp_file"
        echo "  - ✅ 理论学习向实践转化良好" >> "$temp_file"
    elif [ "$project_count" -gt 0 ]; then
        echo "有一定的项目实践" >> "$temp_file"
        echo "  - ⚠️ 可以增加更多实际项目开发" >> "$temp_file"
    else
        echo "缺少项目实践记录" >> "$temp_file"
        echo "  - ❌ 建议将学习内容应用到具体项目中" >> "$temp_file"
    fi

    echo "" >> "$temp_file"

    # 3. 成长指标
    echo "### 成长轨迹" >> "$temp_file"
    echo "" >> "$temp_file"

    # Calculate weekly growth trend (if multiple weeks exist)
    local week_dirs=$(find weeks/ -type d -name "????_????-????" | wc -l | tr -d ' ')

    if [ "$week_dirs" -gt 1 ]; then
        echo "- **学习周期**: 已持续 $week_dirs 周" >> "$temp_file"
        echo "  - ✅ 形成了持续学习的节奏" >> "$temp_file"
    elif [ "$week_dirs" -eq 1 ]; then
        echo "- **学习周期**: 当前第 1 周" >> "$temp_file"
        echo "  - 🌱 刚开始建立学习习惯，继续保持" >> "$temp_file"
    fi

    # Content evolution (comparing early vs recent entries)
    echo "- **内容演进**: " >> "$temp_file"
    if [ "$total_content_entries" -ge 10 ]; then
        echo "内容记录丰富，学习覆盖面广" >> "$temp_file"
    elif [ "$total_content_entries" -ge 5 ]; then
        echo "内容记录中等，可以扩大学习范围" >> "$temp_file"
    else
        echo "内容记录较少，建议增加学习内容的记录" >> "$temp_file"
    fi

    echo "$temp_file"
}

# Function to analyze gaps and generate recommendations
analyze_gaps_and_recommendations() {
    local current_month=$1
    local monthly_goals="$2"
    local learning_content="$3"

    echo "## ⚠️ 差距分析"
    echo ""

    # Basic gap analysis based on goals vs actual content
    if [ -z "$monthly_goals" ]; then
        echo "- 当前阶段目标不明确，建议明确当前月份的具体目标"
    else
        echo "- 对照当前月份目标，分析实际完成情况："
        echo "$monthly_goals" | while read -r line; do
            if [ ! -z "$line" ] && [[ "$line" =~ ^[^#] ]]; then
                echo "  - [ ] $line"
            fi
        done
    fi

    echo ""
    echo "## 🚀 改进建议"
    echo ""

    local video_count=$(cat /tmp/milestone_video_count 2>/dev/null || echo "0")
    local newsletter_count=$(cat /tmp/milestone_newsletter_count 2>/dev/null || echo "0")
    local project_count=$(cat /tmp/milestone_project_count 2>/dev/null || echo "0")
    local total_days=$(cat /tmp/milestone_total_days 2>/dev/null || echo "0")
    local braindump_count=$(cat /tmp/milestone_braindump_count 2>/dev/null || echo "0")

    echo "### 基于学习习惯的改进建议"
    echo ""

    # Generate recommendations based on habit evaluation
    local start_date=$(get_learning_start_date)
    local current_date=$(get_current_date)
    # Calculate days since start (compatible with both BSD and GNU date)
    local current_epoch start_epoch days_since_start
    if date -j -f "%Y-%m-%d" "$current_date" +%s >/dev/null 2>&1; then
        # BSD date (macOS)
        current_epoch=$(date -j -f "%Y-%m-%d" "$current_date" +%s)
        start_epoch=$(date -j -f "%Y-%m-%d" "$start_date" +%s)
    else
        # GNU date (Linux)
        current_epoch=$(date -d "$current_date" +%s)
        start_epoch=$(date -d "$start_date" +%s)
    fi
    days_since_start=$(( ( current_epoch - start_epoch ) / 86400 + 1 ))

    local learning_frequency_pct=0
    if [ "$days_since_start" -gt 0 ]; then
        learning_frequency_pct=$(( total_days * 100 / days_since_start ))
    fi

    # Frequency recommendations
    if [ "$learning_frequency_pct" -lt 60 ]; then
        echo "- **提高学习频率**: 目前学习频率为 ${learning_frequency_pct}%，建议："
        echo "  - 设置固定的学习时间段（如每日早晨或晚上）"
        echo "  - 使用 /daily-start 命令创建每日学习记录"
        echo "  - 即使学习时间有限，也要保持记录的连续性"
        echo ""
    fi

    # Content balance recommendations
    if [ "$video_count" -lt 3 ]; then
        echo "- **增加视频学习**: 建议每周观看 2-3 个技术相关视频教程"
    fi

    if [ "$newsletter_count" -lt 5 ]; then
        echo "- **增加文章阅读**: 建议订阅 AI/技术相关 newsletter，保持行业敏感度"
    fi

    if [ "$braindump_count" -lt "$total_days" ]; then
        echo "- **加强深度思考**: 每日学习后，在 braindump 部分记录："
        echo "  - 学到了什么新知识"
        echo "  - 如何与之前的知识连接"
        echo "  - 可以应用到哪些实际场景"
        echo ""
    fi

    if [ "$project_count" -lt 2 ]; then
        echo "- **增加实践项目**: 将学习内容转化为实际输出："
        echo "  - 搭建简单的 demo 或 MVP"
        echo "  - 写技术博客或总结文档"
        echo "  - 参与开源项目或社区讨论"
        echo ""
    fi

    # Review habit recommendations
    local daily_files=$(find weeks/ -name "????_??_??.md" -type f)
    local files_with_review=0
    local total_files=0

    for file in $daily_files; do
        total_files=$((total_files + 1))
        if grep -q "## review" "$file" && [ -n "$(sed -n '/## review/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d')" ]; then
            files_with_review=$((files_with_review + 1))
        fi
    done

    local review_completion_pct=0
    if [ "$total_files" -gt 0 ]; then
        review_completion_pct=$(( files_with_review * 100 / total_files ))
    fi

    if [ "$review_completion_pct" -lt 80 ]; then
        echo "- **完善每日总结**: 当前总结完成率 ${review_completion_pct}%，建议："
        echo "  - 每日结束时使用 /daily-review 命令"
        echo "  - 回顾当天的学习收获和不足"
        echo "  - 规划第二天的学习重点"
        echo ""
    fi

    echo "### 下一步行动"
    echo ""
    echo "- 定期使用 /milestone 命令（建议每周一次）监控学习习惯"
    echo "- 根据评估结果调整学习策略和时间分配"
    echo "- 寻找学习伙伴或加入相关社群，增加交流和反馈"
    echo "- 设定具体的月度/周度学习目标，并跟踪完成情况"
}

# Function to identify key achievements from learning content
identify_achievements() {
    local achievements_file=$(mktemp)
    echo "## ✅ 主要成就" > "$achievements_file"
    echo "" >> "$achievements_file"

    # Look for achievements in review sections
    local achievement_found=false
    local daily_files=$(find weeks/ -name "????_??_??.md" -type f | sort)

    for file in $daily_files; do
        if grep -q "## review" "$file"; then
            local review_content=$(sed -n '/## review/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d')
            if [ ! -z "$review_content" ]; then
                local file_date=$(basename "$file" .md | sed 's/_/-/g')

                # Look for achievement keywords
                local achievements=$(echo "$review_content" | grep -i -E "(完成|学会|掌握|实现|搭建|成功|达成)")
                if [ ! -z "$achievements" ]; then
                    echo "**$file_date:**" >> "$achievements_file"
                    echo "$achievements" >> "$achievements_file"
                    echo "" >> "$achievements_file"
                    achievement_found=true
                fi
            fi
        fi
    done

    if [ "$achievement_found" = false ]; then
        echo "- 继续记录每日学习成果，形成可展示的成就记录" >> "$achievements_file"
        echo "- 将学习内容转化为具体的项目输出或技能证明" >> "$achievements_file"
    fi

    echo "$achievements_file"
}

# Main function to generate milestone report
generate_milestone_report() {
    echo "=== Starting milestone report generation ===" >&2

    local current_month
    if [ ! -z "$TARGET_MONTH" ]; then
        current_month="$TARGET_MONTH"
    else
        current_month=$(calculate_current_month)
    fi
    echo "Current month: $current_month" >&2

    local start_date=$(get_learning_start_date)
    local current_date=$(get_formatted_date)
    echo "Start date: $start_date, Current date: $current_date" >&2

    # Extract monthly goals
    echo "Extracting monthly goals..." >&2
    local monthly_goals=$(extract_monthly_goals "$current_month")

    # Aggregate learning content
    echo "Aggregating learning content..." >&2
    local learning_content_file=$(aggregate_learning_content)

    # Get statistics
    echo "Reading statistics..." >&2
    local video_count=$(cat /tmp/milestone_video_count 2>/dev/null || echo "0")
    local newsletter_count=$(cat /tmp/milestone_newsletter_count 2>/dev/null || echo "0")
    local braindump_count=$(cat /tmp/milestone_braindump_count 2>/dev/null || echo "0")
    local total_days=$(cat /tmp/milestone_total_days 2>/dev/null || echo "0")
    local project_count=$(cat /tmp/milestone_project_count 2>/dev/null || echo "0")
    echo "Stats: videos=$video_count, newsletters=$newsletter_count, braindumps=$braindump_count, days=$total_days, projects=$project_count" >&2

    # Generate achievements
    local achievements_file=$(identify_achievements)

    # Generate learning habits evaluation
    local habits_file=$(evaluate_learning_habits)

    # Create the milestone report
    local report_content=""

    report_content+="# Milestone Report - $current_date"$'\n'
    report_content+=""$'\n'

    report_content+="## 🎯 当前阶段"$'\n'
    report_content+=""$'\n'
    report_content+="- **计划月份**: 月 $current_month"$'\n'
    report_content+="- **学习开始日期**: $start_date"$'\n'

    if [ ! -z "$monthly_goals" ]; then
        report_content+="- **主要目标**:"$'\n'
        while IFS= read -r line; do
            if [ ! -z "$line" ] && [[ ! "$line" =~ ^[#] ]]; then
                report_content+="  - $line"$'\n'
            fi
        done <<< "$monthly_goals"
    else
        report_content+="- **主要目标**: 当前月份目标待明确"$'\n'
    fi

    report_content+=""$'\n'
    report_content+="## 📊 学习统计"$'\n'
    report_content+=""$'\n'
    report_content+="- **总学习天数**: $total_days 天"$'\n'
    report_content+="- **视频学习**: $video_count 个视频/教程"$'\n'
    report_content+="- **文章阅读**: $newsletter_count 篇文章/通讯"$'\n'
    report_content+="- **思考记录**: $braindump_count 次记录"$'\n'
    report_content+="- **项目产出**: $project_count 项相关活动"$'\n'
    report_content+=""$'\n'

    # Add achievements
    if [ -f "$achievements_file" ]; then
        report_content+="$(cat "$achievements_file")"$'\n'
        report_content+=""$'\n'
    fi

    # Add learning habits evaluation
    if [ -f "$habits_file" ]; then
        report_content+="$(cat "$habits_file")"$'\n'
        report_content+=""$'\n'
    fi

    # Add gap analysis and recommendations
    report_content+="$(analyze_gaps_and_recommendations "$current_month" "$monthly_goals" "$learning_content_file")"$'\n'

    # Output the report
    echo "Generating final report..." >&2
    if [ ! -z "$SAVE_TO_FILE" ]; then
        echo "$report_content" > "$SAVE_TO_FILE"
        echo "Milestone report saved to: $SAVE_TO_FILE"
    else
        echo "$report_content"
    fi
    echo "=== Milestone report generation completed ===" >&2

    # Cleanup temporary files
    rm -f /tmp/milestone_*
    [ -f "$learning_content_file" ] && rm -f "$learning_content_file"
    [ -f "$achievements_file" ] && rm -f "$achievements_file"
    [ -f "$habits_file" ] && rm -f "$habits_file"
}

# Run the milestone report generation
generate_milestone_report
```