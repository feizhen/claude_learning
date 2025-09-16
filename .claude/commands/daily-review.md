# Daily Review Command

Reviews the current day's markdown file content and updates the `## review` section with a summary.

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

# Format daily file name: YYYY_MM_DD.md
daily_file="weeks/$folder_name/$(date +%Y_%m_%d).md"

# Check if daily file exists
if [ ! -f "$daily_file" ]; then
    echo "Daily file does not exist: $daily_file"
    echo "Please run /daily-start first to create the daily file."
    exit 1
fi

echo "Reading and analyzing content from: $daily_file"

# Use Claude Code to read the file and generate a review
claude_code_review() {
    cat << EOF
Based on the content in the daily file, please generate a concise review summary that captures:
1. Key activities and accomplishments from today
2. Important videos watched or resources consumed
3. Notable ideas or insights from braindump section
4. Any patterns or themes that emerged

The review should be 2-3 bullet points maximum, focusing on the most significant items.
EOF
}

# Read current file content
file_content=$(cat "$daily_file")

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
    echo "<!-- Review will be added by /daily-review command -->" >> "$daily_file"
    echo "Added review section to $daily_file"
    echo "Please run this command again or manually update the review section with your daily summary."
fi
```