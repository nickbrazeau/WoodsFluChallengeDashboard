#!/usr/bin/env python3
"""
Quick fix for NaN values in JSON files
Replaces "NaN" and "nan" strings with null
"""

import json
import re
from pathlib import Path

def fix_nan_in_json_file(filepath):
    """Read, fix, and rewrite JSON file"""
    print(f"Processing: {filepath}")

    # Read raw text
    with open(filepath, 'r') as f:
        content = f.read()

    # Count issues
    nan_count = content.count(': NaN')
    nan_count += content.count(': nan')
    nan_count += content.count('": NaN')
    nan_count += content.count('": nan')

    if nan_count == 0:
        print(f"  ✓ No NaN values found")
        return

    print(f"  Found {nan_count} NaN values")

    # Replace patterns
    # Handle ": NaN," and ": NaN}"
    content = re.sub(r': NaN([,}])', r': null\1', content)
    # Handle ": nan," and ": nan}"
    content = re.sub(r': nan([,}])', r': null\1', content)
    # Handle ": "NaN"" patterns
    content = re.sub(r':\s*"NaN"', ': null', content)
    content = re.sub(r':\s*"nan"', ': null', content)

    # Write back
    with open(filepath, 'w') as f:
        f.write(content)

    print(f"  ✓ Fixed and saved")

def main():
    print("="*80)
    print("FIXING NaN VALUES IN JSON FILES")
    print("="*80 + "\n")

    # Fix publications JSON
    pub_file = Path('public/data/publications.json')
    if pub_file.exists():
        fix_nan_in_json_file(pub_file)
    else:
        print(f"Warning: {pub_file} not found")

    # Validate JSON
    print("\nValidating JSON...")
    try:
        with open(pub_file, 'r') as f:
            data = json.load(f)
        print(f"  ✓ Valid JSON - {len(data)} records")
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON Error: {e}")
        return False

    print("\n" + "="*80)
    print("COMPLETE")
    print("="*80)
    return True

if __name__ == '__main__':
    main()
