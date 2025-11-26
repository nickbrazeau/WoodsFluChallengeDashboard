# Woods Lab Influenza Challenge Studies Dashboard

A comprehensive web-based dashboard for exploring biological samples, molecular data, and scientific publications from human influenza challenge studies conducted from 2008-2024.

## Dashboard Features

- **Sample Inventory**: Search and filter 82,046 biological samples with advanced filtering and CSV export
- **Study Overview**: Explore 7 challenge studies with detailed statistics and resources
- **Publications**: Browse 31 scientific publications with filtering by study, year, and journal
- **Assay Data**: View molecular assay information and sample counts by assay type
- **About**: Comprehensive documentation and data dictionary

## Quick Start

### View Locally

The dashboard is a static website that can be viewed by opening `index.html` in a web browser.

**Recommended: Use a local web server**

```bash
# Option 1: Python
python3 -m http.server 8000

# Option 2: Node.js
npx serve

# Then open http://localhost:8000 in your browser
```

### File Structure

```
public/
├── index.html              # Landing page
├── samples.html            # Sample inventory
├── studies.html            # Study overview
├── publications.html       # Publications browser
├── assays.html            # Assay data
├── about.html             # Documentation
├── css/
│   └── main.css           # Stylesheet
├── js/
│   └── main.js            # JavaScript utilities
└── data/                  # JSON data files
    ├── samples.json       # 82,046 samples
    ├── publications.json  # 31 publications
    ├── studies.json       # 7 studies
    ├── assays.json        # 27 assay records
    └── *.json            # Statistics and config
```

## Data Updates

To update the dashboard with new data:

1. Update source files in `data/processed/`
2. Run the conversion script:
   ```bash
   python3 src/data-munging/convert_data_for_dashboard.py
   ```
3. This regenerates all JSON files in `public/data/`
4. Refresh the dashboard in your browser

## Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Data Format**: JSON
- **Styling**: Custom CSS with responsive design
- **No Dependencies**: Pure JavaScript, no frameworks required
- **No Backend**: Static files only, can be hosted anywhere

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers

## Data Version

- **Version**: 1.0.0
- **Data Version**: Phase 2 Complete (November 2025)
- **Total Samples**: 82,046
- **Studies**: 7 (DU08-04 through DU24-01)
- **Publications**: 31
- **Last Updated**: November 25, 2025

## Features

### Sample Inventory
- Search by barcode, participant ID, or study code
- Filter by study, sample type, timepoint, and availability
- Sortable columns
- Pagination (50 samples per page)
- Export filtered results to CSV

### Publications Browser
- Filter by study, year, and journal
- View full citations and abstracts
- Links to PubMed where available
- Publication detail modal

### Study Overview
- Study cards with key statistics
- Sample availability and transfer status
- Links to related samples and publications
- Study detail modal with comprehensive information

### Assay Data
- Assay types and sample counts
- Studies with assay data
- Publications using each assay
- Visual breakdown of assays by type

## Development

### Adding New Pages

1. Create HTML file in `public/`
2. Include navigation from existing pages
3. Link to `css/main.css` and `js/main.js`
4. Add to navigation menu in all pages

### Modifying Styles

Edit `public/css/main.css` to change colors, fonts, or layout.

Color palette:
- Primary Blue: #012169
- Royal Blue: #00539B
- Copper: #C84E00
- Persimmon: #E89923
- Eno (Teal): #339898

### Adding Features

JavaScript utilities are available in `public/js/main.js`:
- `formatNumber()` - Format numbers with commas
- `exportTableToCSV()` - Export data to CSV
- `filterData()` - Filter arrays by search term
- `sortData()` - Sort arrays by field
- `createPagination()` - Generate pagination controls

## Known Limitations

- 12 publications need study ID verification
- DU19-03 (PRISM Family) inventory pending
- 216 samples with unusual timepoints under review
- 4,256 samples missing storage location

These will be addressed in future data updates.

## Contact

For sample requests or collaboration inquiries, please contact Woods Lab through official channels.

## License

This dashboard is for research use by Woods Lab and collaborators.
