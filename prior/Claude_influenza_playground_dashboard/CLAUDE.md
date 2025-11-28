# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This project creates an **interactive dashboard for visualizing the hierarchical structure of prior influenza research work with available CIDDI BioBank data**. The dashboard systematically extracts and organizes influenza study data from the Duke CIDDI BioBank, displaying research aims, experimental designs, sample types, molecular assays, and publications in an accessible format.

### Project Goals

**Primary Objective**: Build a comprehensive dashboard that maps the landscape of influenza research studies with available biobank samples, enabling researchers to:
- Identify relevant influenza studies and available samples
- Understand experimental designs and sample availability
- Access publications and study methodologies
- Compare studies across different influenza strains and experimental approaches

**Target Focus**: Influenza-related research studies, including:
- Influenza challenge studies (H1N1, H3N2, etc.)
- Clinical influenza cohorts
- Experimental inoculation studies
- Vaccine response studies

---

## 🧠 Behavioral Directives

- Prioritize organizing data systematically and clearly
- Focus on influenza-specific datasets and studies
- Prioritize privacy and flag any issues early and often
- Create hierarchical visualizations showing relationships between studies
- Emphasize sample availability and experimental design details

---

## 📁 Repository Structure

```
Claude_playground_dashboard/
├── data/                                    # Source HTML from CIDDI BioBank
├── articles/                                # Downloaded publication PDFs
├── output/                                  # Generated JSON, CSV, and HTML files
│   ├── studies.json                         # Structured influenza study data
│   ├── studies_summary.csv                  # Tabular study summary
│   ├── biodata_matrix.csv                   # Sample/assay availability matrix
│   ├── biodata_matrix.html                  # Standalone biodata visualization
│   ├── research_questions.csv               # Research questions by category
│   ├── pubmed_findings.csv                  # PubMed-scraped findings
│   └── unified_dashboard.html               # Main deliverable (single-page website)
├── extract_studies.py                       # Data extraction (influenza-focused)
├── create_biodata_matrix.py                 # Generate presence/absence matrix
├── scrape_pubmed_abstracts.py               # Fetch findings from PubMed
├── extract_research_questions_from_pdfs.py  # Extract questions from PDFs (optional)
├── generate_unified_dashboard.py            # Main dashboard generator
├── pdf_mapping.json                         # Manual PDF-to-publication mapping
├── run_pipeline.sh                          # Automated pipeline
├── requirements.txt                         # Python dependencies
├── CLAUDE.md                                # This file
└── README.md                                # Project documentation
```

---





## 🔧 Dashboard Design

### Layout Structure

**Top Section**: Summary table displaying all influenza studies in tabular format
- Sortable columns
- Quick overview of all studies at a glance
- Key metrics: subjects, samples, publications
- Active links to publications

**Lower Section**: Detailed study cards
- Expandable detailed information for each study
- Full research aims and experimental design
- Sample type breakdowns
- Complete publication lists with links

### Complete Data Pipeline

The full pipeline extracts and enriches influenza study data:

```
1. Extract Studies (extract_studies.py)
   - Read HTML accordion sections from CIDDI BioBank
   - Filter for influenza-related studies (H1N1, H3N2, etc.)
   - Extract research aims, study type, strain information
   - Parse experimental design: subjects, timepoints, sample types
   - Normalize sample type names (lowercase, collapse whitespace)
   - Extract molecular assays and clinical datasets
   - Parse publications with journal links
   - Output: studies.json, studies_summary.csv

2. Generate Biodata Matrix (create_biodata_matrix.py)
   - Create presence/absence matrix for sample types
   - Map molecular assays to studies
   - Map clinical datasets to studies
   - Generate visual matrix with green ✓/red ✗ indicators
   - Output: biodata_matrix.csv, biodata_matrix.html

3. Scrape PubMed Findings (scrape_pubmed_abstracts.py)
   - Extract PMIDs from publication URLs or search by metadata
   - Fetch structured abstracts from PubMed E-utilities API
   - Parse Methods/Results/Conclusions sections
   - Generate 1-3 sentence summaries of key findings
   - Output: pubmed_findings.csv

4. Generate Unified Dashboard (generate_unified_dashboard.py)
   - Load all data: studies, biodata matrix, research questions, PubMed findings
   - Merge PubMed findings with publications
   - Generate single-page HTML with 4 integrated sections:
     a. Study Overview - sortable summary table
     b. Biodata Availability Matrix - sample/assay presence
     c. Research Questions - categorized by theme with findings
     d. Detailed Study Cards - complete information
   - Output: unified_dashboard.html (main deliverable)
```

## 🏃 Example Data Structure

From a study like this: 

"""

### Influenza H1N1 Challenge

**Research Aims**

Experimental Influenza H1N1 (A/Brisbane/59/2007) challenge study in healthy volunteers. The purpose of this study is to investigate the early pre-symptomatic period following exposure to influenza. Participants were inoculated with H1N1, and dense, longitudinal sample and data collections were performed spanning pre-inoculation baseline through infection and convalescence (2008).

**Experimental Design**

**Subjects:** 31

**Timepoints: 3**

**Sample types:**

- plasma:3864
- serum:1651
- PAXgene RNA:966
- nasal lavage:505
- saliva:830

**Datasets**

**Clinical:** demographics

**Molecular:** viral pathogen testing, Blood RNA microarray, proteomics

 **Publications**

- Fourati et al. [A Crowdsourced Analysis to Identify Ab Initio Molecular Signatures Predictive of Susceptibility to Viral Infection](https://www.nature.com/articles/s41467-018-06735-8). **Nature Communications** (2018)
- Liu et al. [An individualized predictor of health and disease using paired reference and target samples](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4722633/). **BMC Bioinformatics** (2016)
- Rose et al. [Gene Expression Profiles Link Respiratory Viral Infection, Platelet Response to Aspirin, and Acute Myocardial Infarction](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0132259). **PLoS One** (2015)
- Zaas et al. [A Host-Based RT-PCR Gene Expression Signature to Identify Acute Respiratory Viral Infection](https://stm.sciencemag.org/content/5/203/203ra126.long). **Science Translational Medicine** (2013)
- Woods et al. [A Host Transcriptional Signature for Presymptomatic Detection of Infection in Humans Exposed to Influenza H1N1 or H3N2](https://pubmed.ncbi.nlm.nih.gov/24048524/). **PLoS One** (2013)
- Carin et al. [High-Dimensional Longitudinal Genomic Data: An Analysis Used for Monitoring Viral Infections](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3964679/). **IEEE Signal Processing Magazine** (2012)

"""

We should generate this summary table view:

| Study Title | Strain | Study Type | Subjects | Timepoints | Total Samples | Sample Types | Key Assays | Publications |
|-------------|--------|------------|----------|------------|---------------|--------------|------------|--------------|
| Influenza H1N1 Challenge | H1N1 | Challenge/Inoculation | 31 | 3 | 7,816 | plasma, serum, PAXgene RNA, nasal lavage, saliva | Blood RNA microarray, proteomics | 6 publications [link] |

With expandable detailed view below showing:
- Full research aims
- Complete sample breakdown (plasma: 3,864, serum: 1,651, etc.)
- All publication citations with active links
- Molecular assay details

---

## Key Filtering Criteria

**Influenza Study Identification**: Studies must contain one or more of these keywords:
- "Influenza", "H1N1", "H3N2", "H5N1", "flu"
- "Inoculation" or "challenge" with viral context
- Studies explicitly focused on influenza virus

**Non-Influenza Studies**: Exclude studies focused on:
- Other respiratory viruses only (RSV, HRV, coronavirus without flu)
- Bacterial infections only
- Non-respiratory conditions

---

## 📖 Complete Documentation & Usage

### Installation

1. Ensure Python 3.7+ is installed
2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Quick Start - Complete Pipeline

Run the full automated pipeline:
```bash
source venv/bin/activate
python extract_studies.py
python create_biodata_matrix.py
python scrape_pubmed_abstracts.py
python generate_unified_dashboard.py
open output/unified_dashboard.html
```

This will:
1. Extract 6 influenza studies from HTML (filtered from 31 total studies)
2. Generate biodata availability matrix (15 sample types, 8 assays, 4 datasets)
3. Scrape PubMed abstracts and extract key findings (1-3 sentences each)
4. Create unified single-page dashboard with all sections integrated
5. Open dashboard in browser

**Approximate Runtime**: 2-3 minutes (PubMed scraping takes ~30 seconds with rate limiting)

### Manual Workflow

#### Step 1: Extract Influenza Study Data
```bash
source venv/bin/activate
python extract_studies.py
```

**Output**:
- `output/studies.json` - Complete structured data for 6 influenza studies
- `output/studies_summary.csv` - Tabular summary

**Features**:
- Filters for influenza studies (H1N1, H3N2, etc.)
- Excludes 25 non-influenza studies (RSV, HRV, bacterial, etc.)
- Extracts strain information, study type, experimental design
- Normalizes sample type names (lowercase, collapsed whitespace)
- Parses publications with active links

#### Step 2: Generate Biodata Matrix
```bash
python create_biodata_matrix.py
```

**Output**:
- `output/biodata_matrix.csv` - Presence/absence data
- `output/biodata_matrix.html` - Visual matrix with green ✓/red ✗

**Features**:
- 15 unique sample types (plasma, serum, PBMC, nasal lavage, etc.)
- 8 molecular assays (RNA-seq, proteomics, metabolomics, etc.)
- 4 clinical datasets
- Sticky headers for easy navigation

#### Step 3: Scrape PubMed Findings
```bash
python scrape_pubmed_abstracts.py
```

**Output**:
- `output/pubmed_findings.csv` - PMIDs and extracted findings

**Features**:
- Searches PubMed by title/author/year or extracts PMID from URLs
- Fetches structured abstracts via E-utilities API
- Parses Methods/Results/Conclusions sections
- Generates 1-3 sentence summaries
- Success rate: ~33-40% (depends on PMID availability)

#### Step 4: Generate Unified Dashboard
```bash
python generate_unified_dashboard.py
```

**Output**:
- `output/unified_dashboard.html` - Complete single-page website (~103 KB)

**Dashboard Sections**:
1. **Study Overview**: Sortable summary table with key metrics
2. **Biodata Availability Matrix**: Visual presence/absence grid
3. **Research Questions**: 10 categories with PubMed findings
4. **Detailed Study Cards**: Complete study information

**Features**:
- Single HTML file (no external dependencies)
- Smooth scrolling navigation between sections
- PubMed findings displayed in green boxes
- Proper HTML character escaping (all special chars render correctly)
- Mobile-responsive design

#### Step 5: View Dashboard
```bash
open output/unified_dashboard.html  # macOS
xdg-open output/unified_dashboard.html  # Linux
start output/unified_dashboard.html  # Windows
```

### Dashboard Features

**Section 1: Study Overview**
- Sortable summary table (click column headers)
- 6 influenza studies at a glance
- Key metrics: subjects, samples, timepoints, publications
- Quick navigation to detailed cards

**Section 2: Biodata Availability Matrix**
- Visual grid showing sample/assay availability
- Green ✓ for available, red ✗ for not available
- 15 sample types, 8 molecular assays, 4 clinical datasets
- Sticky headers for easy scrolling

**Section 3: Research Questions**
- 10 research question categories
- PubMed-scraped findings (1-3 sentence summaries)
- Green highlighted boxes showing key results
- Organized by theme: Host Gene Expression, Biomarkers, etc.

**Section 4: Detailed Study Cards**
- Full research aims and methodology
- Experimental design breakdown
- Complete sample inventory with counts
- Molecular assays and clinical datasets
- All publications with active journal links

**Interactive Features**:
- Sticky navigation menu for section jumping
- Smooth scrolling between sections
- Hover effects and visual feedback
- Mobile-responsive design
- No external dependencies (works offline)

### Output Files

#### studies.json (22 KB)
Complete structured data with:
- Study ID, title, strain, study type
- Research aims (full text)
- Experimental design (subjects, timepoints, sample types with counts)
- Molecular assays and clinical datasets
- Publications (authors, title, journal, year, URL)

#### studies_summary.csv (7.5 KB)
Tabular format suitable for Excel/R/Python analysis:
- One row per study-sample type combination
- Easy to pivot and analyze
- Includes all key metrics

#### biodata_matrix.csv (1.5 KB)
Presence/absence matrix:
- Rows: 6 influenza studies
- Columns: 15 sample types, 8 assays, 4 datasets
- Values: 1 (present) or 0 (absent)

#### pubmed_findings.csv (12 KB)
PubMed-scraped data:
- 33 publications with metadata
- 11 with extracted findings summaries
- PMIDs for linking to PubMed
- Study associations

#### unified_dashboard.html (103 KB)
**Main deliverable** - standalone HTML dashboard:
- Single file with no external dependencies
- Works offline
- Mobile-responsive
- 4 integrated sections with navigation
- PubMed findings displayed
- Beautiful gradient design
- Proper character encoding

### Customization

#### Modify Influenza Filtering

Edit `extract_studies.py` line 80-87 to change influenza keywords:
```python
influenza_keywords = [
    'influenza', 'h1n1', 'h3n2', 'h5n1', 'h7n9',
    'flu virus', 'flu challenge'
]
```

#### Modify Dashboard Appearance

Edit `generate_dashboard.py` CSS section (lines 35-499) to:
- Change color scheme
- Modify layout grid
- Customize fonts and spacing
- Add new visualizations

#### Add New Data Fields

1. Edit `extract_studies.py` to extract new fields
2. Update `generate_dashboard.py` template to display them
3. Re-run pipeline

### Data Privacy & Ethics

This project processes **publicly available research study summaries only**. No patient data, protected health information (PHI), or individually identifiable information is processed. The system extracts:
- Study metadata and descriptions
- Aggregate statistics (subject counts, sample counts)
- Published research citations (publicly available)
- Experimental protocols (publicly documented)

All data is sourced from the public CIDDI BioBank website and manifests.

### Troubleshooting

**Virtual Environment Issues:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Missing Dependencies:**
```bash
pip install beautifulsoup4 pandas lxml jinja2
```

**HTML File Not Found:**
Ensure the HTML file exists at:
```
data/CIDDI BioBank _ Duke Department of Medicine.html
```

**No Influenza Studies Found:**
Check filtering logic in `extract_studies.py` `_is_influenza_study()` method.

---

## 🎯 Project Goals Achieved

✅ **Unified Single-Page Dashboard**: 4 integrated sections with navigation
✅ **Influenza Focus**: 6 influenza studies filtered from 31 total (H1N1, H3N2)
✅ **Biodata Availability Matrix**: 15 sample types, 8 assays, 4 datasets visualized
✅ **PubMed Integration**: Key findings scraped from abstracts (1-3 sentences)
✅ **Research Questions**: 10 categories mapped to publications
✅ **Interactive Features**: Sortable tables, smooth scrolling, sticky navigation
✅ **Complete Information**: Research aims, sample availability, findings, publications
✅ **Beautiful Design**: Modern gradient UI, mobile-responsive, proper encoding
✅ **Offline Capable**: Single 103 KB HTML file, no external dependencies

## 📊 Key Statistics

- **Studies**: 6 influenza studies (from 31 total CIDDI studies)
- **Subjects**: 412 total participants across all studies
- **Samples**: 52,859 biological samples catalogued
- **Publications**: 33 publications mapped to studies
- **PubMed Findings**: 11 summaries extracted (33% success rate)
- **Sample Types**: 15 unique types (plasma, serum, PBMC, nasal lavage, etc.)
- **Molecular Assays**: 8 unique assays (RNA-seq, proteomics, etc.)
- **Clinical Datasets**: 4 types of clinical data collected
- **Research Categories**: 10 major research question themes identified

---

## 🙏 Credits

**This dashboard was generated with [Claude Code](https://claude.ai/code) with minimal human input.**

- **AI Assistant**: Claude (Anthropic) via Claude Code
- **Human Input**: Project specification and design preferences
- **Data Source**: [CIDDI BioBank](https://medicine.duke.edu/research/research-support-resources/ciddi-biobank), Duke Department of Medicine, Precision Genomics Collaboratory
- **Technologies**: Python, BeautifulSoup, Pandas, Jinja2, HTML/CSS/JavaScript
- **License**: Educational and research purposes

**Workflow:**
1. Human provided: project goals, layout preferences, influenza focus
2. Claude designed and implemented: data extraction, filtering logic, dashboard generation
3. Claude created: all Python code, HTML/CSS, documentation

The entire codebase, from data extraction to dashboard visualization, was written by Claude with minimal human guidance beyond high-level requirements.

---



---