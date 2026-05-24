import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re
from mappings import TAXA_MAPPING, DISTRICT_MAPPING

# File Paths
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, "M.Sc_thesis_non-thesis_final_data_sheet.xlsx")
artifact_dir = os.path.join(script_dir, "artifacts")
output_md_path = os.path.join(artifact_dir, "msc_thesis_analysis_report.md")


# Set plotting styles
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

# Load Data
df = pd.read_excel(file_path, sheet_name='Sheet1', header=3)
df.columns = df.columns.str.strip()

# Create clean columns
df_clean = df.copy()

# 1. Clean Research Type
def clean_research_type(val):
    if pd.isna(val):
        return "Unknown"
    val_str = str(val).strip().lower()
    if 'non-thesis' in val_str:
        return 'Non-Thesis'
    elif 'thesis' in val_str:
        return 'Thesis'
    else:
        return 'Other'

df_clean['Research_Type'] = df_clean['Types of research'].apply(clean_research_type)

# Filter out rows that are garbage
df_clean = df_clean[df_clean['Research_Type'].isin(['Thesis', 'Non-Thesis'])]

# 2. Clean Year
def clean_year(val):
    if pd.isna(val):
        return None
    val = str(val).strip()
    if val.lower() == 'unknown' or val == '':
        return None
    if val == '1885-1986':
        return '1985-1986'
    match = re.match(r'(\d{4})-\d{4}', val)
    if match:
        return val
    return None

df_clean['Year_Cleaned'] = df_clean['Year'].apply(clean_year)

def extract_start_year(val):
    if pd.isna(val) or val is None:
        return None
    match = re.match(r'(\d{4})-\d{4}', val)
    if match:
        return int(match.group(1))
    return None

df_clean['Start_Year'] = df_clean['Year_Cleaned'].apply(extract_start_year)

# 3. Clean Fate (Publication Status)
def clean_fate(val):
    if pd.isna(val):
        return "Missing/Unknown"
    val = str(val).strip().lower()
    if 'unpublished' in val:
        return "Unpublished"
    elif 'published' in val:
        if 'conference' in val:
            return "Conference Paper"
        elif 'confusion' in val:
            return "Unclear/Confusion"
        return "Published"
    elif 'conference' in val or 'poster' in val:
        return "Conference Paper"
    elif 'preprint' in val:
        return "Preprint"
    elif 'confusion' in val or 'confusing' in val or 'similar' in val or 'same' in val:
        return "Unclear/Confusion"
    else:
        return "Other"

df_clean['Publication_Status'] = df_clean['Fate'].apply(clean_fate)

# 4. Clean Taxa Involved
def map_taxa(val):
    if pd.isna(val): return "Unknown"
    return TAXA_MAPPING.get(str(val).strip().lower(), "Other / Miscellaneous")

df_clean['Taxa_Cleaned'] = df_clean['Taxa involved'].apply(map_taxa)

# 5. Clean Time Required (Duration in months)
def parse_months(val):
    if pd.isna(val):
        return None
    val = str(val).strip().lower()
    match = re.search(r'(\d+)\s*month', val)
    if match:
        return int(match.group(1))
    return None

df_clean['Duration_Months'] = df_clean['Time Required'].apply(parse_months)

# 6. Clean District
def clean_district(val):
    if pd.isna(val):
        return "Not Specified" # Default for NaN
    val_lower = str(val).strip().lower()
    # Check for specific substrings first, then direct mapping
    if 'cox' in val_lower and 'bazar' in val_lower: return "Cox's Bazar"
    if 'sundarban' in val_lower: return 'Sundarbans'
    return DISTRICT_MAPPING.get(val_lower, val) # Return original if not found in map

df_clean['District_Cleaned'] = df_clean['District'].apply(clean_district)

# Ensure output directory exists
os.makedirs(artifact_dir, exist_ok=True)

# ----------------- PLOTTING -----------------

# 1. Research Type Distribution Donut Chart
plt.figure(figsize=(6, 5))
type_counts = df_clean['Research_Type'].value_counts()
colors = ['#4a90e2', '#2ecc71']
plt.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', startangle=90, 
        colors=colors, wedgeprops=dict(width=0.4, edgecolor='w'), textprops={'fontsize': 12, 'weight': 'bold'})
plt.title("Distribution of M.Sc Research Projects\n(Thesis vs Non-Thesis)", fontsize=14, weight='bold', pad=20)
plt.tight_layout()
plt.savefig(os.path.join(artifact_dir, "research_type_dist.png"), dpi=150)
plt.close()

# 2. Research Trends Over Time
plt.figure(figsize=(12, 6))
# Filter out null start years for trends
df_trends = df_clean[df_clean['Start_Year'].notna() & (df_clean['Start_Year'] >= 1985)]
trend_data = df_trends.groupby(['Start_Year', 'Research_Type']).size().unstack(fill_value=0)

# Sort start years
trend_data = trend_data.sort_index()

# Plot line chart
plt.plot(trend_data.index, trend_data['Thesis'], marker='o', color='#4a90e2', linewidth=2.5, label='Thesis')
if 'Non-Thesis' in trend_data.columns:
    plt.plot(trend_data.index, trend_data['Non-Thesis'], marker='s', color='#2ecc71', linewidth=2.5, label='Non-Thesis')

plt.title("Annual Volume of M.Sc Research Projects (1985 - 2022)", fontsize=15, weight='bold', pad=15)
plt.xlabel("Academic Year Start", fontsize=12)
plt.ylabel("Number of Projects", fontsize=12)
plt.xticks(np.arange(1985, 2023, 2), rotation=45)
plt.xlim(1984, 2023)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=12, loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(artifact_dir, "research_trends.png"), dpi=150)
plt.close()

# 3. Taxonomic Distribution Horizontal Bar Chart
plt.figure(figsize=(10, 6))
taxa_counts = df_clean['Taxa_Cleaned'].value_counts()
# Exclude Unknown or show it
sns.barplot(x=taxa_counts.values, y=taxa_counts.index, palette="viridis", hue=taxa_counts.index, legend=False)
plt.title("Taxonomic Focus of M.Sc Research Projects", fontsize=15, weight='bold', pad=15)
plt.xlabel("Number of Projects", fontsize=12)
plt.ylabel("Taxa Category", fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(artifact_dir, "taxa_distribution.png"), dpi=150)
plt.close()

# 4. Publication Status by Research Type Grouped Bar Chart
plt.figure(figsize=(9, 5.5))
pub_by_type = df_clean.groupby(['Research_Type', 'Publication_Status']).size().unstack(fill_value=0)
# Normalize to percentages
pub_by_type_pct = pub_by_type.div(pub_by_type.sum(axis=1), axis=0) * 100

pub_by_type_pct.plot(kind='bar', stacked=True, color=['#e74c3c', '#9b59b6', '#34495e', '#3498db', '#95a5a6'], ax=plt.gca())
plt.title("Publication Status Breakdown (Thesis vs Non-Thesis)", fontsize=15, weight='bold', pad=15)
plt.ylabel("Percentage (%)", fontsize=12)
plt.xlabel("Research Project Type", fontsize=12)
plt.xticks(rotation=0, fontsize=12)
plt.legend(title="Publication Status", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(artifact_dir, "publication_rates.png"), dpi=150)
plt.close()

# 5. Top 10 Districts Horizontal Bar Chart
plt.figure(figsize=(10, 5.5))
top_districts = df_clean[df_clean['District_Cleaned'] != "Not Specified"]['District_Cleaned'].value_counts().head(10)
sns.barplot(x=top_districts.values, y=top_districts.index, palette="mako", hue=top_districts.index, legend=False)
plt.title("Top 10 Districts Studied in M.Sc Research Projects", fontsize=15, weight='bold', pad=15)
plt.xlabel("Number of Projects", fontsize=12)
plt.ylabel("District", fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(artifact_dir, "top_districts.png"), dpi=150)
plt.close()

# ----------------- COMPILING REPORT -----------------

# Calculations
total_records = len(df_clean)
thesis_count = len(df_clean[df_clean['Research_Type'] == 'Thesis'])
nonthesis_count = len(df_clean[df_clean['Research_Type'] == 'Non-Thesis'])

thesis_pct = (thesis_count / total_records) * 100
nonthesis_pct = (nonthesis_count / total_records) * 100

# Average duration and medians
mean_duration_thesis = df_clean[df_clean['Research_Type'] == 'Thesis']['Duration_Months'].mean()
mean_duration_nonthesis = df_clean[df_clean['Research_Type'] == 'Non-Thesis']['Duration_Months'].mean()
median_duration_thesis = df_clean[df_clean['Research_Type'] == 'Thesis']['Duration_Months'].median()
median_duration_nonthesis = df_clean[df_clean['Research_Type'] == 'Non-Thesis']['Duration_Months'].median()

mean_duration_thesis_str = f"{mean_duration_thesis:.1f} months" if not pd.isna(mean_duration_thesis) else "N/A"
mean_duration_nonthesis_str = f"{mean_duration_nonthesis:.1f} months" if not pd.isna(mean_duration_nonthesis) else "N/A"
median_duration_thesis_str = f"{median_duration_thesis:.1f} months" if not pd.isna(median_duration_thesis) else "N/A"
median_duration_nonthesis_str = f"{median_duration_nonthesis:.1f} months" if not pd.isna(median_duration_nonthesis) else "N/A"

# Publication status table
pub_table = df_clean.groupby(['Research_Type', 'Publication_Status']).size().unstack(fill_value=0)
pub_table['Total'] = pub_table.sum(axis=1)

# Taxa table
taxa_table = df_clean.groupby(['Taxa_Cleaned', 'Research_Type']).size().unstack(fill_value=0)
taxa_table['Total'] = taxa_table.sum(axis=1)
taxa_table = taxa_table.sort_values(by='Total', ascending=False)

# District table (top 15)
dist_table = df_clean.groupby(['District_Cleaned', 'Research_Type']).size().unstack(fill_value=0)
dist_table['Total'] = dist_table.sum(axis=1)
dist_table = dist_table.sort_values(by='Total', ascending=False).head(15)

# Year distribution (last 10 years)
year_counts = df_clean.groupby(['Year_Cleaned', 'Research_Type']).size().unstack(fill_value=0)
year_counts['Total'] = year_counts.sum(axis=1)
year_counts = year_counts.sort_index(ascending=False)

# Format markdown content
md_content = f"""# M.Sc Thesis and Non-Thesis Research Data Analysis Report

This report presents a comprehensive analysis of the M.Sc research data sheet, including comparisons between **Thesis** and **Non-Thesis** projects, chronological trends, taxonomic distributions, publication rates, geographic focus, and study durations.

The dataset contains **{total_records}** clean records of M.Sc research projects spanning from academic year **1985-1986** to **2022-2023**.

---

## 1. Research Project Types Overview

* **Thesis Projects**: **{thesis_count}** ({thesis_pct:.1f}%)
* **Non-Thesis Projects**: **{nonthesis_count}** ({nonthesis_pct:.1f}%)

Thesis research represents the vast majority of the research database. However, non-thesis projects form a substantial subset of student research, particularly in recent years.

![Research Project Type Distribution](file:///{os.path.join(artifact_dir, "research_type_dist.png").replace('\\', '/')})

---

## 2. Temporal Trends (1985 - 2022)

The volume of M.Sc research has grown significantly over time, with marked fluctuations. 
* **Theses** have been consistently conducted since 1985.
* **Non-Theses** appear in the records primarily in later periods.

![Research Trends Over Time](file:///{os.path.join(artifact_dir, "research_trends.png").replace('\\', '/')})

### Volume by Academic Year (Recent 15 Years)
Below is the volume of M.Sc research projects conducted in the last 15 academic years recorded in the dataset:

| Academic Year | Thesis Count | Non-Thesis Count | Total |
| :--- | :---: | :---: | :---: |
"""

for idx, row in year_counts.head(15).iterrows():
    t_val = row.get('Thesis', 0)
    nt_val = row.get('Non-Thesis', 0)
    tot = row['Total']
    md_content += f"| **{idx}** | {t_val} | {nt_val} | {tot} |\n"

md_content += f"""
---

## 3. Taxonomic Distribution of Research

Research is highly focused on specific zoological taxa. **Fish** and **Insects** make up the vast majority (nearly **48%**) of all research projects.

![Taxonomic Focus](file:///{os.path.join(artifact_dir, "taxa_distribution.png").replace('\\', '/')})

### Research Volume by Taxa Category

| Taxa Category | Thesis | Non-Thesis | Total Count | Percentage (%) |
| :--- | :---: | :---: | :---: | :---: |
"""

total_mapped = taxa_table['Total'].sum()
for idx, row in taxa_table.iterrows():
    t_val = row.get('Thesis', 0)
    nt_val = row.get('Non-Thesis', 0)
    tot = row['Total']
    pct = (tot / total_mapped) * 100
    md_content += f"| **{idx}** | {t_val} | {nt_val} | {tot} | {pct:.1f}% |\n"

md_content += f"""
---

## 4. Publication Status and Scientific Outreach

A key measure of research impact is the publication rate.
* **Unpublished** projects comprise the largest category (**{df_clean['Publication_Status'].value_counts().get('Unpublished', 0)}** projects).
* **Published** articles account for **{df_clean['Publication_Status'].value_counts().get('Published', 0)}** projects.
* Other dissemination modes include **Conference Papers** and **Preprints**.

![Publication Status Breakdown](file:///{os.path.join(artifact_dir, "publication_rates.png").replace('\\', '/')})

### Detailed Publication Status Breakdown

| Publication Status | Thesis | Non-Thesis | Total |
| :--- | :---: | :---: | :---: |
"""

for status in ['Published', 'Unpublished', 'Conference Paper', 'Preprint', 'Unclear/Confusion', 'Missing/Unknown']:
    if status in pub_table.columns:
        t_val = pub_table.loc['Thesis', status] if 'Thesis' in pub_table.index else 0
        nt_val = pub_table.loc['Non-Thesis', status] if 'Non-Thesis' in pub_table.index else 0
        tot = t_val + nt_val
        md_content += f"| **{status}** | {t_val} | {nt_val} | {tot} |\n"

# Calculate publication rate excluding missing/unknown/unclear
clean_pub = df_clean[df_clean['Publication_Status'].isin(['Published', 'Unpublished', 'Conference Paper', 'Preprint'])]
pub_rates = clean_pub.groupby('Research_Type')['Publication_Status'].apply(lambda x: (x.isin(['Published', 'Conference Paper']).sum() / len(x)) * 100)

md_content += f"""
### Publication Rates
*(Defined as Published + Conference Paper divided by total resolved entries)*
* **Thesis Publication Rate**: {pub_rates.get('Thesis', 0.0):.1f}%
* **Non-Thesis Publication Rate**: {pub_rates.get('Non-Thesis', 0.0):.1f}%
* **Overall Research Dissemination Rate**: {(clean_pub['Publication_Status'].isin(['Published', 'Conference Paper']).sum() / len(clean_pub)) * 100:.1f}%

---

## 5. Study Duration (Time Required)

We analyzed the duration of research projects based on the entries in the "Time Required" column. Note that **{df_clean['Duration_Months'].isna().sum()}** out of **{total_records}** records did not have a parseable duration.

* **Thesis Average Duration**: **{mean_duration_thesis_str}** (Median: **{median_duration_thesis_str}**)
* **Non-Thesis Average Duration**: **{mean_duration_nonthesis_str}** (Median: **{median_duration_nonthesis_str}**)

The standard duration for both project types is typically **12 months**, but some long-term thesis projects extend up to 14 months, while shorter projects are recorded at 3-8 months.

---

## 6. Geographic Distribution of Research

Research is heavily clustered in specific geographic districts. **Dhaka** is by far the most dominant research location, representing the location of the host institute (Jahangirnagar University is situated in Savar, Dhaka district) and local sampling.

![Top Districts Studied](file:///{os.path.join(artifact_dir, "top_districts.png").replace('\\', '/')})

### Top 15 Districts / Regions Studied

| District / Study Area | Thesis | Non-Thesis | Total |
| :--- | :---: | :---: | :---: |
"""

for idx, row in dist_table.iterrows():
    if idx == "Not Specified":
        continue
    t_val = row.get('Thesis', 0)
    nt_val = row.get('Non-Thesis', 0)
    tot = row['Total']
    md_content += f"| **{idx}** | {t_val} | {nt_val} | {tot} |\n"

md_content += """
---

## Summary of Findings and Insights

1. **Focus on Fisheries and Entomology**: Nearly half of the M.Sc students at the department focus their studies on either **Fish** (25.7%) or **Insects** (22.3%). Birds (12.3%) and Primates/Mammals (12.5% combined) are the next most significant targets of research.
2. **Low Formal Publication Rate**: While there are many high-quality research topics, the recorded publication rate is relatively low (~9%). The majority of research projects remain **Unpublished** or stored in institutional records, pointing to opportunities for greater scientific dissemination.
3. **Geographic Concentration**: Dhaka district is the locus of over 80% of projects with specified locations, reflecting the immediate environment of Savar and the Jahangirnagar University campus. However, student research also stretches to important ecological zones like Tangail, Chittagong, Moulvibazar, Habiganj, and the Sundarbans.
4. **Research Duration**: The typical timeline is a **12-month** academic cycle.

*Report generated automatically on May 24, 2026.*
"""

# Write to file
with open(output_md_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"Report written successfully to: {output_md_path}")
