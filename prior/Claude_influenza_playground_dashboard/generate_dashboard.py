#!/usr/bin/env python3
"""
CIDDI BioBank Influenza Dashboard Generator

Creates an interactive HTML dashboard from extracted influenza research study data.
Layout: Summary table at top, detailed study cards below.

Generated with Claude Code (claude.ai/code) with minimal input.
"""

import json
import pandas as pd
from pathlib import Path
from jinja2 import Template


class DashboardGenerator:
    """Generate interactive HTML dashboard from influenza study data."""

    def __init__(self, studies_json_path: str):
        self.studies_json_path = Path(studies_json_path)
        with open(self.studies_json_path, 'r', encoding='utf-8') as f:
            self.studies = json.load(f)

    def generate_dashboard(self, output_path: str):
        """Generate the main dashboard HTML with summary table and detailed cards."""

        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Influenza Research Studies | CIDDI BioBank Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
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
            font-size: 2.8em;
            margin-bottom: 10px;
            font-weight: 700;
        }

        header p {
            font-size: 1.2em;
            opacity: 0.95;
            margin-bottom: 5px;
        }

        header .subtitle {
            font-size: 0.95em;
            opacity: 0.8;
            font-style: italic;
        }

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

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-number {
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            display: block;
            margin-bottom: 10px;
        }

        .stat-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .content {
            padding: 40px;
        }

        .section-title {
            font-size: 2em;
            color: #2d3748;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .section-subtitle {
            color: #666;
            font-size: 1.05em;
            margin-bottom: 25px;
            line-height: 1.7;
        }

        /* Summary Table Styles */
        .table-container {
            overflow-x: auto;
            margin-bottom: 60px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        thead {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        th {
            padding: 18px 15px;
            text-align: left;
            font-weight: 600;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            cursor: pointer;
            user-select: none;
            position: relative;
        }

        th:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        th.sortable::after {
            content: ' ⇅';
            opacity: 0.5;
            font-size: 0.8em;
        }

        td {
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }

        tbody tr {
            transition: background 0.2s ease;
        }

        tbody tr:hover {
            background: #f8f9fa;
        }

        tbody tr:nth-child(even) {
            background: #fafbfc;
        }

        tbody tr:nth-child(even):hover {
            background: #f0f2f5;
        }

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

        .pub-link {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }

        .pub-link:hover {
            text-decoration: underline;
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

        /* Detailed Study Cards */
        .study-cards-section {
            margin-top: 60px;
        }

        .study-card {
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 15px;
            padding: 35px;
            margin-bottom: 30px;
            transition: all 0.3s ease;
        }

        .study-card:hover {
            border-color: #667eea;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
        }

        .study-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }

        .study-title {
            font-size: 1.6em;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 12px;
        }

        .study-badges {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .study-id {
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .study-aims {
            margin: 25px 0;
            padding: 25px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 5px;
            font-size: 0.98em;
            line-height: 1.8;
        }

        .study-aims strong {
            color: #667eea;
            font-size: 1.05em;
        }

        .study-design {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 15px;
            margin: 25px 0;
        }

        .design-item {
            padding: 18px;
            background: #e9ecef;
            border-radius: 10px;
            text-align: center;
        }

        .design-label {
            font-size: 0.8em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .design-value {
            font-size: 1.4em;
            font-weight: bold;
            color: #2d3748;
        }

        .sample-types {
            margin: 25px 0;
        }

        .sample-types h4 {
            margin-bottom: 15px;
            color: #2d3748;
            font-size: 1.15em;
        }

        .sample-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 12px;
        }

        .sample-item {
            padding: 12px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9em;
        }

        .sample-type {
            font-weight: 600;
        }

        .sample-count {
            background: rgba(255, 255, 255, 0.3);
            padding: 3px 12px;
            border-radius: 12px;
            font-weight: bold;
        }

        .assays {
            margin: 25px 0;
        }

        .assays h4 {
            margin-bottom: 12px;
            color: #2d3748;
            font-size: 1.15em;
        }

        .assay-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .assay-tag {
            padding: 8px 14px;
            background: #e9ecef;
            border-radius: 15px;
            font-size: 0.85em;
            color: #495057;
        }

        .publications {
            margin-top: 30px;
            padding-top: 30px;
            border-top: 2px solid #f0f0f0;
        }

        .publications h4 {
            margin-bottom: 18px;
            color: #2d3748;
            font-size: 1.15em;
        }

        .publication-item {
            margin-bottom: 15px;
            padding: 18px;
            background: #f8f9fa;
            border-radius: 10px;
            transition: background 0.2s ease;
        }

        .publication-item:hover {
            background: #e9ecef;
        }

        .pub-authors {
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 6px;
        }

        .pub-title {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
            display: block;
            margin-bottom: 6px;
            line-height: 1.5;
        }

        .pub-title:hover {
            text-decoration: underline;
        }

        .pub-journal {
            color: #666;
            font-size: 0.9em;
            font-style: italic;
        }

        footer {
            text-align: center;
            padding: 35px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
            line-height: 1.8;
        }

        footer a {
            color: #667eea;
            text-decoration: none;
        }

        footer a:hover {
            text-decoration: underline;
        }

        .credit {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #dee2e6;
            font-size: 0.85em;
            opacity: 0.8;
        }

        @media (max-width: 768px) {
            header h1 {
                font-size: 2em;
            }

            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .study-design {
                grid-template-columns: repeat(2, 1fr);
            }

            th, td {
                padding: 10px 8px;
                font-size: 0.85em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🦠 Influenza Research Studies</h1>
            <p>CIDDI BioBank Dashboard - Duke Department of Medicine</p>
            <p class="subtitle">Hierarchical Structure of Influenza Research with Available Biobank Data</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">{{ stats.total_studies }}</span>
                <span class="stat-label">Influenza Studies</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{{ stats.total_subjects }}</span>
                <span class="stat-label">Total Subjects</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{{ stats.total_samples }}</span>
                <span class="stat-label">Total Samples</span>
            </div>
            <div class="stat-card">
                <span class="stat-number">{{ stats.total_publications }}</span>
                <span class="stat-label">Publications</span>
            </div>
        </div>

        <div class="content">
            <h2 class="section-title">📊 Summary Table</h2>
            <p class="section-subtitle">
                Overview of all influenza studies in the CIDDI BioBank with key metrics and sample availability.
                Click column headers to sort. Click "View Details" to jump to full study information below.
            </p>

            <div class="table-container">
                <table id="studyTable">
                    <thead>
                        <tr>
                            <th class="sortable" onclick="sortTable(0)">Study Title</th>
                            <th class="sortable" onclick="sortTable(1)">Strain</th>
                            <th class="sortable" onclick="sortTable(2)">Study Type</th>
                            <th class="sortable" onclick="sortTable(3)">Subjects</th>
                            <th class="sortable" onclick="sortTable(4)">Timepoints</th>
                            <th class="sortable" onclick="sortTable(5)">Total Samples</th>
                            <th class="sortable" onclick="sortTable(6)">Sample Types</th>
                            <th class="sortable" onclick="sortTable(7)">Publications</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for study in studies %}
                        {% set total_samples = study.experimental_design.sample_types|sum(attribute='count') %}
                        {% set sample_types_list = study.experimental_design.sample_types|map(attribute='type')|list %}
                        <tr>
                            <td><strong>{{ study.title }}</strong></td>
                            <td><span class="strain-badge">{{ study.strain }}</span></td>
                            <td><span class="study-type-badge">{{ study.study_type }}</span></td>
                            <td>{{ study.experimental_design.subjects or 'N/A' }}</td>
                            <td>{{ study.experimental_design.timepoints or 'N/A' }}</td>
                            <td><strong>{{ "{:,}".format(total_samples) }}</strong></td>
                            <td>{{ sample_types_list[:3]|join(', ') }}{% if sample_types_list|length > 3 %} (+{{ sample_types_list|length - 3 }} more){% endif %}</td>
                            <td>
                                {% if study.publications %}
                                <a href="{{ study.publications[0].url }}" target="_blank" class="pub-link" title="{{ study.publications[0].title }}">
                                    {{ study.publications|length }} pub{% if study.publications|length != 1 %}s{% endif %}
                                </a>
                                {% else %}
                                N/A
                                {% endif %}
                            </td>
                            <td><button class="expand-btn" onclick="scrollToStudy('{{ study.id }}')">View Details</button></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>

            <div class="study-cards-section">
                <h2 class="section-title">📚 Detailed Study Information</h2>
                <p class="section-subtitle">
                    Complete information for each influenza study including research aims, experimental design,
                    sample types, molecular assays, and full publication lists.
                </p>

                {% for study in studies %}
                <div class="study-card" id="study-{{ study.id }}">
                    <div class="study-header">
                        <div>
                            <h3 class="study-title">{{ study.title }}</h3>
                            <div class="study-badges">
                                <span class="study-id">ID: {{ study.id }}</span>
                                <span class="strain-badge">{{ study.strain }}</span>
                                <span class="study-type-badge">{{ study.study_type }}</span>
                            </div>
                        </div>
                    </div>

                    {% if study.research_aims %}
                    <div class="study-aims">
                        <strong>Research Aims:</strong><br>
                        {{ study.research_aims }}
                    </div>
                    {% endif %}

                    {% if study.experimental_design.subjects or study.experimental_design.timepoints %}
                    <div class="study-design">
                        {% if study.experimental_design.subjects %}
                        <div class="design-item">
                            <div class="design-label">Subjects</div>
                            <div class="design-value">{{ study.experimental_design.subjects }}</div>
                        </div>
                        {% endif %}
                        {% if study.experimental_design.timepoints %}
                        <div class="design-item">
                            <div class="design-label">Timepoints</div>
                            <div class="design-value">{{ study.experimental_design.timepoints }}</div>
                        </div>
                        {% endif %}
                        {% if study.experimental_design.sample_types %}
                        <div class="design-item">
                            <div class="design-label">Sample Types</div>
                            <div class="design-value">{{ study.experimental_design.sample_types|length }}</div>
                        </div>
                        {% set total_samples = study.experimental_design.sample_types|sum(attribute='count') %}
                        <div class="design-item">
                            <div class="design-label">Total Samples</div>
                            <div class="design-value">{{ "{:,}".format(total_samples) }}</div>
                        </div>
                        {% endif %}
                    </div>
                    {% endif %}

                    {% if study.experimental_design.sample_types %}
                    <div class="sample-types">
                        <h4>Sample Types & Quantities</h4>
                        <div class="sample-grid">
                            {% for sample in study.experimental_design.sample_types %}
                            <div class="sample-item">
                                <span class="sample-type">{{ sample.type }}</span>
                                <span class="sample-count">{{ "{:,}".format(sample.count) }}</span>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}

                    {% if study.experimental_design.molecular %}
                    <div class="assays">
                        <h4>Molecular Assays & Techniques</h4>
                        <div class="assay-tags">
                            {% for assay in study.experimental_design.molecular %}
                            <span class="assay-tag">{{ assay }}</span>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}

                    {% if study.publications %}
                    <div class="publications">
                        <h4>Publications ({{ study.publications|length }})</h4>
                        {% for pub in study.publications %}
                        <div class="publication-item">
                            {% if pub.first_author %}
                            <div class="pub-authors">{{ pub.first_author }} et al.</div>
                            {% endif %}
                            {% if pub.url %}
                            <a href="{{ pub.url }}" target="_blank" class="pub-title">{{ pub.title }}</a>
                            {% else %}
                            <span class="pub-title">{{ pub.title }}</span>
                            {% endif %}
                            {% if pub.journal and pub.year %}
                            <div class="pub-journal">{{ pub.journal }} ({{ pub.year }})</div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>

        <footer>
            <p><strong>CIDDI BioBank Influenza Research Dashboard</strong></p>
            <p>Duke Department of Medicine - Center for Infectious Disease Diagnosis Innovation</p>
            <p>Generated on {{ generation_date }}</p>
            <div class="credit">
                <p>✨ Dashboard generated with <a href="https://claude.ai/code" target="_blank">Claude Code</a> with minimal human input</p>
                <p>Data extracted from: <a href="https://medicine.duke.edu/research/research-support-resources/ciddi-biobank" target="_blank">CIDDI BioBank</a></p>
            </div>
        </footer>
    </div>

    <script>
        // Smooth scroll to study card
        function scrollToStudy(studyId) {
            const element = document.getElementById('study-' + studyId);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                // Highlight briefly
                element.style.borderColor = '#667eea';
                element.style.boxShadow = '0 8px 20px rgba(102, 126, 234, 0.3)';
                setTimeout(() => {
                    element.style.borderColor = '';
                    element.style.boxShadow = '';
                }, 2000);
            }
        }

        // Table sorting functionality
        function sortTable(columnIndex) {
            const table = document.getElementById('studyTable');
            const tbody = table.tBodies[0];
            const rows = Array.from(tbody.rows);

            // Determine sort direction
            const currentOrder = tbody.getAttribute('data-sort-order') || 'asc';
            const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
            tbody.setAttribute('data-sort-order', newOrder);

            rows.sort((a, b) => {
                let aVal = a.cells[columnIndex].textContent.trim();
                let bVal = b.cells[columnIndex].textContent.trim();

                // Handle numeric values
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

            // Reorder rows
            rows.forEach(row => tbody.appendChild(row));
        }
    </script>
</body>
</html>
        """

        # Calculate statistics
        stats = self._calculate_statistics()

        # Render template
        template = Template(html_template)
        html_output = template.render(
            studies=self.studies,
            stats=stats,
            generation_date=pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_output)

        print(f"\n✓ Dashboard generated: {output_path}")
        print(f"✓ {len(self.studies)} influenza studies included")
        print(f"✓ Layout: Summary table at top, detailed cards below")

    def _calculate_statistics(self) -> dict:
        """Calculate summary statistics from studies."""
        total_studies = len(self.studies)
        total_subjects = sum(s.get('experimental_design', {}).get('subjects', 0) or 0 for s in self.studies)
        total_samples = sum(
            sum(sample.get('count', 0) for sample in s.get('experimental_design', {}).get('sample_types', []))
            for s in self.studies
        )
        total_publications = sum(len(s.get('publications', [])) for s in self.studies)

        return {
            'total_studies': total_studies,
            'total_subjects': total_subjects,
            'total_samples': f"{total_samples:,}",
            'total_publications': total_publications
        }


def main():
    """Main execution function."""
    print("="*60)
    print("CIDDI BioBank Influenza Dashboard Generator")
    print("="*60)

    # Create dashboard
    generator = DashboardGenerator("output/studies.json")
    generator.generate_dashboard("output/index.html")

    print("\n" + "="*60)
    print("Dashboard created successfully!")
    print("="*60)
    print("\nOpen output/index.html in your browser to view the dashboard.")
    print("\nDashboard features:")
    print("  • Summary table with sortable columns")
    print("  • Quick 'View Details' navigation")
    print("  • Detailed study cards with full information")
    print("  • Publication links and sample breakdowns")


if __name__ == "__main__":
    main()
