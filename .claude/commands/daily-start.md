# Daily Start Command

Creates a daily markdown file in the current week's folder with format `YYYY_MM_DD.md`.

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

# Create weeks directory and weekly folder if they don't exist
mkdir -p "weeks/$folder_name"

# Format daily file name: YYYY_MM_DD.md
daily_file="weeks/$folder_name/$(date +%Y_%m_%d).md"

# Create daily file if it doesn't exist
if [ ! -f "$daily_file" ]; then
    # Format date for journal header (MMDD format)
    header_date=$(date +%m%d)

    cat > "$daily_file" << EOF
# $header_date Journal

## video


## newsletter


## braindump


EOF

    echo "Created daily file: $daily_file"
else
    echo "Daily file already exists: $daily_file"
fi
```