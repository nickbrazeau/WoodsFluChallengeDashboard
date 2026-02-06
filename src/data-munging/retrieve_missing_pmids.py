#!/usr/bin/env python3
"""
Retrieve Missing PMIDs for Publications

Automatically retrieves PMIDs for publications with missing PMID values using:
1. DOI lookup (extracted from URLs or DOI field)
2. Title + Author + Year search
3. PMC ID conversion

Updates publications_consolidated.csv with retrieved PMIDs.
"""

import json
import time
import re
import pandas as pd
from pathlib import Path
from datetime import datetime
from Bio import Entrez
from functools import wraps

# Set email for NCBI Entrez (required)
Entrez.email = "duke_biobank@duke.edu"

# Rate limiting configuration
REQUESTS_PER_SECOND = 2.5  # Safe margin under NCBI's 3/sec limit
MIN_REQUEST_INTERVAL = 1.0 / REQUESTS_PER_SECOND

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]  # Exponential backoff

def rate_limit(func):
    """Decorator to enforce rate limiting on Entrez calls"""
    last_called = [0.0]

    @wraps(func)
    def wrapper(*args, **kwargs):
        elapsed = time.time() - last_called[0]
        wait_time = MIN_REQUEST_INTERVAL - elapsed
        if wait_time > 0:
            time.sleep(wait_time)
        result = func(*args, **kwargs)
        last_called[0] = time.time()
        return result
    return wrapper


def extract_doi_from_url(url):
    """
    Extract DOI from journal URLs using regex patterns

    Args:
        url: Journal URL string

    Returns:
        DOI string or None

    Examples:
        'https://onlinelibrary.wiley.com/doi/full/10.1111/cei.12736' → '10.1111/cei.12736'
        'https://www.nature.com/articles/s41467-018-06735-8' → '10.1038/s41467-018-06735-8'
        'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0132259' → '10.1371/journal.pone.0132259'
    """
    if not url or pd.isna(url) or url == 'nan':
        return None

    url = str(url)

    # Pattern 1: Standard DOI format (10.xxxx/xxxxx)
    doi_pattern = r'10\.\d{4,}/[^\s/?"<>]+'
    match = re.search(doi_pattern, url)
    if match:
        doi = match.group()
        # Clean up any trailing punctuation
        doi = doi.rstrip('.,;')
        print(f"    Extracted DOI from URL: {doi}")
        return doi

    # Pattern 2: Nature articles format (convert article ID to DOI)
    if 'nature.com/articles/' in url:
        article_id = url.split('/articles/')[-1].split('?')[0].split('#')[0]
        doi = f'10.1038/{article_id}'
        print(f"    Extracted Nature DOI: {doi}")
        return doi

    return None


def extract_pmc_from_url(url):
    """
    Extract PMC ID from PubMed Central URLs

    Args:
        url: PMC URL string

    Returns:
        PMC ID (e.g., 'PMC4722633') or None

    Example:
        'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4722633/' → 'PMC4722633'
    """
    if not url or pd.isna(url) or url == 'nan':
        return None

    url = str(url)

    if 'pmc/articles/' in url.lower():
        match = re.search(r'PMC(\d+)', url, re.IGNORECASE)
        if match:
            pmc_id = f"PMC{match.group(1)}"
            print(f"    Extracted PMC ID: {pmc_id}")
            return pmc_id

    return None


@rate_limit
def lookup_pmid_by_doi(doi):
    """
    Look up PMID using DOI via Entrez esearch

    Args:
        doi: DOI string

    Returns:
        PMID string or None
    """
    if not doi:
        return None

    for attempt in range(MAX_RETRIES):
        try:
            query = f'{doi}[aid]'
            print(f"    Searching PubMed by DOI: {doi}")

            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=1
            )
            record = Entrez.read(handle)
            handle.close()

            if record['IdList']:
                pmid = record['IdList'][0]
                print(f"    ✓ Found PMID {pmid} via DOI")
                return pmid

            print(f"    No PMID found for DOI: {doi}")
            return None

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"    Error on attempt {attempt + 1}, retrying: {e}")
                time.sleep(RETRY_DELAYS[attempt])
            else:
                print(f"    Error searching by DOI after {MAX_RETRIES} attempts: {e}")
                return None


@rate_limit
def convert_pmc_to_pmid(pmc_id):
    """
    Convert PMC ID to PMID using Entrez elink

    Args:
        pmc_id: PMC ID string (e.g., 'PMC4722633')

    Returns:
        PMID string or None
    """
    if not pmc_id:
        return None

    # Remove 'PMC' prefix if present
    pmc_numeric = pmc_id.replace('PMC', '')

    for attempt in range(MAX_RETRIES):
        try:
            print(f"    Converting PMC ID to PMID: {pmc_id}")

            handle = Entrez.elink(
                dbfrom="pmc",
                db="pubmed",
                id=pmc_numeric
            )
            record = Entrez.read(handle)
            handle.close()

            if record and record[0].get('LinkSetDb'):
                links = record[0]['LinkSetDb'][0].get('Link', [])
                if links:
                    pmid = links[0]['Id']
                    print(f"    ✓ Converted {pmc_id} → PMID {pmid}")
                    return pmid

            print(f"    Could not convert {pmc_id} to PMID")
            return None

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"    Error on attempt {attempt + 1}, retrying: {e}")
                time.sleep(RETRY_DELAYS[attempt])
            else:
                print(f"    Error converting PMC ID after {MAX_RETRIES} attempts: {e}")
                return None


@rate_limit
def lookup_pmid_by_title(title, first_author=None, year=None):
    """
    Look up PMID using title + metadata via Entrez esearch

    Args:
        title: Publication title
        first_author: First author surname (optional)
        year: Publication year (optional)

    Returns:
        PMID string or None
    """
    if not title or pd.isna(title):
        return None

    title = str(title)

    for attempt in range(MAX_RETRIES):
        try:
            # Build query
            query_parts = [f'"{title}"[Title]']

            if first_author and not pd.isna(first_author):
                # Extract last name only
                last_name = str(first_author).split()[0]
                query_parts.append(f'"{last_name}"[Author]')

            if year and not pd.isna(year):
                query_parts.append(f'{year}[pdat]')

            query = ' AND '.join(query_parts)
            print(f"    Searching PubMed by title: {title[:60]}...")

            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=1,
                sort="relevance"
            )
            record = Entrez.read(handle)
            handle.close()

            if record['IdList']:
                pmid = record['IdList'][0]
                print(f"    ✓ Found PMID {pmid} via title search")
                return pmid

            print(f"    No results for title search")
            return None

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"    Error on attempt {attempt + 1}, retrying: {e}")
                time.sleep(RETRY_DELAYS[attempt])
            else:
                print(f"    Error searching by title after {MAX_RETRIES} attempts: {e}")
                return None


def comprehensive_pmid_lookup(publication):
    """
    Attempt all lookup strategies in priority order

    Args:
        publication: Dict/Series with keys: title, first_author, year, pubmed_url, doi

    Returns:
        Dict with keys: pmid, lookup_method, doi_used, success
    """
    result = {
        'pmid': None,
        'lookup_method': None,
        'doi_used': None,
        'success': False
    }

    title = publication.get('title', '')
    print(f"\n  Processing: {title[:70]}...")

    # Strategy 1: Use existing DOI field
    doi = publication.get('doi')
    if doi and not pd.isna(doi) and str(doi) not in ['', 'nan', 'None']:
        pmid = lookup_pmid_by_doi(str(doi))
        if pmid:
            result['pmid'] = pmid
            result['lookup_method'] = 'doi_field'
            result['doi_used'] = str(doi)
            result['success'] = True
            return result

    # Strategy 2: Extract DOI from URL and lookup
    url = publication.get('pubmed_url')
    if url:
        extracted_doi = extract_doi_from_url(url)
        if extracted_doi:
            pmid = lookup_pmid_by_doi(extracted_doi)
            if pmid:
                result['pmid'] = pmid
                result['lookup_method'] = 'doi_extracted_from_url'
                result['doi_used'] = extracted_doi
                result['success'] = True
                return result

    # Strategy 3: Convert PMC ID to PMID
    if url:
        pmc_id = extract_pmc_from_url(url)
        if pmc_id:
            pmid = convert_pmc_to_pmid(pmc_id)
            if pmid:
                result['pmid'] = pmid
                result['lookup_method'] = 'pmc_conversion'
                result['success'] = True
                return result

    # Strategy 4: Title + First Author + Year
    pmid = lookup_pmid_by_title(
        publication.get('title'),
        publication.get('first_author'),
        publication.get('year')
    )
    if pmid:
        result['pmid'] = pmid
        result['lookup_method'] = 'title_author_year'
        result['success'] = True
        return result

    # Strategy 5: Title only (last resort)
    pmid = lookup_pmid_by_title(publication.get('title'))
    if pmid:
        result['pmid'] = pmid
        result['lookup_method'] = 'title_only'
        result['success'] = True
        return result

    print(f"    ❌ Could not find PMID for this publication")
    return result


def identify_publications_needing_pmids(df):
    """
    Identify publications with missing PMIDs

    Args:
        df: DataFrame with publications

    Returns:
        DataFrame of publications needing PMID lookup
    """
    missing_pmid_mask = (
        df['pmid'].isna() |
        (df['pmid'].astype(str) == 'N/A') |
        (df['pmid'].astype(str) == 'nan') |
        (df['pmid'].astype(str) == 'Unknown') |
        (df['pmid'].astype(str) == '')
    )
    return df[missing_pmid_mask].copy()


def detect_and_propagate_duplicates(df):
    """
    Detect duplicate publications and propagate PMIDs from duplicates

    Returns:
        Dict mapping index to PMID for propagation updates
    """
    print("\nChecking for duplicate publications...")

    # Normalize titles for comparison
    df['title_normalized'] = df['title'].str.lower().str.strip()

    propagation_updates = {}
    duplicate_groups = df.groupby('title_normalized')

    for title_norm, group in duplicate_groups:
        if len(group) > 1:
            # Check if any have valid PMID
            valid_pmids = group[
                group['pmid'].notna() &
                (group['pmid'].astype(str) != 'N/A') &
                (group['pmid'].astype(str) != 'nan') &
                (group['pmid'].astype(str) != 'Unknown')
            ]['pmid']

            if len(valid_pmids) > 0:
                canonical_pmid = str(valid_pmids.iloc[0])
                print(f"\n  Found duplicate: {group.iloc[0]['title'][:60]}...")
                print(f"  Propagating PMID {canonical_pmid} to {len(group)} rows")

                for idx in group.index:
                    if pd.isna(df.loc[idx, 'pmid']) or str(df.loc[idx, 'pmid']) in ['N/A', 'nan', 'Unknown', '']:
                        propagation_updates[idx] = {
                            'pmid': canonical_pmid,
                            'lookup_method': 'propagated_from_duplicate',
                            'doi_used': None
                        }

    if propagation_updates:
        print(f"\n✓ Will propagate PMIDs to {len(propagation_updates)} duplicate entries")
    else:
        print("  No duplicates with PMIDs found")

    return propagation_updates


def main():
    """Main execution function"""
    print("="*80)
    print("PMID RETRIEVAL SCRIPT")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Define paths
    base_dir = Path(__file__).parent.parent.parent
    csv_path = base_dir / 'data' / 'publications' / 'publications_consolidated.csv'

    if not csv_path.exists():
        print(f"❌ Error: File not found: {csv_path}")
        return

    print(f"Reading: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Total publications in CSV: {len(df)}\n")

    # Step 1: Check for duplicates and propagate PMIDs
    propagation_updates = detect_and_propagate_duplicates(df)

    # Step 2: Identify publications needing PMIDs
    print("\n" + "="*80)
    print("IDENTIFYING PUBLICATIONS NEEDING PMIDs")
    print("="*80)

    missing_df = identify_publications_needing_pmids(df)
    print(f"\nFound {len(missing_df)} publications with missing PMIDs")

    # Remove publications that will be updated by propagation
    missing_df = missing_df[~missing_df.index.isin(propagation_updates.keys())]
    print(f"After duplicate propagation: {len(missing_df)} publications need lookup\n")

    if len(missing_df) == 0 and len(propagation_updates) == 0:
        print("✓ All publications already have PMIDs!")
        return

    # Step 3: Retrieve PMIDs
    print("="*80)
    print("RETRIEVING PMIDs FROM PUBMED")
    print("="*80)

    pmid_updates = propagation_updates.copy()

    for idx, row in missing_df.iterrows():
        result = comprehensive_pmid_lookup(row)

        if result['success']:
            pmid_updates[idx] = result

    print(f"\n{'='*80}")
    print(f"RESULTS: Successfully retrieved {len([u for u in pmid_updates.values() if u.get('success', True)])} PMIDs")
    print(f"{'='*80}\n")

    if not pmid_updates:
        print("No PMIDs to update.")
        return

    # Step 4: Create backup
    backup_path = csv_path.parent / f"publications_consolidated_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(backup_path, index=False)
    print(f"✓ Backup created: {backup_path}\n")

    # Step 5: Update DataFrame
    changes_log = []

    for idx, update_info in pmid_updates.items():
        old_pmid = df.loc[idx, 'pmid']
        new_pmid = update_info['pmid']

        # Update PMID
        df.loc[idx, 'pmid'] = new_pmid

        # Update DOI if extracted and current DOI is empty
        if update_info.get('doi_used'):
            current_doi = df.loc[idx, 'doi']
            if pd.isna(current_doi) or str(current_doi) in ['', 'nan', 'None']:
                df.loc[idx, 'doi'] = update_info['doi_used']

        # Log change
        changes_log.append({
            'row_index': idx,
            'title': str(df.loc[idx, 'title'])[:60],
            'first_author': df.loc[idx, 'first_author'],
            'year': df.loc[idx, 'year'],
            'old_pmid': old_pmid,
            'new_pmid': new_pmid,
            'lookup_method': update_info['lookup_method'],
            'doi': update_info.get('doi_used', '')
        })

    # Step 6: Save updated CSV
    df.to_csv(csv_path, index=False)
    print(f"✓ Updated: {csv_path}\n")

    # Step 7: Save change log
    changes_df = pd.DataFrame(changes_log)
    log_path = csv_path.parent / f"pmid_update_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    changes_df.to_csv(log_path, index=False)
    print(f"✓ Change log saved: {log_path}\n")

    # Step 8: Display summary
    print("="*80)
    print("UPDATE SUMMARY")
    print("="*80)
    print(f"\nTotal updates: {len(pmid_updates)}")

    method_counts = {}
    for update in pmid_updates.values():
        method = update['lookup_method']
        method_counts[method] = method_counts.get(method, 0) + 1

    print("\nBy method:")
    for method, count in sorted(method_counts.items()):
        print(f"  {method}: {count}")

    print("\nTop 5 updated publications:")
    for i, change in enumerate(changes_log[:5], 1):
        print(f"\n  {i}. {change['title']}")
        print(f"     Author: {change['first_author']} ({change['year']})")
        print(f"     PMID: {change['old_pmid']} → {change['new_pmid']}")
        print(f"     Method: {change['lookup_method']}")

    print(f"\n{'='*80}")
    print("✓ PMID RETRIEVAL COMPLETE")
    print(f"{'='*80}")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nNext steps:")
    print("1. Review change log for accuracy")
    print("2. Run: python src/data-munging/regenerate_publications_json.py")
    print("3. Run: python src/data-munging/convert_data_for_dashboard.py")
    print("4. Test dashboard locally\n")


if __name__ == '__main__':
    main()
