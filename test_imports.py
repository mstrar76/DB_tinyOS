#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify that imports are working correctly after reorganization.
"""

import os
import sys
from datetime import datetime

def log_message(message):
    print(f"[{datetime.now().isoformat()}] {message}")

def test_imports():
    log_message("Testing imports...")
    
    # Test importing from utilities
    try:
        from src.utilities.db_utils import get_db_connection, close_db_connection
        log_message("✅ Utilities imports (db_utils) working")
    except ImportError as e:
        log_message(f"❌ Error importing utilities: {e}")
    
    # Test importing from processing
    try:
        from src.processing.process_data_with_tags import process_order_data
        log_message("✅ Processing imports (process_data_with_tags) working")
    except ImportError as e:
        log_message(f"❌ Error importing processing: {e}")
    
    # Test importing from extraction
    try:
        from src.extraction.fetch_all_orders_with_markers import fetch_and_process_orders_for_period
        log_message("✅ Extraction imports (fetch_all_orders_with_markers) working")
    except ImportError as e:
        log_message(f"❌ Error importing extraction: {e}")

if __name__ == "__main__":
    test_imports()