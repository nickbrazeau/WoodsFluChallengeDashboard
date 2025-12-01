#!/usr/bin/env python3
"""
Consolidate duplicate publications in publications.json
Merge publications with same title into single entries with multiple study codes
"""

import json
from collections import defaultdict

# Load publications
with open('public/data/publications.json', 'r') as f:
    publications = json.load(f)

print(f"Original publication count: {len(publications)}")

# Group by title
title_groups = defaultdict(list)
for pub in publications:
    title_groups[pub['title']].append(pub)

print(f"Unique titles: {len(title_groups)}")

# Consolidate duplicates
consolidated = []
for title, pubs in title_groups.items():
    if len(pubs) == 1:
        # No duplicates - keep as is
        consolidated.append(pubs[0])
    else:
        # Merge duplicates
        print(f"\nConsolidating: {title[:60]}...")
        print(f"  Found in {len(pubs)} studies: {[p['study_code'] for p in pubs]}")

        # Take the entry with the most complete data (prioritize non-null PMID and abstract)
        best_pub = max(pubs, key=lambda p: (
            p['pmid'] is not None and p['pmid'] != 'N/A',
            p['abstract'] is not None and p['abstract'] != '',
            len(str(p.get('abstract', '')))
        ))

        # Collect all unique study codes
        study_codes = list(set(p['study_code'] for p in pubs if p['study_code']))
        study_codes.sort()  # Sort for consistency

        # Create consolidated entry with study_codes array
        merged = best_pub.copy()
        merged['study_codes'] = study_codes  # Array of all studies
        merged['study_code'] = study_codes[0]  # Keep first for backward compatibility

        print(f"  Best data from: {best_pub['study_code']} (PMID: {best_pub['pmid']})")
        print(f"  Study codes: {study_codes}")

        consolidated.append(merged)

print(f"\nConsolidated publication count: {len(consolidated)}")
print(f"Removed {len(publications) - len(consolidated)} duplicates")

# Sort by year (newest first)
consolidated.sort(key=lambda p: (
    int(p['year']) if p['year'] and p['year'] != 'Unknown' else 0
), reverse=True)

# Save consolidated version
with open('public/data/publications.json', 'w') as f:
    json.dump(consolidated, f, indent=2, ensure_ascii=False)

print("\n✓ Successfully consolidated publications.json")
print(f"  New file has {len(consolidated)} unique publications")
