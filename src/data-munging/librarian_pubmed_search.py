#!/usr/bin/env python3
"""
Librarian Agent - PubMed Search Script
Searches PubMed for publications that cite or use Duke influenza challenge study data
"""

import json
import time
from pathlib import Path
from datetime import datetime
from Bio import Entrez
import pandas as pd

# Set your email for NCBI Entrez (required)
Entrez.email = "your_email@duke.edu"  # TODO: Update with actual email

# Study information
STUDIES = {
    'DU08-04': {
        'name': 'DEE2 H3N2 Flu Challenge',
        'virus': 'H3N2',
        'year': 2008
    },
    'DU09-06': {
        'name': 'DEE3 H1N1 Flu Challenge',
        'virus': 'H1N1',
        'year': 2009
    },
    'DU09-07': {
        'name': 'DEE4 H1N1 Flu Challenge',
        'virus': 'H1N1',
        'year': 2009
    },
    'DU11-02': {
        'name': 'DEE5 H3N2 Flu Challenge',
        'virus': 'H3N2',
        'year': 2011
    },
    'DU17-04': {
        'name': 'PROMETHEUS H1N1 ICL Flu Challenge',
        'virus': 'H1N1',
        'year': 2017
    },
    'DU20-01': {
        'name': 'SIGMA Plus H3N2 ICL Flu Challenge',
        'virus': 'H3N2',
        'year': 2020
    },
    'DU24-01': {
        'name': 'EXHALE H3N2 Flu Challenge',
        'virus': 'H3N2',
        'year': 2024
    }
}


def build_search_queries():
    """Build PubMed search queries for challenge studies"""

    queries = []

    # General Duke influenza challenge query
    general_query = {
        'name': 'General Duke Influenza Challenge',
        'query': '(Duke[Affiliation] AND (influenza challenge OR flu challenge) AND (H1N1 OR H3N2))',
        'description': 'Broad search for Duke influenza challenge publications'
    }
    queries.append(general_query)

    # Study-specific queries
    for study_code, study_info in STUDIES.items():
        # Try study code
        query1 = {
            'name': f'{study_code} - Study Code',
            'query': f'{study_code}',
            'study_code': study_code,
            'description': f'Search for exact study code {study_code}'
        }
        queries.append(query1)

        # Try study name (e.g., DEE2, PROMETHEUS)
        study_short_name = study_info['name'].split()[0]
        if study_short_name not in ['H1N1', 'H3N2', 'ICL', 'Flu']:
            query2 = {
                'name': f'{study_code} - Study Name',
                'query': f'(Duke AND {study_short_name} AND influenza)',
                'study_code': study_code,
                'description': f'Search for study name {study_short_name}'
            }
            queries.append(query2)

    # Specific PI or collaboration searches (can be expanded)
    # Example: Add known PIs or collaborating institutions

    return queries


def search_pubmed(query_string, max_results=100):
    """
    Search PubMed using Entrez

    Args:
        query_string: PubMed search query
        max_results: Maximum number of results to retrieve

    Returns:
        List of PubMed IDs (PMIDs)
    """
    try:
        print(f"  Searching: {query_string}")

        # Search PubMed
        handle = Entrez.esearch(
            db="pubmed",
            term=query_string,
            retmax=max_results,
            sort="relevance"
        )
        record = Entrez.read(handle)
        handle.close()

        pmids = record['IdList']
        count = int(record['Count'])

        print(f"    Found {count} results, retrieving {len(pmids)} records")

        # Rate limiting - NCBI requests no more than 3 requests per second
        time.sleep(0.4)

        return pmids

    except Exception as e:
        print(f"    Error searching PubMed: {e}")
        return []


def fetch_publication_details(pmids):
    """
    Fetch detailed information for a list of PMIDs

    Args:
        pmids: List of PubMed IDs

    Returns:
        List of publication dictionaries
    """
    if not pmids:
        return []

    try:
        print(f"  Fetching details for {len(pmids)} publications...")

        # Fetch publication details
        handle = Entrez.efetch(
            db="pubmed",
            id=pmids,
            rettype="medline",
            retmode="xml"
        )
        records = Entrez.read(handle)
        handle.close()

        publications = []

        for record in records['PubmedArticle']:
            try:
                article = record['MedlineCitation']['Article']

                # Extract basic information
                pmid = str(record['MedlineCitation']['PMID'])

                # Title
                title = article.get('ArticleTitle', '')

                # Authors
                authors = []
                if 'AuthorList' in article:
                    for author in article['AuthorList']:
                        if 'LastName' in author and 'Initials' in author:
                            authors.append(f"{author['LastName']} {author['Initials']}")
                        elif 'CollectiveName' in author:
                            authors.append(author['CollectiveName'])

                # Journal
                journal = article['Journal'].get('Title', '')

                # Publication date
                pub_date = ''
                if 'PubDate' in article['Journal']['JournalIssue']:
                    date_parts = article['Journal']['JournalIssue']['PubDate']
                    year = date_parts.get('Year', '')
                    month = date_parts.get('Month', '')
                    day = date_parts.get('Day', '')
                    pub_date = f"{year}-{month}-{day}".strip('-')

                # Abstract
                abstract = ''
                if 'Abstract' in article:
                    abstract_parts = article['Abstract'].get('AbstractText', [])
                    if abstract_parts:
                        abstract = ' '.join([str(part) for part in abstract_parts])

                # DOI
                doi = ''
                if 'ELocationID' in article:
                    for eloc in article['ELocationID']:
                        if eloc.attributes.get('EIdType') == 'doi':
                            doi = str(eloc)

                pub = {
                    'pmid': pmid,
                    'title': title,
                    'authors': authors,
                    'journal': journal,
                    'publication_date': pub_date,
                    'abstract': abstract,
                    'doi': doi,
                    'pubmed_url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    'retrieved_date': datetime.now().isoformat()
                }

                publications.append(pub)

            except Exception as e:
                print(f"    Error parsing record: {e}")
                continue

        # Rate limiting
        time.sleep(0.4)

        return publications

    except Exception as e:
        print(f"  Error fetching publication details: {e}")
        return []


def identify_study_mentions(publication, study_code):
    """
    Check if a publication mentions a specific study

    Args:
        publication: Publication dictionary
        study_code: Study code to search for (e.g., 'DU08-04')

    Returns:
        Boolean indicating if study is mentioned
    """
    # Combine searchable text
    searchable_text = ' '.join([
        publication.get('title', ''),
        publication.get('abstract', ''),
        ' '.join(publication.get('authors', []))
    ]).lower()

    # Check for study code
    if study_code.lower() in searchable_text:
        return True

    # Check for study name
    study_info = STUDIES.get(study_code, {})
    study_name = study_info.get('name', '').split()[0].lower()
    if study_name and study_name in searchable_text and study_name not in ['h1n1', 'h3n2', 'icl', 'flu']:
        return True

    return False


def main():
    """Main librarian function"""
    print("="*80)
    print("LIBRARIAN AGENT - PUBMED SEARCH")
    print("="*80)
    print(f"\nSearching for publications related to {len(STUDIES)} Duke influenza challenge studies\n")

    output_dir = Path('/Users/nbrazeau/Documents/Github/WoodsDashboard/data/publications')
    pubmed_dir = output_dir / 'pubmed_results'
    pubmed_dir.mkdir(exist_ok=True)

    # Build search queries
    queries = build_search_queries()
    print(f"Generated {len(queries)} search queries\n")

    # Track all publications and their study associations
    all_publications = {}  # pmid -> publication dict
    study_citations = {code: [] for code in STUDIES.keys()}  # study -> list of pmids

    # Execute searches
    print("="*80)
    print("EXECUTING PUBMED SEARCHES")
    print("="*80)

    for i, query_info in enumerate(queries, 1):
        print(f"\n[{i}/{len(queries)}] {query_info['name']}")
        print(f"  Query: {query_info['query']}")

        # Search PubMed
        pmids = search_pubmed(query_info['query'], max_results=100)

        if not pmids:
            print("  No results found")
            continue

        # Fetch details for new PMIDs
        new_pmids = [pmid for pmid in pmids if pmid not in all_publications]

        if new_pmids:
            publications = fetch_publication_details(new_pmids)

            for pub in publications:
                all_publications[pub['pmid']] = pub

                # Check if this publication mentions specific studies
                for study_code in STUDIES.keys():
                    if identify_study_mentions(pub, study_code):
                        if pub['pmid'] not in study_citations[study_code]:
                            study_citations[study_code].append(pub['pmid'])
                            print(f"    ✓ Linked to {study_code}: {pub['title'][:60]}...")

    # Generate results
    print("\n" + "="*80)
    print("SEARCH COMPLETE - GENERATING REPORTS")
    print("="*80)

    print(f"\nTotal unique publications found: {len(all_publications)}")

    # Save all publications
    citations_file = output_dir / 'citations.json'
    with open(citations_file, 'w') as f:
        json.dump({
            'search_date': datetime.now().isoformat(),
            'total_publications': len(all_publications),
            'publications': all_publications,
            'study_citations': study_citations,
            'studies': STUDIES
        }, f, indent=2)

    print(f"\n✓ Saved citations database: {citations_file}")

    # Generate summary by study
    print("\n" + "="*80)
    print("CITATIONS BY STUDY")
    print("="*80)

    summary_data = []
    for study_code, pmids in study_citations.items():
        study_info = STUDIES[study_code]
        print(f"\n{study_code} ({study_info['name']})")
        print(f"  Virus: {study_info['virus']}")
        print(f"  Year: {study_info['year']}")
        print(f"  Citations found: {len(pmids)}")

        summary_data.append({
            'study_code': study_code,
            'study_name': study_info['name'],
            'virus': study_info['virus'],
            'year': study_info['year'],
            'citation_count': len(pmids)
        })

        if pmids:
            print(f"  Top citations:")
            for pmid in pmids[:3]:
                pub = all_publications[pmid]
                print(f"    - {pub['title'][:70]}...")
                print(f"      PMID: {pmid}, {pub['journal']}, {pub['publication_date']}")

    # Save summary
    summary_df = pd.DataFrame(summary_data)
    summary_file = output_dir / 'citation_summary_by_study.csv'
    summary_df.to_csv(summary_file, index=False)
    print(f"\n✓ Saved summary: {summary_file}")

    # Generate publication list CSV
    pub_list = []
    for pmid, pub in all_publications.items():
        # Find which studies cite this publication
        citing_studies = [code for code, pmids in study_citations.items() if pmid in pmids]

        pub_list.append({
            'pmid': pmid,
            'title': pub['title'],
            'authors': '; '.join(pub['authors'][:3]) + ('...' if len(pub['authors']) > 3 else ''),
            'journal': pub['journal'],
            'publication_date': pub['publication_date'],
            'doi': pub['doi'],
            'pubmed_url': pub['pubmed_url'],
            'studies_cited': ', '.join(citing_studies),
            'num_studies': len(citing_studies)
        })

    pub_df = pd.DataFrame(pub_list)
    pub_df = pub_df.sort_values('num_studies', ascending=False)
    pub_file = output_dir / 'publications_list.csv'
    pub_df.to_csv(pub_file, index=False)
    print(f"✓ Saved publications list: {pub_file}")

    print("\n" + "="*80)
    print("LIBRARIAN AGENT COMPLETE")
    print("="*80)
    print(f"\nOutput files created in: {output_dir}")
    print(f"  1. citations.json - Complete citation database")
    print(f"  2. citation_summary_by_study.csv - Summary by study")
    print(f"  3. publications_list.csv - All publications with study links")


if __name__ == '__main__':
    main()
