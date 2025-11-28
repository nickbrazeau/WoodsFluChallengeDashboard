#!/usr/bin/env python3
"""
Verify Study IDs from PMIDs
NFB has updated PMIDs - now verify that study assignments are accurate by
fetching publication details from PubMed and checking for study keywords
"""

import json
import time
from pathlib import Path
from datetime import datetime
from Bio import Entrez
import pandas as pd

# Set your email for NCBI
Entrez.email = "woodsdashboard@duke.edu"

# Study keywords for identification
STUDY_KEYWORDS = {
    'DU08-04': ['DEE2', 'H3N2', '2008', 'A/Brisbane/10/2007'],
    'DU09-06': ['DEE3', 'H1N1', '2009', 'A/Brisbane/59/2007', 'pandemic'],
    'DU09-07': ['DEE4', 'H1N1', '2009', 'A/Brisbane/59/2007'],
    'DU11-02': ['DEE5', 'H3N2', '2011', 'A/Victoria/361/2011'],
    'DU17-04': ['PROMETHEUS', 'H1N1', '2017', 'Imperial College London', 'ICL'],
    'DU20-01': ['SIGMA Plus', 'SIGMA+', 'H3N2', '2020'],
    'DU24-01': ['EXHALE', 'H3N2', '2024']
}

def load_citations():
    """Load citations with updated PMIDs"""
    print("="*80)
    print("VERIFYING STUDY IDS FROM PMIDs")
    print("="*80)

    citations_file = Path('data/publications/citations.json')
    with open(citations_file, 'r') as f:
        data = json.load(f)

    publications = data['publications']
    print(f"\nLoaded {len(publications)} publications")

    return publications


def fetch_pubmed_details(pmid):
    """Fetch publication details from PubMed"""
    try:
        # Convert PMID to string and clean
        pmid_str = str(pmid).replace('.0', '').strip()

        if pmid_str == 'nan' or pmid_str == '' or pmid_str == 'N/A':
            return None

        # Fetch from PubMed
        handle = Entrez.efetch(db="pubmed", id=pmid_str, rettype="medline", retmode="text")
        record = handle.read()
        handle.close()

        # Parse key fields
        details = {
            'pmid': pmid_str,
            'title': '',
            'abstract': '',
            'authors': '',
            'journal': '',
            'year': '',
            'keywords': ''
        }

        lines = record.split('\n')
        current_field = None
        for line in lines:
            if line.startswith('TI  - '):
                details['title'] = line[6:]
                current_field = 'title'
            elif line.startswith('AB  - '):
                details['abstract'] = line[6:]
                current_field = 'abstract'
            elif line.startswith('AU  - '):
                if details['authors']:
                    details['authors'] += ', '
                details['authors'] += line[6:]
            elif line.startswith('TA  - '):
                details['journal'] = line[6:]
            elif line.startswith('DP  - '):
                details['year'] = line[6:10]
            elif line.startswith('OT  - '):
                if details['keywords']:
                    details['keywords'] += ', '
                details['keywords'] += line[6:]
            elif current_field == 'title' and line.startswith('      '):
                details['title'] += ' ' + line.strip()
            elif current_field == 'abstract' and line.startswith('      '):
                details['abstract'] += ' ' + line.strip()

        return details

    except Exception as e:
        print(f"  ⚠️  Error fetching PMID {pmid}: {e}")
        return None


def check_study_match(pub_details, assigned_study):
    """Check if publication details match assigned study"""
    if not pub_details:
        return {'confidence': 'unknown', 'reasons': ['No PubMed data available']}

    # Combine searchable text
    search_text = f"{pub_details['title']} {pub_details['abstract']} {pub_details['keywords']}".lower()

    # Check for study keywords
    keywords_found = []
    keywords_expected = STUDY_KEYWORDS.get(assigned_study, [])

    for keyword in keywords_expected:
        if keyword.lower() in search_text:
            keywords_found.append(keyword)

    # Determine confidence
    if len(keywords_found) >= 2:
        confidence = 'high'
    elif len(keywords_found) == 1:
        confidence = 'medium'
    else:
        confidence = 'low'

    # Check if other studies mentioned
    other_studies_mentioned = []
    for study_code, keywords in STUDY_KEYWORDS.items():
        if study_code != assigned_study:
            for keyword in keywords:
                if keyword.lower() in search_text and keyword not in ['h1n1', 'h3n2', '2008', '2009', '2011', '2017', '2020', '2024']:
                    other_studies_mentioned.append(f"{study_code} ({keyword})")

    result = {
        'confidence': confidence,
        'keywords_found': keywords_found,
        'keywords_expected': keywords_expected,
        'match_rate': len(keywords_found) / len(keywords_expected) if keywords_expected else 0,
        'other_studies_mentioned': other_studies_mentioned
    }

    return result


def verify_all_publications(publications):
    """Verify all publications"""
    print("\n" + "="*80)
    print("FETCHING PUBMED DATA AND VERIFYING ASSIGNMENTS")
    print("="*80)

    verification_results = []

    for idx, pub in enumerate(publications, 1):
        print(f"\n{idx}/{len(publications)}: {pub.get('title', 'No title')[:60]}...")

        pmid = pub.get('pmid', 'N/A')
        assigned_study = pub.get('biobank_study_code', 'Unknown')

        print(f"  PMID: {pmid}")
        print(f"  Assigned Study: {assigned_study}")

        # Fetch PubMed details
        if pmid not in ['N/A', 'nan', None, '']:
            pub_details = fetch_pubmed_details(pmid)

            if pub_details:
                # Verify study match
                match_result = check_study_match(pub_details, assigned_study)

                result = {
                    'title': pub.get('title', 'No title')[:100],
                    'pmid': pmid,
                    'assigned_study': assigned_study,
                    'confidence': match_result['confidence'],
                    'keywords_found': ', '.join(match_result['keywords_found']),
                    'keywords_expected': ', '.join(match_result['keywords_expected']),
                    'match_rate': f"{match_result['match_rate']*100:.0f}%",
                    'other_studies_mentioned': ', '.join(match_result['other_studies_mentioned']) if match_result['other_studies_mentioned'] else 'None',
                    'pubmed_title': pub_details['title'],
                    'pubmed_year': pub_details['year'],
                    'notes': ''
                }

                # Add verification notes
                if match_result['confidence'] == 'high':
                    result['notes'] = '✓ Correct assignment (high confidence)'
                    print(f"  ✓ HIGH confidence - {len(match_result['keywords_found'])} keywords matched")
                elif match_result['confidence'] == 'medium':
                    result['notes'] = '⚠️ Check assignment (medium confidence)'
                    print(f"  ⚠️  MEDIUM confidence - {len(match_result['keywords_found'])} keyword matched")
                else:
                    result['notes'] = '🔴 Review assignment (low confidence)'
                    print(f"  🔴 LOW confidence - no clear keywords found")

                if match_result['other_studies_mentioned']:
                    result['notes'] += f" | Other studies mentioned: {match_result['other_studies_mentioned']}"
                    print(f"  ⚠️  Other studies mentioned: {match_result['other_studies_mentioned']}")

            else:
                result = {
                    'title': pub.get('title', 'No title')[:100],
                    'pmid': pmid,
                    'assigned_study': assigned_study,
                    'confidence': 'unknown',
                    'keywords_found': '',
                    'keywords_expected': '',
                    'match_rate': 'N/A',
                    'other_studies_mentioned': '',
                    'pubmed_title': 'Could not fetch',
                    'pubmed_year': '',
                    'notes': 'Could not fetch PubMed data'
                }
                print(f"  ⚠️  Could not fetch PubMed data")

        else:
            result = {
                'title': pub.get('title', 'No title')[:100],
                'pmid': 'N/A',
                'assigned_study': assigned_study,
                'confidence': 'unknown',
                'keywords_found': '',
                'keywords_expected': '',
                'match_rate': 'N/A',
                'other_studies_mentioned': '',
                'pubmed_title': '',
                'pubmed_year': pub.get('year', ''),
                'notes': 'No PMID available'
            }
            print(f"  ⚠️  No PMID available")

        verification_results.append(result)

        # Rate limit - be nice to NCBI
        time.sleep(0.5)

    return verification_results


def generate_verification_report(results):
    """Generate verification report"""
    print("\n" + "="*80)
    print("GENERATING VERIFICATION REPORT")
    print("="*80)

    df = pd.DataFrame(results)

    # Summary statistics
    total = len(df)
    high_conf = len(df[df['confidence'] == 'high'])
    medium_conf = len(df[df['confidence'] == 'medium'])
    low_conf = len(df[df['confidence'] == 'low'])
    unknown = len(df[df['confidence'] == 'unknown'])

    print(f"\n📊 Verification Summary:")
    print(f"  Total publications: {total}")
    print(f"  ✓ High confidence: {high_conf} ({high_conf/total*100:.1f}%)")
    print(f"  ⚠️  Medium confidence: {medium_conf} ({medium_conf/total*100:.1f}%)")
    print(f"  🔴 Low confidence: {low_conf} ({low_conf/total*100:.1f}%)")
    print(f"  ❓ Unknown: {unknown} ({unknown/total*100:.1f}%)")

    # Issues to review
    issues = df[df['confidence'].isin(['low', 'medium'])]
    if len(issues) > 0:
        print(f"\n⚠️  Publications requiring review: {len(issues)}")
        for _, row in issues.iterrows():
            print(f"  • {row['title'][:60]}...")
            print(f"    Assigned: {row['assigned_study']}, Confidence: {row['confidence']}")
            if row['other_studies_mentioned']:
                print(f"    Other studies: {row['other_studies_mentioned']}")

    # Save detailed report
    output_csv = Path('data/curated/corrections/study_id_verification_from_pmids.csv')
    df.to_csv(output_csv, index=False)
    print(f"\n✓ Saved detailed report: {output_csv}")

    # Save summary
    summary = {
        'verification_date': datetime.now().isoformat(),
        'curator': 'NFB',
        'total_publications': total,
        'confidence_breakdown': {
            'high': high_conf,
            'medium': medium_conf,
            'low': low_conf,
            'unknown': unknown
        },
        'issues_to_review': len(issues),
        'publications_needing_review': issues[['title', 'pmid', 'assigned_study', 'confidence', 'notes']].to_dict('records') if len(issues) > 0 else []
    }

    summary_json = Path('data/curated/corrections/study_id_verification_summary.json')
    with open(summary_json, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✓ Saved summary: {summary_json}")

    return df, summary


def create_verification_decisions():
    """Create document for human review of issues"""
    print("\n" + "="*80)
    print("Creating Verification Decisions Template")
    print("="*80)

    template = f"""# Study ID Verification Decisions
**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Task**: Review publications with low/medium confidence study assignments
**Curator**: NFB

## Instructions
For each publication flagged below, review the PubMed details and decide:
1. **Keep** current study assignment (if correct)
2. **Change** to different study (specify which)
3. **Delete** if not relevant to any challenge study

## Publications Requiring Review

Review the detailed CSV: `study_id_verification_from_pmids.csv`

### How to Review:
1. Open CSV and filter for confidence = "medium" or "low"
2. Look up PMID in PubMed to read full abstract
3. Check if keywords match the assigned study
4. Look for mentions of study names (DEE2-5, PROMETHEUS, SIGMA, EXHALE)
5. Make decision below

---

## Decision Template

### Publication 1: [Title]
- **PMID**: [number]
- **Currently Assigned**: DU##-##
- **Confidence**: Low/Medium
- **Issue**: [why flagged]

**Decision**:
- [ ] Keep current assignment (correct)
- [ ] Change to: __________ (specify study code)
- [ ] Delete (not relevant)

**Notes**: _____________________

---

## After Decisions:
1. Update `data/publications/citations.json` with corrected study codes
2. Re-run: `python src/data-munging/agent_data_linker.py`
3. Document changes in this file

---

**Status**: Ready for review
"""

    decisions_file = Path('data/curated/corrections/study_id_verification_decisions.md')
    with open(decisions_file, 'w') as f:
        f.write(template)
    print(f"✓ Created decision template: {decisions_file}")


def main():
    """Main verification function"""
    print("="*80)
    print("STUDY ID VERIFICATION FROM PMIDs")
    print("NFB has updated all PMIDs - verifying study assignments")
    print("="*80)

    # Load citations
    publications = load_citations()

    # Verify all publications
    results = verify_all_publications(publications)

    # Generate report
    df, summary = generate_verification_report(results)

    # Create decisions template
    create_verification_decisions()

    # Final summary
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)

    print(f"\n✓ Verified {len(publications)} publications using PubMed API")
    print(f"✓ High confidence: {summary['confidence_breakdown']['high']}")
    print(f"⚠️  Need review: {summary['issues_to_review']}")

    print("\n📁 Files Created:")
    print("  • study_id_verification_from_pmids.csv - Detailed verification results")
    print("  • study_id_verification_summary.json - Summary statistics")
    print("  • study_id_verification_decisions.md - Template for review decisions")

    print("\n🎯 Next Steps:")
    print("  1. Review study_id_verification_from_pmids.csv")
    print("  2. For publications with low/medium confidence:")
    print("     - Look up PMID in PubMed")
    print("     - Read abstract to verify study assignment")
    print("     - Document decision in study_id_verification_decisions.md")
    print("  3. Update citations.json with any corrections")
    print("  4. Re-run Data Linker if changes made")

    print("\n" + "="*80)


if __name__ == '__main__':
    main()
