#!/usr/bin/env python3
"""
CIDDI BioBank Influenza Research Study Data Extractor

This script extracts INFLUENZA-SPECIFIC research study information from the
CIDDI BioBank HTML file and structures it for dashboard display.

Focus: Influenza challenge studies, clinical cohorts, and vaccine response studies.
"""

import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import pandas as pd


class StudyExtractor:
    """Extract and structure influenza research study data from HTML."""

    # Keywords to identify influenza studies
    INFLUENZA_KEYWORDS = [
        'influenza', 'h1n1', 'h3n2', 'h5n1', 'flu',
        'inoculation', 'challenge'
    ]

    def __init__(self, html_path: str, filter_influenza: bool = True):
        self.html_path = Path(html_path)
        self.filter_influenza = filter_influenza
        with open(self.html_path, 'r', encoding='utf-8') as f:
            self.soup = BeautifulSoup(f.read(), 'html.parser')
        self.studies = []
        self.filtered_count = 0

    def extract_all_studies(self) -> List[Dict]:
        """Extract all influenza studies from the HTML file."""
        # Find all accordion items
        accordion_items = self.soup.find_all('div', class_='accordion-item')

        for item in accordion_items:
            study = self._extract_study(item)
            if study:
                if self.filter_influenza:
                    if self._is_influenza_study(study):
                        self.studies.append(study)
                    else:
                        self.filtered_count += 1
                else:
                    self.studies.append(study)

        return self.studies

    def _is_influenza_study(self, study: Dict) -> bool:
        """Determine if a study is influenza-related."""
        # Check title
        title = study.get('title', '').lower()

        # Check research aims
        aims = study.get('research_aims', '').lower()

        # Priority check: If title explicitly contains influenza strain, it's an influenza study
        influenza_in_title = any(kw in title for kw in ['influenza', 'h1n1', 'h3n2', 'h5n1', 'h7n9'])

        if influenza_in_title:
            return True

        # Exclude non-influenza studies explicitly (only check if NOT in title)
        exclude_keywords = [
            'rsv', 'respiratory syncytial virus',
            'rhinovirus',
            'e.coli', 'etec', 'escherichia',
            'streptococcus', 'pneumoniae',
            'antiplatelet', 'pharmacogenomics',
            'coronavirus', 'covid', 'sars'
        ]

        for exclude in exclude_keywords:
            if exclude in title:
                return False

        # Check for influenza keywords in combined text
        search_text = f"{title} {aims}"
        influenza_keywords = [
            'influenza', 'h1n1', 'h3n2', 'h5n1', 'h7n9',
            'flu virus', 'flu challenge'
        ]

        for keyword in influenza_keywords:
            if keyword in search_text:
                return True

        return False

    def _extract_study(self, accordion_item) -> Optional[Dict]:
        """Extract a single study from an accordion item."""
        # Get study title
        header = accordion_item.find('h3', class_='accordion-header')
        if not header:
            return None

        button = header.find('button')
        if not button:
            return None

        title = button.get_text(strip=True)

        # Get study ID
        study_id = header.get('id', '').replace('heading', '')

        # Get study body
        body = accordion_item.find('div', class_='accordion-body')
        if not body:
            return None

        content = body.find('div', class_='text-formatted')
        if not content:
            return None

        # Extract structured data
        research_aims = self._extract_research_aims(content)
        study_data = {
            'id': study_id,
            'title': title,
            'research_aims': research_aims,
            'strain': self._extract_strain(title, research_aims),
            'study_type': self._extract_study_type(title, research_aims),
            'experimental_design': self._extract_experimental_design(content),
            'publications': self._extract_publications(content),
        }

        return study_data

    def _extract_strain(self, title: str, aims: str) -> str:
        """Extract influenza strain from title or aims."""
        text = f"{title} {aims}".lower()

        # Check for specific strains
        strain_patterns = [
            (r'h1n1', 'H1N1'),
            (r'h3n2', 'H3N2'),
            (r'h5n1', 'H5N1'),
            (r'h7n9', 'H7N9'),
            (r'influenza\s+a', 'Influenza A'),
            (r'influenza\s+b', 'Influenza B'),
        ]

        for pattern, strain_name in strain_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return strain_name

        # Check for specific strain details in parentheses
        strain_match = re.search(r'\(([AB]/[^)]+)\)', aims)
        if strain_match:
            return strain_match.group(1)

        return "Influenza (unspecified)"

    def _extract_study_type(self, title: str, aims: str) -> str:
        """Extract study type from title or aims."""
        text = f"{title} {aims}".lower()

        if any(word in text for word in ['challenge', 'inoculation', 'inoculated']):
            return "Challenge/Inoculation"
        elif any(word in text for word in ['vaccine', 'vaccination', 'immunization']):
            return "Vaccine Response"
        elif any(word in text for word in ['cohort', 'emergency', 'clinical']):
            return "Clinical Cohort"
        elif any(word in text for word in ['observational']):
            return "Observational"
        else:
            return "Research Study"

    def _extract_research_aims(self, content) -> str:
        """Extract research aims text."""
        aims_header = content.find('strong', string='Research Aims')
        if not aims_header:
            return ""

        # Get the paragraph after the header
        para = aims_header.find_parent('p')
        if para:
            next_para = para.find_next_sibling('p')
            if next_para:
                return next_para.get_text(strip=True)

        return ""

    def _extract_experimental_design(self, content) -> Dict:
        """Extract experimental design details."""
        design = {
            'subjects': None,
            'timepoints': None,
            'sample_types': [],
            'datasets': [],
            'molecular': []
        }

        # Find all paragraphs and list items
        text = content.get_text()

        # Extract subjects
        subjects_match = re.search(r'Subjects:\s*(\d+)', text)
        if subjects_match:
            design['subjects'] = int(subjects_match.group(1))

        # Extract timepoints
        timepoints_match = re.search(r'Timepoints?:\s*([^\n]+)', text)
        if timepoints_match:
            design['timepoints'] = timepoints_match.group(1).strip()

        # Extract sample types
        sample_types_section = re.search(r'Sample types?:(.*?)(?:Datasets|Clinical|Molecular|Publications|$)', text, re.DOTALL | re.IGNORECASE)
        if sample_types_section:
            samples_text = sample_types_section.group(1)
            # Find all sample:count pairs
            sample_matches = re.findall(r'(\w+[\s\w]*?):\s*(\d+)', samples_text)
            for sample_type, count in sample_matches:
                # Normalize: lowercase and collapse multiple spaces
                normalized_type = ' '.join(sample_type.strip().lower().split())
                design['sample_types'].append({
                    'type': normalized_type,
                    'count': int(count)
                })

        # Extract datasets info
        datasets_match = re.search(r'Datasets\s*(.*?)(?:Molecular:|Publications|$)', text, re.DOTALL | re.IGNORECASE)
        if datasets_match:
            datasets_text = datasets_match.group(1)
            design['datasets'] = [line.strip() for line in datasets_text.split('\n') if line.strip() and not line.strip().startswith('Molecular')]

        # Extract molecular assays
        molecular_match = re.search(r'Molecular:\s*([^\n]+?)(?:\n\n|Publications|$)', text, re.DOTALL | re.IGNORECASE)
        if molecular_match:
            molecular_text = molecular_match.group(1).strip()
            # Normalize: lowercase and collapse multiple spaces
            design['molecular'] = [' '.join(assay.strip().lower().split()) for assay in re.split(r',\s*', molecular_text) if assay.strip()]

        return design

    def _extract_publications(self, content) -> List[Dict]:
        """Extract publication information."""
        publications = []

        # Find the Publications section
        pubs_header = content.find('strong', string='Publications')
        if not pubs_header:
            return publications

        # Find the list after Publications header
        pub_list = pubs_header.find_parent().find_next_sibling('ul')
        if not pub_list:
            # Try finding it differently
            parent = pubs_header.find_parent('p')
            if parent:
                pub_list = parent.find_next_sibling('ul')

        if pub_list:
            for li in pub_list.find_all('li', recursive=False):
                pub_data = self._parse_publication(li)
                if pub_data:
                    publications.append(pub_data)

        return publications

    def _parse_publication(self, li_element) -> Optional[Dict]:
        """Parse a single publication list item."""
        text = li_element.get_text()

        # Extract authors
        authors_match = re.match(r'([^.]+?)\s+et al\.', text)
        first_author = authors_match.group(1).strip() if authors_match else None

        # Extract title and URL
        link = li_element.find('a')
        title = link.get_text(strip=True) if link else None
        url = link.get('href') if link else None

        # Extract journal and year
        # Pattern: **Journal Name** (Year)
        journal_match = re.search(r'\.\s*([A-Z][^(]+?)\s*\((\d{4})\)', text)
        journal = journal_match.group(1).strip() if journal_match else None
        year = journal_match.group(2) if journal_match else None

        if title or first_author:
            return {
                'first_author': first_author,
                'title': title,
                'journal': journal,
                'year': year,
                'url': url
            }

        return None

    def to_dataframe(self) -> pd.DataFrame:
        """Convert studies to a pandas DataFrame."""
        rows = []

        for study in self.studies:
            exp_design = study['experimental_design']

            # Count total samples
            total_samples = sum(s['count'] for s in exp_design['sample_types'])

            # Get primary publication
            primary_pub = None
            if study['publications']:
                pub = study['publications'][0]
                primary_pub = f"{pub['first_author']} et al. {pub['journal']} ({pub['year']})"

            # Extract unique features from research aims
            aims = study['research_aims']
            unique_features = self._extract_unique_features(aims)

            # Create base row
            base_row = {
                'study_id': study['id'],
                'title': study['title'],
                'unique_features': unique_features,
                'subjects': exp_design['subjects'],
                'timepoints': exp_design['timepoints'],
                'total_samples': total_samples,
                'primary_publication': primary_pub,
                'pub_count': len(study['publications'])
            }

            # Add sample types as separate rows or columns
            if exp_design['sample_types']:
                for sample in exp_design['sample_types']:
                    row = base_row.copy()
                    row['sample_type'] = sample['type']
                    row['sample_count'] = sample['count']
                    rows.append(row)
            else:
                rows.append(base_row)

        return pd.DataFrame(rows)

    def _extract_unique_features(self, aims_text: str) -> str:
        """Extract key unique features from research aims."""
        if not aims_text:
            return ""

        # Look for key phrases
        keywords = [
            'challenge', 'inoculation', 'experimental', 'longitudinal',
            'pre-symptomatic', 'convalescence', 'biorepository', 'multi-site',
            'Emergency Department', 'prospective'
        ]

        features = []
        aims_lower = aims_text.lower()

        for keyword in keywords:
            if keyword.lower() in aims_lower:
                features.append(keyword)

        return ', '.join(features[:3])  # Return top 3 features

    def save_to_json(self, output_path: str):
        """Save extracted data to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.studies, f, indent=2, ensure_ascii=False)
        print(f"Saved study data to {output_path}")

    def save_to_csv(self, output_path: str):
        """Save extracted data to CSV file."""
        df = self.to_dataframe()
        df.to_csv(output_path, index=False)
        print(f"Saved study data to {output_path}")


def main():
    """Main execution function."""
    # Path to the HTML file
    html_path = "data/CIDDI BioBank _ Duke Department of Medicine.html"

    # Create extractor with influenza filtering enabled
    print("="*60)
    print("CIDDI BioBank Influenza Study Extractor")
    print("="*60)
    extractor = StudyExtractor(html_path, filter_influenza=True)

    # Extract all studies
    print("\nExtracting influenza studies from HTML...")
    studies = extractor.extract_all_studies()
    print(f"✓ Found {len(studies)} influenza-related studies")
    print(f"✓ Filtered out {extractor.filtered_count} non-influenza studies")

    # Save to JSON
    extractor.save_to_json("output/studies.json")

    # Save to CSV
    extractor.save_to_csv("output/studies_summary.csv")

    # Print summary
    print("\n" + "="*60)
    print("Influenza Study Summary")
    print("="*60)
    for study in studies:
        exp_design = study['experimental_design']
        total_samples = sum(s['count'] for s in exp_design['sample_types'])
        print(f"\n{study['title']}")
        print(f"  Strain: {study['strain']}")
        print(f"  Type: {study['study_type']}")
        print(f"  Subjects: {exp_design.get('subjects', 'N/A')}")
        print(f"  Samples: {total_samples:,}")
        print(f"  Publications: {len(study['publications'])}")

    print("\n" + "="*60)


if __name__ == "__main__":
    main()
