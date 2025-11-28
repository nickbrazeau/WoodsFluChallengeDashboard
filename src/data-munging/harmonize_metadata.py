#!/usr/bin/env python3
"""
Metadata Harmonization Script
Harmonizes all biobank inventory Excel files into standardized format
"""

import pandas as pd
import re
from pathlib import Path
import json
from datetime import datetime

class TimepointNormalizer:
    """Normalizes timepoint labels across different study formats"""

    @staticmethod
    def extract_day_hour(timepoint_str):
        """
        Extract day and hour from various timepoint formats

        Returns: tuple (day, hour, original_string)
        """
        if pd.isna(timepoint_str):
            return (None, None, timepoint_str)

        timepoint_str = str(timepoint_str).strip()

        # Pattern 1: "XXX hours (Day Y)" or "XXX.X hours (Day Y)"
        match = re.search(r'(\d+\.?\d*)\s*hours?\s*\(Day\s*(-?\d+)\)', timepoint_str, re.IGNORECASE)
        if match:
            hour = float(match.group(1))
            day = int(match.group(2))
            return (day, hour, timepoint_str)

        # Pattern 2: "Baseline -XX hours (Day Y)"
        match = re.search(r'Baseline\s*(-?\d+)\s*hours?\s*\(Day\s*(-?\d+)\)', timepoint_str, re.IGNORECASE)
        if match:
            hour = float(match.group(1))
            day = int(match.group(2))
            return (day, hour, timepoint_str)

        # Pattern 3: "XXX hrs (Day Y)" or "-XXXX hrs (Day Y)"
        match = re.search(r'(-?\d+)\s*hrs?\s*\(Day\s*(-?\d+)\)', timepoint_str, re.IGNORECASE)
        if match:
            hour = float(match.group(1))
            day = int(match.group(2))
            return (day, hour, timepoint_str)

        # Pattern 4: "Day XX" or "Day -X"
        match = re.search(r'Day\s*(-?\d+)', timepoint_str, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            return (day, None, timepoint_str)

        # Pattern 5: "Baseline (Day Y)" or "Pre-Challenge Baseline (Day Y)"
        match = re.search(r'Baseline.*\(Day\s*(-?\d+)\)', timepoint_str, re.IGNORECASE)
        if match:
            day = int(match.group(1))
            return (day, 0.0, timepoint_str)

        # Pattern 6: Just "Baseline" - assume Day -1
        if re.search(r'^Baseline$', timepoint_str, re.IGNORECASE):
            return (-1, 0.0, timepoint_str)

        # Pattern 7: "Screening" - special pre-study timepoint
        if re.search(r'Screening', timepoint_str, re.IGNORECASE):
            return (-999, None, timepoint_str)  # Special code for screening

        # Unable to parse
        return (None, None, timepoint_str)

    @staticmethod
    def normalize_timepoint(timepoint_str):
        """
        Convert timepoint to standardized format

        Returns: dict with parsed timepoint information
        """
        day, hour, original = TimepointNormalizer.extract_day_hour(timepoint_str)

        result = {
            'original_timepoint': original,
            'day': day,
            'hour': hour,
            'normalized_timepoint': None,
            'is_pre_challenge': None,
            'is_inoculation': None,
            'is_post_challenge': None,
            'is_screening': None
        }

        if day is None:
            return result

        # Special handling for screening
        if day == -999:
            result['normalized_timepoint'] = 'Screening'
            result['is_screening'] = True
            result['is_pre_challenge'] = True
            return result

        # Determine challenge phase
        result['is_pre_challenge'] = (day < 0)
        result['is_inoculation'] = (day == 0)
        result['is_post_challenge'] = (day > 0)
        result['is_screening'] = False

        # Create normalized label
        if hour is not None:
            result['normalized_timepoint'] = f"Day {day} ({hour:.1f} hrs)"
        else:
            result['normalized_timepoint'] = f"Day {day}"

        return result


def load_and_harmonize_file(filepath):
    """Load a single Excel file and harmonize to standard schema"""
    print(f"\nProcessing: {filepath.name}")

    try:
        # Read Query 1 sheet (main data)
        df = pd.read_excel(filepath, sheet_name='Query 1')

        # Standardize column names to match data model
        column_mapping = {
            'External Participant ID': 'participant_id',
            'LV Sample ID': 'labvantage_sample_id',
            'Alternate Sample ID': 'sample_barcode_id',
            'Study ID on Sample Family Table': 'study_family_id',
            'Study Code': 'study_code',
            'Storage Status': 'storage_status',
            'Visit / Time Point Name on Sample Family Table': 'timepoint_raw',
            'Current Storage Unit ID': 'storage_unit_id',
            'Label Path': 'storage_location_path',
            'Sample Type': 'sample_type',
            'Note Text': 'notes',
            'Additive Type for Sample': 'additive',
            'Current Qty': 'quantity',
            'Current Units': 'quantity_units'
        }

        df = df.rename(columns=column_mapping)

        # Ensure consistent data types
        df['participant_id'] = df['participant_id'].astype(str)
        df['sample_barcode_id'] = df['sample_barcode_id'].astype(str)
        df['study_code'] = df['study_code'].astype(str)

        # Extract study information from filename
        filename = filepath.stem
        study_name_match = re.search(r'_(.+?)_Full Inventory', filename)
        study_name = study_name_match.group(1) if study_name_match else 'Unknown'

        df['study_name'] = study_name
        df['source_file'] = filepath.name

        # Normalize timepoints
        print(f"  Normalizing {len(df)} timepoints...")
        timepoint_data = df['timepoint_raw'].apply(TimepointNormalizer.normalize_timepoint)

        # Expand timepoint data into separate columns
        df['timepoint_day'] = timepoint_data.apply(lambda x: x['day'])
        df['timepoint_hour'] = timepoint_data.apply(lambda x: x['hour'])
        df['timepoint_normalized'] = timepoint_data.apply(lambda x: x['normalized_timepoint'])
        df['is_pre_challenge'] = timepoint_data.apply(lambda x: x['is_pre_challenge'])
        df['is_inoculation'] = timepoint_data.apply(lambda x: x['is_inoculation'])
        df['is_post_challenge'] = timepoint_data.apply(lambda x: x['is_post_challenge'])
        df['is_screening'] = timepoint_data.apply(lambda x: x['is_screening'])

        # Standardize storage status
        df['is_available'] = df['storage_status'].str.contains('In Circulation', na=False)
        df['is_transferred'] = df['storage_status'].str.contains('3rd Party Transfer', na=False)

        # Add processing metadata
        df['harmonization_date'] = datetime.now().isoformat()
        df['harmonization_version'] = '1.0'

        print(f"  ✓ Processed {len(df)} samples")
        print(f"    - {df['participant_id'].nunique()} unique participants")
        print(f"    - {df['sample_type'].nunique()} sample types")
        print(f"    - {df['is_available'].sum()} samples available")
        print(f"    - {df['is_transferred'].sum()} samples transferred")

        return df

    except Exception as e:
        print(f"  ✗ Error processing file: {e}")
        return None


def main():
    """Main harmonization function"""
    print("="*80)
    print("METADATA HARMONIZATION")
    print("="*80)

    data_dir = Path('/Users/nbrazeau/Documents/Github/WoodsDashboard/data/raw')
    output_dir = Path('/Users/nbrazeau/Documents/Github/WoodsDashboard/data/processed')

    # Find all inventory Excel files (exclude ImmuneProfiling for now)
    inventory_pattern = '*_Full Inventory.xlsx'
    excel_files = list(data_dir.glob(inventory_pattern))

    print(f"\nFound {len(excel_files)} inventory files to process\n")

    # Process each file
    all_dfs = []
    for excel_file in sorted(excel_files):
        df = load_and_harmonize_file(excel_file)
        if df is not None:
            all_dfs.append(df)

    if not all_dfs:
        print("\n✗ No data processed!")
        return

    # Combine all dataframes
    print("\n" + "="*80)
    print("COMBINING DATA")
    print("="*80)

    combined_df = pd.concat(all_dfs, ignore_index=True)

    print(f"\nCombined dataset:")
    print(f"  - Total samples: {len(combined_df):,}")
    print(f"  - Total participants: {combined_df['participant_id'].nunique()}")
    print(f"  - Studies: {combined_df['study_code'].nunique()}")
    print(f"  - Date range: {combined_df['study_code'].min()} to {combined_df['study_code'].max()}")

    # Save combined dataset
    output_file = output_dir / 'combined_inventory_harmonized.csv'
    combined_df.to_csv(output_file, index=False)
    print(f"\n✓ Saved combined dataset: {output_file}")

    # Save as parquet for efficient loading
    output_file_parquet = output_dir / 'combined_inventory_harmonized.parquet'
    combined_df.to_parquet(output_file_parquet, index=False)
    print(f"✓ Saved parquet format: {output_file_parquet}")

    # Generate summary statistics
    print("\n" + "="*80)
    print("SUMMARY STATISTICS BY STUDY")
    print("="*80)

    summary = combined_df.groupby('study_code').agg({
        'sample_barcode_id': 'count',
        'participant_id': 'nunique',
        'sample_type': 'nunique',
        'is_available': 'sum',
        'is_transferred': 'sum',
        'timepoint_day': ['min', 'max']
    }).round(2)

    print("\n", summary.to_string())

    # Save summary
    summary_file = output_dir / 'study_summary_statistics.csv'
    summary.to_csv(summary_file)
    print(f"\n✓ Saved summary statistics: {summary_file}")

    # Generate data quality report
    print("\n" + "="*80)
    print("DATA QUALITY REPORT")
    print("="*80)

    quality_report = {
        'total_samples': len(combined_df),
        'missing_timepoint_day': combined_df['timepoint_day'].isna().sum(),
        'missing_storage_location': combined_df['storage_location_path'].isna().sum(),
        'missing_sample_type': combined_df['sample_type'].isna().sum(),
        'missing_quantity': combined_df['quantity'].isna().sum(),
        'unparseable_timepoints': combined_df[combined_df['timepoint_day'].isna()]['timepoint_raw'].unique().tolist()[:20]
    }

    print(f"\nMissing Data:")
    print(f"  - Timepoint day: {quality_report['missing_timepoint_day']} ({quality_report['missing_timepoint_day']/len(combined_df)*100:.1f}%)")
    print(f"  - Storage location: {quality_report['missing_storage_location']} ({quality_report['missing_storage_location']/len(combined_df)*100:.1f}%)")
    print(f"  - Sample type: {quality_report['missing_sample_type']} ({quality_report['missing_sample_type']/len(combined_df)*100:.1f}%)")
    print(f"  - Quantity: {quality_report['missing_quantity']} ({quality_report['missing_quantity']/len(combined_df)*100:.1f}%)")

    if quality_report['unparseable_timepoints']:
        print(f"\nUnparseable timepoints (first 20):")
        for tp in quality_report['unparseable_timepoints']:
            print(f"  - {tp}")

    quality_file = output_dir / 'data_quality_report.json'
    with open(quality_file, 'w') as f:
        json.dump(quality_report, f, indent=2, default=str)
    print(f"\n✓ Saved quality report: {quality_file}")

    print("\n" + "="*80)
    print("HARMONIZATION COMPLETE!")
    print("="*80)
    print(f"\nOutput files created in: {output_dir}")
    print(f"  1. combined_inventory_harmonized.csv")
    print(f"  2. combined_inventory_harmonized.parquet")
    print(f"  3. study_summary_statistics.csv")
    print(f"  4. data_quality_report.json")


if __name__ == '__main__':
    main()
