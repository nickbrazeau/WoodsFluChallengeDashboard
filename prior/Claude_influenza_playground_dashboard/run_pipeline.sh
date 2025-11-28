#!/bin/bash
# CIDDI BioBank Dashboard Pipeline
# Complete automation script for unified dashboard generation

set -e  # Exit on error

echo "============================================================"
echo "CIDDI BioBank Influenza Research Dashboard Pipeline"
echo "============================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create output directory
echo "Creating output directory..."
mkdir -p output

# Step 1: Extract study data
echo ""
echo "Step 1/4: Extracting influenza study data from HTML..."
python extract_studies.py

# Step 2: Generate biodata matrix
echo ""
echo "Step 2/4: Generating biodata availability matrix..."
python create_biodata_matrix.py

# Step 3: Scrape PubMed abstracts
echo ""
echo "Step 3/4: Scraping PubMed abstracts for key findings..."
echo "  (This may take 30-60 seconds with API rate limiting)"
python scrape_pubmed_abstracts.py

# Step 4: Generate unified dashboard
echo ""
echo "Step 4/4: Generating unified single-page dashboard..."
python generate_unified_dashboard.py

# Summary
echo ""
echo "============================================================"
echo "Pipeline Complete!"
echo "============================================================"
echo ""
echo "Generated files:"
echo "  - output/studies.json                (Structured study data)"
echo "  - output/studies_summary.csv         (Tabular summary)"
echo "  - output/biodata_matrix.csv          (Sample/assay availability)"
echo "  - output/biodata_matrix.html         (Visual matrix)"
echo "  - output/pubmed_findings.csv         (PubMed findings)"
echo "  - output/unified_dashboard.html      (Main deliverable ⭐)"
echo ""
echo "Opening dashboard in browser..."

# Open dashboard (cross-platform)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open output/unified_dashboard.html
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open output/unified_dashboard.html
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    start output/unified_dashboard.html
else
    echo "Please open output/unified_dashboard.html in your browser"
fi

echo ""
echo "Dashboard available at: $(pwd)/output/unified_dashboard.html"
echo ""
