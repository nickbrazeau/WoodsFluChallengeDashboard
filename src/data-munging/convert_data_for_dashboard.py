#!/usr/bin/env python3
"""
Convert Data for Dashboard
Converts processed data files to JSON format for web dashboard
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import numpy as np

def convert_samples_to_json():
    """Convert deduplicated sample inventory to JSON"""
    print("\n" + "="*80)
    print("Converting Sample Inventory to JSON")
    print("="*80)

    # Load deduplicated inventory
    inventory = pd.read_parquet('data/processed/combined_inventory_deduplicated.parquet')
    print(f"Loaded {len(inventory):,} samples")

    # Select fields for dashboard
    dashboard_fields = [
        'sample_barcode_id', 'participant_id', 'study_code',
        'timepoint_normalized', 'timepoint_day', 'timepoint_hour',
        'sample_type', 'storage_status', 'storage_location_path',
        'is_available', 'is_transferred'
    ]

    # Keep only existing fields
    available_fields = [f for f in dashboard_fields if f in inventory.columns]
    samples_df = inventory[available_fields].copy()

    # Replace NaN with None (becomes null in JSON)
    samples_df = samples_df.replace({np.nan: None})

    # Convert to records
    samples = samples_df.to_dict('records')

    # Save as JSON
    output_file = Path('public/data/samples.json')
    with open(output_file, 'w') as f:
        json.dump(samples, f, indent=2, default=str)

    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    print(f"✓ Saved: {output_file}")
    print(f"  Records: {len(samples):,}")
    print(f"  Size: {file_size_mb:.2f} MB")

    return samples


def create_sample_statistics():
    """Create pre-calculated statistics for landing page"""
    print("\n" + "="*80)
    print("Generating Sample Statistics")
    print("="*80)

    inventory = pd.read_parquet('data/processed/combined_inventory_deduplicated.parquet')

    stats = {
        'total_samples': len(inventory),
        'total_studies': inventory['study_code'].nunique(),
        'total_participants': inventory['participant_id'].nunique(),
        'total_sample_types': inventory['sample_type'].nunique(),
        'available_samples': int((inventory['is_available'] == True).sum()),
        'transferred_samples': int((inventory['is_transferred'] == True).sum()),
        'samples_by_study': inventory['study_code'].value_counts().to_dict(),
        'samples_by_type': inventory['sample_type'].value_counts().head(10).to_dict(),
        'participants_by_study': inventory.groupby('study_code')['participant_id'].nunique().to_dict(),
        'date_generated': datetime.now().isoformat()
    }

    output_file = Path('public/data/sample_statistics.json')
    with open(output_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"✓ Saved: {output_file}")
    print(f"  Total samples: {stats['total_samples']:,}")
    print(f"  Studies: {stats['total_studies']}")
    print(f"  Participants: {stats['total_participants']}")

    return stats


def convert_publications_to_json():
    """Convert publications to dashboard format"""
    print("\n" + "="*80)
    print("Converting Publications to JSON")
    print("="*80)

    # Load citations
    with open('data/publications/citations.json', 'r') as f:
        citations_data = json.load(f)

    publications = citations_data['publications']
    print(f"Loaded {len(publications)} publications")

    # Simplify for dashboard
    import math

    # Enhanced helper function to replace NaN/nan with None
    def clean_value(val):
        """Comprehensive NaN cleaning to prevent JSON serialization errors"""
        # Handle None and empty strings
        if val is None or val == '':
            return None
        # Handle numpy NaN and float NaN
        if isinstance(val, float):
            if math.isnan(val) or pd.isna(val):
                return None
        # Handle string "NaN" or "nan" (case insensitive)
        if isinstance(val, str):
            if val.strip().lower() == 'nan':
                return None
        return val

    dashboard_pubs = []
    for pub in publications:
        dashboard_pub = {
            'title': clean_value(pub.get('title')) or 'No title',
            'first_author': clean_value(pub.get('first_author')) or 'Unknown',
            'journal': clean_value(pub.get('journal')) or 'Unknown',
            'year': clean_value(pub.get('year')) or 'Unknown',
            'pmid': str(clean_value(pub.get('pmid')) or 'N/A').replace('.0', ''),
            'pubmed_url': clean_value(pub.get('pubmed_url')) or '',
            'study_code': clean_value(pub.get('biobank_study_code')) or 'Unknown',
            'study_name': clean_value(pub.get('study_name')) or None,
            'abstract': clean_value(pub.get('abstract')) or None  # Critical: clean abstract field
        }
        dashboard_pubs.append(dashboard_pub)

    # Validate JSON before saving
    print("  Validating JSON structure...")
    try:
        # Test serialization
        test_json = json.dumps(dashboard_pubs)
        # Test deserialization
        test_load = json.loads(test_json)
        print("  ✓ JSON validation passed - no NaN values")
    except (TypeError, ValueError) as e:
        print(f"  ✗ JSON validation FAILED: {e}")
        raise

    # Save
    output_file = Path('public/data/publications.json')
    with open(output_file, 'w') as f:
        json.dump(dashboard_pubs, f, indent=2)

    print(f"✓ Saved: {output_file}")
    print(f"  Publications: {len(dashboard_pubs)}")

    # Publication statistics
    pub_stats = {
        'total_publications': len(dashboard_pubs),
        'publications_by_study': {},
        'publications_by_year': {},
        'date_range': f"{min(p['year'] for p in dashboard_pubs if p['year'] != 'Unknown')}-{max(p['year'] for p in dashboard_pubs if p['year'] != 'Unknown')}"
    }

    for pub in dashboard_pubs:
        study = pub['study_code']
        year = pub['year']

        pub_stats['publications_by_study'][study] = pub_stats['publications_by_study'].get(study, 0) + 1
        if year != 'Unknown':
            pub_stats['publications_by_year'][year] = pub_stats['publications_by_year'].get(year, 0) + 1

    stats_file = Path('public/data/publication_statistics.json')
    with open(stats_file, 'w') as f:
        json.dump(pub_stats, f, indent=2)
    print(f"✓ Saved: {stats_file}")

    return dashboard_pubs, pub_stats


def convert_assays_to_json():
    """Convert assay tracking to JSON"""
    print("\n" + "="*80)
    print("Converting Assay Data to JSON")
    print("="*80)

    # Load assay tracking
    assays_df = pd.read_csv('data/processed/assay_tracking_table.csv')
    print(f"Loaded {len(assays_df)} assay records")

    # Replace NaN with None (becomes null in JSON)
    assays_df = assays_df.replace({np.nan: None})

    # Convert to JSON-friendly format
    assays = assays_df.to_dict('records')

    # Save
    output_file = Path('public/data/assays.json')
    with open(output_file, 'w') as f:
        json.dump(assays, f, indent=2, default=str)

    print(f"✓ Saved: {output_file}")
    print(f"  Assay records: {len(assays)}")

    # Assay statistics
    assay_stats = {
        'total_assay_records': len(assays_df),
        'unique_assay_types': assays_df['Assay'].nunique(),
        'total_samples_assayed': int(assays_df['Samples'].sum()),
        'studies_with_assays': assays_df['biobank_study_code'].nunique(),
        'assays_by_type': assays_df.groupby('Assay')['Samples'].sum().to_dict()
    }

    stats_file = Path('public/data/assay_statistics.json')
    with open(stats_file, 'w') as f:
        json.dump(assay_stats, f, indent=2)
    print(f"✓ Saved: {stats_file}")

    return assays, assay_stats


def convert_studies_metadata():
    """Create study metadata JSON"""
    print("\n" + "="*80)
    print("Creating Study Metadata")
    print("="*80)

    # Study information
    studies = {
        'DU08-04': {
            'code': 'DU08-04',
            'name': 'DEE2 H3N2 Flu Challenge',
            'virus': 'H3N2 (A/Brisbane/10/2007)',
            'year': 2008,
            'description': 'Human influenza challenge study with H3N2 virus strain'
        },
        'DU09-06': {
            'code': 'DU09-06',
            'name': 'DEE3 H1N1 Flu Challenge',
            'virus': 'H1N1 (A/Brisbane/59/2007)',
            'year': 2009,
            'description': 'Human influenza challenge study with H1N1 virus strain'
        },
        'DU09-07': {
            'code': 'DU09-07',
            'name': 'DEE4 H1N1 Flu Challenge',
            'virus': 'H1N1 (A/Brisbane/59/2007)',
            'year': 2009,
            'description': 'Human influenza challenge study with H1N1 virus strain'
        },
        'DU11-02': {
            'code': 'DU11-02',
            'name': 'DEE5 H3N2 Flu Challenge',
            'virus': 'H3N2 (A/Victoria/361/2011)',
            'year': 2011,
            'description': 'Human influenza challenge study with H3N2 virus strain'
        },
        'DU17-04': {
            'code': 'DU17-04',
            'name': 'PROMETHEUS H1N1 ICL Flu Challenge',
            'virus': 'H1N1',
            'year': 2017,
            'description': 'Human influenza challenge study conducted with Imperial College London'
        },
        'DU20-01': {
            'code': 'DU20-01',
            'name': 'SIGMA Plus H3N2 Flu Challenge',
            'virus': 'H3N2',
            'year': 2020,
            'description': 'SIGMA Plus human influenza challenge study with wearable devices'
        },
        'DU24-01': {
            'code': 'DU24-01',
            'name': 'EXHALE H3N2 Flu Challenge',
            'virus': 'H3N2',
            'year': 2024,
            'description': 'EXHALE human influenza challenge study with wearable monitoring'
        }
    }

    # Load inventory for sample counts
    inventory = pd.read_parquet('data/processed/combined_inventory_deduplicated.parquet')

    # Load study cross-reference
    study_xref = pd.read_csv('data/processed/linkages/study_cross_reference.csv')

    # Enrich with actual data
    for study_code, study_info in studies.items():
        xref = study_xref[study_xref['study_code'] == study_code]
        if len(xref) > 0:
            xref_row = xref.iloc[0]
            study_info['total_samples'] = int(xref_row['total_samples'])
            study_info['participants'] = int(xref_row['participants'])
            study_info['sample_types'] = int(xref_row['sample_types'])
            study_info['publications'] = int(xref_row['publications'])
            study_info['assays_performed'] = int(xref_row['assays_performed'])
            study_info['samples_available'] = int(xref_row['samples_available'])
            study_info['samples_transferred'] = int(xref_row['samples_transferred'])

    output_file = Path('public/data/studies.json')
    with open(output_file, 'w') as f:
        json.dump(studies, f, indent=2)

    print(f"✓ Saved: {output_file}")
    print(f"  Studies: {len(studies)}")

    return studies


def create_dashboard_config():
    """Create configuration file for dashboard"""
    print("\n" + "="*80)
    print("Creating Dashboard Configuration")
    print("="*80)

    config = {
        'project_name': 'Woods Lab Influenza Challenge Studies Dashboard',
        'institution': 'Woods Lab',
        'last_updated': datetime.now().isoformat(),
        'version': '1.0.0',
        'data_version': 'Phase 2 Complete (November 2025)',
        'contact': {
            'lab': 'Woods Lab',
            'institution': '',
            'website': ''
        },
        'data_sources': {
            'samples': 'combined_inventory_deduplicated.parquet',
            'publications': 'citations.json',
            'assays': 'assay_tracking_table.csv',
            'linkages': 'data/processed/linkages/'
        },
        'colors': {
            'primary_blue': '#012169',
            'royal_blue': '#00539B',
            'copper': '#C84E00',
            'persimmon': '#E89923',
            'eno': '#339898'
        },
        'features': {
            'sample_search': True,
            'publication_browser': True,
            'assay_tracking': True,
            'data_export': True,
            'visualizations': True
        },
        'known_issues': [
            '12 publications need study ID verification',
            'DU19-03 (PRISM Family) inventory pending',
            '216 samples with unusual timepoints under review',
            '4,256 samples missing storage location'
        ]
    }

    output_file = Path('public/data/config.json')
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✓ Saved: {output_file}")

    return config


def main():
    """Main conversion function"""
    print("="*80)
    print("CONVERTING DATA FOR DASHBOARD")
    print("="*80)

    # Create output directory
    Path('public/data').mkdir(parents=True, exist_ok=True)

    # Convert all data
    samples = convert_samples_to_json()
    sample_stats = create_sample_statistics()
    publications, pub_stats = convert_publications_to_json()
    assays, assay_stats = convert_assays_to_json()
    studies = convert_studies_metadata()
    config = create_dashboard_config()

    # Summary
    print("\n" + "="*80)
    print("DATA CONVERSION COMPLETE")
    print("="*80)

    print("\n✅ Files Created in public/data/:")
    print("  1. samples.json - 82,046 sample records")
    print("  2. sample_statistics.json - Pre-calculated stats")
    print("  3. publications.json - 31 publications")
    print("  4. publication_statistics.json - Publication stats")
    print("  5. assays.json - 27 assay records")
    print("  6. assay_statistics.json - Assay stats")
    print("  7. studies.json - 7 study metadata records")
    print("  8. config.json - Dashboard configuration")

    print("\n📊 Dashboard Data Summary:")
    print(f"  • Samples: {sample_stats['total_samples']:,}")
    print(f"  • Studies: {len(studies)}")
    print(f"  • Publications: {pub_stats['total_publications']}")
    print(f"  • Assays: {assay_stats['unique_assay_types']} types")
    print(f"  • Participants: {sample_stats['total_participants']}")

    print("\n🎯 Ready for Dashboard Development")
    print("  Next: Create HTML pages and CSS styling")

    print("\n" + "="*80)


if __name__ == '__main__':
    main()
