#!/usr/bin/env python3
"""
Agent Data Locator
Searches for missing files and documents data file locations
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import os

def load_gaps_document():
    """Load gaps document to understand what's missing"""
    print("="*80)
    print("AGENT DATA LOCATOR - Analyzing Gaps")
    print("="*80)

    gaps_file = Path('docs/GAPS_AND_FOLLOWUP_QUESTIONS.md')

    if gaps_file.exists():
        print(f"✓ Loaded gaps document: {gaps_file}")
        with open(gaps_file, 'r') as f:
            gaps_content = f.read()
        return gaps_content
    else:
        print(f"⚠️  Gaps document not found at {gaps_file}")
        return None


def search_for_missing_inventory_files():
    """Search for DU19-03 and any other missing inventory files"""
    print("\n" + "="*80)
    print("SEARCHING: Missing Inventory Files")
    print("="*80)

    data_raw = Path('data/raw')
    found_files = []
    missing_files = []

    # Expected studies
    expected_studies = [
        'DU08-04', 'DU09-06', 'DU09-07', 'DU11-02',
        'DU17-04', 'DU20-01', 'DU24-01', 'DU19-03'
    ]

    print(f"\nSearching in: {data_raw.absolute()}")

    # Search for Excel files
    excel_files = list(data_raw.glob('*.xlsx')) + list(data_raw.glob('*.xls'))
    excel_files = [f for f in excel_files if not f.name.startswith('~')]

    print(f"Found {len(excel_files)} Excel files")

    for file in excel_files:
        found_files.append({
            'filename': file.name,
            'path': str(file.absolute()),
            'size_mb': file.stat().st_size / (1024 * 1024),
            'type': 'Excel Inventory'
        })

    # Check which studies have inventory files
    found_study_codes = set()
    for file in excel_files:
        for study in expected_studies:
            if study in file.name:
                found_study_codes.add(study)

    missing_study_codes = set(expected_studies) - found_study_codes

    print(f"\n✓ Found inventory files for: {sorted(found_study_codes)}")

    if len(missing_study_codes) > 0:
        print(f"🔴 Missing inventory files for: {sorted(missing_study_codes)}")
        for study in sorted(missing_study_codes):
            missing_files.append({
                'type': 'Inventory Excel',
                'study_code': study,
                'expected_pattern': f'{study}*.xlsx',
                'status': 'NOT FOUND',
                'impact': 'Critical' if study == 'DU19-03' else 'Medium'
            })
    else:
        print(f"✓ All expected inventory files found")

    return found_files, missing_files


def search_for_sequencing_data():
    """Search for RNA-seq and other sequencing data"""
    print("\n" + "="*80)
    print("SEARCHING: Sequencing Data Files")
    print("="*80)

    search_paths = [
        Path('data'),
        Path('.'),
    ]

    sequencing_patterns = [
        '**/*.fastq', '**/*.fastq.gz', '**/*.fq', '**/*.fq.gz',
        '**/*.bam', '**/*.sam',
        '**/*.vcf', '**/*.vcf.gz',
        '**/counts*.csv', '**/counts*.txt',
        '**/RNA*', '**/rna*',
        '**/Cytokine*', '**/cytokine*'
    ]

    found_seq_files = []
    search_dirs = set()

    print(f"\nSearching for sequencing data patterns...")

    for base_path in search_paths:
        if not base_path.exists():
            continue

        # Limit search depth to avoid performance issues
        for pattern in ['**/*RNA*', '**/*seq*', '**/*FASTQ*']:
            try:
                matches = list(base_path.glob(pattern))[:20]  # Limit results
                for match in matches:
                    if match.is_file() and match.stat().st_size > 1024:  # > 1KB
                        found_seq_files.append({
                            'filename': match.name,
                            'path': str(match.absolute()),
                            'size_mb': match.stat().st_size / (1024 * 1024),
                            'type': 'Sequencing Data (potential)'
                        })
                        search_dirs.add(str(match.parent))
            except PermissionError:
                continue

    if len(found_seq_files) > 0:
        print(f"✓ Found {len(found_seq_files)} potential sequencing data files")
        print(f"  Directories: {len(search_dirs)}")
    else:
        print(f"⚠️  No sequencing data files found in project directory")
        print(f"  → Data may be stored on external servers or different location")

    return found_seq_files


def scan_project_structure():
    """Scan and document complete project file structure"""
    print("\n" + "="*80)
    print("SCANNING: Project File Structure")
    print("="*80)

    base_path = Path('.')
    structure = {
        'data/raw': [],
        'data/processed': [],
        'data/publications': [],
        'data/curated': [],
        'src': [],
        'docs': []
    }

    for key in structure.keys():
        dir_path = Path(key)
        if dir_path.exists():
            files = []
            for item in dir_path.rglob('*'):
                if item.is_file() and not item.name.startswith('.'):
                    files.append({
                        'filename': item.name,
                        'path': str(item.relative_to(base_path)),
                        'size_mb': round(item.stat().st_size / (1024 * 1024), 2),
                        'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
            structure[key] = files
            print(f"  {key}: {len(files)} files")

    return structure


def create_file_manifest():
    """Create comprehensive file manifest"""
    print("\n" + "="*80)
    print("CREATING: Complete File Manifest")
    print("="*80)

    manifest = {
        'metadata': {
            'scan_date': datetime.now().isoformat(),
            'scan_location': str(Path('.').absolute())
        },
        'inventory_files': {
            'found': [],
            'missing': []
        },
        'processed_data': {
            'harmonized': [],
            'linkages': [],
            'validation': []
        },
        'publications': {
            'pdfs': [],
            'citations': []
        },
        'sequencing_data': {
            'found': [],
            'expected_not_found': []
        },
        'scripts': []
    }

    # Inventory files
    data_raw = Path('data/raw')
    if data_raw.exists():
        for f in data_raw.glob('*.xlsx'):
            if not f.name.startswith('~'):
                manifest['inventory_files']['found'].append({
                    'filename': f.name,
                    'path': str(f),
                    'size_mb': f.stat().st_size / (1024 * 1024)
                })

    # Processed data
    processed_dirs = {
        'harmonized': Path('data/processed'),
        'linkages': Path('data/processed/linkages'),
        'validation': Path('data/processed/validation')
    }

    for key, dir_path in processed_dirs.items():
        if dir_path.exists():
            for f in dir_path.glob('*'):
                if f.is_file():
                    manifest['processed_data'][key].append({
                        'filename': f.name,
                        'path': str(f),
                        'size_mb': f.stat().st_size / (1024 * 1024)
                    })

    # Publications
    pub_dir = Path('data/publications')
    if pub_dir.exists():
        pdf_dir = pub_dir / 'pdfs'
        if pdf_dir.exists():
            for f in pdf_dir.glob('*.pdf'):
                manifest['publications']['pdfs'].append({
                    'filename': f.name,
                    'path': str(f),
                    'size_mb': f.stat().st_size / (1024 * 1024)
                })

        for f in pub_dir.glob('*.json'):
            manifest['publications']['citations'].append({
                'filename': f.name,
                'path': str(f),
                'size_kb': f.stat().st_size / 1024
            })

    # Scripts
    src_dir = Path('src/data-munging')
    if src_dir.exists():
        for f in src_dir.glob('*.py'):
            manifest['scripts'].append({
                'filename': f.name,
                'path': str(f),
                'lines': len(open(f).readlines())
            })

    print(f"\n✓ Manifest created:")
    print(f"  • Inventory files found: {len(manifest['inventory_files']['found'])}")
    print(f"  • Processed data files: {sum(len(v) for v in manifest['processed_data'].values())}")
    print(f"  • Publications (PDFs): {len(manifest['publications']['pdfs'])}")
    print(f"  • Scripts: {len(manifest['scripts'])}")

    return manifest


def document_data_access_paths():
    """Create data access guide"""
    print("\n" + "="*80)
    print("DOCUMENTING: Data Access Paths")
    print("="*80)

    access_guide = """# Data Access Guide
**Generated**: {date}

## Available Data

### 1. Sample Inventory
**Location**: `data/processed/combined_inventory_harmonized.parquet`
**Format**: Parquet (compressed)
**Size**: 2.5 MB
**Records**: 84,226 samples across 7 studies
**Access**: Python (pandas), R (arrow), SQL-compatible tools

```python
import pandas as pd
df = pd.read_parquet('data/processed/combined_inventory_harmonized.parquet')
```

### 2. Publication Database
**Location**: `data/publications/citations.json`
**Format**: JSON
**Size**: 219 KB
**Records**: 34 publications with full metadata
**Access**: Any JSON parser

```python
import json
with open('data/publications/citations.json', 'r') as f:
    citations = json.load(f)
```

### 3. Assay Tracking
**Location**: `data/processed/assay_tracking_table.csv`
**Format**: CSV
**Records**: 27 assay records
**Studies**: PROMETHEUS (primary), EXHALE, PRISM, SIGMA Plus

### 4. Data Linkages
**Location**: `data/processed/linkages/`
**Files**:
- `publication_to_study_linkage.csv` - Links publications to studies
- `publication_to_assay_linkage.csv` - Links publications to assays
- `sample_to_publication_linkage.csv` - Maps samples to publications (316K records)
- `multi_use_samples.csv` - Samples used in multiple publications
- `data_provenance_chains.json` - Complete provenance graphs
- `study_cross_reference.csv` - Study-level summary

### 5. Validation Reports
**Location**: `data/processed/validation/`
**Files**:
- `validation_report.json` - Complete validation results
- `data_conflicts.csv` - Identified data conflicts
- `orphaned_records.csv` - Records lacking proper linkages
- `data_quality_metrics.json` - Quality statistics
- `validation_summary.md` - Human-readable summary

## Missing Data

### 🔴 Critical
- **DU19-03 (PRISM Family) Inventory**: Full inventory Excel file not found
  - Impact: 4,996 samples not in harmonized dataset
  - Assay data exists but not linked to sample records

### 🟡 High Priority
- **RNA-seq Data Files**: FASTQ/BAM files for PROMETHEUS not located
  - Assay tracking shows 233 samples sequenced
  - Files may be on external server or Duke cluster

- **Cytokine Data Files**: Measurement files for PROMETHEUS
  - 396 samples with cytokine assays
  - Platform/format unknown

- **Metabolomics Data**: Multiple assay types for PROMETHEUS
  - FIA P180, Oxylipin, Purines/Pyrimidines, HSC
  - File locations not documented

- **Wearable Device Data**: Multiple studies use wearables
  - Empatica, Faros, Garmin, OMED, Reciva devices
  - Data storage location unknown

### 🟢 Medium Priority
- **Older Study Assay Data**: DEE2-5 (2008-2011) assay tracking
  - Publications show extensive molecular profiling
  - Assay tracking files may be in separate system

## External Resources

### Data Repositories (Potential)
- **GEO (Gene Expression Omnibus)**: Check for deposited RNA-seq data
- **SRA (Sequence Read Archive)**: Search for raw sequencing data
- **Duke Research Data Repository**: Internal data storage
- **Collaborator Institutions**: Data may be at partner sites

### Contact Points
- Lab Manager: For missing file locations
- IT/Data Management: For external server access
- PIs: For older study data locations
- Collaborators: For 3rd party transfer data

## Data Access Requirements

### Internal Users
- Network access to Duke systems
- Permissions for data directories
- Python/R environment with appropriate packages

### External Collaborators
- Data sharing agreements may be required
- Restricted access to unpublished data
- Contact PI for collaboration requests

## Notes
- All paths are relative to project root: `{project_root}`
- Parquet files require pandas >= 1.0 or Apache Arrow
- Some data may require decompression (*.gz files)
- Check IRB protocols for data usage restrictions
""".format(date=datetime.now().strftime('%Y-%m-%d'), project_root=Path('.').absolute())

    print("✓ Data access guide created")
    return access_guide


def create_storage_location_map():
    """Map data storage locations"""
    print("\n" + "="*80)
    print("MAPPING: Data Storage Locations")
    print("="*80)

    storage_map = {
        'local_storage': {
            'raw_data': {
                'path': 'data/raw',
                'type': 'Excel inventory files',
                'count': len(list(Path('data/raw').glob('*.xlsx'))) if Path('data/raw').exists() else 0
            },
            'processed_data': {
                'path': 'data/processed',
                'type': 'Harmonized datasets, linkages, validation',
                'size_mb': sum(f.stat().st_size for f in Path('data/processed').rglob('*') if f.is_file()) / (1024 * 1024) if Path('data/processed').exists() else 0
            },
            'publications': {
                'path': 'data/publications',
                'type': 'PDFs and citation database',
                'pdf_count': len(list(Path('data/publications/pdfs').glob('*.pdf'))) if Path('data/publications/pdfs').exists() else 0
            }
        },
        'external_storage': {
            'sequencing_data': {
                'status': 'NOT LOCATED',
                'expected_types': ['FASTQ', 'BAM', 'VCF', 'count matrices'],
                'potential_locations': [
                    'Duke HPC cluster',
                    'Lab network storage',
                    'External collaborator servers',
                    'GEO/SRA repositories'
                ]
            },
            'cytokine_data': {
                'status': 'NOT LOCATED',
                'expected_format': 'Platform-specific (Luminex, ELISA, etc.)',
                'samples': 396
            },
            'metabolomics_data': {
                'status': 'NOT LOCATED',
                'assay_types': ['FIA P180', 'Oxylipin', 'Purines/Pyrimidines', 'HSC'],
                'samples': 547
            },
            'wearable_data': {
                'status': 'NOT LOCATED',
                'device_types': ['Empatica', 'Faros', 'Garmin', 'OMED', 'Reciva'],
                'studies': ['PROMETHEUS', 'EXHALE', 'PRISM', 'SIGMA Plus']
            }
        },
        'missing_critical': {
            'DU19-03_inventory': {
                'status': 'MISSING',
                'expected_file': 'DU19-03*Full Inventory*.xlsx',
                'impact': 'Cannot harmonize 4,996 samples',
                'action': 'Contact lab manager'
            }
        }
    }

    print(f"\n✓ Storage location map created")
    print(f"  • Local storage documented: {len(storage_map['local_storage'])} locations")
    print(f"  • External storage identified: {len(storage_map['external_storage'])} types")
    print(f"  • Missing critical files: {len(storage_map['missing_critical'])}")

    return storage_map


def main():
    """Main execution function"""
    print("="*80)
    print("AGENT DATA LOCATOR")
    print("Searching for missing files and documenting data locations")
    print("="*80)

    output_dir = Path('data/processed/file_locations')
    output_dir.mkdir(exist_ok=True, parents=True)

    # Step 1: Load gaps document
    gaps_content = load_gaps_document()

    # Step 2: Search for missing inventory files
    found_inventory, missing_inventory = search_for_missing_inventory_files()

    # Step 3: Search for sequencing data
    sequencing_files = search_for_sequencing_data()

    # Step 4: Scan project structure
    project_structure = scan_project_structure()

    # Step 5: Create file manifest
    file_manifest = create_file_manifest()

    # Step 6: Document data access paths
    access_guide = document_data_access_paths()

    # Step 7: Create storage location map
    storage_map = create_storage_location_map()

    # Save outputs
    print("\n" + "="*80)
    print("SAVING OUTPUTS")
    print("="*80)

    # Save file manifest
    manifest_output = output_dir / 'file_manifest.json'
    with open(manifest_output, 'w') as f:
        json.dump(file_manifest, f, indent=2, default=str)
    print(f"✓ Saved: {manifest_output}")

    # Save missing files report
    missing_report = {
        'metadata': {
            'scan_date': datetime.now().isoformat(),
            'total_missing': len(missing_inventory)
        },
        'missing_inventory_files': missing_inventory,
        'sequencing_data_status': 'NOT LOCATED' if len(sequencing_files) == 0 else f'{len(sequencing_files)} potential files found',
        'critical_missing': [m for m in missing_inventory if m.get('impact') == 'Critical']
    }

    missing_output = output_dir / 'missing_files_report.csv'
    if len(missing_inventory) > 0:
        pd.DataFrame(missing_inventory).to_csv(missing_output, index=False)
        print(f"✓ Saved: {missing_output}")

    missing_json = output_dir / 'missing_files_report.json'
    with open(missing_json, 'w') as f:
        json.dump(missing_report, f, indent=2)
    print(f"✓ Saved: {missing_json}")

    # Save data access guide
    guide_output = output_dir / 'data_access_guide.md'
    with open(guide_output, 'w') as f:
        f.write(access_guide)
    print(f"✓ Saved: {guide_output}")

    # Save storage locations
    storage_output = output_dir / 'storage_locations.json'
    with open(storage_output, 'w') as f:
        json.dump(storage_map, f, indent=2)
    print(f"✓ Saved: {storage_output}")

    # Save data size inventory
    size_data = []
    for category, files in project_structure.items():
        for f in files:
            size_data.append({
                'category': category,
                'filename': f['filename'],
                'size_mb': f['size_mb'],
                'path': f['path']
            })

    if len(size_data) > 0:
        size_df = pd.DataFrame(size_data)
        size_output = output_dir / 'data_size_inventory.csv'
        size_df.to_csv(size_output, index=False)
        print(f"✓ Saved: {size_output}")

    # Summary report
    print("\n" + "="*80)
    print("DATA LOCATOR SUMMARY")
    print("="*80)

    print(f"\n📁 Files Found:")
    print(f"  • Inventory files: {len(found_inventory)}")
    print(f"  • Processed data files: {sum(len(files) for files in project_structure.values())}")
    print(f"  • Sequencing data files: {len(sequencing_files)}")

    print(f"\n🔴 Files Missing:")
    print(f"  • Critical inventory files: {len([m for m in missing_inventory if m.get('impact') == 'Critical'])}")
    print(f"  • Total missing inventory: {len(missing_inventory)}")

    if len([m for m in missing_inventory if m.get('impact') == 'Critical']) > 0:
        print(f"\n⚠️  Critical Missing Files:")
        for m in [mi for mi in missing_inventory if mi.get('impact') == 'Critical']:
            print(f"  • {m['study_code']}: {m['expected_pattern']}")

    print(f"\n📊 Data Locations:")
    print(f"  • Local storage: {len(storage_map['local_storage'])} locations documented")
    print(f"  • External storage: {len(storage_map['external_storage'])} types identified (not located)")
    print(f"  • Missing critical: {len(storage_map['missing_critical'])} files")

    print(f"\n📄 Output Files:")
    print(f"  • file_manifest.json")
    print(f"  • missing_files_report.json")
    print(f"  • missing_files_report.csv")
    print(f"  • data_access_guide.md")
    print(f"  • storage_locations.json")
    print(f"  • data_size_inventory.csv")

    print("\n" + "="*80)
    print("AGENT DATA LOCATOR COMPLETE")
    print("="*80)

    return {
        'found_inventory': len(found_inventory),
        'missing_inventory': len(missing_inventory),
        'sequencing_files': len(sequencing_files),
        'total_files_cataloged': sum(len(files) for files in project_structure.values())
    }


if __name__ == '__main__':
    main()
