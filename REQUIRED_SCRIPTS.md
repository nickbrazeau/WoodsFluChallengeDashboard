# Required Scripts for Site Generation

This document lists the essential scripts needed to generate the Woods Lab Influenza Challenge Studies Dashboard from raw data.

## Essential Data Processing Pipeline

These scripts must be run in the specified order to generate the dashboard data files.

### Phase 1: Raw Data Extraction

#### 1. harmonize_metadata.py
**Location:** `src/data-munging/harmonize_metadata.py`
**Purpose:** Extracts and normalizes sample inventory from raw Excel files
**Input:** 8 Excel workbooks in `data/raw/` (24 total sheets)
**Output:**
- `data/processed/combined_inventory_harmonized.parquet` (84K+ samples)
- `data/processed/combined_inventory_harmonized.csv`

```bash
python src/data-munging/harmonize_metadata.py
```

#### 2. process_immuneprofiling.py
**Location:** `src/data-munging/process_immuneprofiling.py`
**Purpose:** Extracts assay tracking data from ImmuneProfiling Excel
**Input:** `data/raw/ImmuneProfiling_cn.xlsx`
**Output:**
- `data/processed/assay_tracking_table.csv` (27 assay records)
- `data/processed/assay_summary_by_study.csv`

```bash
python src/data-munging/process_immuneprofiling.py
```

#### 3. librarian_pubmed_search.py
**Location:** `src/data-munging/librarian_pubmed_search.py`
**Purpose:** Search PubMed for publications and extract metadata
**Input:** PubMed API queries + local PDFs
**Output:** `data/publications/publications_consolidated.csv`

```bash
python src/data-munging/librarian_pubmed_search.py
```

#### 4. regenerate_publications_json.py
**Location:** `src/data-munging/regenerate_publications_json.py`
**Purpose:** Convert publication CSV to structured JSON database
**Input:** `data/publications/publications_consolidated.csv`
**Output:** `data/publications/citations.json` (master publication database)

```bash
python src/data-munging/regenerate_publications_json.py
```

### Phase 2: Data Linking & Validation

#### 5. agent_data_linker.py
**Location:** `src/data-munging/agent_data_linker.py`
**Purpose:** Create bidirectional links between samples, assays, and publications
**Input:**
- `combined_inventory_harmonized.parquet`
- `citations.json`
- `assay_tracking_table.csv`

**Output:**
- `data/processed/linkages/complete_linkage_data.json`
- `data/processed/linkages/sample_to_publication_linkage.csv`
- `data/processed/linkages/study_cross_reference.csv` (REQUIRED by convert_data_for_dashboard.py)
- `data/processed/linkages/data_provenance_chains.json`

```bash
python src/data-munging/agent_data_linker.py
```

#### 6. agent_validator.py
**Location:** `src/data-munging/agent_validator.py`
**Purpose:** Validate data consistency and referential integrity
**Input:** All processed datasets
**Output:**
- `data/processed/validation/validation_report.json`
- `data/processed/validation/data_conflicts.csv`
- `data/processed/validation/orphaned_records.csv`

```bash
python src/data-munging/agent_validator.py
```

### Phase 3: Dashboard Data Generation

#### 7. convert_data_for_dashboard.py ⚠️ CRITICAL
**Location:** `src/data-munging/convert_data_for_dashboard.py`
**Purpose:** Convert processed data to JSON files for web dashboard
**Input:**
- `data/processed/combined_inventory_deduplicated.parquet` (MUST EXIST)
- `data/publications/citations.json`
- `data/processed/assay_tracking_table.csv`
- `data/processed/linkages/study_cross_reference.csv` (REQUIRED)

**Output:** All files in `public/data/`:
- `samples_private.json` (33 MB, 82K records with storage paths)
- `publications.json` (99 KB, 31 publications)
- `assays.json` (7 KB, 27 assay records)
- `studies.json` (2.8 KB, 7 studies)
- `sample_statistics_private.json`
- `publication_statistics.json`
- `assay_statistics.json`
- `config.json` (dashboard configuration)

```bash
python src/data-munging/convert_data_for_dashboard.py
```

**⚠️ CRITICAL:** This script requires `combined_inventory_deduplicated.parquet` to exist. If missing, check if deduplication was run or rename `combined_inventory_harmonized.parquet`.

#### 8. agent_scrubber.py
**Location:** `src/data-munging/agent_scrubber.py`
**Purpose:** Remove PHI (storage locations) to create public-safe versions
**Input:**
- `public/data/samples_private.json`
- `public/data/sample_statistics_private.json`

**Output:**
- `public/data/samples_public.json` (29 MB, storage paths nulled)
- `public/data/sample_statistics_public.json`
- `data/processed/scrubber_audit_log.json`

```bash
python src/data-munging/agent_scrubber.py
```

---

## Optional Maintenance Scripts

These scripts are kept for specific maintenance tasks but are not required for regular site generation.

### fix_study_associations.py
**Purpose:** Correct study code mapping errors when discovered
**Use:** Run when data validation identifies incorrect study associations

### update_publications_from_review.py
**Purpose:** Integrate human-curated publication corrections
**Use:** Run after manual review of publication data

### add_user_curated_publications.py
**Purpose:** Add manually-curated publication entries
**Use:** Run when adding publications not found via PubMed search

### agent_data_locator.py
**Purpose:** Find missing data files and generate documentation
**Use:** Run when documenting data provenance or tracking down files

---

## Quick Start: Full Pipeline

To regenerate all dashboard data from scratch:

```bash
# Phase 1: Extract raw data
python src/data-munging/harmonize_metadata.py
python src/data-munging/process_immuneprofiling.py
python src/data-munging/librarian_pubmed_search.py
python src/data-munging/regenerate_publications_json.py

# Phase 2: Link and validate
python src/data-munging/agent_data_linker.py
python src/data-munging/agent_validator.py

# Phase 3: Generate dashboard files
python src/data-munging/convert_data_for_dashboard.py
python src/data-munging/agent_scrubber.py

# Deploy
git add public/data/*.json
git commit -m "Update dashboard data"
git push origin main
```

---

## Critical Dependencies

### Required Input Files
- `data/raw/*.xlsx` - 8 Excel inventory files
- `data/raw/ImmuneProfiling_cn.xlsx` - Assay tracking
- `data/processed/combined_inventory_deduplicated.parquet` - For dashboard conversion

### Output Files Served to Dashboard
The HTML pages directly load these JSON files:

| File | Size | Loaded By |
|------|------|-----------|
| samples_public.json / samples_private.json | 29-33 MB | samples.html |
| publications.json | 99 KB | publications.html |
| assays.json | 7 KB | assays.html |
| studies.json | 2.8 KB | studies.html, index.html |
| config.json | 1 KB | All pages |
| *_statistics.json | <1 KB each | Various pages |

**Note:** Authentication determines whether `samples_public.json` or `samples_private.json` is loaded (see `public/js/main.js`).

---

## Troubleshooting

### "FileNotFoundError: combined_inventory_deduplicated.parquet"
**Solution:** Either:
1. Run deduplication step (if script exists)
2. Copy/rename `combined_inventory_harmonized.parquet` to `combined_inventory_deduplicated.parquet`

### "Missing study_cross_reference.csv"
**Solution:** Ensure `agent_data_linker.py` completed successfully.

### Empty or missing JSON files in public/data/
**Solution:** Re-run `convert_data_for_dashboard.py` and verify all input files exist.

### Public site shows "Unexpected token '<'" error
**Solution:** JSON files not committed to git. Run:
```bash
git add -f public/data/*.json
git commit -m "Add dashboard data files"
git push origin main
```

---

**Last Updated:** 2025-12-19
**Maintainer:** Woods Lab / Claude Code
