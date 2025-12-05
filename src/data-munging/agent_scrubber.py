#!/usr/bin/env python3
"""
PHI Scrubber Agent - Generates public-safe data files

This agent removes Protected Health Information (PHI) from dashboard data files
to create public-facing versions suitable for web deployment.

Author: Claude Code
Date: December 4, 2025
"""

import json
from pathlib import Path
from datetime import datetime


def scrub_samples():
    """
    Remove storage_location_path from all samples.

    Loads the private samples file and creates a public version with
    storage locations set to null.

    Returns:
        tuple: (scrubbed samples list, count of storage locations removed)
    """
    print("Scrubbing samples data...")

    # Load private data
    private_file = Path('public/data/samples_private.json')
    if not private_file.exists():
        raise FileNotFoundError(
            f"Private samples file not found: {private_file}\n"
            "Please run convert_data_for_dashboard.py first."
        )

    with open(private_file, 'r') as f:
        samples = json.load(f)

    # Remove storage locations
    scrubbed = []
    removed_count = 0

    for sample in samples:
        scrubbed_sample = sample.copy()

        # Check if storage location exists
        if sample.get('storage_location_path'):
            removed_count += 1

        # Set to null in public version
        scrubbed_sample['storage_location_path'] = None
        scrubbed.append(scrubbed_sample)

    # Save public version
    public_file = Path('public/data/samples_public.json')
    with open(public_file, 'w') as f:
        json.dump(scrubbed, f, indent=2)

    print(f"✓ Scrubbed {len(scrubbed):,} samples")
    print(f"✓ Removed {removed_count:,} storage locations")

    return scrubbed, removed_count


def scrub_statistics():
    """
    Copy statistics file for public version.

    Statistics contain aggregated data with no PHI, so they can be copied
    directly without modification.
    """
    print("Creating public statistics...")

    # Load private statistics
    private_file = Path('public/data/sample_statistics_private.json')
    if not private_file.exists():
        raise FileNotFoundError(
            f"Private statistics file not found: {private_file}\n"
            "Please run convert_data_for_dashboard.py first."
        )

    with open(private_file, 'r') as f:
        stats = json.load(f)

    # No PHI in statistics, safe to copy as-is
    public_file = Path('public/data/sample_statistics_public.json')
    with open(public_file, 'w') as f:
        json.dump(stats, f, indent=2)

    print("✓ Public statistics created")


def create_audit_log(total_samples, storage_removed):
    """
    Create audit trail documenting PHI scrubbing process.

    Args:
        total_samples (int): Total number of samples processed
        storage_removed (int): Number of storage locations removed

    Returns:
        dict: Audit report
    """
    print("Creating audit log...")

    report = {
        'timestamp': datetime.now().isoformat(),
        'agent': 'PHI Scrubber',
        'version': '1.0',
        'total_samples_processed': total_samples,
        'transformations': {
            'storage_locations_removed': storage_removed,
            'participant_ids_modified': 0,  # Keeping as-is per user request
            'fields_scrubbed': ['storage_location_path']
        },
        'public_data_files_created': [
            'public/data/samples_public.json',
            'public/data/sample_statistics_public.json'
        ],
        'phi_classification': {
            'removed': ['storage_location_path'],
            'kept_as_is': [
                'participant_id',  # Already de-identified (e.g., FLU017)
                'study_code',
                'timepoint_normalized',
                'sample_type',
                'sample_barcode_id'
            ]
        },
        'notes': [
            'Participant IDs are study-assigned codes (e.g., FLU017), not real patient names',
            'Timepoints are normalized to relative days (Day 0, Day 1, etc.), not calendar dates',
            'Storage locations contain operational lab information removed for public view'
        ]
    }

    # Save audit log
    audit_file = Path('data/processed/scrubber_audit_log.json')
    audit_file.parent.mkdir(parents=True, exist_ok=True)

    with open(audit_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✓ Audit log saved to {audit_file}")

    return report


def main():
    """Main execution function."""
    print("=" * 80)
    print("PHI SCRUBBER - Generating Public Data Files")
    print("=" * 80)
    print()

    try:
        # Scrub samples
        scrubbed, removed = scrub_samples()
        print()

        # Scrub statistics
        scrub_statistics()
        print()

        # Create audit report
        create_audit_log(len(scrubbed), removed)
        print()

        print("=" * 80)
        print("✅ Public data files created successfully")
        print("=" * 80)
        print()
        print("Summary:")
        print(f"  • Total samples processed: {len(scrubbed):,}")
        print(f"  • Storage locations removed: {removed:,}")
        print(f"  • Public files created: 2")
        print(f"  • Audit log: data/processed/scrubber_audit_log.json")
        print()
        print("Next steps:")
        print("  1. Review audit log for verification")
        print("  2. Test public data files load correctly")
        print("  3. Deploy updated files to GitHub Pages")
        print()

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERROR: PHI scrubbing failed")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print()
        raise


if __name__ == '__main__':
    main()
