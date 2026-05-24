# Agent Context: M.Sc Research Analytics

## Project Purpose
This project analyzes M.Sc. research trends (Thesis vs. Non-Thesis) from the Department of Zoology at Jahangirnagar University (1985–2023). It transforms a raw Excel data sheet into a structured analytical report with visualizations.

## Data Pipeline Details
- **Source File:** `M.Sc_thesis_non-thesis_final_data_sheet.xlsx`
- **Primary Script:** `generate_analysis.py`
- **Tech Stack:** Python (Pandas, Matplotlib, Seaborn, Regex)

## Data Cleaning Rules (Domain Logic)
1. **Research Type:** Categorized into `Thesis` or `Non-Thesis`.
2. **Year:** Standardized to academic year ranges (e.g., `YYYY-YYYY`). The `Start_Year` is extracted for chronological plotting.
3. **Publication Status (Fate):** Mapped from raw strings to `Published`, `Unpublished`, `Conference Paper`, `Preprint`, or `Unclear`.
4. **Taxa Mapping:** Groups specific species or orders into broader categories:
   - `Fish` (includes Actinopterygii)
   - `Insects` (includes Diptera, Culicidae)
   - `Mammals (non-primate)` (includes rodents)
   - `Primates`
   - `Ecology & Conservation` (covers biodiversity and management topics)
5. **Geography:** Standardizes district names, with a heavy focus on `Dhaka` (where the university is located).

## Key Metrics
- **Publication Rate:** Calculated as `(Published + Conference Paper) / Resolved Entries`.
- **Duration:** Extracted from "Time Required" column, typically centering around a 12-month cycle.

## Project Structure
- `generate_analysis.py`: Main processing and report generation.
- `inspect_*.py`: Utility scripts for data validation and header checking.
- `msc_thesis_analysis_report.md`: The final generated output.
- `README_STREAMLIT.md`: Instructions for the interactive dashboard.

## Agent Instructions
- When modifying `generate_analysis.py`, ensure that any new taxa or district mappings are added to the corresponding cleaning functions (`map_taxa` or `clean_district`).
- Visualizations should maintain the `whitegrid` theme and use the specific color hex codes (e.g., `#4a90e2` for Thesis) for consistency.
- Paths are currently hardcoded to `D:\data ana\`. If moving to a portable environment, consider using relative paths.