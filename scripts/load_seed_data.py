#!/usr/bin/env python3
"""
Seed data loader for WMS application.

Loads test data from JSON files into the database.
"""

import sys
import os
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.data.logs import LogManager


def load_json_file(file_path: Path) -> dict:
    """Load JSON file and return data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Seed file not found: {file_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {file_path}: {e}")
        return {}


def print_seed_info(seed_dir: Path):
    """Print information about available seed data."""
    print("Available seed data files:")
    
    seed_files = {
        'users.json': 'User accounts',
        'warehouses.json': 'Warehouse data',
        'products.json': 'Product catalog',
        'customers.json': 'Customer information',
        'inventory.json': 'Initial inventory'
    }
    
    for filename, description in seed_files.items():
        file_path = seed_dir / filename
        if file_path.exists():
            data = load_json_file(file_path)
            print(f"  ✓ {filename}: {description} ({len(data)} records)")
        else:
            print(f"  ✗ {filename}: {description} (not found)")


def main():
    """Main seed data loader."""
    print("WMS Seed Data Loader")
    print("=" * 40)
    
    # Path to seed data directory
    seed_dir = Path(__file__).parent.parent / 'src' / 'app' / 'data' / 'seed_data'
    
    if not seed_dir.exists():
        print(f"Error: Seed data directory not found: {seed_dir}")
        return
    
    # Print available seed data
    print_seed_info(seed_dir)
    
    print("\nTo use seed data:")
    print("1. Import this module in your application")
    print("2. Call load_json_file() for each seed file")
    print("3. Insert data into your database")
    
    print(f"\nSeed data directory: {seed_dir}")


if __name__ == "__main__":
    main()
