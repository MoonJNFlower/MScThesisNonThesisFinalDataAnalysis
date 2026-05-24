# M.Sc Research Analytics Dashboard

An interactive Streamlit dashboard for analyzing research trends (Thesis vs. Non-Thesis) from the Department of Zoology at Jahangirnagar University (1985–2023).

## Features
- **Interactive Filtering**: Filter by research type, academic year, taxa, publication status, and geographic area.
- **Trend Analysis**: Visualize the annual volume of research over nearly four decades.
- **Taxonomic Breakdown**: Insights into the most studied animal groups.
- **Publication Outcomes**: Track dissemination rates and publication status.
- **Geographic Mapping**: Distribution of study areas across Bangladesh.
- **Automated Reporting**: Generates a static Markdown report with embedded visualizations.

## Installation

> **Note:** The source dataset (`M.Sc_thesis_non-thesis_final_data_sheet.xlsx`) is excluded from this repository for privacy and secrecy. You must provide your own copy of the Excel file in the root directory to use this tool.

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the Dashboard
```bash
streamlit run app.py
```

### Generate Static Report
```bash
python generate_analysis.py
```