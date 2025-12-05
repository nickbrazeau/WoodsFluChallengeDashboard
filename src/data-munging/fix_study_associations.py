#!/usr/bin/env python3
"""
Fix study associations in publications CSV
- Remove Phan et al. 2025 (non-challenge study from Sri Lanka/Vietnam)
- Change "Unknown" to "NA" for publications without confirmed study links
- Fix malformed study codes
"""

import csv
from pathlib import Path

def main():
    csv_path = Path('data/publications/publications_consolidated.csv')

    # Read existing publications
    publications = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            pmid = row.get('pmid', '').strip()

            # Remove Phan 2025 (PMID: 41127485)
            if pmid == '41127485':
                print(f"✗ Removed: Phan et al. (2025) - PMID: 41127485 (non-challenge study)")
                continue

            # Fix study codes
            study_code = row.get('biobank_study_code', '').strip()

            # Convert "Unknown" to "NA"
            if study_code == 'Unknown' or not study_code:
                row['biobank_study_code'] = 'NA'

            # Fix malformed entries
            if 'http' in study_code:
                row['biobank_study_code'] = 'NA'
                print(f"  Fixed malformed study code for PMID: {pmid}")

            if study_code in ['2016', ' Guiding Early Therapy', ' Platelet Response to Aspirin']:
                row['biobank_study_code'] = 'NA'
                print(f"  Fixed malformed study code for PMID: {pmid}")

            publications.append(row)

    # Write back
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(publications)

    print(f"\n✓ Total publications: {len(publications)}")
    print(f"✓ Updated: {csv_path}")

    # Count by study
    study_counts = {}
    for pub in publications:
        study = pub.get('biobank_study_code', 'NA')
        study_counts[study] = study_counts.get(study, 0) + 1

    print("\nPublications by study:")
    for study in sorted(study_counts.keys()):
        print(f"  {study}: {study_counts[study]}")

if __name__ == '__main__':
    main()
