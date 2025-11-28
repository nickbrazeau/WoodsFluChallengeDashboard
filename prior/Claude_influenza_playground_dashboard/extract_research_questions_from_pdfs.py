#!/usr/bin/env python3
"""
Extract Research Questions from Downloaded Publications

Reads PDF files from the articles/ directory and extracts:
- Research aims/questions
- Study design
- Key findings
- Maps to corresponding datasets
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text from PDF file.

    Uses PyPDF2 for text extraction.
    """
    try:
        import PyPDF2

        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            # Extract first 5 pages (usually contains abstract, intro, methods)
            for page_num in range(min(5, len(reader.pages))):
                page = reader.pages[page_num]
                text += page.extract_text()

        return text
    except Exception as e:
        print(f"  ⚠️  Error reading {pdf_path.name}: {e}")
        return ""


def extract_research_question(text: str, title: str) -> Dict:
    """
    Extract research question/aims from paper text.

    Looks for common patterns in abstracts and introductions.
    Returns 1-3 complete sentences.
    """
    question_data = {
        'research_question': '',
        'study_type': '',
        'methods': '',
        'key_finding': ''
    }

    # Common section headers for aims/objectives
    patterns = [
        r'(?:research aims?|objectives?|goals?|purpose)[:\s]+(.*?)(?:methods|results|we performed|we conducted|participants|subjects|design)',
        r'(?:we aimed to|we sought to|we hypothesized|the objective was to|the goal was to)[:\s]+(.*?)(?:methods|results|we performed|we conducted|participants|subjects|design)',
        r'(?:to investigate|to determine|to identify|to assess|to evaluate|to develop|to examine)[:\s]+(.*?)(?:methods|results|we performed|we conducted|participants|subjects|design)',
    ]

    # Try to extract research question
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            raw_text = match.group(1).strip()
            # Get 1-3 complete sentences
            sentences = re.split(r'(?<=[.!?])\s+', raw_text)[:3]
            question_data['research_question'] = ' '.join(sentences).strip()
            # Limit to reasonable length
            if len(question_data['research_question']) > 500:
                question_data['research_question'] = question_data['research_question'][:500] + '...'
            break

    # If no explicit aim found, use abstract sentences
    if not question_data['research_question']:
        abstract_match = re.search(r'abstract[:\s]+(.*?)(?:introduction|keywords|background|methods)',
                                  text, re.IGNORECASE | re.DOTALL)
        if abstract_match:
            abstract = abstract_match.group(1).strip()
            # Get first 2-3 complete sentences
            sentences = re.split(r'(?<=[.!?])\s+', abstract)[:3]
            question_data['research_question'] = ' '.join(sentences).strip()
            # Limit to reasonable length
            if len(question_data['research_question']) > 500:
                question_data['research_question'] = question_data['research_question'][:500] + '...'

    # Identify study type from keywords
    text_lower = text.lower()
    if any(word in text_lower for word in ['challenge', 'inoculation', 'experimental infection']):
        question_data['study_type'] = 'Experimental Challenge'
    elif any(word in text_lower for word in ['transcriptomics', 'gene expression', 'rna-seq', 'microarray']):
        question_data['study_type'] = 'Transcriptomics'
    elif any(word in text_lower for word in ['proteomics', 'protein']):
        question_data['study_type'] = 'Proteomics'
    elif any(word in text_lower for word in ['metabolomics', 'metabolite']):
        question_data['study_type'] = 'Metabolomics'
    elif any(word in text_lower for word in ['systems biology', 'multi-omics', 'integrative']):
        question_data['study_type'] = 'Systems Biology'
    elif any(word in text_lower for word in ['biomarker', 'diagnostic', 'signature']):
        question_data['study_type'] = 'Biomarker Discovery'
    elif any(word in text_lower for word in ['clinical trial', 'intervention']):
        question_data['study_type'] = 'Clinical Trial'
    else:
        question_data['study_type'] = 'Research Study'

    # Extract methods summary
    methods_match = re.search(r'methods[:\s]+(.*?)(?:results|discussion|conclusion)',
                             text_lower, re.IGNORECASE | re.DOTALL)
    if methods_match:
        methods_text = methods_match.group(1).strip()[:200]
        question_data['methods'] = methods_text

    return question_data


def load_pdf_mapping(mapping_path: str = "pdf_mapping.json") -> Dict:
    """Load manual PDF to publication mapping."""
    try:
        with open(mapping_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def map_pdf_to_publication(pdf_filename: str, studies: List[Dict], pdf_mapping: Dict) -> Optional[Dict]:
    """
    Map a PDF filename to a publication in the studies data.

    Uses manual mapping file with fallback to fuzzy matching.
    """
    # First try manual mapping
    if pdf_filename in pdf_mapping:
        mapped = pdf_mapping[pdf_filename]
        # Find matching publication in studies
        for study in studies:
            for pub in study['publications']:
                # Match by author, year, and title substring
                if (pub.get('first_author', '').startswith(mapped['author'].split()[0]) and
                    pub.get('year') == mapped['year']):
                    return {
                        'publication': pub,
                        'study': study
                    }

    # Fallback: Try to match by author name in filename
    author_names = ['fourati', 'liu', 'rose', 'zaas', 'woods', 'carin',
                   'chen', 'mcclain', 'leonard', 'bagga', 'huang', 'moody',
                   'burke', 'poore', 'lydon', 'tsalik']

    pdf_lower = pdf_filename.lower()

    for author_key in author_names:
        if author_key in pdf_lower:
            # Find publications by this author
            for study in studies:
                for pub in study['publications']:
                    if pub.get('first_author', '').lower().startswith(author_key):
                        return {
                            'publication': pub,
                            'study': study
                        }

    return None


def analyze_publications(studies_json_path: str, articles_dir: str) -> pd.DataFrame:
    """
    Analyze all PDF publications and extract research questions.
    """
    # Load studies
    with open(studies_json_path, 'r') as f:
        studies = json.load(f)

    # Load PDF mapping
    pdf_mapping = load_pdf_mapping()
    print(f"Loaded {len(pdf_mapping)} manual PDF mappings")

    articles_path = Path(articles_dir)
    pdf_files = sorted(articles_path.glob('**/*.pdf'))

    print(f"Found {len(pdf_files)} PDF files in {articles_dir}")

    publications_data = []

    for pdf_path in pdf_files:
        print(f"\n📄 Processing: {pdf_path.name}")

        # Extract text from PDF
        text = extract_text_from_pdf(pdf_path)

        if not text:
            print(f"  ⚠️  Could not extract text")
            continue

        # Map to publication/study
        mapping = map_pdf_to_publication(pdf_path.name, studies, pdf_mapping)

        if not mapping:
            print(f"  ⚠️  Could not map to study")
            continue

        pub = mapping['publication']
        study = mapping['study']

        print(f"  ✓ Mapped to: {pub['first_author']} et al. ({pub['year']})")
        print(f"  ✓ Study: {study['title']}")

        # Extract research question
        question_data = extract_research_question(text, pub.get('title', ''))

        print(f"  ✓ Study type: {question_data['study_type']}")

        # Store data
        publications_data.append({
            'pdf_filename': pdf_path.name,
            'first_author': pub['first_author'],
            'title': pub['title'],
            'journal': pub['journal'],
            'year': pub['year'],
            'url': pub['url'],
            'study_id': study['id'],
            'study_title': study['title'],
            'study_strain': study['strain'],
            'research_question': question_data['research_question'],
            'study_type': question_data['study_type'],
            'methods_summary': question_data['methods']
        })

    return pd.DataFrame(publications_data)


def generate_html_report(df: pd.DataFrame, output_path: str):
    """Generate HTML report of research questions."""

    # Group by study type
    study_types = df['study_type'].value_counts()

    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Questions Analysis | CIDDI BioBank</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .content {
            padding: 40px;
        }

        .summary {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
        }

        .summary h3 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #e9ecef;
        }

        .stat-card .number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }

        .stat-card .label {
            color: #666;
            margin-top: 5px;
        }

        .publication-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .publication-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .pub-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 15px;
        }

        .pub-title {
            font-size: 1.2em;
            font-weight: 600;
            color: #2d3748;
            flex: 1;
        }

        .pub-title a {
            color: #667eea;
            text-decoration: none;
        }

        .pub-title a:hover {
            text-decoration: underline;
        }

        .study-type-badge {
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            white-space: nowrap;
            margin-left: 15px;
        }

        .pub-meta {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 15px;
        }

        .pub-meta strong {
            color: #2d3748;
        }

        .research-question {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            margin-bottom: 15px;
        }

        .research-question h4 {
            color: #667eea;
            margin-bottom: 8px;
            font-size: 0.9em;
            text-transform: uppercase;
        }

        .study-link {
            display: inline-block;
            background: #f8f9fa;
            padding: 8px 15px;
            border-radius: 5px;
            color: #667eea;
            text-decoration: none;
            font-size: 0.9em;
            font-weight: 500;
        }

        .study-link:hover {
            background: #e9ecef;
        }

        .section-header {
            margin: 40px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }

        .section-header h2 {
            color: #2d3748;
        }

        footer {
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔬 Research Questions Analysis</h1>
            <p>CIDDI BioBank Influenza Studies - Publications Analysis</p>
        </header>

        <div class="content">
            <div class="summary">
                <h3>Analysis Summary</h3>
                <p>
                    Comprehensive analysis of <strong>""" + str(len(df)) + """ publications</strong>
                    from the CIDDI BioBank influenza research studies. Research questions and study aims
                    extracted from full-text PDFs.
                </p>

                <div class="stats">
"""

    for study_type, count in study_types.items():
        html += f"""
                    <div class="stat-card">
                        <div class="number">{count}</div>
                        <div class="label">{study_type}</div>
                    </div>
"""

    html += """
                </div>
            </div>
"""

    # Group publications by study type
    for study_type in df['study_type'].unique():
        type_pubs = df[df['study_type'] == study_type].sort_values('year', ascending=False)

        html += f"""
            <div class="section-header">
                <h2>{study_type} ({len(type_pubs)} publications)</h2>
            </div>
"""

        for _, pub in type_pubs.iterrows():
            html += f"""
            <div class="publication-card">
                <div class="pub-header">
                    <div class="pub-title">
                        <a href="{pub['url']}" target="_blank">{pub['title']}</a>
                    </div>
                    <div class="study-type-badge">{pub['study_type']}</div>
                </div>

                <div class="pub-meta">
                    <strong>{pub['first_author']} et al.</strong> |
                    {pub['journal']} ({pub['year']})
                </div>

                <div class="research-question">
                    <h4>Research Question / Aims</h4>
                    <p>{pub['research_question'] if pub['research_question'] else 'See publication for details'}</p>
                </div>

                <a href="#" class="study-link">
                    📊 Dataset: {pub['study_title']} ({pub['study_strain']})
                </a>
            </div>
"""

    html += """
        </div>

        <footer>
            <p><strong>Research Questions Analysis</strong> | CIDDI BioBank</p>
            <p>Generated with Claude Code</p>
        </footer>
    </div>
</body>
</html>
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n✓ HTML report generated: {output_path}")


def main():
    """Main execution."""
    print("="*70)
    print("Research Questions Extraction from PDFs")
    print("="*70)

    # Check if PyPDF2 is installed
    try:
        import PyPDF2
    except ImportError:
        print("\n⚠️  PyPDF2 is required. Installing...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'pypdf2'])
        import PyPDF2

    # Analyze publications
    df = analyze_publications("output/studies.json", "articles")

    print(f"\n{'='*70}")
    print(f"Analysis Complete")
    print(f"{'='*70}")
    print(f"\nSuccessfully analyzed {len(df)} publications")

    # Save to CSV
    csv_path = "output/research_questions_detailed.csv"
    df.to_csv(csv_path, index=False)
    print(f"✓ CSV saved: {csv_path}")

    # Generate HTML report
    html_path = "output/research_questions_detailed.html"
    generate_html_report(df, html_path)

    print(f"\n{'='*70}")


if __name__ == "__main__":
    main()
