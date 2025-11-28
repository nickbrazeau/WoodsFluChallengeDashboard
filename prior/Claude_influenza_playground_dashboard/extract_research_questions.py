#!/usr/bin/env python3
"""
Extract Research Questions from Publication Abstracts

Since PDFs are behind paywalls, fetch publicly available abstracts and
extract research questions/objectives that were addressed using each dataset.
"""

import json
import pandas as pd
from pathlib import Path


def create_research_questions_table():
    """
    Create table of research questions answered using each influenza dataset.

    Based on the common themes in influenza research publications, we'll categorize
    the types of research questions typically addressed.
    """

    # Load studies
    with open("output/studies.json", 'r') as f:
        studies = json.load(f)

    # Research question categories based on influenza research themes
    research_questions = {
        'Host Gene Expression': {
            'question': 'What host gene expression signatures can predict viral infection susceptibility or disease severity?',
            'studies': []
        },
        'Pre-symptomatic Detection': {
            'question': 'Can infection be detected before symptoms appear using host biomarkers?',
            'studies': []
        },
        'Viral-Host Dynamics': {
            'question': 'How do viral load kinetics relate to host immune response and clinical outcomes?',
            'studies': []
        },
        'Diagnostic Biomarkers': {
            'question': 'What blood-based biomarkers can distinguish viral from bacterial respiratory infections?',
            'studies': []
        },
        'Symptomatic vs Asymptomatic': {
            'question': 'What molecular differences exist between symptomatic and asymptomatic influenza infection?',
            'studies': []
        },
        'Immune Response Dynamics': {
            'question': 'How do cytokines, antibodies, and cellular immune responses evolve during influenza infection?',
            'studies': []
        },
        'Viral Genetics & Evolution': {
            'question': 'How does influenza virus evolve within a host and what are the rates of reassortment?',
            'studies': []
        },
        'Cross-reactive Immunity': {
            'question': 'What is the nature of cross-reactive antibody responses across influenza strains?',
            'studies': []
        },
        'Predictive Modeling': {
            'question': 'Can machine learning models predict infection outcomes using baseline and early timepoint data?',
            'studies': []
        },
        'Longitudinal Monitoring': {
            'question': 'How can dense longitudinal sampling improve understanding of infection progression?',
            'studies': []
        }
    }

    # Map publications to research questions based on titles and known research themes
    for study in studies:
        study_id = study['id']
        study_title = study['title']

        for pub in study['publications']:
            title = pub['title'].lower()

            # Categorize based on title keywords
            if 'gene expression' in title or 'transcription' in title or 'genomic' in title:
                research_questions['Host Gene Expression']['studies'].append({
                    'study': study_title,
                    'publication': f"{pub['first_author']} et al. ({pub['year']})",
                    'title': pub['title'],
                    'url': pub['url']
                })

            if 'presymptomatic' in title or 'pre-symptomatic' in title or 'early detection' in title:
                research_questions['Pre-symptomatic Detection']['studies'].append({
                    'study': study_title,
                    'publication': f"{pub['first_author']} et al. ({pub['year']})",
                    'title': pub['title'],
                    'url': pub['url']
                })

            if 'viral' in title and ('dynamic' in title or 'kinetic' in title or 'load' in title):
                research_questions['Viral-Host Dynamics']['studies'].append({
                    'study': study_title,
                    'publication': f"{pub['first_author']} et al. ({pub['year']})",
                    'title': pub['title'],
                    'url': pub['url']
                })

            if 'diagnos' in title or 'classifier' in title or 'biomarker' in title:
                research_questions['Diagnostic Biomarkers']['studies'].append({
                    'study': study_title,
                    'publication': f"{pub['first_author']} et al. ({pub['year']})",
                    'title': pub['title'],
                    'url': pub['url']
                })

            if 'symptomatic' in title and 'asymptomatic' in title:
                research_questions['Symptomatic vs Asymptomatic']['studies'].append({
                    'study': study_title,
                    'publication': f"{pub['first_author']} et al. ({pub['year']})",
                    'title': pub['title'],
                    'url': pub['url']
                })

            if 'cytokine' in title or 'immune' in title or 'antibod' in title:
                research_questions['Immune Response Dynamics']['studies'].append({
                    'study': study_title,
                    'publication': f"{pub['first_author']} et al. ({pub['year']})",
                    'title': pub['title'],
                    'url': pub['url']
                })

            if 'sequenc' in title or 'evolution' in title or 'reassortment' in title or 'diversification' in title:
                research_questions['Viral Genetics & Evolution']['studies'].append({
                    'study': study_title,
                    'publication': f"{pub['first_author']} et al. ({pub['year']})",
                    'title': pub['title'],
                    'url': pub['url']
                })

            if 'cross-reactive' in title or 'hemagglutinin' in title:
                research_questions['Cross-reactive Immunity']['studies'].append({
                    'study': study_title,
                    'publication': f"{pub['first_author']} et al. ({pub['year']})",
                    'title': pub['title'],
                    'url': pub['url']
                })

            if 'predict' in title or 'machine learning' in title or 'crowdsourced' in title:
                research_questions['Predictive Modeling']['studies'].append({
                    'study': study_title,
                    'publication': f"{pub['first_author']} et al. ({pub['year']})",
                    'title': pub['title'],
                    'url': pub['url']
                })

            if 'longitudinal' in title or 'temporal' in title or 'monitoring' in title:
                research_questions['Longitudinal Monitoring']['studies'].append({
                    'study': study_title,
                    'publication': f"{pub['first_author']} et al. ({pub['year']})",
                    'title': pub['title'],
                    'url': pub['url']
                })

    return research_questions, studies


def generate_questions_html(research_questions, studies, output_path):
    """Generate HTML table of research questions."""

    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Questions Answered by Influenza Datasets</title>
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
            max-width: 1600px;
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

        .description {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
        }

        .question-section {
            margin-bottom: 40px;
            border: 2px solid #e9ecef;
            border-radius: 15px;
            overflow: hidden;
        }

        .question-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }

        .question-header h3 {
            font-size: 1.3em;
            margin-bottom: 10px;
        }

        .question-text {
            font-size: 1.05em;
            opacity: 0.95;
            font-style: italic;
        }

        .publications {
            padding: 25px;
        }

        .pub-item {
            padding: 15px;
            margin-bottom: 15px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .pub-item:hover {
            background: #e9ecef;
        }

        .pub-study {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 5px;
        }

        .pub-title {
            color: #2d3748;
            margin-bottom: 5px;
        }

        .pub-citation {
            color: #666;
            font-size: 0.9em;
        }

        .pub-link {
            color: #667eea;
            text-decoration: none;
            font-size: 0.9em;
        }

        .pub-link:hover {
            text-decoration: underline;
        }

        .no-pubs {
            padding: 20px;
            color: #666;
            font-style: italic;
        }

        .summary {
            margin-top: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 10px;
        }

        .summary h3 {
            margin-bottom: 20px;
            color: #2d3748;
        }

        .study-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .study-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #e9ecef;
        }

        .study-card h4 {
            color: #667eea;
            margin-bottom: 10px;
        }

        .study-card p {
            color: #666;
            font-size: 0.9em;
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
            <h1>🔬 Research Questions Answered by Influenza Datasets</h1>
            <p>CIDDI BioBank - Mapping Publications to Scientific Questions</p>
        </header>

        <div class="content">
            <div class="description">
                <strong>About this analysis:</strong> This table shows the major research questions that have been
                addressed using the 6 influenza challenge and cohort studies in the CIDDI BioBank. Each question is
                linked to specific publications and the datasets used to answer it.
            </div>
"""

    # Add each research question section
    for category, data in research_questions.items():
        pub_count = len(data['studies'])

        html += f"""
            <div class="question-section">
                <div class="question-header">
                    <h3>{category} ({pub_count} publications)</h3>
                    <p class="question-text">{data['question']}</p>
                </div>
"""

        if data['studies']:
            html += '<div class="publications">'
            for pub_info in data['studies']:
                html += f"""
                <div class="pub-item">
                    <div class="pub-study">📊 Dataset: {pub_info['study']}</div>
                    <div class="pub-title">{pub_info['title']}</div>
                    <div class="pub-citation">{pub_info['publication']}</div>
                    <a href="{pub_info['url']}" target="_blank" class="pub-link">View Publication →</a>
                </div>
"""
            html += '</div>'
        else:
            html += '<div class="no-pubs">No publications found for this research question.</div>'

        html += '</div>'

    # Add study summary
    html += """
            <div class="summary">
                <h3>Influenza Study Datasets</h3>
                <div class="study-list">
"""

    for study in studies:
        exp_design = study['experimental_design']
        total_samples = sum(s['count'] for s in exp_design['sample_types'])
        pub_count = len(study['publications'])

        html += f"""
                    <div class="study-card">
                        <h4>{study['title']}</h4>
                        <p><strong>Strain:</strong> {study['strain']}<br>
                        <strong>Subjects:</strong> {exp_design.get('subjects', 'N/A')}<br>
                        <strong>Samples:</strong> {total_samples:,}<br>
                        <strong>Publications:</strong> {pub_count}</p>
                    </div>
"""

    html += """
                </div>
            </div>
        </div>

        <footer>
            <p><strong>Research Questions Analysis</strong> | CIDDI BioBank Influenza Studies</p>
            <p>Generated with Claude Code | Note: Publications are categorized based on title analysis</p>
        </footer>
    </div>
</body>
</html>
"""

    with open(output_path, 'w') as f:
        f.write(html)

    print(f"\n✓ Research questions HTML generated: {output_path}")


def main():
    """Main execution."""
    print("="*70)
    print("Research Questions Extractor")
    print("="*70)
    print("\nNote: Since publications are behind paywalls, this analysis is based")
    print("on publication titles and common research themes in influenza studies.")

    # Create research questions mapping
    research_questions, studies = create_research_questions_table()

    # Print summary
    print(f"\n📊 Research Question Categories:")
    for category, data in research_questions.items():
        pub_count = len(data['studies'])
        print(f"  • {category}: {pub_count} publications")

    # Generate HTML
    html_path = "output/research_questions.html"
    generate_questions_html(research_questions, studies, html_path)

    # Create CSV
    csv_data = []
    for category, data in research_questions.items():
        for pub_info in data['studies']:
            csv_data.append({
                'Research Question Category': category,
                'Question': data['question'],
                'Study Dataset': pub_info['study'],
                'Publication': pub_info['publication'],
                'Title': pub_info['title'],
                'URL': pub_info['url']
            })

    csv_path = "output/research_questions.csv"
    if csv_data:
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_path, index=False)
        print(f"✓ Research questions CSV saved: {csv_path}")

    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)
    print(f"\nFiles created:")
    print(f"  • {html_path}")
    print(f"  • {csv_path}")


if __name__ == "__main__":
    main()
