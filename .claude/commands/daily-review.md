# Daily Review Command

Reviews the current day's markdown file content and updates the `## review` section with a summary.

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

# Check if review section already exists
if grep -q "## review" "$daily_file"; then
    echo "Review section already exists in $daily_file"
    echo "Current content:"
    cat "$daily_file"
else
    # Add review section to the file
    echo "" >> "$daily_file"
    echo "## review" >> "$daily_file"
    echo "" >> "$daily_file"

    # Generate automatic review based on content
    if [ -n "$video_content" ] || [ -n "$newsletter_content" ] || [ -n "$braindump_content" ] || [ -n "$output_content" ]; then
        echo "Today's activities summary:" >> "$daily_file"

        if [ -n "$video_content" ]; then
            echo "- **Video learning**: Watched content related to project setup and development tools" >> "$daily_file"
        fi

        if [ -n "$newsletter_content" ]; then
            echo "- **Reading**: Consumed newsletter and article content" >> "$daily_file"
        fi

        if [ -n "$braindump_content" ]; then
            echo "- **Project work**: $(echo "$braindump_content" | head -n 1 | sed 's/^- *//')" >> "$daily_file"
        fi

        if [ -n "$output_content" ]; then
            echo "- **Learning output**: Created and shared learning content" >> "$daily_file"
        fi
    else
        echo "<!-- Review will be added by /daily-review command -->" >> "$daily_file"
    fi

    echo "Added review section to $daily_file"
fi
```