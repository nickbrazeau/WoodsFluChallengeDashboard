#!/usr/bin/env python3
"""
Regenerate publications.json from cleaned data sources
- Base data: data/publications/publications_consolidated.csv
- User curated: data/publications/user_input/ (PDFs with key findings)
"""

import json
import csv
from pathlib import Path
from datetime import datetime

def load_publications_from_csv():
    """Load publications from consolidated CSV"""
    csv_path = Path('data/publications/publications_consolidated.csv')
    publications = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip if no title
            if not row.get('title'):
                continue

            # Clean up pmid
            pmid = row.get('pmid', '').strip()
            if pmid and pmid != 'nan':
                try:
                    pmid = str(int(float(pmid)))
                except:
                    pmid = pmid
            else:
                pmid = None

            pub = {
                'pmid': pmid,
                'title': row.get('title', '').strip(),
                'first_author': row.get('first_author', '').strip(),
                'journal': row.get('journal', '').strip(),
                'year': row.get('year', '').strip(),
                'pubmed_url': row.get('pubmed_url', '').strip(),
                'doi': row.get('doi', '').strip() if row.get('doi') != 'nan' else None,
                'abstract': row.get('abstract', '').strip() if row.get('abstract') != 'nan' else None,
                'biobank_study_code': row.get('biobank_study_code', '').strip(),
                'findings_summary': row.get('findings_summary', '').strip(),
                'study_name': row.get('study_name', '').strip(),
                'authors': row.get('authors', '').strip() if row.get('authors') != 'nan' else None
            }

            # Parse study metadata
            try:
                pub['study_sample_count'] = int(float(row.get('study_sample_count', 0)))
            except:
                pub['study_sample_count'] = 0

            try:
                pub['study_participant_count'] = int(float(row.get('study_participant_count', 0)))
            except:
                pub['study_participant_count'] = 0

            pub['study_sample_types'] = row.get('study_sample_types', '').strip()

            publications.append(pub)

    return publications

def main():
    print("=" * 80)
    print("REGENERATING PUBLICATIONS JSON FROM CLEAN DATA")
    print("=" * 80)
    print()

    # Load publications from CSV
    print("Loading publications from CSV...")
    publications = load_publications_from_csv()
    print(f"  Loaded {len(publications)} publications")

    # Create output structure
    output = {
        'metadata': {
            'generated_date': datetime.now().isoformat(),
            'total_publications': len(publications),
            'data_sources': [
                'data/publications/publications_consolidated.csv',
                'data/publications/user_input/'
            ]
        },
        'publications': publications
    }

    # Save to citations.json
    output_path = Path('data/publications/citations.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved: {output_path}")
    print(f"  Total publications: {len(publications)}")

    # Count by year
    year_counts = {}
    for pub in publications:
        year = pub.get('year', 'Unknown')
        year_counts[year] = year_counts.get(year, 0) + 1

    print("\nPublications by year:")
    for year in sorted(year_counts.keys()):
        print(f"  {year}: {year_counts[year]}")

    # Count by study
    study_counts = {}
    for pub in publications:
        study = pub.get('biobank_study_code', 'Unknown')
        study_counts[study] = study_counts.get(study, 0) + 1

    print("\nPublications by study:")
    for study in sorted(study_counts.keys()):
        if study and study != 'Unknown':
            print(f"  {study}: {study_counts[study]}")

    print()
    print("=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
