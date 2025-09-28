#!/usr/bin/env python3
"""
Week Review Script

Reviews all daily files in the current week's folder and creates a comprehensive
weekly summary in `week_review.md`.
"""

import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class WeekReviewGenerator:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.weeks_dir = self.base_dir / "weeks"

    def get_week_dates(self, date: datetime = None) -> tuple[datetime, datetime]:
        """Get the Monday and Sunday dates for the week containing the given date."""
        if date is None:
            date = datetime.now()

        # Find Monday of the week (Python weekday: Monday=0, Sunday=6)
        days_since_monday = date.weekday()
        monday = date - timedelta(days=days_since_monday)
        sunday = monday + timedelta(days=6)

        return monday, sunday

    def get_week_folder_name(self, date: datetime = None) -> str:
        """Calculate the week folder name for a given date."""
        monday, sunday = self.get_week_dates(date)

        monday_formatted = monday.strftime("%m%d")
        sunday_formatted = sunday.strftime("%m%d")
        year = monday.strftime("%Y")

        return f"{year}_{monday_formatted}-{sunday_formatted}"

    def get_week_folder_path(self, date: datetime = None) -> Path:
        """Get the path to the week folder."""
        folder_name = self.get_week_folder_name(date)
        return self.weeks_dir / folder_name

    def extract_section_content(self, file_content: str, section: str) -> str:
        """Extract content from a specific markdown section."""
        # Pattern to match section header until next section or end of file
        pattern = rf"^## {re.escape(section)}$(.*?)(?=^## |\Z)"
        match = re.search(pattern, file_content, re.MULTILINE | re.DOTALL)

        if match:
            content = match.group(1).strip()
            return content

        return ""

    def find_daily_files(self, week_folder: Path) -> List[Path]:
        """Find all daily markdown files in the week folder."""
        if not week_folder.exists():
            return []

        # Pattern matches: YYYY_MM_DD.md
        daily_files = []
        for file_path in week_folder.glob("????_??_??.md"):
            if file_path.is_file():
                daily_files.append(file_path)

        # Sort by date
        daily_files.sort(key=lambda x: x.stem)
        return daily_files

    def format_date_for_display(self, filename: str) -> str:
        """Convert filename format YYYY_MM_DD to readable date."""
        try:
            parts = filename.split('_')
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])

            date_obj = datetime(year, month, day)
            return date_obj.strftime("%B %d")
        except (ValueError, IndexError):
            return filename

    def process_daily_file(self, file_path: Path) -> Dict[str, str]:
        """Process a single daily file and extract sections."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            sections = {}
            section_names = ['video', 'newsletter', 'braindump', 'output', 'review', 'WayToAce', 'TODO']

            for section in section_names:
                sections[section] = self.extract_section_content(content, section)

            return sections
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return {}

    def generate_weekly_summary(self, week_folder: Path, monday: datetime, sunday: datetime) -> str:
        """Generate the complete weekly summary content."""
        folder_name = week_folder.name
        date_range = f"{monday.strftime('%B %d')} - {sunday.strftime('%B %d, %Y')}"

        # Start with header
        content = [
            f"# Weekly Review: {folder_name}",
            "",
            f"Week of {date_range}",
            "",
            "## Summary",
            "",
        ]

        # Find daily files
        daily_files = self.find_daily_files(week_folder)

        if not daily_files:
            content.extend([
                "No daily journal entries found for this week.",
                "",
            ])
        else:
            print(f"Found daily files to review: {[f.name for f in daily_files]}")

            # Add daily summaries section
            content.extend([
                "## Daily Summaries",
                "",
            ])

            # Process each daily file
            for file_path in daily_files:
                filename = file_path.stem  # Remove .md extension
                display_date = self.format_date_for_display(filename)

                content.append(f"### {display_date}")
                content.append("")

                sections = self.process_daily_file(file_path)

                # Add each section if it has content
                section_mappings = {
                    'video': '**Videos/Learning:**',
                    'newsletter': '**Newsletter/Reading:**',
                    'braindump': '**Ideas/Thoughts:**',
                    'output': '**Learning Output:**',
                    'review': '**Daily Review:**'
                }

                for section_key, section_title in section_mappings.items():
                    section_content = sections.get(section_key, '').strip()
                    if section_content:
                        content.append(section_title)
                        content.append(section_content)
                        content.append("")

                # Add WayToAce progress if exists
                waytoace_content = sections.get('WayToAce', '').strip()
                if waytoace_content:
                    content.append("**WayToAce Progress:**")
                    content.append(waytoace_content)
                    content.append("")

                content.append("---")
                content.append("")

        # Add weekly insights and action items sections
        content.extend([
            "",
            "## Weekly Insights",
            "",
            "<!-- Add your weekly reflections, key learnings, and insights here -->",
            "",
            "## Action Items for Next Week",
            "",
            "<!-- Add action items and goals for the upcoming week -->",
            "",
        ])

        return "\n".join(content)

    def create_week_review(self, date: datetime = None) -> bool:
        """Create the weekly review for the specified date."""
        monday, sunday = self.get_week_dates(date)
        week_folder = self.get_week_folder_path(date)

        # Check if week folder exists
        if not week_folder.exists():
            print(f"Week folder does not exist: {week_folder}")
            print("Please run /week-start first to create the weekly folder.")
            return False

        # Create week review file
        review_file = week_folder / "week_review.md"

        print(f"Generating weekly review for: {week_folder}")

        # Generate review content
        review_content = self.generate_weekly_summary(week_folder, monday, sunday)

        # Write to file
        try:
            with open(review_file, 'w', encoding='utf-8') as f:
                f.write(review_content)

            print(f"Weekly review created: {review_file}")
            print("Please review and add your weekly insights and action items.")
            return True

        except Exception as e:
            print(f"Error creating review file: {e}")
            return False


def main():
    """Main entry point for the week review script."""
    generator = WeekReviewGenerator()

    # Parse command line arguments for custom date if needed
    target_date = datetime.now()
    if len(sys.argv) > 1:
        try:
            target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        except ValueError:
            print(f"Invalid date format: {sys.argv[1]}. Use YYYY-MM-DD format.")
            return 1

    success = generator.create_week_review(target_date)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())