#!/usr/bin/env python3
"""
Add user-curated publications from PDFs to the publications CSV
"""

import csv
from pathlib import Path

# Publications from more_pubs_v2.pdf and more_pubs_v3.pdf
NEW_PUBLICATIONS = [
    # From more_pubs_v2.pdf
    {
        'pmid': '35759279',
        'title': 'Wearable sensor-based detection of influenza in presymptomatic and asymptomatic individuals',
        'first_author': 'Temple',
        'journal': 'Journal of Infectious Diseases',
        'year': '2022',
        'pubmed_url': f'https://pubmed.ncbi.nlm.nih.gov/35759279/',
        'biobank_study_code': 'DU08-04',
        'findings_summary': 'In a human H3N2 challenge (n=20), wearable ECG/activity sensors with a trained anomaly-detection algorithm identified 16/17 infected subjects (94%) before symptom onset (mean 23h early). Early alerts were compatible with smartwatch data, supporting wearable early-detection strategies.',
        'authors': 'Temple DS et al.',
        'study_name': 'H3N2 Challenge Study'
    },
    {
        'pmid': '30619110',
        'title': 'A miRNA host response signature accurately discriminates acute respiratory infection etiologies',
        'first_author': 'Poore',
        'journal': 'Frontiers in Microbiology',
        'year': '2018',
        'pubmed_url': f'https://pubmed.ncbi.nlm.nih.gov/30619110/',
        'biobank_study_code': 'DU08-04',
        'findings_summary': 'Blood miRNA signatures were generated from influenza-challenged healthy adults vs. bacterial pneumonia patients. The signature distinguished viral vs. bacterial ARI with high accuracy (mean ~100% healthy vs pneumonia, 91.3% pneumonia vs influenza).',
        'authors': 'Poore GD et al.',
        'study_name': 'H3N2 Challenge Study'
    },
    {
        'pmid': '32979932',
        'title': 'Blood-based host gene expression assay for early detection of respiratory viral infection',
        'first_author': 'McClain',
        'journal': 'Lancet Infectious Diseases',
        'year': '2021',
        'pubmed_url': f'https://pubmed.ncbi.nlm.nih.gov/32979932/',
        'biobank_study_code': 'DU08-04',
        'findings_summary': 'In a prospective index-cluster cohort (n≈1465), a 36-gene blood transcriptomic assay predicted proven viral respiratory infection with AUROC ~0.94 at peak symptoms, and 0.74–0.87 up to 3 days before peak (when many were asymptomatic and not shedding virus).',
        'authors': 'McClain MT et al.',
        'study_name': 'H3N2 Challenge Study'
    },
    {
        'pmid': '28238698',
        'title': 'Nasopharyngeal Protein Biomarkers of Acute Respiratory Virus Infection',
        'first_author': 'Burke',
        'journal': 'EBioMedicine',
        'year': '2017',
        'pubmed_url': f'https://pubmed.ncbi.nlm.nih.gov/28238698/',
        'biobank_study_code': 'DU08-04',
        'findings_summary': 'Unbiased proteomic profiling of nasopharyngeal lavage from human volunteers challenged with influenza A/H3N2 or rhinovirus identified 438 proteins altered by viral infection. A targeted 10-peptide signature classified infected vs. uninfected samples with AUROC = 0.8623, 75% sensitivity, 97.5% specificity.',
        'authors': 'Burke TW, Henao R, et al.',
        'study_name': 'H3N2 Challenge Study'
    },
    {
        'pmid': '40966076',
        'title': 'Innate immune molecular landscape following controlled human influenza virus infection',
        'first_author': 'Thistlethwaite',
        'journal': 'Cell Reports',
        'year': '2025',
        'pubmed_url': f'https://pubmed.ncbi.nlm.nih.gov/40966076/',
        'biobank_study_code': 'DU08-04',
        'findings_summary': 'Multi-omics (RNA-seq, ATAC-seq) on blood from a human H3N2 challenge showed persistent innate immune changes post-infection. Findings included reduced cytokine and AP-1 gene expression and increased interferon-pathway accessibility. Influenza thus "rewires" innate immune chromatin and transcriptional programs.',
        'authors': 'Thistlethwaite W et al.',
        'study_name': 'H3N2 Challenge Study'
    },
    {
        'pmid': '34777354',
        'title': 'The host response to viral infections reveals common and virus-specific signatures',
        'first_author': 'Tsalik',
        'journal': 'Frontiers in Immunology',
        'year': '2021',
        'pubmed_url': f'https://pubmed.ncbi.nlm.nih.gov/34777354/',
        'biobank_study_code': 'DU08-04',
        'findings_summary': 'Blood transcriptomes from 162 patients with viral infections (influenza, rhinovirus, dengue, etc.) showed both shared and unique responses. All viruses triggered interferon pathways; influenza specifically upregulated antiviral defense genes and downregulated T-cell/neutrophil pathways.',
        'authors': 'Tsalik EL et al.',
        'study_name': 'Multiple Studies'
    },
    {
        'pmid': '20622030',
        'title': 'Viral load drives disease in humans experimentally infected with RSV',
        'first_author': 'DeVincenzo',
        'journal': 'American Journal of Respiratory and Critical Care Medicine',
        'year': '2010',
        'pubmed_url': f'https://pubmed.ncbi.nlm.nih.gov/20622030/',
        'biobank_study_code': 'Unknown',
        'findings_summary': 'In a human respiratory syncytial virus (RSV) challenge (n=35 healthy adults), 77% became infected. Viral load peaked in parallel with symptom severity and nasal mucus. Higher RSV RNA levels correlated with higher pro-inflammatory cytokines (IL-6, IL-8) and worse clinical scores.',
        'authors': 'DeVincenzo JP et al.',
        'study_name': 'RSV Challenge Study'
    },
    {
        'pmid': '41127485',
        'title': 'Diverse respiratory viruses detected among hospitalized pneumonia patients in Sri Lanka and Vietnam',
        'first_author': 'Phan',
        'journal': 'IJID Regions',
        'year': '2025',
        'pubmed_url': f'https://pubmed.ncbi.nlm.nih.gov/41127485/',
        'biobank_study_code': 'Unknown',
        'findings_summary': 'Surveillance in 204 Sri Lankan and 197 Vietnamese adults with pneumonia revealed multiple known respiratory viruses including influenza A (H1N1pdm09), RSV-B, rhinovirus, enterovirus, etc. Notably, 43.9% of coronavirus-positive Vietnamese samples were the novel CCoV-HuPn-2018.',
        'authors': 'Phan PT et al.',
        'study_name': 'Pneumonia Surveillance Study'
    },
    {
        'pmid': '36702771',
        'title': 'A Multicenter, Controlled Human Infection Study of Influenza A(H1N1)pdm09 in Healthy Adults',
        'first_author': 'Ortiz',
        'journal': 'Journal of Infectious Diseases',
        'year': '2023',
        'pubmed_url': f'https://pubmed.ncbi.nlm.nih.gov/36702771/',
        'biobank_study_code': 'Unknown',
        'findings_summary': 'In a multicenter H1N1pdm09 challenge trial (NCT04044352), 76 healthy adults received intranasal H1N1pdm09 virus. Overall 54/76 (71.1%) developed "mild-to-moderate influenza disease". Subjects with higher baseline HAI or microneutralization titers (≥40) had lower attack rates.',
        'authors': 'Ortiz JR, Bernstein DI, et al.',
        'study_name': 'H1N1pdm09 Challenge Study'
    },
    # From more_pubs_v3.pdf
    {
        'pmid': 'PMC8482058',
        'title': 'Diagnostic Accuracy of a Host Gene Expression Test in Emergency Department Patients With Suspected COVID-19',
        'first_author': 'Tsalik',
        'journal': 'JAMA Network Open',
        'year': '2021',
        'pubmed_url': f'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8482058/',
        'biobank_study_code': 'Unknown',
        'findings_summary': 'Wearable sensor data and machine learning achieved up to 92% accuracy detecting H1N1 infection and 88% for rhinovirus. Models also predicted disease severity with 90% accuracy prior to symptom onset, demonstrating the feasibility of presymptomatic viral detection using passive biometric monitoring.',
        'authors': 'Tsalik EL et al.',
        'study_name': 'COVID-19 Diagnostic Study'
    },
    {
        'pmid': 'Unknown',
        'title': 'Single-cell genome-wide association reveals that a nonsynonymous variant in ERAP1 confers increased susceptibility to influenza virus',
        'first_author': 'Nedelec',
        'journal': 'Cell Genomics',
        'year': '2022',
        'pubmed_url': '',
        'doi': '10.1016/j.xgen.2022.100207',
        'biobank_study_code': 'Unknown',
        'findings_summary': 'Using single-cell RNA-seq and genome-wide association in infected lymphoblastoid cells, ERAP1 G346D was linked to higher influenza A burden. Functional validation in vitro and in a human challenge confirmed that this variant increased viral replication and worsened symptoms, implicating ERAP1 in host susceptibility.',
        'authors': 'Nedelec et al.',
        'study_name': 'Genetic Susceptibility Study'
    }
]

def main():
    csv_path = Path('data/publications/publications_consolidated.csv')

    # Read existing publications
    existing_pubs = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        existing_pubs = list(reader)

    # Get existing PMIDs to avoid duplicates
    existing_pmids = {pub.get('pmid', '').strip() for pub in existing_pubs if pub.get('pmid')}

    print(f"Existing publications: {len(existing_pubs)}")
    print(f"Existing PMIDs: {len(existing_pmids)}")

    # Add new publications
    added = 0
    for new_pub in NEW_PUBLICATIONS:
        pmid = new_pub['pmid']
        if pmid not in existing_pmids and pmid != 'Unknown':
            # Create row with all fields
            row = {field: '' for field in fieldnames}
            row.update({
                'pmid': new_pub['pmid'],
                'title': new_pub['title'],
                'first_author': new_pub['first_author'],
                'journal': new_pub['journal'],
                'year': new_pub['year'],
                'pubmed_url': new_pub.get('pubmed_url', ''),
                'biobank_study_code': new_pub['biobank_study_code'],
                'findings_summary': new_pub['findings_summary'],
                'source': 'user_curated',
                'authors': new_pub.get('authors', ''),
                'doi': new_pub.get('doi', ''),
                'study_name': new_pub.get('study_name', ''),
                'study_sample_count': 0,
                'study_participant_count': 0,
                'study_sample_types': ''
            })
            existing_pubs.append(row)
            added += 1
            print(f"  + Added: {new_pub['first_author']} et al. ({new_pub['year']}) - PMID: {pmid}")
        else:
            print(f"  - Skipped (duplicate or unknown): {new_pub['first_author']} et al. ({new_pub['year']}) - PMID: {pmid}")

    # Write back to CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_pubs)

    print()
    print(f"✓ Added {added} new publications")
    print(f"✓ Total publications: {len(existing_pubs)}")
    print(f"✓ Updated: {csv_path}")

if __name__ == '__main__':
    main()
