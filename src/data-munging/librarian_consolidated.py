#!/usr/bin/env python3
"""
Enhanced Librarian Agent - Consolidated Publication Analysis
Consolidates existing publications, runs new PubMed searches, extracts methods/results,
and links citations to sample data.
"""

import json
import time
import re
from pathlib import Path
from datetime import datetime
from Bio import Entrez
import pandas as pd
import PyPDF2

# Set your email for NCBI Entrez (required)
Entrez.email = "duke_biobank@duke.edu"  # Update if needed

# Study information with enhanced search terms
STUDIES = {
    'DU08-04': {
        'name': 'DEE2 H3N2 Flu Challenge',
        'virus': 'H3N2',
        'year': 2008,
        'old_study_ids': ['5236'],  # From prior work
        'search_terms': ['DEE2', 'H3N2 challenge 2008 Duke']
    },
    'DU09-06': {
        'name': 'DEE3 H1N1 Flu Challenge',
        'virus': 'H1N1',
        'year': 2009,
        'old_study_ids': ['5233'],
        'search_terms': ['DEE3', 'H1N1 challenge 2009 Duke']
    },
    'DU09-07': {
        'name': 'DEE4 H1N1 Flu Challenge',
        'virus': 'H1N1',
        'year': 2009,
        'old_study_ids': ['5234'],
        'search_terms': ['DEE4', 'H1N1 intervention 2009 Duke']
    },
    'DU11-02': {
        'name': 'DEE5 H3N2 Flu Challenge',
        'virus': 'H3N2',
        'year': 2011,
        'old_study_ids': ['5237'],
        'search_terms': ['DEE5', 'H3N2 challenge 2011 Duke', 'cure-before']
    },
    'DU17-04': {
        'name': 'PROMETHEUS H1N1 ICL Flu Challenge',
        'virus': 'H1N1',
        'year': 2017,
        'old_study_ids': [],
        'search_terms': ['PROMETHEUS', 'PROMETHEUS influenza', 'PROMETHEUS Duke', 'PROM H1N1', 'ICL flu challenge 2017']
    },
    'DU20-01': {
        'name': 'SIGMA Plus H3N2 ICL Flu Challenge',
        'virus': 'H3N2',
        'year': 2020,
        'old_study_ids': [],
        'search_terms': ['SIGMA Plus', 'SIGMA Plus influenza', 'SIGMA H3N2', 'SPFC', 'ICL flu challenge 2020']
    },
    'DU24-01': {
        'name': 'EXHALE H3N2 Flu Challenge',
        'virus': 'H3N2',
        'year': 2024,
        'old_study_ids': [],
        'search_terms': ['EXHALE', 'EXHALE influenza', 'EXHALE H3N2', 'EXHALE Duke']
    }
}


def load_existing_publications():
    """Load existing publications from prior work"""
    existing_file = Path('/Users/nbrazeau/Documents/Github/WoodsDashboard/data/publications/pubmed_findings.csv')

    if not existing_file.exists():
        print("No existing publications file found")
        return pd.DataFrame()

    print(f"Loading existing publications from {existing_file}")
    df = pd.read_csv(existing_file)
    print(f"  Loaded {len(df)} existing publication records")

    return df


def map_old_study_ids_to_new(existing_df):
    """Map old study IDs to new biobank codes"""
    study_mapping = {}
    for new_code, info in STUDIES.items():
        for old_id in info['old_study_ids']:
            study_mapping[old_id] = new_code

    # Create new column with mapped study codes
    if 'study_id' in existing_df.columns:
        existing_df['biobank_study_code'] = existing_df['study_id'].astype(str).map(study_mapping)
        existing_df['biobank_study_code'].fillna('Unknown', inplace=True)

        mapped_count = (existing_df['biobank_study_code'] != 'Unknown').sum()
        print(f"  Mapped {mapped_count} publications to biobank study codes")

    return existing_df


def search_pubmed(query_string, max_results=50):
    """Search PubMed using Entrez"""
    try:
        print(f"  Searching: {query_string}")

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
        time.sleep(0.4)

        return pmids

    except Exception as e:
        print(f"    Error searching PubMed: {e}")
        return []


def fetch_publication_details(pmids):
    """Fetch detailed information for a list of PMIDs"""
    if not pmids:
        return []

    try:
        print(f"  Fetching details for {len(pmids)} publications...")

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
                pmid = str(record['MedlineCitation']['PMID'])

                # Extract basic information
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
                    'first_author': authors[0] if authors else '',
                    'journal': journal,
                    'publication_date': pub_date,
                    'year': pub_date.split('-')[0] if pub_date else '',
                    'abstract': abstract,
                    'doi': doi,
                    'pubmed_url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    'retrieved_date': datetime.now().isoformat(),
                    'source': 'PubMed_new_search'
                }

                publications.append(pub)

            except Exception as e:
                print(f"    Error parsing record: {e}")
                continue

        time.sleep(0.4)
        return publications

    except Exception as e:
        print(f"  Error fetching publication details: {e}")
        return []


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ''

            # Extract text from all pages
            for page in pdf_reader.pages:
                text += page.extract_text() + '\n'

            return text

    except Exception as e:
        print(f"    Error extracting PDF text: {e}")
        return ''


def extract_methods_results(text, title=''):
    """Extract methods and results sections from text"""
    if not text:
        return {'methods': '', 'results': '', 'data_types': []}

    text_lower = text.lower()

    # Find Methods section
    methods_patterns = [
        r'methods?\s*\n(.*?)\n\s*results?',
        r'materials and methods?\s*\n(.*?)\n\s*results?',
        r'experimental procedures?\s*\n(.*?)\n\s*results?'
    ]

    methods = ''
    for pattern in methods_patterns:
        match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
        if match:
            methods = match.group(1)[:2000]  # Limit to 2000 chars
            break

    # Find Results section
    results_patterns = [
        r'results?\s*\n(.*?)\n\s*discussion',
        r'results?\s*\n(.*?)\n\s*conclusion',
        r'results?\s*\n(.*?)(?:\n\s*[A-Z][a-z]+\s*\n|$)'
    ]

    results = ''
    for pattern in results_patterns:
        match = re.search(pattern, text_lower, re.DOTALL | re.IGNORECASE)
        if match:
            results = match.group(1)[:2000]  # Limit to 2000 chars
            break

    # Identify data types mentioned
    data_keywords = [
        'RNA-seq', 'RNA sequencing', 'transcriptomics',
        'proteomics', 'mass spectrometry',
        'metabolomics',
        'flow cytometry', 'FACS',
        'microarray', 'gene expression',
        'ELISA', 'cytokine',
        'viral load', 'qPCR', 'RT-PCR',
        'sequencing', 'deep sequencing',
        'antibody', 'serology',
        'nasal lavage', 'nasal swab',
        'plasma', 'serum', 'PBMC'
    ]

    found_data_types = []
    for keyword in data_keywords:
        if keyword.lower() in text_lower:
            found_data_types.append(keyword)

    return {
        'methods': methods.strip() if methods else 'Not extracted',
        'results': results.strip() if results else 'Not extracted',
        'data_types': found_data_types
    }


def analyze_pdfs():
    """Analyze existing PDF files"""
    pdf_dir = Path('/Users/nbrazeau/Documents/Github/WoodsDashboard/data/publications/pdfs')

    if not pdf_dir.exists():
        print("No PDF directory found")
        return {}

    pdf_files = list(pdf_dir.glob('*.pdf'))
    print(f"\nAnalyzing {len(pdf_files)} PDF files for methods/results extraction...")

    pdf_analysis = {}

    for pdf_file in pdf_files:
        if pdf_file.name == 'download_report.json':
            continue

        print(f"  Processing: {pdf_file.name}")
        text = extract_text_from_pdf(pdf_file)

        if text:
            analysis = extract_methods_results(text)
            pdf_analysis[pdf_file.name] = analysis

            if analysis['data_types']:
                print(f"    Found data types: {', '.join(analysis['data_types'][:5])}")

    return pdf_analysis


def link_to_sample_data(publications_df):
    """Link publications to sample data from harmonized inventory"""
    inventory_file = Path('/Users/nbrazeau/Documents/Github/WoodsDashboard/data/processed/combined_inventory_harmonized.parquet')

    if not inventory_file.exists():
        print("\nWarning: Harmonized inventory not found. Skipping sample linkage.")
        return publications_df

    print("\nLinking publications to sample data...")
    inventory_df = pd.read_parquet(inventory_file)

    # Create study summary
    study_summary = inventory_df.groupby('study_code').agg({
        'sample_barcode_id': 'count',
        'participant_id': 'nunique',
        'sample_type': lambda x: ', '.join([str(s) for s in x.dropna().unique()[:10]]),
        'is_available': 'sum',
        'is_transferred': 'sum'
    }).to_dict('index')

    # Add sample info to publications
    publications_df['study_sample_count'] = publications_df['biobank_study_code'].map(
        lambda x: study_summary.get(x, {}).get('sample_barcode_id', 0)
    )
    publications_df['study_participant_count'] = publications_df['biobank_study_code'].map(
        lambda x: study_summary.get(x, {}).get('participant_id', 0)
    )
    publications_df['study_sample_types'] = publications_df['biobank_study_code'].map(
        lambda x: study_summary.get(x, {}).get('sample_type', '')
    )

    print(f"  Linked {len(publications_df)} publications to sample inventory")

    return publications_df


def main():
    """Main consolidated librarian function"""
    print("="*80)
    print("ENHANCED LIBRARIAN AGENT - CONSOLIDATED PUBLICATION ANALYSIS")
    print("="*80)

    output_dir = Path('/Users/nbrazeau/Documents/Github/WoodsDashboard/data/publications')

    # Step 1: Load existing publications
    print("\n" + "="*80)
    print("STEP 1: LOADING EXISTING PUBLICATIONS")
    print("="*80)

    existing_df = load_existing_publications()
    existing_df = map_old_study_ids_to_new(existing_df)

    # Step 2: Analyze existing PDFs
    print("\n" + "="*80)
    print("STEP 2: ANALYZING EXISTING PDFs")
    print("="*80)

    pdf_analysis = analyze_pdfs()

    # Step 3: Run new PubMed searches (focus on PROMETHEUS and SIGMA Plus)
    print("\n" + "="*80)
    print("STEP 3: NEW PUBMED SEARCHES")
    print("="*80)

    new_publications = []
    existing_pmids = set(existing_df['pmid'].dropna().astype(str))

    priority_studies = ['DU17-04', 'DU20-01']  # PROMETHEUS and SIGMA Plus

    for study_code in priority_studies:
        study_info = STUDIES[study_code]
        print(f"\n{study_code} ({study_info['name']})")

        for search_term in study_info['search_terms']:
            query = f"({search_term}) AND (Duke OR Durham) AND (influenza OR flu)"
            pmids = search_pubmed(query, max_results=20)

            # Filter out existing PMIDs
            new_pmids = [pmid for pmid in pmids if pmid not in existing_pmids]

            if new_pmids:
                pubs = fetch_publication_details(new_pmids)

                for pub in pubs:
                    pub['biobank_study_code'] = study_code
                    pub['study_name'] = study_info['name']
                    new_publications.append(pub)
                    existing_pmids.add(pub['pmid'])

    print(f"\nFound {len(new_publications)} new publications")

    # Step 4: Consolidate all publications
    print("\n" + "="*80)
    print("STEP 4: CONSOLIDATING PUBLICATIONS")
    print("="*80)

    # Convert existing_df to match new format
    existing_records = []
    for _, row in existing_df.iterrows():
        existing_records.append({
            'pmid': str(row.get('pmid', '')),
            'title': row.get('title', ''),
            'first_author': row.get('first_author', ''),
            'journal': row.get('journal', ''),
            'year': str(row.get('year', '')),
            'pubmed_url': row.get('url', ''),
            'biobank_study_code': row.get('biobank_study_code', 'Unknown'),
            'findings_summary': row.get('findings_summary', ''),
            'source': 'existing_database'
        })

    # Combine all publications
    all_publications = existing_records + new_publications
    publications_df = pd.DataFrame(all_publications)

    print(f"Total publications: {len(publications_df)}")
    print(f"  - Existing: {len(existing_records)}")
    print(f"  - New: {len(new_publications)}")

    # Step 5: Link to sample data
    publications_df = link_to_sample_data(publications_df)

    # Step 6: Generate outputs
    print("\n" + "="*80)
    print("STEP 5: GENERATING OUTPUTS")
    print("="*80)

    # Save consolidated citations
    citations_json = output_dir / 'citations.json'
    citations_data = {
        'metadata': {
            'generation_date': datetime.now().isoformat(),
            'total_publications': len(publications_df),
            'studies_covered': publications_df['biobank_study_code'].nunique(),
            'date_range': f"{publications_df['year'].min()}-{publications_df['year'].max()}"
        },
        'studies': STUDIES,
        'publications': publications_df.to_dict('records'),
        'pdf_analysis': pdf_analysis
    }

    with open(citations_json, 'w') as f:
        json.dump(citations_data, f, indent=2, default=str)
    print(f"✓ Saved: {citations_json}")

    # Save publications list CSV
    pub_csv = output_dir / 'publications_consolidated.csv'
    publications_df.to_csv(pub_csv, index=False)
    print(f"✓ Saved: {pub_csv}")

    # Generate citation summary by study
    summary_data = publications_df.groupby('biobank_study_code').agg({
        'pmid': 'count',
        'year': lambda x: f"{x.min()}-{x.max()}",
        'study_sample_count': 'first',
        'study_participant_count': 'first'
    }).reset_index()

    summary_data.columns = ['Study Code', 'Publications', 'Year Range', 'Total Samples', 'Total Participants']

    summary_csv = output_dir / 'citation_summary_by_study.csv'
    summary_data.to_csv(summary_csv, index=False)
    print(f"✓ Saved: {summary_csv}")

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY BY STUDY")
    print("="*80)
    print(summary_data.to_string(index=False))

    print("\n" + "="*80)
    print("LIBRARIAN AGENT COMPLETE")
    print("="*80)
    print(f"\nOutput files created in: {output_dir}")
    print(f"  1. citations.json - Complete citation database with PDF analysis")
    print(f"  2. publications_consolidated.csv - All publications with metadata")
    print(f"  3. citation_summary_by_study.csv - Summary by study")


if __name__ == '__main__':
    main()
