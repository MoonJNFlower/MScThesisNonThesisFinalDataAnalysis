from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


DATA_FILE = Path(__file__).with_name("M.Sc_thesis_non-thesis_final_data_sheet.xlsx")


def clean_research_type(value: object) -> str:
    if pd.isna(value):
        return "Unknown"
    text = str(value).strip().lower()
    if "non-thesis" in text or "non thesis" in text:
        return "Non-Thesis"
    if "thesis" in text:
        return "Thesis"
    return "Other"


def clean_year(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text.lower() == "unknown" or not text:
        return None
    if text == "1885-1986":
        return "1985-1986"
    if re.match(r"^\d{4}-\d{4}$", text):
        return text
    return None


def extract_start_year(value: object) -> int | None:
    if pd.isna(value) or value is None:
        return None
    match = re.match(r"^(\d{4})-\d{4}$", str(value))
    return int(match.group(1)) if match else None


def clean_publication_status(value: object) -> str:
    if pd.isna(value):
        return "Missing/Unknown"
    text = str(value).strip().lower()
    if "unpublished" in text:
        return "Unpublished"
    if "published" in text:
        if "conference" in text:
            return "Conference Paper"
        if "confusion" in text:
            return "Unclear/Confusion"
        return "Published"
    if "conference" in text or "poster" in text:
        return "Conference Paper"
    if "preprint" in text:
        return "Preprint"
    if any(token in text for token in ["confusion", "confusing", "similar", "simiar", "same"]):
        return "Unclear/Confusion"
    return "Other"


def clean_taxa(value: object) -> str:
    if pd.isna(value):
        return "Unknown"
    text = str(value).strip().lower()
    mapping = {
        "Fish": ["fish", "actinopterygii", "actinopterygii."],
        "Insects": ["insect", "insecta", "insecct", "inset", "diptera, culicidae.", "diptera, culicidae"],
        "Birds": ["birds", "bird", "aves"],
        "Mammals (non-primate)": ["mammals", "mammal", "mammalia", "rhodents"],
        "Primates": ["primate", "primates", "primtes", "primates and \nmammals"],
        "Reptiles & Amphibians": [
            "amphibia",
            "reptile",
            "reptiles",
            "reptilia",
            "amphibia, reptiles",
            "amphibia,reptile",
        ],
        "Invertebrates (non-insect)": [
            "arthropods",
            "arthropod",
            "arthopods",
            "arachmids",
            "mollusca",
            "micro-invertebrates",
            "macro-invertebrates",
        ],
        "Plankton & Benthos": [
            "plankton",
            "benthos",
            "phytoplankton",
            "zoo plankton",
            "rotifera,daphnia",
            "plankton diversity",
        ],
        "Ecology & Conservation": [
            "conservation",
            "diversity",
            "fisherman livelihood",
            "wildlife",
            "condition",
            "biodiversity",
            "threatened",
            "impact",
            "pollution",
            "quality",
            "threat",
            "management",
            "livlihood",
        ],
        "Micro-organisms / Toxicology": ["insecticide", "micro-organism", "pesticide", "protists"],
        "Mixed Taxa": [
            "fish and \nthropods",
            "fish and arthropods",
            "birds and mammals",
            "mammal and aves",
            "fish and \narthropods",
        ],
    }
    for label, values in mapping.items():
        if text in values:
            return label
    return "Other / Miscellaneous"


def parse_duration_months(value: object) -> int | None:
    if pd.isna(value):
        return None
    match = re.search(r"(\d+)\s*month", str(value).strip().lower())
    return int(match.group(1)) if match else None


def clean_district(value: object) -> str:
    if pd.isna(value):
        return "Not Specified"
    text = str(value).strip()
    lowered = text.lower()
    if lowered == "dhaka":
        return "Dhaka"
    if "cox" in lowered and "bazar" in lowered:
        return "Cox's Bazar"
    if "moulovibazar" in lowered or "moulvibazar" in lowered:
        return "Moulvibazar"
    if "chittagong" in lowered:
        return "Chittagong"
    if "sylhet" in lowered:
        return "Sylhet"
    if "tangail" in lowered:
        return "Tangail"
    if "gazipur" in lowered:
        return "Gazipur"
    if "manikganj" in lowered:
        return "Manikganj"
    if "habiganj" in lowered:
        return "Habiganj"
    if "dinajpur" in lowered:
        return "Dinajpur"
    if "sundarban" in lowered:
        return "Sundarbans"
    if "madaripur" in lowered:
        return "Madaripur"
    if "netrokona" in lowered:
        return "Netrokona"
    if "pabna" in lowered:
        return "Pabna"
    if "rangpur" in lowered:
        return "Rangpur"
    if "jessore" in lowered:
        return "Jessore"
    if "narayanganj" in lowered:
        return "Narayanganj"
    if "comilla" in lowered:
        return "Comilla"
    return text


def load_data(file_path: str | Path = DATA_FILE) -> pd.DataFrame:
    df = pd.read_excel(file_path, sheet_name="Sheet1", header=3)
    df.columns = df.columns.str.strip()

    cleaned = df.copy()
    cleaned["Research_Type"] = cleaned["Types of research"].apply(clean_research_type)
    cleaned = cleaned[cleaned["Research_Type"].isin(["Thesis", "Non-Thesis"])].copy()
    cleaned["Year_Cleaned"] = cleaned["Year"].apply(clean_year)
    cleaned["Start_Year"] = cleaned["Year_Cleaned"].apply(extract_start_year)
    cleaned["Publication_Status"] = cleaned["Fate"].apply(clean_publication_status)
    cleaned["Taxa_Cleaned"] = cleaned["Taxa involved"].apply(clean_taxa)
    cleaned["Duration_Months"] = cleaned["Time Required"].apply(parse_duration_months)
    cleaned["District_Cleaned"] = cleaned["District"].apply(clean_district)
    cleaned["Title"] = cleaned["Title"].fillna("Untitled").astype(str).str.strip()
    cleaned["Author"] = cleaned["Author"].fillna("Unknown").astype(str).str.strip()
    cleaned["Location"] = cleaned["Location"].fillna("Not Specified").astype(str).str.strip()
    return cleaned.reset_index(drop=True)


def filter_data(
    df: pd.DataFrame,
    research_types: list[str],
    year_range: tuple[int, int],
    taxa: list[str],
    statuses: list[str],
    districts: list[str],
    search_text: str = "",
) -> pd.DataFrame:
    filtered = df.copy()
    if research_types:
        filtered = filtered[filtered["Research_Type"].isin(research_types)]
    filtered = filtered[
        filtered["Start_Year"].isna()
        | filtered["Start_Year"].between(year_range[0], year_range[1])
    ]
    if taxa:
        filtered = filtered[filtered["Taxa_Cleaned"].isin(taxa)]
    if statuses:
        filtered = filtered[filtered["Publication_Status"].isin(statuses)]
    if districts:
        filtered = filtered[filtered["District_Cleaned"].isin(districts)]
    if search_text.strip():
        pattern = re.escape(search_text.strip())
        searchable = (
            filtered["Title"].astype(str)
            + " "
            + filtered["Author"].astype(str)
            + " "
            + filtered["Taxa_Cleaned"].astype(str)
            + " "
            + filtered["District_Cleaned"].astype(str)
        )
        filtered = filtered[searchable.str.contains(pattern, case=False, na=False)]
    return filtered


def summary_metrics(df: pd.DataFrame) -> dict[str, object]:
    resolved_pub = df[df["Publication_Status"].isin(["Published", "Unpublished", "Conference Paper", "Preprint"])]
    disseminated = resolved_pub["Publication_Status"].isin(["Published", "Conference Paper"]).sum()
    publication_rate = (disseminated / len(resolved_pub) * 100) if len(resolved_pub) else 0
    return {
        "records": len(df),
        "thesis": int((df["Research_Type"] == "Thesis").sum()),
        "non_thesis": int((df["Research_Type"] == "Non-Thesis").sum()),
        "year_min": int(df["Start_Year"].min()) if df["Start_Year"].notna().any() else None,
        "year_max": int(df["Start_Year"].max()) if df["Start_Year"].notna().any() else None,
        "publication_rate": publication_rate,
        "published": int((df["Publication_Status"] == "Published").sum()),
        "conference": int((df["Publication_Status"] == "Conference Paper").sum()),
        "avg_duration": df["Duration_Months"].mean(),
        "missing_duration": int(df["Duration_Months"].isna().sum()),
        "top_taxa": df["Taxa_Cleaned"].value_counts().idxmax() if not df.empty else "N/A",
        "top_district": df["District_Cleaned"].value_counts().idxmax() if not df.empty else "N/A",
    }
