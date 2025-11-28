#!/usr/bin/env python3
"""
Scrape PubMed Abstracts for Study Findings

Uses PubMed E-utilities API to fetch abstracts for publications
and extracts structured findings (methods/results) to summarize
in 1-3 sentences.
"""

import json
import time
import re
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path

try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'requests'])
    import requests


class PubMedScraper:
    """Scrape publication data from PubMed."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def __init__(self, email: str = "research@example.com"):
        """Initialize with email for NCBI API compliance."""
        self.email = email
        self.session = requests.Session()

    def extract_pmid_from_url(self, url: str) -> Optional[str]:
        """Extract PubMed ID from various URL formats."""
        if not url:
            return None

        # Direct PMID in URL
        pmid_match = re.search(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d+)', url)
        if pmid_match:
            return pmid_match.group(1)

        # PMC format
        pmc_match = re.search(r'/pmc/articles/PMC(\d+)', url)
        if pmc_match:
            # Convert PMC to PMID using API
            return self.convert_pmc_to_pmid(f"PMC{pmc_match.group(1)}")

        return None

    def convert_pmc_to_pmid(self, pmc_id: str) -> Optional[str]:
        """Convert PMC ID to PMID using NCBI API."""
        url = f"{self.BASE_URL}elink.fcgi"
        params = {
            'dbfrom': 'pmc',
            'db': 'pubmed',
            'id': pmc_id.replace('PMC', ''),
            'retmode': 'json'
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()

            if 'linksets' in data and len(data['linksets']) > 0:
                linkset = data['linksets'][0]
                if 'linksetdbs' in linkset and len(linkset['linksetdbs']) > 0:
                    links = linkset['linksetdbs'][0].get('links', [])
                    if links:
                        return str(links[0])
        except Exception as e:
            print(f"  ⚠️  Error converting {pmc_id}: {e}")

        return None

    def search_pubmed(self, title: str, author: str, year: str) -> Optional[str]:
        """Search PubMed by title, author, and year to find PMID."""
        # Clean up the search query
        title_clean = title.replace('"', '').replace("'", "")
        author_last = author.split()[0] if author else ""

        query = f'{title_clean}[Title] AND {author_last}[Author] AND {year}[pdat]'

        url = f"{self.BASE_URL}esearch.fcgi"
        params = {
            'db': 'pubmed',
            'term': query,
            'retmode': 'json',
            'retmax': 1,
            'email': self.email
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()

            if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                ids = data['esearchresult']['idlist']
                if ids:
                    return ids[0]
        except Exception as e:
            print(f"  ⚠️  Error searching PubMed: {e}")

        return None

    def fetch_abstract(self, pmid: str) -> Optional[Dict]:
        """Fetch abstract and metadata from PubMed."""
        url = f"{self.BASE_URL}efetch.fcgi"
        params = {
            'db': 'pubmed',
            'id': pmid,
            'rettype': 'abstract',
            'retmode': 'xml',
            'email': self.email
        }

        try:
            response = self.session.get(url, params=params, timeout=10)

            if response.status_code == 200:
                return self.parse_abstract_xml(response.text)
        except Exception as e:
            print(f"  ⚠️  Error fetching abstract: {e}")

        return None

    def parse_abstract_xml(self, xml_text: str) -> Dict:
        """Parse PubMed XML to extract structured abstract."""
        abstract_data = {
            'background': '',
            'methods': '',
            'results': '',
            'conclusions': '',
            'full_abstract': ''
        }

        # Extract structured abstract sections
        patterns = {
            'background': r'<AbstractText Label="(?:BACKGROUND|OBJECTIVE|PURPOSE)"[^>]*>(.*?)</AbstractText>',
            'methods': r'<AbstractText Label="(?:METHODS|DESIGN|MATERIALS AND METHODS)"[^>]*>(.*?)</AbstractText>',
            'results': r'<AbstractText Label="(?:RESULTS|FINDINGS)"[^>]*>(.*?)</AbstractText>',
            'conclusions': r'<AbstractText Label="(?:CONCLUSIONS?|INTERPRETATION)"[^>]*>(.*?)</AbstractText>',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, xml_text, re.IGNORECASE | re.DOTALL)
            if match:
                text = match.group(1)
                # Remove XML tags
                text = re.sub(r'<[^>]+>', '', text)
                text = text.strip()
                abstract_data[key] = text

        # Get full abstract if structured sections not available
        all_abstract = re.findall(r'<AbstractText[^>]*>(.*?)</AbstractText>', xml_text, re.DOTALL)
        if all_abstract:
            full_text = ' '.join(all_abstract)
            full_text = re.sub(r'<[^>]+>', '', full_text)
            abstract_data['full_abstract'] = full_text.strip()

        return abstract_data

    def summarize_findings(self, abstract_data: Dict) -> str:
        """Create 1-3 sentence summary of study findings."""
        summary_parts = []

        # Prioritize results and conclusions
        if abstract_data['results']:
            # Get first 2 sentences of results
            results = abstract_data['results']
            sentences = re.split(r'(?<=[.!?])\s+', results)[:2]
            summary_parts.extend(sentences)

        if abstract_data['conclusions'] and len(summary_parts) < 3:
            # Add conclusion if we need more
            conclusions = abstract_data['conclusions']
            sentences = re.split(r'(?<=[.!?])\s+', conclusions)[:1]
            summary_parts.extend(sentences)

        # Fallback to full abstract
        if not summary_parts and abstract_data['full_abstract']:
            sentences = re.split(r'(?<=[.!?])\s+', abstract_data['full_abstract'])
            # Skip first sentence (usually background), take next 2-3
            summary_parts = sentences[1:4] if len(sentences) > 1 else sentences[:3]

        summary = ' '.join(summary_parts[:3])

        # Limit length
        if len(summary) > 500:
            summary = summary[:497] + '...'

        return summary


def process_publications(studies_json_path: str) -> pd.DataFrame:
    """Process all publications and fetch PubMed abstracts."""

    print("="*70)
    print("PubMed Abstract Scraper")
    print("="*70)

    # Load studies
    with open(studies_json_path, 'r') as f:
        studies = json.load(f)

    scraper = PubMedScraper()

    results = []
    total_pubs = sum(len(study['publications']) for study in studies)
    processed = 0

    print(f"\nProcessing {total_pubs} publications...")

    for study in studies:
        study_id = study['id']
        study_title = study['title']
        study_strain = study['strain']

        for pub in study['publications']:
            processed += 1
            print(f"\n[{processed}/{total_pubs}] Processing: {pub['first_author']} et al. ({pub['year']})")

            # Try to get PMID
            pmid = None

            # First, try extracting from URL
            if pub.get('url'):
                pmid = scraper.extract_pmid_from_url(pub['url'])
                if pmid:
                    print(f"  ✓ Found PMID from URL: {pmid}")

            # If no PMID from URL, search by metadata
            if not pmid:
                print(f"  → Searching PubMed by title/author...")
                pmid = scraper.search_pubmed(
                    pub.get('title', ''),
                    pub.get('first_author', ''),
                    pub.get('year', '')
                )
                if pmid:
                    print(f"  ✓ Found PMID: {pmid}")

            if not pmid:
                print(f"  ✗ Could not find PMID")
                results.append({
                    'study_id': study_id,
                    'study_title': study_title,
                    'study_strain': study_strain,
                    'first_author': pub.get('first_author', ''),
                    'title': pub.get('title', ''),
                    'journal': pub.get('journal', ''),
                    'year': pub.get('year', ''),
                    'url': pub.get('url', ''),
                    'pmid': None,
                    'findings_summary': ''
                })
                continue

            # Fetch abstract
            print(f"  → Fetching abstract...")
            time.sleep(0.4)  # Be nice to NCBI servers

            abstract_data = scraper.fetch_abstract(pmid)

            if not abstract_data:
                print(f"  ✗ Could not fetch abstract")
                findings = ""
            else:
                print(f"  ✓ Abstract retrieved")
                findings = scraper.summarize_findings(abstract_data)
                print(f"  ✓ Summary: {findings[:100]}...")

            results.append({
                'study_id': study_id,
                'study_title': study_title,
                'study_strain': study_strain,
                'first_author': pub.get('first_author', ''),
                'title': pub.get('title', ''),
                'journal': pub.get('journal', ''),
                'year': pub.get('year', ''),
                'url': pub.get('url', ''),
                'pmid': pmid,
                'findings_summary': findings
            })

    return pd.DataFrame(results)


def main():
    """Main execution."""

    # Process publications
    df = process_publications("output/studies.json")

    print(f"\n{'='*70}")
    print("Processing Complete")
    print(f"{'='*70}")

    # Count successes
    found_pmid = df['pmid'].notna().sum()
    found_summary = df['findings_summary'].str.len().gt(0).sum()

    print(f"\nResults:")
    print(f"  • Total publications: {len(df)}")
    print(f"  • Found PMID: {found_pmid}")
    print(f"  • Generated summaries: {found_summary}")

    # Save results
    csv_path = "output/pubmed_findings.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n✓ Saved to: {csv_path}")

    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
