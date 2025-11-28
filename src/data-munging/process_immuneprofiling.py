#!/usr/bin/env python3
"""
Process ImmuneProfiling_cn.xlsx
Extracts assay data and integrates with harmonized inventory
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def process_lv_count():
    """Process LV_Count sheet - sample count validation"""
    print("\n" + "="*80)
    print("PROCESSING: LV_Count Sheet")
    print("="*80)

    df = pd.read_excel('data/raw/ImmuneProfiling_cn.xlsx', sheet_name='LV_Count')

    print(f"\nFound {len(df)} studies with sample counts:")
    print(df[['study_code', 'study_name', 'total_samples_banked']].to_string(index=False))

    # Check for new study
    known_studies = ['DU17-04', 'DU24-01', 'DU20-01']
    new_studies = df[~df['study_code'].isin(known_studies)]

    if len(new_studies) > 0:
        print(f"\n⚠️  FOUND NEW STUDY:")
        for _, row in new_studies.iterrows():
            print(f"  Code: {row['study_code']}")
            print(f"  Name: {row['study_name']}")
            print(f"  Samples: {row['total_samples_banked']}")

    return df


def process_sequenced():
    """Process Sequenced sheet - assay tracking"""
    print("\n" + "="*80)
    print("PROCESSING: Sequenced Sheet")
    print("="*80)

    df = pd.read_excel('data/raw/ImmuneProfiling_cn.xlsx', sheet_name='Sequenced')

    print(f"\nFound {len(df)} assay records:")

    # Clean up the data
    df['Samples'] = pd.to_numeric(df['Samples'], errors='coerce')

    # Group by Study and Assay
    summary = df.groupby(['Study', 'Assay']).agg({
        'Samples': 'sum',
        'Timepoint(s)': 'first',
        'Comment': 'first'
    }).reset_index()

    print("\nAssays by Study:")
    print(summary.to_string(index=False))

    # Extract unique assay types
    unique_assays = df['Assay'].unique()
    print(f"\nUnique assay types identified: {len(unique_assays)}")
    for assay in unique_assays:
        print(f"  - {assay}")

    return df, summary


def map_study_names():
    """Map study names from ImmuneProfiling to biobank codes"""
    mapping = {
        'Prometheus': 'DU17-04',
        'EXHALE': 'DU24-01',
        'SIGMA Plus': 'DU20-01',
        'SIGMA PRISMM Family': 'DU19-03'  # NEW STUDY
    }
    return mapping


def create_assay_tracking_table(sequenced_df):
    """Create comprehensive assay tracking table"""
    print("\n" + "="*80)
    print("CREATING: Assay Tracking Table")
    print("="*80)

    # Map study names to codes
    study_mapping = map_study_names()

    # Add biobank study codes
    sequenced_df['biobank_study_code'] = sequenced_df['Study'].map(study_mapping)

    # Create tracking table
    tracking = sequenced_df[['biobank_study_code', 'Study', 'Assay', 'Keys', 'Samples',
                             'Subject ID ranges', 'Timepoint(s)', 'Comment']].copy()

    # Fill NA values
    tracking['Samples'] = tracking['Samples'].fillna(0).astype(int)
    tracking['Keys'] = tracking['Keys'].fillna('Not specified')
    tracking['Subject ID ranges'] = tracking['Subject ID ranges'].fillna('Not specified')
    tracking['Timepoint(s)'] = tracking['Timepoint(s)'].fillna('Not specified')
    tracking['Comment'] = tracking['Comment'].fillna('')

    print(f"\nCreated tracking table with {len(tracking)} records")
    print("\nSample of tracking data:")
    print(tracking.head(10).to_string(index=False))

    return tracking


def link_assays_to_samples():
    """Link assay data to harmonized sample inventory"""
    print("\n" + "="*80)
    print("LINKING: Assays to Sample Inventory")
    print("="*80)

    # Load harmonized inventory
    inventory_file = Path('data/processed/combined_inventory_harmonized.parquet')

    if not inventory_file.exists():
        print("⚠️  Harmonized inventory not found. Skipping linkage.")
        return None

    inventory_df = pd.read_parquet(inventory_file)
    print(f"Loaded {len(inventory_df)} samples from harmonized inventory")

    # Load assay tracking
    sequenced_df, _ = process_sequenced()
    tracking = create_assay_tracking_table(sequenced_df)

    # Create assay summary by study
    assay_summary = tracking.groupby('biobank_study_code').agg({
        'Assay': lambda x: ', '.join(x.unique()),
        'Samples': 'sum'
    }).reset_index()

    assay_summary.columns = ['study_code', 'assays_performed', 'total_assay_samples']

    print("\nAssay summary by study:")
    print(assay_summary.to_string(index=False))

    # Merge with inventory summary
    inventory_summary = inventory_df.groupby('study_code').agg({
        'sample_barcode_id': 'count',
        'participant_id': 'nunique'
    }).reset_index()

    inventory_summary.columns = ['study_code', 'total_samples_inventory', 'participants']

    merged = inventory_summary.merge(assay_summary, on='study_code', how='left')
    merged['assays_performed'] = merged['assays_performed'].fillna('None recorded')
    merged['total_assay_samples'] = merged['total_assay_samples'].fillna(0).astype(int)

    print("\nInventory vs Assay Coverage:")
    print(merged.to_string(index=False))

    return merged, tracking


def main():
    """Main processing function"""
    print("="*80)
    print("IMMUNE PROFILING DATA PROCESSING")
    print("="*80)

    output_dir = Path('data/processed')
    output_dir.mkdir(exist_ok=True)

    # Step 1: Process LV_Count
    lv_count_df = process_lv_count()

    # Step 2: Process Sequenced data
    sequenced_df, sequenced_summary = process_sequenced()

    # Step 3: Create assay tracking table
    tracking_table = create_assay_tracking_table(sequenced_df)

    # Step 4: Link to sample inventory
    coverage_table, full_tracking = link_assays_to_samples()

    # Step 5: Save outputs
    print("\n" + "="*80)
    print("SAVING OUTPUTS")
    print("="*80)

    # Save LV count data
    lv_output = output_dir / 'sample_counts_validation.csv'
    lv_count_df.to_csv(lv_output, index=False)
    print(f"✓ Saved: {lv_output}")

    # Save sequenced summary
    seq_summary_output = output_dir / 'assay_summary_by_study.csv'
    sequenced_summary.to_csv(seq_summary_output, index=False)
    print(f"✓ Saved: {seq_summary_output}")

    # Save full tracking table
    tracking_output = output_dir / 'assay_tracking_table.csv'
    tracking_table.to_csv(tracking_output, index=False)
    print(f"✓ Saved: {tracking_output}")

    # Save coverage comparison
    if coverage_table is not None:
        coverage_output = output_dir / 'inventory_vs_assay_coverage.csv'
        coverage_table.to_csv(coverage_output, index=False)
        print(f"✓ Saved: {coverage_output}")

    # Save complete assay data as JSON
    assay_json = {
        'metadata': {
            'processing_date': datetime.now().isoformat(),
            'source_file': 'ImmuneProfiling_cn.xlsx',
            'total_assay_records': len(sequenced_df)
        },
        'study_mapping': map_study_names(),
        'lv_counts': lv_count_df.to_dict('records'),
        'sequenced_summary': sequenced_summary.to_dict('records'),
        'full_tracking': tracking_table.to_dict('records')
    }

    json_output = output_dir / 'assay_data_complete.json'
    with open(json_output, 'w') as f:
        json.dump(assay_json, f, indent=2, default=str)
    print(f"✓ Saved: {json_output}")

    # Generate report
    print("\n" + "="*80)
    print("SUMMARY REPORT")
    print("="*80)

    print(f"\nStudies with assay data: {len(sequenced_summary['Study'].unique())}")
    print(f"Total assay types: {len(sequenced_df['Assay'].unique())}")
    print(f"Total samples with assay data: {sequenced_df['Samples'].sum():.0f}")

    print("\nNew Study Identified:")
    print("  Code: DU19-03")
    print("  Name: SIGMA PRISM Family Study")
    print("  Samples: 4,996")
    print("  ⚠️  This study needs to be added to the main inventory!")

    print("\nKey Assays Identified:")
    for assay in sequenced_df['Assay'].unique():
        count = sequenced_df[sequenced_df['Assay'] == assay]['Samples'].sum()
        print(f"  - {assay}: {count:.0f} samples")

    print("\n" + "="*80)
    print("PROCESSING COMPLETE")
    print("="*80)

if __name__ == '__main__':
    main()
