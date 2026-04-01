#!/usr/bin/env python3
"""
Automatic log cleanup script for WMS.

Removes log files older than 7 days.
Can be run manually or scheduled via cron.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.data.logs import LogManager


def main():
    """Main cleanup function."""
    print("Starting log cleanup...")
    
    # Initialize log manager
    log_manager = LogManager()
    
    # Clean up logs older than 7 days
    log_manager.cleanup_old_logs(days=7)
    
    # Log cleanup information
    log_manager.log_cleanup_info()
    
    print("Log cleanup completed successfully.")


if __name__ == "__main__":
    main()
