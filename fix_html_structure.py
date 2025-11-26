#!/usr/bin/env python3
"""
Fix HTML structure for all dashboard pages
- Update navigation order
- Add MIT license footer
- Add last updated date to footer
"""

import re
from pathlib import Path

# New navigation HTML
NEW_NAV = '''            <ul class="nav-links">
                <li><a href="index.html">Home</a></li>
                <li><a href="studies.html">Studies</a></li>
                <li><a href="data-inventory.html">Data Inventory</a></li>
                <li><a href="samples.html">Sample Inventory</a></li>
                <li><a href="publications.html">Publications</a></li>
                <li><a href="about.html">About</a></li>
            </ul>'''

# New footer HTML
NEW_FOOTER = '''    <!-- Footer -->
    <footer>
        <div class="footer-container">
            <p><strong>Woods Lab Influenza Challenge Studies Dashboard</strong></p>
            <p style="font-size: 0.875rem;">Last Updated: <span id="footer-last-updated">Loading...</span></p>
            <p style="font-size: 0.875rem; margin-top: 0.5rem;">
                © 2025 Woods Lab. Released under the <a href="https://opensource.org/licenses/MIT" target="_blank" style="color: var(--royal-blue); text-decoration: underline;">MIT License</a>.
            </p>
            <p style="margin-top: 1rem; font-size: 0.875rem; color: var(--hatteras);">
                For sample requests or collaboration inquiries, please contact the lab.
            </p>
        </div>
    </footer>'''

def fix_html_file(filepath):
    """Fix navigation and footer in an HTML file"""
    print(f"Processing {filepath.name}...")

    with open(filepath, 'r') as f:
        content = f.read()

    # Fix navigation - find <ul class="nav-links"> to </ul>
    nav_pattern = r'<ul class="nav-links">.*?</ul>'
    content = re.sub(nav_pattern, NEW_NAV, content, flags=re.DOTALL)

    # Fix footer - find <!-- Footer --> to </footer>
    footer_pattern = r'<!-- Footer -->.*?</footer>'
    content = re.sub(footer_pattern, NEW_FOOTER, content, flags=re.DOTALL)

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"✓ Fixed {filepath.name}")

def main():
    public_dir = Path('public')
    html_files = ['publications.html', 'samples.html', 'about.html']

    for filename in html_files:
        filepath = public_dir / filename
        if filepath.exists():
            fix_html_file(filepath)
        else:
            print(f"⚠ {filename} not found")

    print("\n✅ All HTML files updated!")

if __name__ == '__main__':
    main()
