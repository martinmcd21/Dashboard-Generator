import streamlit as st
import yaml
import json
from utils.file_loader import load_file
from services.schema_loader import load_schema
from services.azure_openai_mapper import map_columns
from services.data_cleaner import build_canonical_df
from services.powerbi_integration import generate_pbix

st.set_page_config(page_title="PowerDash HR", layout="wide")

with open("config/reports.yaml") as f:
    REPORTS = yaml.safe_load(f)["reports"]

st.title("PowerDash HR – AI Dashboard Generator")

report_key = st.selectbox(
    "Select Report",
    options=REPORTS.keys(),
    format_func=lambda k: REPORTS[k]["name"]
)

file = st.file_uploader("Upload HRIS Export (CSV/XLSX)")

if file:
    df = load_file(file)
    st.subheader("Detected Columns")
    st.write(df.columns.tolist())

    schema = load_schema(REPORTS[report_key]["schema"])

    mapping = map_columns(df, schema["required"] + schema["optional"])

    st.subheader("AI Column Mapping")
    for field, info in mapping.items():
        col, conf = st.columns([3, 1])
        col.write(f"{field} → {info['mapped_column']}")
        conf.write(info["confidence"])

    missing = [
        f for f in schema["required"]
        if not mapping.get(f) or not mapping[f]["mapped_column"]
    ]

    if missing:
        st.error("Missing required fields:")
        st.write(missing)
        st.stop()

    if st.button("Generate Power BI Dashboard"):
        canonical = build_canonical_df(df, mapping)
        canonical.to_csv("data.csv", index=False)

        generate_pbix(
            REPORTS[report_key]["pbix"],
            "data.csv",
            "PowerDash_Output.pbix"
        )

        st.success("Dashboard generated successfully!")
        st.download_button(
            "Download PBIX",
            open("PowerDash_Output.pbix", "rb"),
            file_name="PowerDash_Output.pbix"
        )
