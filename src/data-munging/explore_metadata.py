#!/usr/bin/env python3
"""
Metadata Exploration Script
Explores all Excel files in data/raw to understand structure and contents
"""

import pandas as pd
import os
from pathlib import Path
import json

def explore_excel_file(filepath):
    """Explore a single Excel file and return metadata about it"""
    print(f"\n{'='*80}")
    print(f"Exploring: {os.path.basename(filepath)}")
    print(f"{'='*80}")

    file_info = {
        'filename': os.path.basename(filepath),
        'filepath': str(filepath),
        'sheets': {}
    }

    try:
        # Get all sheet names
        excel_file = pd.ExcelFile(filepath)
        sheet_names = excel_file.sheet_names

        print(f"\nFound {len(sheet_names)} sheet(s): {', '.join(sheet_names)}")

        for sheet_name in sheet_names:
            print(f"\n{'-'*80}")
            print(f"Sheet: {sheet_name}")
            print(f"{'-'*80}")

            # Read the sheet
            df = pd.read_excel(filepath, sheet_name=sheet_name)

            sheet_info = {
                'rows': len(df),
                'columns': list(df.columns),
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'null_counts': df.isnull().sum().to_dict(),
                'sample_data': df.head(3).to_dict('records') if len(df) > 0 else []
            }

            file_info['sheets'][sheet_name] = sheet_info

            print(f"Rows: {len(df)}")
            print(f"Columns ({len(df.columns)}): {', '.join(df.columns)}")

            # Show sample data
            if len(df) > 0:
                print("\nFirst 3 rows:")
                print(df.head(3).to_string())

                # Check for key fields we're looking for
                key_fields = ['External participant', 'Alternate sample ID', 'Study Code',
                             'Storage status', 'Visit', 'Timepoint', 'Storage unit', 'Label path']
                found_fields = [field for field in key_fields if field in df.columns]
                if found_fields:
                    print(f"\n✓ Found key fields: {', '.join(found_fields)}")
            else:
                print("Empty sheet")

    except Exception as e:
        print(f"Error reading file: {e}")
        file_info['error'] = str(e)

    return file_info

def main():
    """Main exploration function"""
    data_dir = Path('/Users/nbrazeau/Documents/Github/WoodsDashboard/data/raw')

    # Find all Excel files
    excel_files = list(data_dir.glob('*.xlsx')) + list(data_dir.glob('*.xls'))
    excel_files = [f for f in excel_files if not f.name.startswith('~')]  # Skip temp files

    print(f"Found {len(excel_files)} Excel file(s) to explore\n")

    all_file_info = {}

    for excel_file in sorted(excel_files):
        file_info = explore_excel_file(excel_file)
        all_file_info[file_info['filename']] = file_info

    # Save exploration results
    output_path = Path('/Users/nbrazeau/Documents/Github/WoodsDashboard/docs/metadata_exploration.json')
    with open(output_path, 'w') as f:
        json.dump(all_file_info, f, indent=2, default=str)

    print(f"\n{'='*80}")
    print(f"Exploration complete! Results saved to: {output_path}")
    print(f"{'='*80}")

    # Summary
    print("\n\nSUMMARY")
    print(f"{'='*80}")
    print(f"Total files explored: {len(all_file_info)}")

    for filename, info in all_file_info.items():
        if 'error' not in info:
            total_rows = sum(sheet['rows'] for sheet in info['sheets'].values())
            print(f"\n{filename}:")
            print(f"  - {len(info['sheets'])} sheet(s)")
            print(f"  - {total_rows} total rows")
            for sheet_name, sheet_info in info['sheets'].items():
                print(f"    • {sheet_name}: {sheet_info['rows']} rows, {len(sheet_info['columns'])} columns")

if __name__ == '__main__':
    main()
