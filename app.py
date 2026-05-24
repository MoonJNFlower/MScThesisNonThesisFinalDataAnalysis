from __future__ import annotations

import io
import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from analysis_core import DATA_FILE, filter_data, load_data, summary_metrics


st.set_page_config(
    page_title="M.Sc Research Analytics Dashboard",
    page_icon="bar_chart",
    layout="wide",
    initial_sidebar_state="expanded",
)

sns.set_theme(style="whitegrid")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]

PALETTE = {
    "blue": "#2563EB",
    "green": "#059669",
    "amber": "#D97706",
    "red": "#DC2626",
    "slate": "#334155",
    "muted": "#64748B",
}


st.markdown(
    """
    <style>
    .block-container { padding-top: 1.7rem; padding-bottom: 2rem; }
    .main-title { font-size: 2.25rem; font-weight: 800; color: #0F172A; margin-bottom: .25rem; }
    .subtitle { color: #475569; font-size: 1.02rem; margin-bottom: 1.2rem; }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 14px 16px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, .04);
    }
    div[data-testid="stMetricLabel"] p { color: #475569; font-size: .86rem; }
    div[data-testid="stMetricValue"] { color: #0F172A; font-size: 1.6rem; }
    .insight-box {
        border-left: 4px solid #2563EB;
        background: #F8FAFC;
        padding: 1rem 1.1rem;
        border-radius: 8px;
        margin: .5rem 0 1rem 0;
    }
    .section-note { color: #64748B; font-size: .94rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Logic to handle secret data on Cloud
def get_data():
    # 1. Try to load from local file (for local development)
    if os.path.exists(DATA_FILE):
        return cached_load_data(DATA_FILE)
    
    # 2. If file is missing, ask for upload (Fallback)
    st.warning("⚠️ Research dataset (.parquet) not found in the repository.")
    uploaded_file = st.sidebar.file_uploader("Upload dataset", type=["xlsx", "parquet"])
    
    if uploaded_file is not None:
        return cached_load_data(uploaded_file)
    else:
        st.info("Please upload the required Excel dataset in the sidebar to proceed.")
        st.stop()

@st.cache_data(show_spinner="Processing workbook...")
def cached_load_data(source) -> pd.DataFrame:
    return load_data(source)


def pct(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.1f}%"


def months(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{value:.1f} mo"


def fig_to_download(fig: plt.Figure) -> bytes:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=180, bbox_inches="tight")
    return buffer.getvalue()


def show_barh(data: pd.Series, title: str, xlabel: str, color: str = "#2563EB") -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, max(4, len(data) * 0.42)))
    sns.barplot(x=data.values, y=data.index, ax=ax, color=color)
    ax.set_title(title, fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    ax.bar_label(ax.containers[0], padding=4, fontsize=9)
    sns.despine(left=True, bottom=True)
    fig.tight_layout()
    return fig


def empty_state(message: str) -> None:
    st.info(message)


df = get_data()
year_values = sorted(df["Start_Year"].dropna().astype(int).unique())
min_year = min(year_values)
max_year = max(year_values)

with st.sidebar:
    st.header("Filters")
    selected_types = st.multiselect(
        "Research type",
        sorted(df["Research_Type"].unique()),
        default=sorted(df["Research_Type"].unique()),
    )
    selected_years = st.slider("Academic year start", min_year, max_year, (min_year, max_year))
    selected_taxa = st.multiselect("Taxa category", sorted(df["Taxa_Cleaned"].unique()))
    selected_statuses = st.multiselect("Publication status", sorted(df["Publication_Status"].unique()))
    top_district_options = sorted(df["District_Cleaned"].unique())
    selected_districts = st.multiselect("District / study area", top_district_options)
    search_text = st.text_input("Search title, author, taxa, district")

    st.divider()
    st.caption("Tip: leave optional filters blank to include all values.")

filtered = filter_data(
    df,
    research_types=selected_types,
    year_range=selected_years,
    taxa=selected_taxa,
    statuses=selected_statuses,
    districts=selected_districts,
    search_text=search_text,
)

metrics = summary_metrics(filtered)
all_metrics = summary_metrics(df)

st.markdown('<div class="main-title">M.Sc Thesis and Non-Thesis Research Analytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Interactive dashboard for research trends, taxa focus, publication outcomes, study duration, and geographic distribution.</div>',
    unsafe_allow_html=True,
)

if filtered.empty:
    empty_state("No records match the current filters. Clear one or more filters to restore the dashboard.")
    st.stop()

metric_cols = st.columns(6)
metric_cols[0].metric("Clean Records", f"{metrics['records']:,}", f"{metrics['records'] - all_metrics['records']:+,} vs all")
metric_cols[1].metric("Thesis", f"{metrics['thesis']:,}")
metric_cols[2].metric("Non-Thesis", f"{metrics['non_thesis']:,}")
metric_cols[3].metric(
    "Publication Rate", 
    pct(metrics["publication_rate"]),
    help="Ratio of 'Published' or 'Conference Paper' to all resolved publication records (excludes Missing/Unknown/Unclear)."
)
metric_cols[4].metric("Avg Duration", months(metrics["avg_duration"]))
metric_cols[5].metric("Top Taxa", str(metrics["top_taxa"]))

tabs = st.tabs(
    [
        "Executive Summary",
        "Trends",
        "Taxa",
        "Publication",
        "Geography",
        "Duration",
        "Data Explorer",
        "Methodology",
    ]
)

with tabs[0]:
    left, right = st.columns([1.05, 1])
    with left:
        type_counts = filtered["Research_Type"].value_counts()
        fig, ax = plt.subplots(figsize=(7, 5))
        colors = [PALETTE["blue"] if label == "Thesis" else PALETTE["green"] for label in type_counts.index]
        wedges, texts, autotexts = ax.pie(
            type_counts.values,
            labels=type_counts.index,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            wedgeprops={"width": 0.42, "edgecolor": "white"},
            textprops={"fontsize": 11, "fontweight": "bold"},
        )
        ax.set_title("Research Type Distribution", fontsize=15, fontweight="bold", pad=14)
        st.pyplot(fig, use_container_width=True)
    with right:
        st.subheader("Professor-ready summary")
        st.markdown(
            f"""
            <div class="insight-box">
            The filtered dataset contains <b>{metrics['records']:,}</b> valid M.Sc research records.
            Thesis projects account for <b>{metrics['thesis']:,}</b> records and non-thesis projects account for
            <b>{metrics['non_thesis']:,}</b>. The strongest taxonomic focus is <b>{metrics['top_taxa']}</b>,
            while the most common study area is <b>{metrics['top_district']}</b>.
            </div>
            """,
            unsafe_allow_html=True,
        )
        published_total = metrics["published"] + metrics["conference"]
        st.write(
            f"Formal dissemination is limited: {published_total:,} records are classified as published or conference papers "
            f"within the current filter, giving a resolved dissemination rate of {pct(metrics['publication_rate'])}."
        )
        st.write(
            f"Duration data is incomplete for {metrics['missing_duration']:,} records, so duration findings should be interpreted cautiously."
        )

    st.subheader("Top findings")
    finding_cols = st.columns(3)
    finding_cols[0].success(f"Most common taxa: {metrics['top_taxa']}")
    finding_cols[1].info(f"Most common district: {metrics['top_district']}")
    finding_cols[2].warning(f"Missing duration rows: {metrics['missing_duration']:,}")

with tabs[1]:
    st.subheader("Annual Research Volume")
    trend = (
        filtered.dropna(subset=["Start_Year"])
        .groupby(["Start_Year", "Research_Type"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )
    if trend.empty:
        empty_state("No year data is available for the current filter.")
    else:
        fig, ax = plt.subplots(figsize=(12, 5.7))
        for research_type, color, marker in [("Thesis", PALETTE["blue"], "o"), ("Non-Thesis", PALETTE["green"], "s")]:
            if research_type in trend.columns:
                ax.plot(trend.index, trend[research_type], marker=marker, linewidth=2.5, label=research_type, color=color)
        ax.set_title("Annual Volume of M.Sc Research Projects", fontsize=15, fontweight="bold", pad=14)
        ax.set_xlabel("Academic Year Start")
        ax.set_ylabel("Number of Projects")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.45)
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        st.download_button("Download trend chart", fig_to_download(fig), "research_trend.png", "image/png")

        recent = trend.copy()
        recent["Total"] = recent.sum(axis=1)
        st.dataframe(recent.sort_index(ascending=False).head(20), use_container_width=True)

with tabs[2]:
    st.subheader("Taxonomic Focus")
    taxa_counts = filtered["Taxa_Cleaned"].value_counts()
    fig = show_barh(taxa_counts, "Research Volume by Taxa Category", "Number of Projects", PALETTE["blue"])
    st.pyplot(fig, use_container_width=True)

    taxa_table = filtered.groupby(["Taxa_Cleaned", "Research_Type"]).size().unstack(fill_value=0)
    taxa_table["Total"] = taxa_table.sum(axis=1)
    taxa_table["Share (%)"] = taxa_table["Total"] / taxa_table["Total"].sum() * 100
    st.dataframe(taxa_table.sort_values("Total", ascending=False).round({"Share (%)": 1}), use_container_width=True)

with tabs[3]:
    st.subheader("Publication and Dissemination")
    pub_table = filtered.groupby(["Research_Type", "Publication_Status"]).size().unstack(fill_value=0)
    pub_pct = pub_table.div(pub_table.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(11, 5.5))
    pub_pct.plot(kind="bar", stacked=True, ax=ax, colormap="tab20c")
    ax.set_title("Publication Status by Research Type", fontsize=15, fontweight="bold", pad=14)
    ax.set_xlabel("")
    ax.set_ylabel("Percentage of records")
    ax.legend(title="Status", bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)

    detail = filtered.groupby(["Publication_Status", "Research_Type"]).size().unstack(fill_value=0)
    detail["Total"] = detail.sum(axis=1)
    st.dataframe(detail.sort_values("Total", ascending=False), use_container_width=True)

with tabs[4]:
    st.subheader("Geographic Distribution")
    geo = filtered[filtered["District_Cleaned"] != "Not Specified"]["District_Cleaned"].value_counts().head(15)
    if geo.empty:
        empty_state("No specified districts are available for the current filter.")
    else:
        fig = show_barh(geo, "Top Districts / Study Areas", "Number of Projects", PALETTE["green"])
        st.pyplot(fig, use_container_width=True)

    district_table = filtered.groupby(["District_Cleaned", "Research_Type"]).size().unstack(fill_value=0)
    district_table["Total"] = district_table.sum(axis=1)
    st.dataframe(district_table.sort_values("Total", ascending=False).head(30), use_container_width=True)

with tabs[5]:
    st.subheader("Study Duration")
    duration_df = filtered.dropna(subset=["Duration_Months"])
    if duration_df.empty:
        empty_state("No parseable duration data is available for the current filter.")
    else:
        fig, ax = plt.subplots(figsize=(10, 5.3))
        sns.boxplot(data=duration_df, x="Research_Type", y="Duration_Months", ax=ax, palette=[PALETTE["blue"], PALETTE["green"]])
        sns.stripplot(data=duration_df, x="Research_Type", y="Duration_Months", ax=ax, color="#0F172A", alpha=0.35, size=4)
        ax.set_title("Distribution of Project Duration", fontsize=15, fontweight="bold", pad=14)
        ax.set_xlabel("")
        ax.set_ylabel("Duration in months")
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)

        duration_summary = duration_df.groupby("Research_Type")["Duration_Months"].agg(["count", "mean", "median", "min", "max"])
        st.dataframe(duration_summary.round(1), use_container_width=True)
    st.caption("Durations are extracted only when the source text contains a recognizable month count.")

with tabs[6]:
    st.subheader("Filtered Records")
    display_cols = [
        "Research_Type",
        "Year_Cleaned",
        "Taxa_Cleaned",
        "Title",
        "Publication_Status",
        "Author",
        "Location",
        "District_Cleaned",
        "Duration_Months",
        "Link of publications",
    ]
    st.dataframe(filtered[display_cols], use_container_width=True, height=520)
    csv = filtered[display_cols].to_csv(index=False).encode("utf-8-sig")
    st.download_button("Download filtered CSV", csv, "msc_research_filtered.csv", "text/csv")

with tabs[7]:
    st.subheader("Methodology and Data Notes")
    st.markdown(
        """
        - Source workbook: `M.Sc_thesis_non-thesis_final_data_sheet.xlsx`
        - Header row: Excel row 4 / pandas `header=3`
        - Records retained: rows classified as `Thesis` or `Non-Thesis`
        - Year typo handled: `1885-1986` is treated as `1985-1986`
        - Publication rate definition: `(Published + Conference Paper) / resolved publication records`
        - Duration parsing: extracts numeric values followed by the word `month`
        - Taxa and district categories are normalized from spelling variants and mixed labels
        """
    )
    st.markdown('<p class="section-note">Use the filters in the sidebar to produce focused views for specific taxa, years, districts, or publication outcomes.</p>', unsafe_allow_html=True)
