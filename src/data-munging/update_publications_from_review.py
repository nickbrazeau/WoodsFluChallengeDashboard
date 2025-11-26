#!/usr/bin/env python3
"""
Update Publications from PDF Review
Extracts publication information from the comprehensive review PDF
and updates citations.json with enriched metadata
"""

import json
import re
from pathlib import Path
from datetime import datetime

# Publication data extracted from the PDF review
PUBLICATIONS_FROM_REVIEW = [
    {
        "pmid": "19664979",
        "title": "Gene Expression Signatures for Diagnosing Viral Infection",
        "first_author": "Zaas",
        "year": "2009",
        "journal": "Cell Host & Microbe",
        "study_question": "Could a host blood gene expression profile be used to reliably detect acute influenza and other respiratory virus infections in humans?",
        "key_findings": "Identified a robust host genomic signature (~30 genes, predominantly interferon-stimulated and inflammation-related) that distinguished symptomatic influenza infection from health. This laid the groundwork for host-based diagnostic tests for influenza.",
        "methods_summary": "Healthy adult volunteers were intranasally inoculated with influenza A (H3N2). Blood samples at multiple time points. Genome-wide expression microarrays analyzed to identify differentially expressed genes.",
        "biobank_study_code": "DU08-04"
    },
    {
        "pmid": "20643599",
        "title": "Statistical Classification of Viral Infection from Gene Expression",
        "first_author": "Chen",
        "year": "2011",
        "journal": "BMC Bioinformatics",
        "study_question": "Can advanced statistical modeling of gene expression improve detection of viral respiratory infections?",
        "key_findings": "Machine-learning classifiers successfully detected viral infections with high accuracy using a relatively small subset of informative genes (a few dozen). Demonstrated transition from broad gene signature discovery to practical automated diagnostic algorithm.",
        "methods_summary": "Applied machine-learning classifiers (sparse logistic regression, support vector machines) to host gene expression data from human challenge studies.",
        "biobank_study_code": "DU08-04"
    },
    {
        "pmid": "21901105",
        "title": "Symptomatic vs. Asymptomatic Influenza Infections – Transcriptional Differences",
        "first_author": "Huang",
        "year": "2011",
        "journal": "PLoS Genetics",
        "study_question": "Why do some people infected with influenza remain asymptomatic while others develop illness?",
        "key_findings": "Symptomatic subjects showed early and robust upregulation of innate immune/inflammatory genes, whereas asymptomatic subjects showed blunted response. Temporal dynamics of host transcriptome correlate with disease expression and can predict clinical outcome.",
        "methods_summary": "Analyzed placebo-controlled influenza A/H3N2 human challenge. Compared peripheral blood transcriptional responses between symptomatic and asymptomatic volunteers.",
        "biobank_study_code": "DU08-04"
    },
    {
        "pmid": "22039424",
        "title": "H3N2 Influenza Infection Elicits More Cross-Reactive and Less Clonally Expanded Anti-Hemagglutinin Antibodies",
        "first_author": "Moody",
        "year": "2011",
        "journal": "PLoS Pathogens",
        "study_question": "How does the human B-cell/antibody response to influenza infection differ from that induced by influenza vaccination?",
        "key_findings": "Natural H3N2 infection elicited antibodies that were more broadly cross-reactive to diverse influenza strains with less clonal focusing, whereas vaccination induced a narrower, more strain-specific antibody response. Infection provides qualitatively different humoral imprint with greater cross-strain reactivity.",
        "methods_summary": "Studied adults challenged with H3N2 versus those receiving trivalent vaccine. Isolated and characterized anti-hemagglutinin antibodies, examining epitope specificity and cross-reactivity.",
        "biobank_study_code": "DU08-04"
    },
    {
        "pmid": "23714753",
        "title": "Comparing Influenza and RSV Viral and Disease Dynamics in Experimentally Infected Adults",
        "first_author": "Bagga",
        "year": "2013",
        "journal": "Journal of Infectious Diseases",
        "study_question": "How do viral load kinetics and symptom dynamics of influenza A compare to RSV in experimentally infected adults?",
        "key_findings": "Influenza had shorter incubation and earlier peak than RSV. Influenza: viral load and symptoms peaked ~2 days post-inoculation, with peak viral load ~9.6 hours before peak symptoms. RSV: peaked around day 5. For both viruses, rise and fall of viral titers closely paralleled symptom progression.",
        "methods_summary": "17 volunteers challenged with H3N2 influenza, 20 with RSV-A. Nasal wash samples taken twice daily for ~7 days for viral load measurement and symptom recording.",
        "biobank_study_code": "DU08-04"
    },
    {
        "pmid": "24048524",
        "title": "RT-PCR Host Gene Signature for Viral Infection",
        "first_author": "Zaas",
        "year": "2013",
        "journal": "Science Translational Medicine",
        "study_question": "Can the complex host gene expression signature of viral infection be translated into a practical clinical test?",
        "key_findings": "Developed rapid RT-PCR assay based on small host gene panel (IFI27, IFIT, TRAIL) that accurately identified acute viral infections. Achieved high sensitivity/specificity distinguishing viral ARIs from bacterial infections. Signal became positive before conventional symptoms fully developed, enabling presymptomatic diagnosis.",
        "methods_summary": "Distilled microarray findings into minimal gene panel. Designed multiplex quantitative RT-PCR assay. Evaluated in independent cohorts including challenge subjects and patients with fever/respiratory symptoms.",
        "biobank_study_code": "DU08-04"
    },
    {
        "pmid": "24140015",
        "title": "Longitudinal Analysis of Leukocyte Differentials in Peripheral Blood",
        "first_author": "McClain",
        "year": "2013",
        "journal": "Open Forum Infectious Diseases",
        "study_question": "Do routine white blood cell differentials change characteristically during influenza infection?",
        "key_findings": "Influenza-infected subjects showed relative lymphopenia and monocytosis during symptomatic phase. L:M ratio fell below 2 at illness peak in 100% of influenza cases. These WBC changes closely mirrored clinical illness course and provide supportive evidence of acute influenza.",
        "methods_summary": "Analyzed daily complete blood count with differentials in volunteers challenged with influenza A/H3N2, rhinovirus, or RSV. Tracked leukocyte subpopulations from pre-inoculation through recovery.",
        "biobank_study_code": "DU08-04"
    },
    {
        "pmid": "24678238",
        "title": "Monitoring Infection via High-Dimensional Genomic Data",
        "first_author": "Carin",
        "year": "2014",
        "journal": "IEEE Signal Processing Magazine",
        "study_question": "How can one harness high-dimensional, longitudinal genomic data to monitor the course of an infection?",
        "key_findings": "Temporal genomic data can be distilled into meaningful trajectories corresponding to infection stages (pre-symptomatic, acute response, recovery). Proper statistical modeling yields intuitive markers of infection progression that could inform monitoring and decision-making.",
        "methods_summary": "Applied advanced statistical signal processing techniques (factor analysis, state-space modeling) to longitudinal gene expression profiles from experimentally inoculated subjects.",
        "biobank_study_code": "DU08-04"
    },
    {
        "pmid": "26193668",
        "title": "Gene Expression Profiles Link Respiratory Viral Infection, Platelet Response to Aspirin, and Acute Myocardial Infarction",
        "first_author": "Rose",
        "year": "2015",
        "journal": "PLoS ONE",
        "study_question": "Does viral infection predispose to myocardial infarction, and through what mechanism?",
        "key_findings": "Individuals with host-virus gene expression signature had double the odds of acute MI (OR ~2.3). Only H1N1 influenza infection significantly increased platelet activation gene signature. Provides mechanistic clue (virus-induced platelet activation) to why influenza can precipitate cardiovascular events.",
        "methods_summary": "Case-control cohort of 594 cardiac patients tested for 11-gene viral signature. Separately, 81 volunteers exposed to viruses (RSV, rhinovirus, H1N1, H3N2) followed longitudinally for 30-gene platelet function signature.",
        "biobank_study_code": "DU09-06"
    },
    {
        "pmid": "26506932",
        "title": "Cytokine Profiles in Symptomatic vs. Asymptomatic Influenza",
        "first_author": "McClain",
        "year": "2016",
        "journal": "PLoS ONE",
        "study_question": "Do baseline or early post-exposure cytokine levels predict who will develop symptoms?",
        "key_findings": "Symptomatic influenza characterized by pronounced early surge in pro-inflammatory cytokines (IL-6, TNF-α, IP-10), whereas asymptomatic infections showed blunted response. Heightened early cytokine responses associated with symptomatic influenza, potentially contributing to immunopathology and symptoms.",
        "methods_summary": "Re-examined 2009 H1N1 challenge data. Measured panel of cytokines/chemokines in serum at multiple timepoints. Compared trajectories between symptomatic and asymptomatic groups.",
        "biobank_study_code": "DU09-06"
    },
    {
        "pmid": "26801061",
        "title": "An Individualized Predictor of Health and Disease Using Paired Reference and Target Samples",
        "first_author": "Liu",
        "year": "2016",
        "journal": "BMC Bioinformatics",
        "study_question": "Can comparing post-exposure gene expression to one's own healthy baseline improve infection prediction accuracy?",
        "key_findings": "Using paired-reference approach boosted prediction accuracy by 14% for H3N2 and 6% for H1N1, while using fewer genes. Each person serves as their own control. Personalized genomic approach improved both sensitivity and specificity of early infection prediction.",
        "methods_summary": "Large-scale analysis of 151 volunteers across seven challenge studies (H1N1, H3N2, RSV, HRV). Applied reference-aided machine learning comparing post-exposure to personal baseline.",
        "biobank_study_code": "DU08-04"
    },
    {
        "pmid": "26933666",
        "title": "A Genomic Signature of Influenza Infection Shows Potential for Presymptomatic Detection, Guiding Early Therapy",
        "first_author": "McClain",
        "year": "2016",
        "journal": "Open Forum Infectious Diseases",
        "study_question": "Could early intervention guided by genomic signature improve outcomes?",
        "key_findings": "Early pre-symptomatic oseltamivir intervention (timed by genomic signature onset at ~36h post-exposure) led to significantly milder illness: less than half symptom burden, recovered 20h faster, reduced viral shedding, lower inflammatory cytokines. Host genomic signature provides actionable window for therapy.",
        "methods_summary": "Used flu challenge trial data and host-virus expression signature. Simulated 'Early Treatment' scenario with antiviral initiated at first genomic signature rather than waiting for clinical symptoms.",
        "biobank_study_code": "DU08-04"
    },
    {
        "pmid": "27707932",
        "title": "Deep Sequencing of Influenza A Virus from a Human Challenge Study Reveals a Selective Bottleneck",
        "first_author": "Sobel Leonard",
        "year": "2016",
        "journal": "Journal of Virology",
        "study_question": "How much does influenza mutate within a single human host, and is there a genetic bottleneck at infection initiation?",
        "key_findings": "Influenza faced selective bottleneck upon infecting humans: cell-culture adaptations were rapidly lost. Non-synonymous variants in key genes (HA, NP) were purged by selection. Within-host evolution dominated by purifying selection rather than generation of new diversity. Tight bottleneck at infection point with genetic stability maintained.",
        "methods_summary": "18 volunteers challenged with H3N2. Next-generation sequencing on viral stock and serial nasal wash samples from 7 infected subjects. Tracked mutation frequencies across 8 genome segments.",
        "biobank_study_code": "DU08-04"
    },
    {
        "pmid": "27885969",
        "title": "IgG2 Levels and Influenza Severity",
        "first_author": "Rodríguez de Castro",
        "year": "2016",
        "journal": "Critical Care (abstract)",
        "study_question": "Are baseline IgG subclass 2 levels linked to severe influenza risk?",
        "key_findings": "Lower IgG2 level did not predispose to more severe influenza outcomes. No significant association found between IgG2 deficiency and flu severity. Other immune factors are more critical in determining flu severity than IgG2.",
        "methods_summary": "Measured serum IgG subclass concentrations and correlated with influenza illness severity. Conference abstract presentation (ISICEM 2016).",
        "biobank_study_code": "DU17-04"
    },
    {
        "pmid": "28170438",
        "title": "The Effective Rate of Influenza Reassortment is Limited During Human Infection",
        "first_author": "Sobel Leonard",
        "year": "2017",
        "journal": "PLOS Pathogens",
        "study_question": "How often does reassortment occur within a single human influenza infection?",
        "key_findings": "Effective reassortment in human hosts is very low. Polymorphisms on different segments tended to remain correlated - original segment combinations preserved. During acute infection, diversity arises through mutations; multiple genotypes rarely swap segments. Spatial/timing factors limit reassortment opportunities.",
        "methods_summary": "Re-analyzed deep sequencing from H3N2 and H1N1 challenge studies. Tracked SNVs on different genome segments and evaluated independence vs. linkage. Estimated effective reassortment rate.",
        "biobank_study_code": "DU08-04"
    },
    {
        "pmid": "28238698",
        "title": "Nasopharyngeal Protein Biomarkers of Acute Respiratory Virus Infection",
        "first_author": "Burke",
        "year": "2017",
        "journal": "EBioMedicine",
        "study_question": "Can we detect viral infection by measuring proteins at the site of infection (nasopharynx)?",
        "key_findings": "Viral infection induced changes in 3,285 peptides (438 unique proteins). Protein signature (complement cascade, acute phase reactants, neutrophil enzymes) achieved ~75% sensitivity and 97% specificity (AUC ~0.86). Nasopharyngeal protein signature enables quick screening and can distinguish viral from bacterial causes.",
        "methods_summary": "Nasopharyngeal lavage samples from H3N2 and rhinovirus challenge trials. High-resolution mass-spectrometry proteomics. Developed diagnostic classifier tested by targeted mass spec in independent cohorts.",
        "biobank_study_code": "DU08-04"
    },
    {
        "pmid": "30356117",
        "title": "A Crowdsourced Analysis to Identify Ab Initio Molecular Signatures Predictive of Susceptibility to Viral Infection",
        "first_author": "Fourati",
        "year": "2018",
        "journal": "Nature Communications",
        "study_question": "Are there pre-infection biomarkers that predict who will get sick when exposed to a virus?",
        "key_findings": "Individual susceptibility to viral infection is predictable from pre-exposure gene expression profiles. Most enriched pathway: heme metabolism - higher expression of hemoglobin/iron regulation genes correlated with greater susceptibility. Baseline erythropoietic/iron-inflammatory state linked to resilience or vulnerability to viral illness.",
        "methods_summary": "DREAM Respiratory Viral Challenge: crowdsourced consortium analyzed 125 subjects from seven challenge studies (4 viruses). Dozens of teams built predictive models using baseline and 24h post-exposure data.",
        "biobank_study_code": "DU09-07"
    },
    {
        "pmid": "30619110",
        "title": "A miRNA Host Response Signature Accurately Discriminates Acute Respiratory Infection Etiologies",
        "first_author": "Poore",
        "year": "2018",
        "journal": "Frontiers in Microbiology",
        "study_question": "Can host microRNAs distinguish viral from bacterial respiratory infection?",
        "key_findings": "Blood miRNA signatures highly accurate: 11 miRNAs perfectly separated bacterial pneumonia from controls (100%). Different miRNA panel differentiated bacterial from viral infection with ~91% accuracy (AUC 0.96). miRNA–mRNA network showed bacterial infection triggers neutrophil activation, viral triggers interferon-mediated response.",
        "methods_summary": "Analyzed blood from 13 symptomatic H3N2-infected subjects and 10 S. pneumoniae pneumonia patients, plus 21 healthy controls. High-throughput sequencing of miRNAs, microarrays of mRNAs. Sparse logistic regression to derive signatures.",
        "biobank_study_code": "DU11-02"
    }
]

def load_current_citations():
    """Load existing citations.json"""
    citations_file = Path('data/publications/citations.json')
    with open(citations_file, 'r') as f:
        return json.load(f)

def update_publication(existing_pub, review_pub):
    """Update an existing publication with enriched data from review"""
    # Add or update fields from the review
    if 'study_question' not in existing_pub or not existing_pub.get('study_question'):
        existing_pub['study_question'] = review_pub.get('study_question', '')

    if 'key_findings' not in existing_pub or not existing_pub.get('key_findings'):
        existing_pub['key_findings'] = review_pub.get('key_findings', '')

    if 'methods_summary' not in existing_pub or not existing_pub.get('methods_summary'):
        existing_pub['methods_summary'] = review_pub.get('methods_summary', '')

    # Update abstract if it's more detailed
    review_abstract = f"{review_pub.get('study_question', '')} {review_pub.get('methods_summary', '')} {review_pub.get('key_findings', '')}"
    existing_abstract = existing_pub.get('abstract', '')
    # Handle case where abstract might be NaN or float
    if not isinstance(existing_abstract, str):
        existing_abstract = ''
    if len(review_abstract) > len(existing_abstract):
        existing_pub['abstract'] = review_abstract

    # Update or add journal if missing
    if not existing_pub.get('journal') or existing_pub.get('journal') == 'Unknown':
        existing_pub['journal'] = review_pub.get('journal', 'Unknown')

    # Mark as enriched from review
    existing_pub['enriched_from_review'] = True
    existing_pub['review_date'] = datetime.now().isoformat()

    return existing_pub

def main():
    print("="*80)
    print("UPDATING PUBLICATIONS FROM COMPREHENSIVE REVIEW")
    print("="*80)

    # Load current citations
    print("\nLoading current citations...")
    citations_data = load_current_citations()
    publications = citations_data['publications']

    print(f"Current publications: {len(publications)}")
    print(f"Publications in review: {len(PUBLICATIONS_FROM_REVIEW)}")

    # Create PMID lookup for existing publications
    pmid_lookup = {}
    for i, pub in enumerate(publications):
        pmid = str(pub.get('pmid', '')).replace('.0', '')
        if pmid:
            pmid_lookup[pmid] = i

    # Update or add publications from review
    updated_count = 0
    added_count = 0

    for review_pub in PUBLICATIONS_FROM_REVIEW:
        pmid = review_pub['pmid']

        if pmid in pmid_lookup:
            # Update existing publication
            idx = pmid_lookup[pmid]
            publications[idx] = update_publication(publications[idx], review_pub)
            updated_count += 1
            print(f"✓ Updated: {review_pub['first_author']} et al. ({review_pub['year']}) - PMID: {pmid}")
        else:
            # Add new publication
            new_pub = {
                'pmid': pmid,
                'title': review_pub['title'],
                'first_author': review_pub['first_author'],
                'journal': review_pub['journal'],
                'year': review_pub['year'],
                'pubmed_url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                'biobank_study_code': review_pub['biobank_study_code'],
                'study_question': review_pub['study_question'],
                'key_findings': review_pub['key_findings'],
                'methods_summary': review_pub['methods_summary'],
                'abstract': f"{review_pub['study_question']} {review_pub['methods_summary']} {review_pub['key_findings']}",
                'enriched_from_review': True,
                'review_date': datetime.now().isoformat(),
                'source': 'Comprehensive Review PDF',
                'retrieved_date': datetime.now().isoformat()
            }
            publications.append(new_pub)
            added_count += 1
            print(f"+ Added: {review_pub['first_author']} et al. ({review_pub['year']}) - PMID: {pmid}")

    # Update metadata
    citations_data['metadata']['total_publications'] = len(publications)
    citations_data['metadata']['last_updated'] = datetime.now().isoformat()
    citations_data['publications'] = publications

    # Backup original
    backup_file = Path('data/publications/citations_backup_pre_review_update.json')
    with open('data/publications/citations.json', 'r') as f:
        with open(backup_file, 'w') as f_backup:
            f_backup.write(f.read())
    print(f"\n✓ Backed up original to: {backup_file}")

    # Save updated citations
    output_file = Path('data/publications/citations.json')
    with open(output_file, 'w') as f:
        json.dump(citations_data, f, indent=2)

    print(f"\n✓ Saved updated citations: {output_file}")
    print(f"\n{'='*80}")
    print("SUMMARY")
    print("="*80)
    print(f"Updated publications: {updated_count}")
    print(f"Added publications: {added_count}")
    print(f"Total publications: {len(publications)}")
    print("\nPublications now include:")
    print("  • Study questions")
    print("  • Key findings")
    print("  • Methods summaries")
    print("  • Enhanced abstracts")
    print("="*80)

if __name__ == '__main__':
    main()
