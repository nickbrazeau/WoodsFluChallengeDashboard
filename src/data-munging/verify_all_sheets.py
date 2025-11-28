#!/usr/bin/env python3
"""
Verify All Sheets in All Excel Workbooks
Comprehensive check to ensure no data was missed
"""

import pandas as pd
from pathlib import Path
import json

def check_all_sheets():
    """Check all sheets in all Excel files"""
    data_dir = Path('/Users/nbrazeau/Documents/Github/WoodsDashboard/data/raw')
    excel_files = list(data_dir.glob('*.xlsx')) + list(data_dir.glob('*.xls'))
    excel_files = [f for f in excel_files if not f.name.startswith('~')]

    print("="*80)
    print("COMPREHENSIVE SHEET VERIFICATION")
    print("="*80)
    print(f"\nFound {len(excel_files)} Excel files\n")

    all_file_info = {}

    for excel_file in sorted(excel_files):
        print(f"\n{'='*80}")
        print(f"FILE: {excel_file.name}")
        print(f"{'='*80}")

        try:
            xls = pd.ExcelFile(excel_file)
            sheet_names = xls.sheet_names

            print(f"Total sheets: {len(sheet_names)}")
            print(f"Sheet names: {', '.join(sheet_names)}\n")

            file_info = {
                'filename': excel_file.name,
                'total_sheets': len(sheet_names),
                'sheets': {}
            }

            for sheet_name in sheet_names:
                print(f"  Sheet: '{sheet_name}'")
                df = pd.read_excel(excel_file, sheet_name=sheet_name)

                sheet_info = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'non_null_columns': [col for col in df.columns if df[col].notna().any()]
                }

                print(f"    Rows: {len(df)}")
                print(f"    Columns: {len(df.columns)}")
                print(f"    Non-empty columns: {len(sheet_info['non_null_columns'])}")

                # Check if this is a data sheet or pivot/summary
                if len(df) > 0 and len(sheet_info['non_null_columns']) > 0:
                    print(f"    ✓ Contains data")
                    print(f"    Sample columns: {', '.join(df.columns[:5].tolist())}")
                else:
                    print(f"    ⚠️  Empty or header-only sheet")

                file_info['sheets'][sheet_name] = sheet_info
                print()

            all_file_info[excel_file.name] = file_info

        except Exception as e:
            print(f"  ✗ Error reading file: {e}\n")
            all_file_info[excel_file.name] = {'error': str(e)}

    # Save verification report
    output_file = Path('/Users/nbrazeau/Documents/Github/WoodsDashboard/docs/sheet_verification.json')
    with open(output_file, 'w') as f:
        json.dump(all_file_info, f, indent=2)

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    total_sheets = 0
    total_data_sheets = 0

    for filename, info in all_file_info.items():
        if 'error' not in info:
            print(f"\n{filename}:")
            total_sheets += info['total_sheets']
            for sheet_name, sheet_info in info['sheets'].items():
                data_indicator = "✓" if sheet_info['rows'] > 0 and len(sheet_info['non_null_columns']) > 0 else "○"
                print(f"  {data_indicator} {sheet_name}: {sheet_info['rows']} rows, {sheet_info['columns']} columns")
                if sheet_info['rows'] > 0 and len(sheet_info['non_null_columns']) > 0:
                    total_data_sheets += 1

    print(f"\nTotal sheets across all files: {total_sheets}")
    print(f"Sheets with data: {total_data_sheets}")
    print(f"\n✓ Verification complete. Report saved to: {output_file}")

if __name__ == '__main__':
    check_all_sheets()
