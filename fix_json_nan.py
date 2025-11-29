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
    # Handle ": NaN," ": NaN}" and ": NaN\n"
    content = re.sub(r': NaN([,}\n])', r': null\1', content)
    # Handle ": nan," ": nan}" and ": nan\n"
    content = re.sub(r': nan([,}\n])', r': null\1', content)
    # Handle standalone ": NaN" at end of line
    content = re.sub(r':\s*NaN\s*$', ': null', content, flags=re.MULTILINE)
    content = re.sub(r':\s*nan\s*$', ': null', content, flags=re.MULTILINE)
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

    # Fix SOURCE citations JSON (critical - this is where NaN originates)
    citations_file = Path('data/publications/citations.json')
    if citations_file.exists():
        fix_nan_in_json_file(citations_file)
    else:
        print(f"Warning: {citations_file} not found")

    # Fix OUTPUT publications JSON
    pub_file = Path('public/data/publications.json')
    if pub_file.exists():
        fix_nan_in_json_file(pub_file)
    else:
        print(f"Warning: {pub_file} not found")

    # Validate both JSON files
    print("\nValidating JSON files...")
    all_valid = True

    for filepath in [citations_file, pub_file]:
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                print(f"  ✓ {filepath.name}: Valid JSON - {len(data.get('publications', data) if isinstance(data, dict) else data)} records")
            except json.JSONDecodeError as e:
                print(f"  ✗ {filepath.name}: JSON Error: {e}")
                all_valid = False

    print("\n" + "="*80)
    if all_valid:
        print("COMPLETE - All files fixed and validated")
    else:
        print("COMPLETE - Some files had errors")
    print("="*80)
    return all_valid

if __name__ == '__main__':
    main()
