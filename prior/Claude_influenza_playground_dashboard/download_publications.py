#!/usr/bin/env python3
"""
Download Publications from Influenza Studies

Attempts to download all publications from the influenza studies.
Tracks which publications are successfully downloaded vs behind paywalls.
"""

import json
import requests
import time
from pathlib import Path
from urllib.parse import urlparse
import re


def sanitize_filename(title: str, first_author: str, year: str) -> str:
    """Create a safe filename from publication info."""
    # Remove special characters
    safe_title = re.sub(r'[^\w\s-]', '', title)
    safe_title = re.sub(r'[-\s]+', '_', safe_title)
    safe_author = re.sub(r'[^\w\s-]', '', first_author)

    # Truncate if too long
    if len(safe_title) > 100:
        safe_title = safe_title[:100]

    return f"{safe_author}_{year}_{safe_title}.pdf"


def download_publication(url: str, output_path: Path) -> dict:
    """
    Attempt to download a publication.
    Returns dict with status info.
    """
    result = {
        'url': url,
        'success': False,
        'status': 'pending',
        'message': '',
        'file_path': None
    }

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        result['status_code'] = response.status_code

        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()

            # Check if it's actually a PDF
            if 'application/pdf' in content_type or response.content[:4] == b'%PDF':
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                result['success'] = True
                result['status'] = 'downloaded'
                result['message'] = 'Successfully downloaded PDF'
                result['file_path'] = str(output_path)
            else:
                # It's an HTML page (likely abstract or paywall)
                result['status'] = 'paywall_or_abstract'
                result['message'] = f'Not a PDF (content-type: {content_type}). Likely behind paywall or abstract page.'

                # Check for common paywall indicators
                html_content = response.text.lower()
                if any(keyword in html_content for keyword in ['subscribe', 'purchase', 'access', 'paywall', 'login']):
                    result['message'] += ' Paywall detected.'
        else:
            result['status'] = 'error'
            result['message'] = f'HTTP {response.status_code}'

    except requests.exceptions.Timeout:
        result['status'] = 'timeout'
        result['message'] = 'Request timed out'
    except requests.exceptions.RequestException as e:
        result['status'] = 'error'
        result['message'] = str(e)
    except Exception as e:
        result['status'] = 'error'
        result['message'] = f'Unexpected error: {str(e)}'

    return result


def main():
    """Download all publications from studies."""
    print("="*70)
    print("Publication Downloader for Influenza Studies")
    print("="*70)

    # Create articles directory
    articles_dir = Path("articles")
    articles_dir.mkdir(exist_ok=True)
    print(f"\n📁 Created directory: {articles_dir}")

    # Load studies
    with open("output/studies.json", 'r') as f:
        studies = json.load(f)

    # Collect all publications
    all_publications = []
    for study in studies:
        study_id = study['id']
        study_title = study['title']
        for pub in study['publications']:
            pub_info = pub.copy()
            pub_info['study_id'] = study_id
            pub_info['study_title'] = study_title
            all_publications.append(pub_info)

    print(f"\n📚 Found {len(all_publications)} publications across {len(studies)} studies")
    print(f"\nAttempting to download publications...")
    print("-"*70)

    results = []
    downloaded_count = 0
    paywall_count = 0
    error_count = 0

    for i, pub in enumerate(all_publications, 1):
        print(f"\n[{i}/{len(all_publications)}] {pub['first_author']} et al. ({pub['year']})")
        print(f"    {pub['title'][:80]}...")
        print(f"    URL: {pub['url']}")

        # Create filename
        filename = sanitize_filename(
            pub['title'],
            pub['first_author'],
            pub['year']
        )
        output_path = articles_dir / filename

        # Attempt download
        result = download_publication(pub['url'], output_path)
        result['publication'] = pub
        results.append(result)

        # Print result
        if result['success']:
            print(f"    ✅ {result['message']}")
            downloaded_count += 1
        elif result['status'] == 'paywall_or_abstract':
            print(f"    🔒 {result['message']}")
            paywall_count += 1
        else:
            print(f"    ❌ {result['message']}")
            error_count += 1

        # Be nice to servers
        time.sleep(2)

    # Summary
    print("\n" + "="*70)
    print("Download Summary")
    print("="*70)
    print(f"\n✅ Successfully downloaded: {downloaded_count}")
    print(f"🔒 Behind paywall or abstract page: {paywall_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Total publications: {len(all_publications)}")

    # Save detailed report
    report_path = articles_dir / "download_report.json"
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Detailed report saved: {report_path}")

    # Create summary report
    print("\n" + "="*70)
    print("Publications Behind Paywalls:")
    print("="*70)
    for result in results:
        if result['status'] == 'paywall_or_abstract':
            pub = result['publication']
            print(f"\n• {pub['first_author']} et al. ({pub['year']})")
            print(f"  {pub['title']}")
            print(f"  Journal: {pub['journal']}")
            print(f"  URL: {pub['url']}")
            print(f"  Study: {pub['study_title']}")

    print("\n" + "="*70)
    print("Successfully Downloaded Publications:")
    print("="*70)
    for result in results:
        if result['success']:
            pub = result['publication']
            print(f"\n✓ {Path(result['file_path']).name}")
            print(f"  {pub['first_author']} et al. ({pub['year']})")
            print(f"  Study: {pub['study_title']}")


if __name__ == "__main__":
    main()
