# Week Start Command

Creates a weekly folder in the `weeks` directory with format `YYYY_MMDD1-MMDD2` where DD1 is Monday and DD2 is Sunday of the current week.

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

# Create weeks directory if it doesn't exist
mkdir -p weeks

# Create weekly folder if it doesn't exist
if [ ! -d "weeks/$folder_name" ]; then
    mkdir -p "weeks/$folder_name"
    echo "Created weekly folder: weeks/$folder_name"
else
    echo "Weekly folder already exists: weeks/$folder_name"
fi
```