#!/usr/bin/env python3
"""
Agent Data Linker
Creates comprehensive linkages between publications, assay datasets, and sample inventory
to establish complete data provenance chains
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_all_data():
    """Load harmonized inventory, citations, and assay tracking"""
    print("="*80)
    print("AGENT DATA LINKER - Loading Data")
    print("="*80)

    # Load harmonized inventory
    print("\n1. Loading harmonized sample inventory...")
    inventory_df = pd.read_parquet('data/processed/combined_inventory_harmonized.parquet')
    print(f"   ✓ Loaded {len(inventory_df):,} samples from {inventory_df['study_code'].nunique()} studies")

    # Load citations
    print("\n2. Loading citation database...")
    with open('data/publications/citations.json', 'r') as f:
        citations_data = json.load(f)
    publications = citations_data['publications']
    print(f"   ✓ Loaded {len(publications)} publications")

    # Load assay tracking
    print("\n3. Loading assay tracking data...")
    assay_tracking_df = pd.read_csv('data/processed/assay_tracking_table.csv')
    print(f"   ✓ Loaded {len(assay_tracking_df)} assay records")

    with open('data/processed/assay_data_complete.json', 'r') as f:
        assay_data = json.load(f)

    return inventory_df, publications, assay_tracking_df, assay_data


def link_publications_to_studies(publications, inventory_df):
    """Link each publication to the studies it used"""
    print("\n" + "="*80)
    print("LINKING: Publications to Studies")
    print("="*80)

    pub_to_study_links = []

    for pub in publications:
        study_code = pub.get('biobank_study_code', 'Unknown')

        if study_code != 'Unknown':
            # Get sample info for this study
            study_samples = inventory_df[inventory_df['study_code'] == study_code]

            link = {
                'publication_id': pub.get('title', 'Unknown')[:100],
                'pmid': pub.get('pmid', 'N/A'),
                'year': pub.get('year', 'Unknown'),
                'study_code': study_code,
                'study_name': pub.get('study_name', 'Unknown'),
                'total_samples_in_study': len(study_samples),
                'participants_in_study': study_samples['participant_id'].nunique() if len(study_samples) > 0 else 0,
                'sample_types_available': ', '.join(study_samples['sample_type'].dropna().unique()[:10]) if len(study_samples) > 0 else 'N/A'
            }
            pub_to_study_links.append(link)

    pub_study_df = pd.DataFrame(pub_to_study_links)
    print(f"\n✓ Created {len(pub_study_df)} publication-to-study links")

    if len(pub_study_df) > 0:
        print(f"\nPublications by study:")
        print(pub_study_df['study_code'].value_counts().to_string())
    else:
        print("\n⚠️  No publication-to-study links created (all publications may have 'Unknown' study code)")

    return pub_study_df


def link_publications_to_assays(publications, assay_tracking_df):
    """Link publications to specific assays that generated data"""
    print("\n" + "="*80)
    print("LINKING: Publications to Assays")
    print("="*80)

    pub_to_assay_links = []

    for pub in publications:
        study_code = pub.get('biobank_study_code', 'Unknown')

        if study_code != 'Unknown':
            # Find assays performed for this study
            study_assays = assay_tracking_df[assay_tracking_df['biobank_study_code'] == study_code]

            if len(study_assays) > 0:
                for _, assay in study_assays.iterrows():
                    link = {
                        'publication_title': pub.get('title', 'Unknown')[:100],
                        'pmid': pub.get('pmid', 'N/A'),
                        'year': pub.get('year', 'Unknown'),
                        'study_code': study_code,
                        'assay_type': assay['Assay'],
                        'assay_samples': assay['Samples'],
                        'subject_range': assay['Subject ID ranges'],
                        'timepoints': assay['Timepoint(s)'],
                        'data_key': assay['Keys']
                    }
                    pub_to_assay_links.append(link)
            else:
                # No assays found for this study - note it
                link = {
                    'publication_title': pub.get('title', 'Unknown')[:100],
                    'pmid': pub.get('pmid', 'N/A'),
                    'year': pub.get('year', 'Unknown'),
                    'study_code': study_code,
                    'assay_type': 'No assays tracked',
                    'assay_samples': 0,
                    'subject_range': 'N/A',
                    'timepoints': 'N/A',
                    'data_key': 'N/A'
                }
                pub_to_assay_links.append(link)

    pub_assay_df = pd.DataFrame(pub_to_assay_links)
    print(f"\n✓ Created {len(pub_assay_df)} publication-to-assay links")

    # Summary
    if len(pub_assay_df) > 0:
        assays_with_pubs = pub_assay_df[pub_assay_df['assay_type'] != 'No assays tracked']
        print(f"\nPublications with assay data: {len(assays_with_pubs)}")
        print(f"Publications without assay tracking: {len(pub_assay_df[pub_assay_df['assay_type'] == 'No assays tracked'])}")
    else:
        print("\n⚠️  No publication-to-assay links created")

    return pub_assay_df


def create_sample_to_publication_map(inventory_df, publications):
    """Map which samples could have been used in which publications"""
    print("\n" + "="*80)
    print("MAPPING: Samples to Publications")
    print("="*80)

    sample_pub_map = []

    for pub in publications:
        study_code = pub.get('biobank_study_code', 'Unknown')

        if study_code != 'Unknown':
            # Get all samples from this study
            study_samples = inventory_df[inventory_df['study_code'] == study_code]

            for _, sample in study_samples.iterrows():
                mapping = {
                    'sample_barcode_id': sample['sample_barcode_id'],
                    'participant_id': sample['participant_id'],
                    'study_code': study_code,
                    'timepoint_normalized': sample['timepoint_normalized'],
                    'sample_type': sample['sample_type'],
                    'is_available': sample['is_available'],
                    'is_transferred': sample['is_transferred'],
                    'publication_title': pub.get('title', 'Unknown')[:80],
                    'publication_year': pub.get('year', 'Unknown'),
                    'publication_pmid': pub.get('pmid', 'N/A')
                }
                sample_pub_map.append(mapping)

    sample_pub_df = pd.DataFrame(sample_pub_map)
    print(f"\n✓ Created {len(sample_pub_df):,} sample-to-publication potential linkages")

    return sample_pub_df


def identify_multi_use_samples(sample_pub_df):
    """Identify samples that appear in multiple publications"""
    print("\n" + "="*80)
    print("IDENTIFYING: Multi-Use Samples")
    print("="*80)

    # Count publications per sample
    sample_pub_counts = sample_pub_df.groupby('sample_barcode_id').agg({
        'publication_pmid': 'nunique',
        'publication_title': lambda x: ' | '.join(x.unique()[:3]),
        'study_code': 'first',
        'sample_type': 'first',
        'is_transferred': 'first'
    }).reset_index()

    sample_pub_counts.columns = ['sample_barcode_id', 'num_publications', 'publication_titles',
                                   'study_code', 'sample_type', 'is_transferred']

    # Filter to samples in multiple publications
    multi_use = sample_pub_counts[sample_pub_counts['num_publications'] > 1].copy()
    multi_use = multi_use.sort_values('num_publications', ascending=False)

    print(f"\n✓ Found {len(multi_use):,} samples potentially used in multiple publications")

    if len(multi_use) > 0:
        print(f"\nTop multi-use samples:")
        print(multi_use.head(10)[['sample_barcode_id', 'num_publications', 'study_code', 'sample_type']].to_string(index=False))

    return multi_use


def create_provenance_chains(inventory_df, assay_tracking_df, publications):
    """Create complete provenance chains: Collection → Assay → Publication"""
    print("\n" + "="*80)
    print("BUILDING: Data Provenance Chains")
    print("="*80)

    provenance_chains = []

    # For each study with assays
    for study_code in assay_tracking_df['biobank_study_code'].unique():
        study_assays = assay_tracking_df[assay_tracking_df['biobank_study_code'] == study_code]
        study_samples = inventory_df[inventory_df['study_code'] == study_code]
        study_pubs = [p for p in publications if p.get('biobank_study_code') == study_code]

        for _, assay in study_assays.iterrows():
            chain = {
                'study_code': study_code,
                'collection': {
                    'total_samples_collected': len(study_samples),
                    'participants': study_samples['participant_id'].nunique() if len(study_samples) > 0 else 0,
                    'sample_types': list(study_samples['sample_type'].dropna().unique()[:10]) if len(study_samples) > 0 else [],
                    'date_range': f"{study_samples['study_code'].iloc[0]}" if len(study_samples) > 0 else 'Unknown'
                },
                'assay': {
                    'assay_type': assay['Assay'],
                    'samples_assayed': int(assay['Samples']) if pd.notna(assay['Samples']) else 0,
                    'subjects': assay['Subject ID ranges'],
                    'timepoints': assay['Timepoint(s)'],
                    'data_key': assay['Keys']
                },
                'publications': [
                    {
                        'title': p.get('title', 'Unknown')[:80],
                        'year': p.get('year', 'Unknown'),
                        'pmid': p.get('pmid', 'N/A'),
                        'journal': p.get('journal', 'Unknown')
                    }
                    for p in study_pubs
                ],
                'num_publications': len(study_pubs)
            }
            provenance_chains.append(chain)

    print(f"\n✓ Created {len(provenance_chains)} complete provenance chains")

    # Summary statistics
    total_assays = len(provenance_chains)
    assays_with_pubs = sum(1 for c in provenance_chains if c['num_publications'] > 0)

    print(f"\nProvenance Summary:")
    print(f"  • Total assay-to-publication chains: {total_assays}")
    print(f"  • Chains with publications: {assays_with_pubs}")
    print(f"  • Chains without publications: {total_assays - assays_with_pubs}")

    return provenance_chains


def generate_cross_reference_tables(inventory_df, publications, assay_tracking_df):
    """Generate cross-reference tables for dashboard navigation"""
    print("\n" + "="*80)
    print("GENERATING: Cross-Reference Tables")
    print("="*80)

    # Study-level cross-reference
    study_xref = []

    for study_code in inventory_df['study_code'].unique():
        study_samples = inventory_df[inventory_df['study_code'] == study_code]
        study_assays = assay_tracking_df[assay_tracking_df['biobank_study_code'] == study_code]
        study_pubs = [p for p in publications if p.get('biobank_study_code') == study_code]

        xref = {
            'study_code': study_code,
            'total_samples': len(study_samples),
            'participants': study_samples['participant_id'].nunique(),
            'sample_types': study_samples['sample_type'].nunique(),
            'assays_performed': len(study_assays),
            'unique_assay_types': study_assays['Assay'].nunique() if len(study_assays) > 0 else 0,
            'total_assay_samples': study_assays['Samples'].sum() if len(study_assays) > 0 else 0,
            'publications': len(study_pubs),
            'samples_available': (study_samples['is_available'] == True).sum(),
            'samples_transferred': (study_samples['is_transferred'] == True).sum()
        }
        study_xref.append(xref)

    study_xref_df = pd.DataFrame(study_xref)
    print(f"\n✓ Created study-level cross-reference table with {len(study_xref_df)} studies")
    print("\nStudy Cross-Reference:")
    print(study_xref_df.to_string(index=False))

    return study_xref_df


def main():
    """Main execution function"""
    print("="*80)
    print("AGENT DATA LINKER")
    print("Creating comprehensive data linkages and provenance chains")
    print("="*80)

    output_dir = Path('data/processed/linkages')
    output_dir.mkdir(exist_ok=True, parents=True)

    # Step 1: Load all data
    inventory_df, publications, assay_tracking_df, assay_data = load_all_data()

    # Step 2: Link publications to studies
    pub_study_links = link_publications_to_studies(publications, inventory_df)

    # Step 3: Link publications to assays
    pub_assay_links = link_publications_to_assays(publications, assay_tracking_df)

    # Step 4: Map samples to publications
    sample_pub_map = create_sample_to_publication_map(inventory_df, publications)

    # Step 5: Identify multi-use samples
    multi_use_samples = identify_multi_use_samples(sample_pub_map)

    # Step 6: Create provenance chains
    provenance_chains = create_provenance_chains(inventory_df, assay_tracking_df, publications)

    # Step 7: Generate cross-reference tables
    study_xref = generate_cross_reference_tables(inventory_df, publications, assay_tracking_df)

    # Save outputs
    print("\n" + "="*80)
    print("SAVING OUTPUTS")
    print("="*80)

    # Save publication-to-study linkage
    pub_study_output = output_dir / 'publication_to_study_linkage.csv'
    pub_study_links.to_csv(pub_study_output, index=False)
    print(f"✓ Saved: {pub_study_output}")

    # Save publication-to-assay linkage
    pub_assay_output = output_dir / 'publication_to_assay_linkage.csv'
    pub_assay_links.to_csv(pub_assay_output, index=False)
    print(f"✓ Saved: {pub_assay_output}")

    # Save sample-to-publication mapping (sample for large file)
    sample_pub_output = output_dir / 'sample_to_publication_linkage.csv'
    sample_pub_map.to_csv(sample_pub_output, index=False)
    print(f"✓ Saved: {sample_pub_output} ({len(sample_pub_map):,} records)")

    # Save multi-use samples
    multi_use_output = output_dir / 'multi_use_samples.csv'
    multi_use_samples.to_csv(multi_use_output, index=False)
    print(f"✓ Saved: {multi_use_output}")

    # Save provenance chains as JSON
    provenance_output = output_dir / 'data_provenance_chains.json'
    provenance_data = {
        'metadata': {
            'generation_date': datetime.now().isoformat(),
            'total_chains': len(provenance_chains),
            'studies_covered': len(set(c['study_code'] for c in provenance_chains))
        },
        'provenance_chains': provenance_chains
    }
    with open(provenance_output, 'w') as f:
        json.dump(provenance_data, f, indent=2, default=str)
    print(f"✓ Saved: {provenance_output}")

    # Save cross-reference table
    xref_output = output_dir / 'study_cross_reference.csv'
    study_xref.to_csv(xref_output, index=False)
    print(f"✓ Saved: {xref_output}")

    # Save complete linkage data as JSON
    complete_linkage = {
        'metadata': {
            'generation_date': datetime.now().isoformat(),
            'total_samples': len(inventory_df),
            'total_publications': len(publications),
            'total_assays': len(assay_tracking_df),
            'studies': inventory_df['study_code'].nunique()
        },
        'publication_study_links': pub_study_links.to_dict('records'),
        'publication_assay_links': pub_assay_links.to_dict('records'),
        'multi_use_samples_summary': {
            'total_multi_use': len(multi_use_samples),
            'top_samples': multi_use_samples.head(20).to_dict('records')
        },
        'study_cross_reference': study_xref.to_dict('records')
    }

    complete_output = output_dir / 'complete_linkage_data.json'
    with open(complete_output, 'w') as f:
        json.dump(complete_linkage, f, indent=2, default=str)
    print(f"✓ Saved: {complete_output}")

    # Generate summary report
    print("\n" + "="*80)
    print("LINKAGE SUMMARY REPORT")
    print("="*80)

    print(f"\n📊 Data Processed:")
    print(f"  • Total samples: {len(inventory_df):,}")
    print(f"  • Total publications: {len(publications)}")
    print(f"  • Total assay records: {len(assay_tracking_df)}")
    print(f"  • Studies covered: {inventory_df['study_code'].nunique()}")

    print(f"\n🔗 Linkages Created:")
    print(f"  • Publication-to-study links: {len(pub_study_links)}")
    print(f"  • Publication-to-assay links: {len(pub_assay_links)}")
    print(f"  • Sample-to-publication mappings: {len(sample_pub_map):,}")
    print(f"  • Multi-use samples identified: {len(multi_use_samples):,}")
    print(f"  • Provenance chains: {len(provenance_chains)}")

    print(f"\n📁 Output Files:")
    print(f"  • publication_to_study_linkage.csv")
    print(f"  • publication_to_assay_linkage.csv")
    print(f"  • sample_to_publication_linkage.csv")
    print(f"  • multi_use_samples.csv")
    print(f"  • data_provenance_chains.json")
    print(f"  • study_cross_reference.csv")
    print(f"  • complete_linkage_data.json")

    print("\n" + "="*80)
    print("AGENT DATA LINKER COMPLETE")
    print("="*80)

    return {
        'pub_study_links': len(pub_study_links),
        'pub_assay_links': len(pub_assay_links),
        'sample_pub_mappings': len(sample_pub_map),
        'multi_use_samples': len(multi_use_samples),
        'provenance_chains': len(provenance_chains)
    }


if __name__ == '__main__':
    main()
