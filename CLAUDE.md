# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a repository to make a Dashboard on all of the historic influenza challenge data collected over the various years at Duke.

### Project Goals

**Primary Objective**: Identify and characterize prior studies and organize data in an interpretable manner with a comprehensive reference dashboard.

### Problem Complexity

There have been numerous influenza challenge studies at Duke that have generated a corpus of data. However, this is across multiple primary investigators, postdocs, graduate students, etc over the past 20 years and has not been systematically cataloged recently. Additionally, new collaborations have waxed/waned at that time with various use of the samples and further generation of novel data. Coalescing this data into a single reference dashboard will be of great utility to ensure optimizing resources and collaboration. 

---

## 🧠 Agents

### Streamlined 9-Agent Workflow

- **Agent Maestro**: Coordinates work across all agents, manages task prioritization, and ensures consistency.

- **Agent Summarizer**: Synthesizes all data connections between influenza studies, collaborators, and data locations. Creates narrative summaries and documentation for dashboard implementation.

- **Agent Data Munger**: Processes all metadata from Excel workbooks, PowerPoint presentations, and emails. Extracts and harmonizes sample inventory, assay tracking, and molecular data (RNA-seq, cytokines, metabolomics, wearables). Key field mappings: External participant = subject ID, Alternate sample ID = unique barcode, Study Code = biobank study ID, Storage status = availability indicator.

- **Agent Web Builder**: Develops dashboard from summarized data. Implements interactive elements, data visualizations, and search functionality. Handles both frontend and backend development.

- **Agent Web Designer**: Focuses on aesthetic appeal and user experience using Duke University's official color palette. Ensures responsive design, accessibility, and Duke branding compliance.

- **Agent Web Code Reviewer**: Reviews code for bugs, discrepancies, and best practices. Validates syntax, logic, and adherence to standards before deployment.

- **Agent Deployer**: Manages deployment pipeline. Handles GitHub Pages setup, version control, testing, and production releases. Ensures smooth transitions between development and live environments.

- **Agent Documentarian**: Maintains comprehensive project documentation. Creates README files, guides for future contributors, and documents data provenance, workflows, and system architecture.

- **Agent Quality Control**: Performs final validation of dashboard functionality. Tests data integrity, visualization accuracy, search features, and cross-browser compatibility before release.

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: [To be determined - React, Vue, or vanilla JS]
- **Visualization**: D3.js, Plotly, or similar for data visualization
- **UI Framework**: Bootstrap, Tailwind, or Material UI for responsive design

### Backend
- **Language**: Python or Node.js for data processing
- **Database**: SQL (PostgreSQL/MySQL) or NoSQL (MongoDB) depending on data structure

### Data Processing
- **Languages**: Python (pandas, openpyxl for Excel processing)
- **Format Standardization**: CSV, JSON for data interchange

---

## 🎨 Design Guidelines



**Primary Colors:**

- **Dark Blue**: #012169 (Primary brand color)
- ** Royal Blue**: #00539B (Secondary brand color)
- **White**: #FFFFFF

**Secondary/Accent Colors:**
- ** Navy**: #001A57
- **Copper**: #C84E00
- **Persimmon**: #E89923
- **Dandelion**: #FFD960
- **Piedmont**: #A1B70D
- **Eno**: #339898
- **Magnolia**: #1D6363
- **Prussian Blue**: #005587
- **Shale Blue**: #0577B1
- **Ironweed**: #993399
- **Hatteras**: #E5E5E5 (Light gray)
- **Whisperwood**: #F3F2ED (Off-white)
- **Graphite**: #666666
- **Cast Iron**: #262626

### Design Principles
- Use Blue (#012169) as the primary color for headers, navigation, and key elements
- Maintain high contrast for accessibility
- Use white space effectively
- Ensure mobile responsiveness

---

## 📁 Project Structure

```
WoodsDashboard/
├── data/               # Raw and processed data files
│   ├── raw/           # Original Excel, PowerPoint, email exports
│   ├── processed/     # Cleaned and standardized datasets
│   ├── curated/       # Human-reviewed and manually added content
│   │   ├── tables/    # Manually provided tables
│   │   ├── figures/   # Manually provided figures and images
│   │   ├── corrections/ # Human corrections to automated extractions
│   │   └── provenance.json # Tracking of all human additions
│   ├── publications/  # Scientific publications using challenge study data
│   │   ├── pubmed_results/ # PubMed search results and metadata
│   │   ├── citations.json  # Citation database with study linkages
│   │   └── pdfs/      # Full-text PDFs (if available)
│   └── metadata/      # Data dictionaries and documentation
├── src/               # Source code
│   ├── components/    # Reusable UI components
│   ├── pages/         # Dashboard pages and views
│   ├── utils/         # Helper functions and utilities
│   └── data-munging/  # Scripts for data processing
├── docs/              # Documentation and reports
├── tests/             # Test files
└── CLAUDE.md          # This file
```

---

## 📊 Data Sources & Model

### Primary Data Types
- **Clinical Trial Data**: Patient demographics, outcomes, treatment protocols
- **Assay Results**: Laboratory test results across multiple assays
- **Sample Metadata**: Sample collection, storage, and usage tracking
- **Collaboration Records**: Cross-institutional data sharing and joint studies
- **Publications**: Scientific literature citing or using challenge study data, tracked via PubMed and other databases

### Source Formats
- Excel workbooks (often with multiple sheets)
- PowerPoint presentations with embedded data
- Email communications with scattered metadata
- Legacy databases and flat files

### Core Data Model & Terminology

**Subject & Sample Identifiers:**
- **External participant**: Study assigned subject ID (links to participant across timepoints)
- **Alternate sample ID**: Unique sample barcode ID for each physical sample unit or aliquot
- **Study Code**: Biobank assigned study ID that corresponds to one challenge study
  - Example: DEE3 = H1N1 challenge study
  - Each study code represents a distinct influenza challenge protocol

**Sample Tracking:**
- **Storage status**: Indicates current sample availability
  - `In circulation`: Sample is available in lab freezers
  - `3rd party transfer`: Sample has been transferred to collaborators or consumed (no longer available)
- **Storage unit**: Hierarchical sample location (freezer → shelf → rack → box → row/col)
- **Label path**: Complete path string for physical sample location

**Temporal Data:**
- **Visit/Timepoint**: Position along longitudinal challenge timeline
  - **Time 0**: Inoculation timepoint (challenge day)
  - **Negative values (e.g., -7, -1)**: Pre-inoculation timepoints
  - **Positive values (e.g., +1, +7, +28)**: Post-inoculation timepoints
  - **IMPORTANT**: Timepoint labeling is inconsistent across studies - requires careful standardization

**Data Standardization Priorities:**
1. Normalize timepoint labels across studies
2. Ensure consistent subject ID tracking
3. Validate sample ID uniqueness
4. Maintain storage location integrity
5. Track all third-party transfers and collaborations

---

## 🚀 Development Workflow

### Phase 1: Data Processing (Maestro + Data Munger + Summarizer)
1. **Data discovery and extraction**
   - Locate all Excel workbooks, metadata files, assay tracking spreadsheets
   - Extract and harmonize sample inventory, assay data, molecular data
   - Normalize timepoints, participant IDs, and storage information
   - Process all data types: RNA-seq, cytokines, metabolomics, wearables

2. **Publication analysis and linkages**
   - Query PubMed for challenge study publications
   - Link publications to specific studies and samples
   - Create citation database with study linkages

3. **Data synthesis**
   - Create narrative summaries of data connections
   - Document data provenance and usage patterns
   - Prepare comprehensive reports for dashboard development

### Phase 2: Dashboard Development (Web Designer + Web Builder)
1. **Design and interface**
   - Create responsive design using Duke color palette
   - Define user flows and navigation
   - Ensure accessibility and mobile compatibility

2. **Implementation**
   - Build interactive visualizations (D3.js, Plotly, Chart.js)
   - Implement search and filter capabilities
   - Add data export functionality
   - Integrate JSON data files

### Phase 3: Quality Assurance (Web Code Reviewer + Quality Control)
1. **Code review**
   - Check syntax, logic, and best practices
   - Validate against standards
   - Ensure cross-browser compatibility

2. **Testing**
   - Test data integrity and visualization accuracy
   - Verify search and filter functionality
   - Check responsive design across devices

### Phase 4: Documentation & Deployment (Documentarian + Deployer)
1. **Documentation**
   - Create README files and guides
   - Document system architecture and workflows
   - Prepare handoff materials for future contributors

2. **Deployment**
   - Configure GitHub Pages
   - Manage version control and releases
   - Monitor production environment

---

## 📝 Coding Standards

- **Documentation**: Comment complex logic, document all data transformations
- **Naming Conventions**: Use clear, descriptive variable and function names
- **Data Provenance**: Always track the source and transformation history of data
- **Version Control**: Commit frequently with descriptive messages
- **Testing**: Write tests for critical data processing functions

---

## 🎯 Key Considerations

- **Data Privacy**: Ensure all patient/participant data is properly de-identified
- **Reproducibility**: Document all data transformations and processing steps
- **Scalability**: Design for potential addition of new studies and data types
- **Collaboration**: Enable multiple researchers to contribute and access data
- **Auditability**: Maintain clear records of who accessed/modified what data and when

