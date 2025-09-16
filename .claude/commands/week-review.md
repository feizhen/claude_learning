# Week Review Command

Reviews all daily files in the current week's folder and creates a comprehensive weekly summary in `week_review.md`.

```bash
#!/bin/bash

# Get current date
current_date=$(date +%Y-%m-%d)

# Get the Monday of current week (start of week)
monday=$(date -j -f "%Y-%m-%d" "$current_date" -v-$(date -j -f "%Y-%m-%d" "$current_date" +%u)d -v+1d +%Y-%m-%d)

# Get the Sunday of current week (end of week)
sunday=$(date -j -f "%Y-%m-%d" "$monday" -v+6d +%Y-%m-%d)

# Format folder name: YYYY_MMDD1-MMDD2
monday_formatted=$(date -j -f "%Y-%m-%d" "$monday" +%m%d)
sunday_formatted=$(date -j -f "%Y-%m-%d" "$sunday" +%m%d)
year=$(date -j -f "%Y-%m-%d" "$monday" +%Y)

folder_name="${year}_${monday_formatted}-${sunday_formatted}"
week_folder="weeks/$folder_name"

# Check if week folder exists
if [ ! -d "$week_folder" ]; then
    echo "Week folder does not exist: $week_folder"
    echo "Please run /week-start first to create the weekly folder."
    exit 1
fi

# Create week review file
review_file="$week_folder/week_review.md"

echo "Generating weekly review for: $week_folder"

# Start creating the review file
cat > "$review_file" << EOF
# Weekly Review: $folder_name

Week of $(date -j -f "%Y-%m-%d" "$monday" +"%B %d") - $(date -j -f "%Y-%m-%d" "$sunday" +"%B %d, %Y")

## Summary

EOF

# Find all daily markdown files in the week folder
daily_files=$(find "$week_folder" -name "????_??_??.md" -type f | sort)

if [ -z "$daily_files" ]; then
    echo "No daily files found in $week_folder"
    cat >> "$review_file" << EOF
No daily journal entries found for this week.

EOF
else
    echo "Found daily files to review:"
    echo "$daily_files"

    # Add daily summaries section
    cat >> "$review_file" << EOF
## Daily Summaries

EOF

    # Process each daily file
    for file in $daily_files; do
        filename=$(basename "$file" .md)

        # Format date for display (YYYY_MM_DD -> Month DD)
        year_part=$(echo "$filename" | cut -d'_' -f1)
        month_part=$(echo "$filename" | cut -d'_' -f2)
        day_part=$(echo "$filename" | cut -d'_' -f3)

        display_date=$(date -j -f "%Y-%m-%d" "$year_part-$month_part-$day_part" +"%B %d")

        cat >> "$review_file" << EOF
### $display_date

EOF

        # Extract content from each section of the daily file
        if grep -q "## video" "$file"; then
            video_content=$(sed -n '/## video/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d')
            if [ ! -z "$video_content" ]; then
                echo "**Videos/Learning:**" >> "$review_file"
                echo "$video_content" >> "$review_file"
                echo "" >> "$review_file"
            fi
        fi

        if grep -q "## newsletter" "$file"; then
            newsletter_content=$(sed -n '/## newsletter/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d')
            if [ ! -z "$newsletter_content" ]; then
                echo "**Newsletter/Reading:**" >> "$review_file"
                echo "$newsletter_content" >> "$review_file"
                echo "" >> "$review_file"
            fi
        fi

        if grep -q "## braindump" "$file"; then
            braindump_content=$(sed -n '/## braindump/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d')
            if [ ! -z "$braindump_content" ]; then
                echo "**Ideas/Thoughts:**" >> "$review_file"
                echo "$braindump_content" >> "$review_file"
                echo "" >> "$review_file"
            fi
        fi

        if grep -q "## review" "$file"; then
            review_content=$(sed -n '/## review/,/## [a-z]/p' "$file" | sed '$d' | tail -n +2 | sed '/^$/d' | grep -v "<!-- Review will be added")
            if [ ! -z "$review_content" ]; then
                echo "**Daily Review:**" >> "$review_file"
                echo "$review_content" >> "$review_file"
                echo "" >> "$review_file"
            fi
        fi

        echo "---" >> "$review_file"
        echo "" >> "$review_file"
    done
fi

# Add weekly insights section
cat >> "$review_file" << EOF

## Weekly Insights

<!-- Add your weekly reflections, key learnings, and insights here -->

## Action Items for Next Week

<!-- Add action items and goals for the upcoming week -->

EOF

echo "Weekly review created: $review_file"
echo "Please review and add your weekly insights and action items."
```