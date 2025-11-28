#!/usr/bin/env python3
"""
Create Presence/Absence Matrix for Biodata Availability

Generates a matrix showing which types of biodata (sample types, assays, datasets)
are available for each influenza study.
"""

import json
import pandas as pd
from pathlib import Path


def create_biodata_matrix(studies_json_path: str):
    """Create presence/absence matrix for biodata availability."""

    # Load studies
    with open(studies_json_path, 'r') as f:
        studies = json.load(f)

    # Collect all unique sample types and assays across all studies
    # Use lowercase for normalization to avoid duplicates
    all_sample_types = set()
    all_assays = set()
    all_datasets = set()

    for study in studies:
        exp_design = study['experimental_design']

        # Sample types - normalize to lowercase
        for sample in exp_design.get('sample_types', []):
            all_sample_types.add(sample['type'].lower())

        # Molecular assays - normalize to lowercase
        for assay in exp_design.get('molecular', []):
            all_assays.add(assay.lower())

        # Datasets - keep as is (more structured)
        for dataset in exp_design.get('datasets', []):
            all_datasets.add(dataset)

    # Sort for consistent ordering
    all_sample_types = sorted(all_sample_types)
    all_assays = sorted(all_assays)
    all_datasets = sorted(all_datasets)

    print(f"\nFound across all studies:")
    print(f"  • {len(all_sample_types)} unique sample types")
    print(f"  • {len(all_assays)} unique molecular assays")
    print(f"  • {len(all_datasets)} unique datasets")

    # Create matrix
    matrix_data = []

    for study in studies:
        row = {
            'Study ID': study['id'],
            'Study Title': study['title'],
            'Strain': study['strain'],
            'Subjects': study['experimental_design'].get('subjects', 'N/A'),
            'Timepoints': study['experimental_design'].get('timepoints', 'N/A')
        }

        exp_design = study['experimental_design']

        # Add sample types (1 if present, 0 if absent)
        # Normalize to lowercase for comparison
        study_samples = {s['type'].lower() for s in exp_design.get('sample_types', [])}
        for sample_type in all_sample_types:
            row[f'Sample: {sample_type}'] = 1 if sample_type in study_samples else 0

        # Add molecular assays - normalize to lowercase for comparison
        study_assays = {a.lower() for a in exp_design.get('molecular', [])}
        for assay in all_assays:
            row[f'Assay: {assay}'] = 1 if assay in study_assays else 0

        # Add datasets
        study_datasets = set(exp_design.get('datasets', []))
        for dataset in all_datasets:
            row[f'Data: {dataset}'] = 1 if dataset in study_datasets else 0

        matrix_data.append(row)

    # Create DataFrame
    df = pd.DataFrame(matrix_data)

    return df, all_sample_types, all_assays, all_datasets


def generate_html_matrix(df, all_sample_types, all_assays, all_datasets, output_path: str):
    """Generate HTML visualization of the biodata matrix."""

    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biodata Availability Matrix | Influenza Studies</title>
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
        }

        .container {
            max-width: 1800px;
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
            line-height: 1.7;
        }

        .legend {
            display: flex;
            gap: 30px;
            justify-content: center;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .legend-box {
            width: 30px;
            height: 30px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }

        .present {
            background: #10b981;
        }

        .absent {
            background: #ef4444;
        }

        .table-container {
            overflow-x: auto;
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
            padding: 15px 10px;
            text-align: left;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }

        th.rotate {
            writing-mode: vertical-rl;
            transform: rotate(180deg);
            white-space: nowrap;
            padding: 15px 8px;
            min-width: 40px;
            max-width: 40px;
        }

        th.study-col {
            position: sticky;
            left: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            z-index: 20;
            min-width: 250px;
        }

        th.info-col {
            min-width: 80px;
        }

        td {
            padding: 12px 10px;
            border-bottom: 1px solid #e9ecef;
            text-align: center;
        }

        td.study-cell {
            position: sticky;
            left: 0;
            background: #f8f9fa;
            font-weight: 600;
            text-align: left;
            z-index: 5;
            border-right: 2px solid #dee2e6;
        }

        td.info-cell {
            background: #fafbfc;
        }

        tbody tr:hover {
            background: #f0f2f5;
        }

        tbody tr:hover td.study-cell {
            background: #e9ecef;
        }

        .cell-present {
            background: #10b981;
            color: white;
            font-weight: bold;
        }

        .cell-absent {
            background: #ef4444;
            color: white;
            opacity: 0.3;
        }

        .section-header {
            background: #6366f1 !important;
            color: white !important;
            font-weight: bold;
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

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #e9ecef;
        }

        .summary-card h4 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .summary-card ul {
            list-style: none;
            padding-left: 0;
        }

        .summary-card li {
            padding: 5px 0;
            color: #4b5563;
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
            <h1>🧬 Biodata Availability Matrix</h1>
            <p>Influenza Studies - CIDDI BioBank</p>
        </header>

        <div class="content">
            <div class="description">
                <strong>About this matrix:</strong> This presence/absence table shows which types of biological data
                (sample types, molecular assays, clinical datasets) are available for each influenza study in the
                CIDDI BioBank. Green cells (✓) indicate the data type is available; red cells (✗) indicate it is not.
            </div>

            <div class="legend">
                <div class="legend-item">
                    <div class="legend-box present"></div>
                    <span><strong>Available (✓)</strong></span>
                </div>
                <div class="legend-item">
                    <div class="legend-box absent"></div>
                    <span><strong>Not Available (✗)</strong></span>
                </div>
            </div>

            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th class="study-col">Study Title</th>
                            <th class="info-col">Strain</th>
                            <th class="info-col">Subjects</th>
                            <th class="info-col">Timepoints</th>
"""

    # Add sample type headers
    html += '<th class="section-header" colspan="{}">SAMPLE TYPES</th>'.format(len(all_sample_types))
    if all_assays:
        html += '<th class="section-header" colspan="{}">MOLECULAR ASSAYS</th>'.format(len(all_assays))
    if all_datasets:
        html += '<th class="section-header" colspan="{}">DATASETS</th>'.format(len(all_datasets))
    html += '</tr>\n<tr><th class="study-col"></th><th class="info-col"></th><th class="info-col"></th><th class="info-col"></th>'

    # Add rotated column headers
    for sample_type in all_sample_types:
        html += f'<th class="rotate">{sample_type}</th>'
    for assay in all_assays:
        html += f'<th class="rotate">{assay}</th>'
    for dataset in all_datasets:
        html += f'<th class="rotate">{dataset}</th>'

    html += '</tr>\n</thead>\n<tbody>'

    # Add data rows
    for _, row in df.iterrows():
        html += '<tr>'
        html += f'<td class="study-cell">{row["Study Title"]}</td>'
        html += f'<td class="info-cell">{row["Strain"]}</td>'
        html += f'<td class="info-cell">{row["Subjects"]}</td>'
        html += f'<td class="info-cell">{row["Timepoints"]}</td>'

        # Sample types
        for sample_type in all_sample_types:
            val = row[f'Sample: {sample_type}']
            cell_class = 'cell-present' if val == 1 else 'cell-absent'
            symbol = '✓' if val == 1 else '✗'
            html += f'<td class="{cell_class}">{symbol}</td>'

        # Assays
        for assay in all_assays:
            val = row[f'Assay: {assay}']
            cell_class = 'cell-present' if val == 1 else 'cell-absent'
            symbol = '✓' if val == 1 else '✗'
            html += f'<td class="{cell_class}">{symbol}</td>'

        # Datasets
        for dataset in all_datasets:
            val = row[f'Data: {dataset}']
            cell_class = 'cell-present' if val == 1 else 'cell-absent'
            symbol = '✓' if val == 1 else '✗'
            html += f'<td class="{cell_class}">{symbol}</td>'

        html += '</tr>'

    html += """
                    </tbody>
                </table>
            </div>

            <div class="summary">
                <h3>Summary Statistics</h3>
                <div class="summary-grid">
                    <div class="summary-card">
                        <h4>Sample Types (""" + str(len(all_sample_types)) + """)</h4>
                        <ul>
"""

    for sample_type in all_sample_types[:10]:
        html += f'<li>• {sample_type}</li>'
    if len(all_sample_types) > 10:
        html += f'<li>• ... and {len(all_sample_types) - 10} more</li>'

    html += """
                        </ul>
                    </div>
"""

    if all_assays:
        html += '<div class="summary-card"><h4>Molecular Assays (' + str(len(all_assays)) + ')</h4><ul>'
        for assay in all_assays[:10]:
            html += f'<li>• {assay}</li>'
        if len(all_assays) > 10:
            html += f'<li>• ... and {len(all_assays) - 10} more</li>'
        html += '</ul></div>'

    if all_datasets:
        html += '<div class="summary-card"><h4>Datasets (' + str(len(all_datasets)) + ')</h4><ul>'
        for dataset in all_datasets[:10]:
            html += f'<li>• {dataset}</li>'
        if len(all_datasets) > 10:
            html += f'<li>• ... and {len(all_datasets) - 10} more</li>'
        html += '</ul></div>'

    html += """
                </div>
            </div>
        </div>

        <footer>
            <p><strong>Biodata Availability Matrix</strong> | CIDDI BioBank Influenza Studies</p>
            <p>Generated with Claude Code</p>
        </footer>
    </div>
</body>
</html>
"""

    # Write HTML
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"\n✓ HTML matrix generated: {output_path}")


def main():
    """Main execution."""
    print("="*60)
    print("Biodata Availability Matrix Generator")
    print("="*60)

    # Create matrix
    df, sample_types, assays, datasets = create_biodata_matrix("output/studies.json")

    # Save CSV
    csv_path = "output/biodata_matrix.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n✓ CSV matrix saved: {csv_path}")

    # Generate HTML
    html_path = "output/biodata_matrix.html"
    generate_html_matrix(df, sample_types, assays, datasets, html_path)

    print("\n" + "="*60)
    print("Matrix generation complete!")
    print("="*60)
    print(f"\nFiles created:")
    print(f"  • {csv_path}")
    print(f"  • {html_path}")


if __name__ == "__main__":
    main()
