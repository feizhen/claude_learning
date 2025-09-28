#!/usr/bin/env python3
"""
Week Start Script

Creates a weekly folder in the `weeks` directory with format `YYYY_MMDD1-MMDD2`
where DD1 is Monday and DD2 is Sunday of the current week.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


class WeekStartManager:
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

    def create_week_folder(self, date: datetime = None) -> bool:
        """Create the weekly folder for the specified date."""
        folder_name = self.get_week_folder_name(date)

        # Create weeks directory if it doesn't exist
        self.weeks_dir.mkdir(exist_ok=True)

        # Create weekly folder if it doesn't exist
        week_folder = self.weeks_dir / folder_name

        if not week_folder.exists():
            week_folder.mkdir(parents=True)
            print(f"Created weekly folder: weeks/{folder_name}")
            return True
        else:
            print(f"Weekly folder already exists: weeks/{folder_name}")
            return False

    def get_week_info(self, date: datetime = None) -> dict:
        """Get information about the week."""
        monday, sunday = self.get_week_dates(date)
        folder_name = self.get_week_folder_name(date)

        return {
            'folder_name': folder_name,
            'monday': monday,
            'sunday': sunday,
            'week_folder_path': self.weeks_dir / folder_name
        }


def main():
    """Main entry point for the week start script."""
    manager = WeekStartManager()

    # Parse command line arguments for custom date if needed
    target_date = datetime.now()
    if len(sys.argv) > 1:
        try:
            target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        except ValueError:
            print(f"Invalid date format: {sys.argv[1]}. Use YYYY-MM-DD format.")
            return 1

    # Create the week folder
    created = manager.create_week_folder(target_date)

    # Show week information
    week_info = manager.get_week_info(target_date)

    if created:
        print(f"Week folder created for: {week_info['monday'].strftime('%B %d')} - {week_info['sunday'].strftime('%B %d, %Y')}")
    else:
        print(f"Using existing week folder for: {week_info['monday'].strftime('%B %d')} - {week_info['sunday'].strftime('%B %d, %Y')}")

    print(f"Folder path: {week_info['week_folder_path']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())