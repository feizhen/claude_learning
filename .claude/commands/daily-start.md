# Daily Start Command

Creates a daily markdown file in the current week's folder with format `YYYY_MM_DD.md`.

```bash
#!/bin/bash

# Set locale to avoid Chinese date format issues
export LC_ALL=C

# Get day of week (1=Monday, 7=Sunday)
dow=$(date +%u)

# Calculate days to Monday (if today is Monday, days_to_monday=0)
days_to_monday=$((dow - 1))

# Get Monday's date using GNU date arithmetic
monday=$(date -d "-${days_to_monday} days" +%Y-%m-%d)
monday_formatted=$(date -d "-${days_to_monday} days" +%m%d)
monday_year=$(date -d "-${days_to_monday} days" +%Y)

# Get Sunday's date (6 days after Monday)
sunday_days=$((6 - days_to_monday))
sunday_formatted=$(date -d "+${sunday_days} days" +%m%d)

folder_name="${monday_year}_${monday_formatted}-${sunday_formatted}"

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

[] AI Vally

[] The Keyword

## braindump


## output


EOF

    echo "Created daily file: $daily_file"
else
    echo "Daily file already exists: $daily_file"
fi
```