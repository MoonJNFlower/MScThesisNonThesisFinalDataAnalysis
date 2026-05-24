from __future__ import annotations

import os
import re
import pandas as pd
import numpy as np
from typing import Union, IO
from mappings import TAXA_MAPPING, DISTRICT_MAPPING

# Define the data file path relative to this script
SCRIPT_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(SCRIPT_DIR, "M.Sc_research_data.parquet")

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

def extract_start_year(val):
    if pd.isna(val) or val is None:
        return None
    match = re.match(r'(\d{4})-\d{4}', val)
    if match:
        return int(match.group(1))
    return None

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

def map_taxa(val):
    if pd.isna(val): return "Unknown"
    return TAXA_MAPPING.get(str(val).strip().lower(), "Other / Miscellaneous")

def parse_months(val):
    if pd.isna(val):
        return None
    val = str(val).strip().lower()
    match = re.search(r'(\d+)\s*month', val)
    if match:
        return int(match.group(1))
    return None

def clean_district(val):
    if pd.isna(val):
        return "Not Specified"
    val_lower = str(val).strip().lower()
    if 'cox' in val_lower and 'bazar' in val_lower:
        return "Cox's Bazar"
    if 'sundarban' in val_lower:
        return 'Sundarbans'
    return DISTRICT_MAPPING.get(val_lower, val)

def load_data(file_source: Union[str, IO]) -> pd.DataFrame:
    # Detect if we are loading a Parquet file or Excel
    is_parquet = False
    if isinstance(file_source, str):
        is_parquet = file_source.endswith('.parquet')
    elif hasattr(file_source, 'name'):
        is_parquet = file_source.name.endswith('.parquet')

    try:
        if is_parquet:
            return pd.read_parquet(file_source, engine='pyarrow')
        df = pd.read_excel(file_source, sheet_name='Sheet1', header=3)
    except Exception as e:
        raise FileNotFoundError(f"Could not load data. Error: {e}")

    df.columns = df.columns.str.strip()

    # Robustness: Validate expected columns exist
    required = ['Types of research', 'Year', 'Fate', 'Taxa involved', 'Time Required', 'District', 'Title', 'Author']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Excel sheet is missing required columns: {missing}")

    df_clean = df.copy()
    df_clean['Research_Type'] = df_clean['Types of research'].apply(clean_research_type)
    df_clean = df_clean[df_clean['Research_Type'].isin(['Thesis', 'Non-Thesis'])]
    df_clean['Year_Cleaned'] = df_clean['Year'].apply(clean_year)
    df_clean['Start_Year'] = df_clean['Year_Cleaned'].apply(extract_start_year)
    df_clean['Publication_Status'] = df_clean['Fate'].apply(clean_fate)
    df_clean['Taxa_Cleaned'] = df_clean['Taxa involved'].apply(map_taxa)
    df_clean['Duration_Months'] = df_clean['Time Required'].apply(parse_months)
    df_clean['District_Cleaned'] = df_clean['District'].apply(clean_district)

    return df_clean

def filter_data(
    df: pd.DataFrame,
    research_types: list[str],
    year_range: tuple[int, int],
    taxa: list[str],
    statuses: list[str],
    districts: list[str],
    search_text: str,
) -> pd.DataFrame:
    # Performance: Use a boolean mask for filtering instead of creating multiple intermediate copies
    mask = pd.Series(True, index=df.index)

    if research_types:
        mask &= df["Research_Type"].isin(research_types)
    if year_range:
        min_year, max_year = year_range
        mask &= (df["Start_Year"] >= min_year) & (df["Start_Year"] <= max_year)
    if taxa:
        mask &= df["Taxa_Cleaned"].isin(taxa)
    if statuses:
        mask &= df["Publication_Status"].isin(statuses)
    if districts:
        mask &= df["District_Cleaned"].isin(districts)

    if search_text:
        s = search_text.lower()
        # Performance: Vectorized string search is significantly faster than row-by-row apply()
        search_mask = (
            df["Title"].str.contains(s, case=False, na=False) |
            df["Author"].str.contains(s, case=False, na=False) |
            df["Taxa_Cleaned"].str.contains(s, case=False, na=False) |
            df["District_Cleaned"].str.contains(s, case=False, na=False)
        )
        mask &= search_mask

    return df[mask]

def summary_metrics(df: pd.DataFrame) -> dict:
    total_records = len(df)
    thesis_count = df[df["Research_Type"] == "Thesis"].shape[0]
    non_thesis_count = df[df["Research_Type"] == "Non-Thesis"].shape[0]

    published = df[df["Publication_Status"] == "Published"].shape[0]
    conference = df[df["Publication_Status"] == "Conference Paper"].shape[0]
    resolved_pubs = df[
        df["Publication_Status"].isin(
            ["Published", "Unpublished", "Conference Paper", "Preprint"]
        )
    ].shape[0]
    publication_rate = (
        ((published + conference) / resolved_pubs * 100) if resolved_pubs > 0 else 0
    )

    avg_duration = df["Duration_Months"].mean()
    missing_duration = df["Duration_Months"].isna().sum()

    top_taxa = df["Taxa_Cleaned"].mode()[0] if not df["Taxa_Cleaned"].empty else "N/A"
    top_district = (
        df[df["District_Cleaned"] != "Not Specified"]["District_Cleaned"].mode()[0]
        if not df[df["District_Cleaned"] != "Not Specified"].empty
        else "N/A"
    )

    return {
        "records": total_records,
        "thesis": thesis_count,
        "non_thesis": non_thesis_count,
        "published": published,
        "conference": conference,
        "publication_rate": publication_rate,
        "avg_duration": avg_duration,
        "missing_duration": missing_duration,
        "top_taxa": top_taxa,
        "top_district": top_district,
    }