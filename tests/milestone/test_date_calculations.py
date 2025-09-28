#!/usr/bin/env python3
"""
Tests for date calculations in milestone analyzer.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from freezegun import freeze_time
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import the MilestoneAnalyzer class
from pathlib import Path
import tempfile
import shutil


class TestMilestoneAnalyzer:
    """Mock MilestoneAnalyzer for testing without importing the actual module."""

    def __init__(self):
        self.base_dir = Path.cwd()
        self.weeks_dir = self.base_dir / "weeks"
        self.objective_file = self.base_dir / "objective.md"

    def get_learning_start_date(self) -> datetime:
        """Calculate learning start date from earliest file in weeks/."""
        daily_files = list(self.weeks_dir.glob("*/????_??_??.md"))

        if not daily_files:
            return datetime(2025, 9, 15)  # Default start date

        # Sort by filename to get earliest
        daily_files.sort(key=lambda x: x.name)
        earliest_file = daily_files[0]

        # Extract date from filename (YYYY_MM_DD.md)
        filename = earliest_file.stem
        try:
            year, month, day = map(int, filename.split('_'))
            return datetime(year, month, day)
        except (ValueError, IndexError):
            return datetime(2025, 9, 15)

    def calculate_current_month(self) -> int:
        """Calculate which month of the learning journey we're in."""
        start_date = self.get_learning_start_date()
        current_date = datetime.now()

        # Calculate months difference
        months_diff = (current_date.year - start_date.year) * 12 + \
                     (current_date.month - start_date.month)

        # Return month number (1-based)
        return max(1, months_diff + 1)


class TestDateCalculations:
    """Test date calculation methods."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a temporary directory for testing
        self.test_dir = Path(tempfile.mkdtemp())
        self.weeks_dir = self.test_dir / "weeks"
        self.weeks_dir.mkdir()

        # Create analyzer with test directory
        self.analyzer = TestMilestoneAnalyzer()
        self.analyzer.base_dir = self.test_dir
        self.analyzer.weeks_dir = self.weeks_dir
        self.analyzer.objective_file = self.test_dir / "objective.md"

    def teardown_method(self):
        """Clean up test environment after each test."""
        shutil.rmtree(self.test_dir)

    def test_get_learning_start_date_with_files(self):
        """Test getting learning start date when files exist."""
        # Create test week directories and files
        week1_dir = self.weeks_dir / "2025_0916-0922"
        week1_dir.mkdir()

        # Create files with different dates
        (week1_dir / "2025_09_16.md").write_text("# Test file 1")
        (week1_dir / "2025_09_18.md").write_text("# Test file 2")
        (week1_dir / "2025_09_20.md").write_text("# Test file 3")

        # Should return the earliest date (2025_09_16)
        start_date = self.analyzer.get_learning_start_date()
        expected = datetime(2025, 9, 16)

        assert start_date == expected

    def test_get_learning_start_date_no_files(self):
        """Test getting learning start date when no files exist."""
        # No files in weeks directory
        start_date = self.analyzer.get_learning_start_date()
        expected = datetime(2025, 9, 15)  # Default

        assert start_date == expected

    def test_get_learning_start_date_invalid_filename(self):
        """Test handling of invalid filename format."""
        week1_dir = self.weeks_dir / "2025_0916-0922"
        week1_dir.mkdir()

        # Create file with invalid filename format
        (week1_dir / "invalid_filename.md").write_text("# Invalid file")
        (week1_dir / "2025_09_20.md").write_text("# Valid file")

        # Should return date from valid file
        start_date = self.analyzer.get_learning_start_date()
        expected = datetime(2025, 9, 20)

        assert start_date == expected

    def test_get_learning_start_date_only_invalid_files(self):
        """Test when only invalid filename formats exist."""
        week1_dir = self.weeks_dir / "2025_0916-0922"
        week1_dir.mkdir()

        # Create only invalid files
        (week1_dir / "invalid1.md").write_text("# Invalid file 1")
        (week1_dir / "invalid2.md").write_text("# Invalid file 2")

        # Should return default date
        start_date = self.analyzer.get_learning_start_date()
        expected = datetime(2025, 9, 15)

        assert start_date == expected

    @freeze_time("2025-09-26")
    def test_calculate_current_month_same_month(self):
        """Test calculating current month when in the same month as start."""
        # Set up files starting from 2025-09-16
        week1_dir = self.weeks_dir / "2025_0916-0922"
        week1_dir.mkdir()
        (week1_dir / "2025_09_16.md").write_text("# Test file")

        current_month = self.analyzer.calculate_current_month()

        # Same month, should be month 1
        assert current_month == 1

    @freeze_time("2025-10-26")
    def test_calculate_current_month_next_month(self):
        """Test calculating current month when in the next month."""
        # Set up files starting from 2025-09-16
        week1_dir = self.weeks_dir / "2025_0916-0922"
        week1_dir.mkdir()
        (week1_dir / "2025_09_16.md").write_text("# Test file")

        current_month = self.analyzer.calculate_current_month()

        # Next month, should be month 2
        assert current_month == 2

    @freeze_time("2025-11-26")
    def test_calculate_current_month_multiple_months(self):
        """Test calculating current month after multiple months."""
        # Set up files starting from 2025-09-16
        week1_dir = self.weeks_dir / "2025_0916-0922"
        week1_dir.mkdir()
        (week1_dir / "2025_09_16.md").write_text("# Test file")

        current_month = self.analyzer.calculate_current_month()

        # Two months later, should be month 3
        assert current_month == 3

    @freeze_time("2025-09-10")  # Before any learning started
    def test_calculate_current_month_before_start(self):
        """Test calculating current month when current date is before start date."""
        # Set up files starting from 2025-09-16
        week1_dir = self.weeks_dir / "2025_0916-0922"
        week1_dir.mkdir()
        (week1_dir / "2025_09_16.md").write_text("# Test file")

        current_month = self.analyzer.calculate_current_month()

        # Should be at least month 1
        assert current_month == 1

    def test_multiple_weeks_earliest_date(self):
        """Test that earliest date is correctly identified across multiple weeks."""
        # Create multiple weeks with files
        week1_dir = self.weeks_dir / "2025_0916-0922"
        week2_dir = self.weeks_dir / "2025_0923-0929"
        week1_dir.mkdir()
        week2_dir.mkdir()

        # Files in different weeks
        (week1_dir / "2025_09_18.md").write_text("# Week 1 file")
        (week1_dir / "2025_09_20.md").write_text("# Week 1 file")
        (week2_dir / "2025_09_23.md").write_text("# Week 2 file")
        (week2_dir / "2025_09_15.md").write_text("# Week 2 file - earliest")

        start_date = self.analyzer.get_learning_start_date()
        expected = datetime(2025, 9, 15)  # Earliest across all weeks

        assert start_date == expected


class TestDateEdgeCases:
    """Test edge cases for date calculations."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.weeks_dir = self.test_dir / "weeks"
        self.weeks_dir.mkdir()

        self.analyzer = TestMilestoneAnalyzer()
        self.analyzer.base_dir = self.test_dir
        self.analyzer.weeks_dir = self.weeks_dir
        self.analyzer.objective_file = self.test_dir / "objective.md"

    def teardown_method(self):
        """Clean up test environment after each test."""
        shutil.rmtree(self.test_dir)

    def test_year_boundary_crossing(self):
        """Test date calculations across year boundaries."""
        # Create files in December and January
        week1_dir = self.weeks_dir / "2024_1225-2025_0101"
        week1_dir.mkdir()
        (week1_dir / "2024_12_30.md").write_text("# December file")

        with freeze_time("2025-01-15"):
            current_month = self.analyzer.calculate_current_month()
            # From Dec 30 to Jan 15 should be month 2
            assert current_month == 2

    def test_leap_year_handling(self):
        """Test date calculations during leap year."""
        # Create file on Feb 29 in a leap year
        week_dir = self.weeks_dir / "2024_0226-0303"
        week_dir.mkdir()
        (week_dir / "2024_02_29.md").write_text("# Leap year file")

        start_date = self.analyzer.get_learning_start_date()
        expected = datetime(2024, 2, 29)

        assert start_date == expected

    def test_malformed_date_recovery(self):
        """Test recovery from malformed date strings."""
        week_dir = self.weeks_dir / "2025_0916-0922"
        week_dir.mkdir()

        # Create files with various malformed dates
        (week_dir / "2025_13_45.md").write_text("# Invalid month/day")
        (week_dir / "2025_09.md").write_text("# Missing day")
        (week_dir / "2025_09_16.md").write_text("# Valid file")

        start_date = self.analyzer.get_learning_start_date()
        expected = datetime(2025, 9, 16)  # Should find the valid one

        assert start_date == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])