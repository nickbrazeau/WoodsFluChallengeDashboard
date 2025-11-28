#!/usr/bin/env python3
"""
Generate Unified Dashboard - Single Page Website

Combines all three dashboards into one comprehensive HTML file:
1. Study Overview & Summary Table
2. Biodata Availability Matrix
3. Research Questions by Dataset

Navigation between sections via smooth scrolling.
"""

import json
import pandas as pd
from pathlib import Path
from html import escape as html_escape


def main():
    """Generate unified single-page dashboard."""
    print("="*70)
    print("Unified Influenza Dashboard Generator")
    print("="*70)

    # Load data
    with open("output/studies.json", 'r') as f:
        studies = json.load(f)

    biodata_df = pd.read_csv("output/biodata_matrix.csv")

    # Try to load PubMed findings
    try:
        pubmed_df = pd.read_csv("output/pubmed_findings.csv")
        print("  ✓ Loaded PubMed findings")

        # Create a lookup dictionary for findings by publication
        findings_lookup = {}
        for _, row in pubmed_df.iterrows():
            key = f"{row['first_author']}_{row['year']}"
            findings_lookup[key] = row['findings_summary']

        questions_df = pd.read_csv("output/research_questions.csv")

        # Add findings to questions dataframe
        questions_df['findings'] = questions_df.apply(
            lambda row: findings_lookup.get(
                f"{row['Publication'].split('(')[0].strip().replace(' et al.', '')}_{row['Publication'].split('(')[-1].replace(')', '')}",
                ''
            ),
            axis=1
        )
        print("  ✓ Merged PubMed findings with research questions")
    except FileNotFoundError:
        questions_df = pd.read_csv("output/research_questions.csv")
        questions_df['findings'] = ''
        print("  ✓ Loaded research questions (no PubMed findings available)")

    # Calculate stats
    total_studies = len(studies)
    total_subjects = sum(s.get('experimental_design', {}).get('subjects', 0) or 0 for s in studies)
    total_samples = sum(
        sum(sample.get('count', 0) for sample in s.get('experimental_design', {}).get('sample_types', []))
        for s in studies
    )
    total_publications = sum(len(s.get('publications', [])) for s in studies)

    # Extract biodata columns
    all_cols = biodata_df.columns.tolist()
    sample_cols = [c for c in all_cols if c.startswith('Sample: ')]
    assay_cols = [c for c in all_cols if c.startswith('Assay: ')]
    data_cols = [c for c in all_cols if c.startswith('Data: ')]

    sample_types = [c.replace('Sample: ', '') for c in sample_cols]
    assays = [c.replace('Assay: ', '') for c in assay_cols]
    datasets = [c.replace('Data: ', '') for c in data_cols]

    # Group research questions
    research_categories = {}

    # Handle PDF-based analysis format
    if 'study_type' in questions_df.columns:
        for study_type in questions_df['study_type'].unique():
            type_data = questions_df[questions_df['study_type'] == study_type]
            research_categories[study_type] = {
                'question': f"Research using {study_type.lower()} approaches",
                'publications': type_data.to_dict('records')
            }
    # Handle title-based analysis format
    elif 'Research Question Category' in questions_df.columns:
        for category in questions_df['Research Question Category'].unique():
            category_data = questions_df[questions_df['Research Question Category'] == category]
            research_categories[category] = {
                'question': category_data.iloc[0]['Question'],
                'publications': category_data.to_dict('records')
            }

    print(f"\nLoaded:")
    print(f"  • {total_studies} influenza studies")
    print(f"  • {len(sample_types)} sample types")
    print(f"  • {len(assays)} molecular assays")
    print(f"  • {len(research_categories)} research question categories")

    # Generate HTML (inline to keep it simple)
    html = generate_html(studies, total_studies, total_subjects, total_samples, total_publications,
                        biodata_df, sample_types, assays, datasets, research_categories)

    # Write output
    output_path = Path("output/unified_dashboard.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    file_size = output_path.stat().st_size / 1024
    print(f"\n✓ Unified dashboard generated: {output_path}")
    print(f"✓ File size: {file_size:.1f} KB")
    print(f"✓ Single HTML file - ready to share!")

    print("\n" + "="*70)
    print("Dashboard Features:")
    print("="*70)
    print("  1. Navigation menu to jump between sections")
    print("  2. Study Overview with sortable summary table")
    print("  3. Biodata Availability Matrix (presence/absence)")
    print("  4. Research Questions mapped to datasets")
    print("  5. Detailed study cards with full information")
    print("\n" + "="*70)


def generate_html(studies, total_studies, total_subjects, total_samples, total_publications,
                 biodata_df, sample_types, assays, datasets, research_categories):
    """Generate the complete HTML."""

    # Start HTML
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Influenza Research Dashboard | CIDDI BioBank</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 1800px;
            margin: 20px auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }

        /* Header & Navigation */
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        header h1 { font-size: 2.5em; margin-bottom: 10px; font-weight: 700; }
        header .subtitle { font-size: 1.1em; opacity: 0.9; }

        nav {
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            margin-top: 20px;
            border-radius: 10px;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 10px;
        }

        nav a {
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        nav a:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }

        /* Stats Grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }

        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }

        .stat-card:hover { transform: translateY(-5px); }
        .stat-number { font-size: 3em; font-weight: bold; color: #667eea; display: block; margin-bottom: 10px; }
        .stat-label { color: #666; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }

        /* Sections */
        section {
            padding: 50px 40px;
            border-bottom: 2px solid #f0f0f0;
        }

        section:last-child { border-bottom: none; }

        .section-header {
            font-size: 2.2em;
            color: #2d3748;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }

        .section-subtitle {
            color: #666;
            font-size: 1.05em;
            margin-bottom: 30px;
            line-height: 1.7;
        }

        /* Tables */
        .table-container {
            overflow-x: auto;
            margin: 30px 0;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            font-size: 0.9em;
        }

        thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        th {
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
        }

        th:hover { background: rgba(255, 255, 255, 0.1); }

        th.sortable::after { content: ' ⇅'; opacity: 0.5; }

        th.rotate {
            writing-mode: vertical-rl;
            transform: rotate(180deg);
            padding: 15px 8px;
            min-width: 40px;
        }

        th.study-col {
            position: sticky;
            left: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            z-index: 20;
            min-width: 250px;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #e9ecef;
        }

        td.study-cell {
            position: sticky;
            left: 0;
            background: #f8f9fa;
            font-weight: 600;
            z-index: 5;
            border-right: 2px solid #dee2e6;
        }

        tbody tr:hover { background: #f8f9fa; }
        tbody tr:hover td.study-cell { background: #e9ecef; }

        .cell-present { background: #10b981; color: white; font-weight: bold; text-align: center; }
        .cell-absent { background: #ef4444; color: white; opacity: 0.3; text-align: center; }
        .section-header-th { background: #6366f1 !important; }

        /* Badges */
        .strain-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: 600;
            background: #667eea;
            color: white;
        }

        .study-type-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            background: #e9ecef;
            color: #495057;
        }

        .expand-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85em;
            font-weight: 600;
            transition: all 0.2s ease;
        }

        .expand-btn:hover {
            background: #5568d3;
            transform: scale(1.05);
        }

        /* Research Questions */
        .question-section {
            margin-bottom: 30px;
            border: 2px solid #e9ecef;
            border-radius: 15px;
            overflow: hidden;
        }

        .question-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
        }

        .question-header h3 { font-size: 1.2em; margin-bottom: 10px; }
        .question-text { font-size: 1.05em; opacity: 0.95; font-style: italic; }

        .publications {
            padding: 20px;
            background: #f8f9fa;
        }

        .pub-item {
            padding: 15px;
            margin-bottom: 10px;
            background: white;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .pub-study { font-weight: 600; color: #667eea; margin-bottom: 5px; font-size: 0.9em; }
        .pub-title { color: #2d3748; margin-bottom: 8px; font-weight: 500; }
        .pub-findings {
            background: #e6f7f1;
            padding: 12px;
            margin: 10px 0;
            border-radius: 5px;
            font-size: 0.9em;
            color: #2d3748;
            line-height: 1.6;
            border-left: 3px solid #10b981;
        }
        .pub-findings strong {
            color: #059669;
        }
        .pub-citation { color: #666; font-size: 0.85em; margin-top: 8px; }

        .pub-link {
            color: #667eea;
            text-decoration: none;
            font-size: 0.85em;
        }

        .pub-link:hover { text-decoration: underline; }

        /* Study Cards */
        .study-cards {
            display: grid;
            gap: 25px;
            margin-top: 30px;
        }

        .study-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 15px;
            padding: 30px;
            transition: all 0.3s ease;
        }

        .study-card:hover {
            border-color: #667eea;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
        }

        .study-title {
            font-size: 1.5em;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 15px;
        }

        .study-badges { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }

        .study-aims {
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 5px;
            line-height: 1.7;
        }

        .design-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }

        .design-item {
            padding: 15px;
            background: #e9ecef;
            border-radius: 8px;
            text-align: center;
        }

        .design-label {
            font-size: 0.8em;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 5px;
        }

        .design-value {
            font-size: 1.3em;
            font-weight: bold;
            color: #2d3748;
        }

        footer {
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #666;
            line-height: 1.8;
        }

        footer a { color: #667eea; text-decoration: none; }
        footer a:hover { text-decoration: underline; }

        .credit {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #dee2e6;
            font-size: 0.85em;
            opacity: 0.8;
        }

        @media (max-width: 768px) {
            header h1 { font-size: 1.8em; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            section { padding: 30px 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🦠 Influenza Research Dashboard</h1>
            <p class="subtitle">CIDDI BioBank - Duke Department of Medicine</p>
            <nav>
                <a href="#overview">📊 Overview</a>
                <a href="#biodata">🧬 Biodata Matrix</a>
                <a href="#questions">🔬 Research Questions</a>
                <a href="#studies">📚 Detailed Studies</a>
            </nav>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">""" + str(total_studies) + """</span>
                <span class="stat-label">Influenza Studies</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">""" + str(total_subjects) + """</span>
                <span class="stat-label">Total Subjects</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">""" + str(total_samples) + """</span>
                <span class="stat-label">Total Samples</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">""" + str(total_publications) + """</span>
                <span class="stat-label">Publications</span>
            </div>
        </div>

        <!-- SECTION 1: STUDY OVERVIEW -->
        <section id="overview">
            <h2 class="section-header">📊 Study Overview</h2>
            <p class="section-subtitle">
                Summary of all influenza studies with key metrics. Click column headers to sort.
                Click "View Details" to jump to full study information below.
            </p>

            <div class="table-container">
                <table id="studyTable">
                    <thead>
                        <tr>
                            <th class="sortable" onclick="sortTable(0, 'studyTable')">Study Title</th>
                            <th class="sortable" onclick="sortTable(1, 'studyTable')">Strain</th>
                            <th class="sortable" onclick="sortTable(2, 'studyTable')">Study Type</th>
                            <th class="sortable" onclick="sortTable(3, 'studyTable')">Subjects</th>
                            <th class="sortable" onclick="sortTable(4, 'studyTable')">Timepoints</th>
                            <th class="sortable" onclick="sortTable(5, 'studyTable')">Total Samples</th>
                            <th class="sortable" onclick="sortTable(6, 'studyTable')">Publications</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>"""

    # Add study rows
    for study in studies:
        exp_design = study['experimental_design']
        total_study_samples = sum(s['count'] for s in exp_design['sample_types'])
        sample_types_list = [s['type'] for s in exp_design['sample_types']]

        html += f"""
                        <tr>
                            <td><strong>{study['title']}</strong></td>
                            <td><span class="strain-badge">{study['strain']}</span></td>
                            <td><span class="study-type-badge">{study['study_type']}</span></td>
                            <td>{exp_design.get('subjects', 'N/A')}</td>
                            <td>{exp_design.get('timepoints', 'N/A')}</td>
                            <td><strong>{total_study_samples:,}</strong></td>
                            <td>{len(study['publications'])}</td>
                            <td><button class="expand-btn" onclick="scrollToStudy('{study['id']}')">View Details</button></td>
                        </tr>"""

    html += """
                    </tbody>
                </table>
            </div>
        </section>

        <!-- SECTION 2: BIODATA MATRIX -->
        <section id="biodata">
            <h2 class="section-header">🧬 Biodata Availability Matrix</h2>
            <p class="section-subtitle">
                Presence/absence table showing which sample types, molecular assays, and datasets are available
                for each study. Green (✓) = available, Red (✗) = not available.
            </p>

            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th class="study-col">Study</th>
                            <th>Subjects</th>
                            <th class="section-header-th" colspan=\"""" + str(len(sample_types)) + """\">SAMPLE TYPES</th>"""

    if assays:
        html += '<th class="section-header-th" colspan="' + str(len(assays)) + '">MOLECULAR ASSAYS</th>'
    if datasets:
        html += '<th class="section-header-th" colspan="' + str(len(datasets)) + '">DATASETS</th>'

    html += """
                        </tr>
                        <tr>
                            <th class="study-col"></th>
                            <th></th>"""

    # Add column headers
    for st in sample_types:
        html += f'<th class="rotate">{st}</th>'
    for assay in assays:
        html += f'<th class="rotate">{assay}</th>'
    for ds in datasets:
        html += f'<th class="rotate">{ds[:30]}</th>'

    html += """
                        </tr>
                    </thead>
                    <tbody>"""

    # Add biodata rows
    for _, row in biodata_df.iterrows():
        html += f"""
                        <tr>
                            <td class="study-cell">{row['Study Title']}</td>
                            <td>{row['Subjects']}</td>"""

        # Sample types
        for st in sample_types:
            val = row[f'Sample: {st}']
            cell_class = 'cell-present' if val == 1 else 'cell-absent'
            symbol = '✓' if val == 1 else '✗'
            html += f'<td class="{cell_class}">{symbol}</td>'

        # Assays
        for assay in assays:
            val = row[f'Assay: {assay}']
            cell_class = 'cell-present' if val == 1 else 'cell-absent'
            symbol = '✓' if val == 1 else '✗'
            html += f'<td class="{cell_class}">{symbol}</td>'

        # Datasets
        for ds in datasets:
            val = row[f'Data: {ds}']
            cell_class = 'cell-present' if val == 1 else 'cell-absent'
            symbol = '✓' if val == 1 else '✗'
            html += f'<td class="{cell_class}">{symbol}</td>'

        html += '</tr>'

    html += """
                    </tbody>
                </table>
            </div>
        </section>

        <!-- SECTION 3: RESEARCH QUESTIONS -->
        <section id="questions">
            <h2 class="section-header">🔬 Research Questions Answered by Datasets</h2>
            <p class="section-subtitle">
                Major research questions addressed using these influenza studies, mapped to specific publications and datasets.
            </p>"""

    # Add research question categories
    for category, data in sorted(research_categories.items()):
        pub_count = len(data['publications'])
        category_escaped = html_escape(str(category))
        question_escaped = html_escape(str(data['question']))
        html += f"""
            <div class="question-section">
                <div class="question-header">
                    <h3>{category_escaped} ({pub_count} publications)</h3>
                    <p class="question-text">{question_escaped}</p>
                </div>
                <div class="publications">"""

        for pub in data['publications']:
            # Handle PDF-based analysis format
            if 'study_title' in pub:
                dataset = f"{pub['study_title']} ({pub['study_strain']})"
                title = pub['title']
                citation = f"{pub['first_author']} et al. {pub['journal']} ({pub['year']})"
                url = pub['url']
                research_q = pub.get('research_question', '')
                findings = pub.get('findings', '')
                # Handle NaN values from pandas
                if isinstance(research_q, float):
                    research_q = ''
                if isinstance(findings, float):
                    findings = ''
            # Handle title-based analysis format
            else:
                dataset = pub.get('Study Dataset', '')
                title = pub.get('Title', '')
                citation = pub.get('Publication', '')
                url = pub.get('URL', '')
                research_q = ''
                findings = pub.get('findings', '')
                # Handle NaN values
                if isinstance(findings, float):
                    findings = ''

            # Escape HTML entities for proper rendering
            dataset_escaped = html_escape(str(dataset))
            title_escaped = html_escape(str(title))
            citation_escaped = html_escape(str(citation))

            html_content = f"""
                    <div class="pub-item">
                        <div class="pub-study">📊 Dataset: {dataset_escaped}</div>
                        <div class="pub-title">{title_escaped}</div>"""

            # Add findings summary if available
            if findings and len(str(findings).strip()) > 0:
                findings_escaped = html_escape(str(findings))
                html_content += f"""
                        <div class="pub-findings">
                            <strong>Key Findings:</strong> {findings_escaped}
                        </div>"""

            html_content += f"""
                        <div class="pub-citation">{citation_escaped}</div>
                        <a href="{url}" target="_blank" class="pub-link">View Publication →</a>
                    </div>"""

            html += html_content

        html += """
                </div>
            </div>"""

    html += """
        </section>

        <!-- SECTION 4: DETAILED STUDY CARDS -->
        <section id="studies">
            <h2 class="section-header">📚 Detailed Study Information</h2>
            <p class="section-subtitle">
                Complete information for each influenza study including research aims, experimental design,
                sample types, molecular assays, and publications.
            </p>

            <div class="study-cards">"""

    # Add detailed study cards
    for study in studies:
        exp_design = study['experimental_design']
        total_study_samples = sum(s['count'] for s in exp_design['sample_types'])

        html += f"""
                <div class="study-card" id="study-{study['id']}">
                    <h3 class="study-title">{study['title']}</h3>
                    <div class="study-badges">
                        <span class="strain-badge">{study['strain']}</span>
                        <span class="study-type-badge">{study['study_type']}</span>
                    </div>"""

        if study['research_aims']:
            html += f"""
                    <div class="study-aims">
                        <strong>Research Aims:</strong><br>
                        {study['research_aims']}
                    </div>"""

        html += f"""
                    <div class="design-grid">
                        <div class="design-item">
                            <div class="design-label">Subjects</div>
                            <div class="design-value">{exp_design.get('subjects', 'N/A')}</div>
                        </div>
                        <div class="design-item">
                            <div class="design-label">Timepoints</div>
                            <div class="design-value">{exp_design.get('timepoints', 'N/A')}</div>
                        </div>
                        <div class="design-item">
                            <div class="design-label">Sample Types</div>
                            <div class="design-value">{len(exp_design['sample_types'])}</div>
                        </div>
                        <div class="design-item">
                            <div class="design-label">Total Samples</div>
                            <div class="design-value">{total_study_samples:,}</div>
                        </div>
                    </div>"""

        if study['publications']:
            html += f"""
                    <div style="margin-top: 25px; padding-top: 25px; border-top: 2px solid #f0f0f0;">
                        <h4 style="margin-bottom: 15px; color: #2d3748;">Publications ({len(study['publications'])})</h4>"""

            for pub in study['publications']:
                html += f"""
                        <div style="margin-bottom: 12px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                            <div style="font-weight: 600; color: #2d3748; margin-bottom: 5px;">{pub['first_author']} et al.</div>
                            <a href="{pub['url']}" target="_blank" style="color: #667eea; text-decoration: none; display: block; margin-bottom: 5px;">{pub['title']}</a>
                            <div style="color: #666; font-size: 0.9em; font-style: italic;">{pub['journal']} ({pub['year']})</div>
                        </div>"""

            html += """
                    </div>"""

        html += """
                </div>"""

    html += """
            </div>
        </section>

        <footer>
            <p><strong>Influenza Research Dashboard</strong> | CIDDI BioBank</p>
            <p>Duke Department of Medicine - Center for Infectious Disease Diagnosis Innovation</p>
            <div class="credit">
                <p>✨ Generated with <a href="https://claude.ai/code" target="_blank">Claude Code</a> with minimal human input</p>
                <p>Data source: <a href="https://medicine.duke.edu/research/research-support-resources/ciddi-biobank" target="_blank">CIDDI BioBank</a></p>
            </div>
        </footer>
    </div>

    <script>
        // Smooth scroll to study
        function scrollToStudy(studyId) {
            const element = document.getElementById('study-' + studyId);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                element.style.borderColor = '#667eea';
                element.style.boxShadow = '0 8px 20px rgba(102, 126, 234, 0.3)';
                setTimeout(() => {
                    element.style.borderColor = '';
                    element.style.boxShadow = '';
                }, 2000);
            }
        }

        // Table sorting
        function sortTable(columnIndex, tableId) {
            const table = document.getElementById(tableId);
            const tbody = table.tBodies[0];
            const rows = Array.from(tbody.rows);

            const currentOrder = tbody.getAttribute('data-sort-order') || 'asc';
            const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
            tbody.setAttribute('data-sort-order', newOrder);

            rows.sort((a, b) => {
                let aVal = a.cells[columnIndex].textContent.trim();
                let bVal = b.cells[columnIndex].textContent.trim();

                if (!isNaN(aVal.replace(/,/g, '')) && !isNaN(bVal.replace(/,/g, ''))) {
                    aVal = parseFloat(aVal.replace(/,/g, ''));
                    bVal = parseFloat(bVal.replace(/,/g, ''));
                }

                if (newOrder === 'asc') {
                    return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
                } else {
                    return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
                }
            });

            rows.forEach(row => tbody.appendChild(row));
        }

        // Smooth scroll for navigation links
        document.querySelectorAll('nav a').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });
    </script>
</body>
</html>"""

    return html


if __name__ == "__main__":
    main()
