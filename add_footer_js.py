#!/usr/bin/env python3
import re

files = [
    'public/publications.html',
    'public/samples.html'
]

footer_js = '''
                // Update footer last updated
                const configResponse = await fetch('data/config.json');
                const config = await configResponse.json();
                const lastUpdated = new Date(config.last_updated);
                document.getElementById('footer-last-updated').textContent = lastUpdated.toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });'''

for filepath in files:
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Add footer JS before } catch in the main load function
    if 'footer-last-updated' not in content:
        # Find the first async function and add it after data loading
        content = re.sub(
            r'(const \w+ = await \w+Response\.json\(\);)',
            r'\1' + footer_js,
            content,
            count=1
        )
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✓ Updated {filepath}")

print("Done!")
