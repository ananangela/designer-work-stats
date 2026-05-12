#!/usr/bin/env python3
"""
Data persistence manager for design work statistics
Saves raw data in JSON format organized by execution date
"""
import os
import json
from datetime import datetime
from pathlib import Path

class DataManager:
    def __init__(self, base_dir="data"):
        """Initialize data manager with base directory"""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def get_today_directory(self):
        """Get or create today's data directory"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_dir = self.base_dir / today
        today_dir.mkdir(exist_ok=True)
        return today_dir

    def save_raw_data(self, data, filename="raw_data.json"):
        """Save raw sheet data to JSON file"""
        today_dir = self.get_today_directory()
        filepath = today_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def save_statistics(self, stats_by_product, stats_by_category, filename="statistics.json"):
        """Save computed statistics to JSON file"""
        today_dir = self.get_today_directory()
        filepath = today_dir / filename

        stats = {
            'timestamp': datetime.now().isoformat(),
            'by_product_category': stats_by_product,
            'by_category': stats_by_category
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def save_metadata(self, metadata, filename="metadata.json"):
        """Save execution metadata"""
        today_dir = self.get_today_directory()
        filepath = today_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def list_all_data(self):
        """List all saved data directories and files"""
        result = {}
        if not self.base_dir.exists():
            return result

        for date_dir in sorted(self.base_dir.iterdir(), reverse=True):
            if date_dir.is_dir():
                files = sorted([f.name for f in date_dir.iterdir() if f.is_file()])
                result[date_dir.name] = files

        return result

    def load_raw_data(self, date=None, filename="raw_data.json"):
        """Load raw data from a specific date (default: today)"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        filepath = self.base_dir / date / filename

        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_statistics(self, date=None, filename="statistics.json"):
        """Load statistics from a specific date (default: today)"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        filepath = self.base_dir / date / filename

        if not filepath.exists():
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

if __name__ == '__main__':
    dm = DataManager()
    print("📁 Data structure:")
    all_data = dm.list_all_data()
    for date, files in all_data.items():
        print(f"  {date}/")
        for file in files:
            print(f"    - {file}")
