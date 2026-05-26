from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pandas as pd

os.environ.setdefault("STREAMLIT_SERVER_FILE_WATCHER_TYPE", "none")

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline import MedicalReportAnalyzer


st.set_page_config(page_title="Medical Report Analyzer", layout="wide")
st.title("Medical Report Analyzer")

analyzer = MedicalReportAnalyzer()

with st.sidebar:
    st.header("Input")
    mode = st.radio("Report source", ["Paste text", "Upload PDF"])
    persist = st.toggle("Store analysis in SQLite", value=True)

payload = None
if mode == "Paste text":
    sample = (
        "Patient Name: John Doe\nAge: 62\nSex: Male\n"
        "Complains of fever, cough and shortness of breath. BP 150/92. "
        "Diagnosis: pneumonia and hypertension. Started Amoxicillin 500 mg daily. "
        "Chest X-ray and CBC advised."
    )
    text = st.text_area("Medical report text", value=sample, height=220)
    if st.button("Analyze", type="primary"):
        payload = analyzer.analyze_text(text, persist=persist)
else:
    uploaded = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded and st.button("Analyze PDF", type="primary"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded.getbuffer())
            tmp_path = Path(tmp.name)
        try:
            payload = analyzer.analyze_pdf(tmp_path, persist=persist)
        finally:
            tmp_path.unlink(missing_ok=True)

if payload:
    rows = []
    for label, items in payload["entities"].items():
        rows.extend({"label": label, **item} for item in items)
    entity_df = pd.DataFrame(rows)

    patient = payload.get("patient_details", {})
    metrics = payload.get("metadata", {})
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Entities", metrics.get("entity_count", 0))
    col2.metric("Report Length", metrics.get("text_length", 0))
    col3.metric("Patient Age", patient.get("age", "N/A"))
    col4.metric("Sex", patient.get("sex", "N/A"))

    overview_tab, findings_tab, confidence_tab, export_tab = st.tabs(
        ["Report Summary", "Clinical Findings", "Confidence", "Export"]
    )

    with overview_tab:
        st.subheader("Patient Summary")
        st.success(payload["summary"] or "No summary could be generated.")

        st.subheader("Patient Details")
        if patient:
            safe_patient = {
                "Name": patient.get("name", "[REDACTED]"),
                "Age": patient.get("age", "N/A"),
                "Sex": patient.get("sex", "N/A"),
                "MRN": patient.get("mrn", "[REDACTED]"),
            }
            st.table(pd.DataFrame([safe_patient]))
        else:
            st.info("No patient header details were detected.")

        st.subheader("Analysis Notes")
        st.write(
            "The system redacts patient identifiers, extracts medical entities, assigns confidence scores, "
            "and stores structured results when SQLite persistence is enabled."
        )

    with findings_tab:
        st.subheader("Clinical Findings")
        priority = ["DIAGNOSIS", "SYMPTOM", "MEDICINE", "TEST", "OBSERVATION", "DATE"]
        if entity_df.empty:
            st.info("No clinical entities were detected.")
        else:
            for label in priority:
                group = entity_df[entity_df["label"] == label]
                if group.empty:
                    continue
                readable = label.title().replace("_", " ")
                st.markdown(f"**{readable}**")
                display = group[["text", "confidence", "source"]].copy()
                display["confidence"] = display["confidence"].map(lambda x: f"{float(x):.2f}")
                st.dataframe(display, hide_index=True, use_container_width=True)

            other = entity_df[~entity_df["label"].isin(priority)]
            if not other.empty:
                st.markdown("**Other Extracted Terms**")
                display = other[["label", "text", "confidence", "source"]].copy()
                display["confidence"] = display["confidence"].map(lambda x: f"{float(x):.2f}")
                st.dataframe(display, hide_index=True, use_container_width=True)

            st.subheader("Entity Distribution")
            st.bar_chart(entity_df["label"].value_counts())

    with confidence_tab:
        st.subheader("Explainability")
        explanations = pd.DataFrame(payload["explanations"])
        if explanations.empty:
            st.info("No explanations are available.")
        else:
            explanations["confidence"] = explanations["confidence"].map(lambda x: f"{float(x):.2f}")
            st.dataframe(explanations, hide_index=True, use_container_width=True)

    with export_tab:
        summary_text = (
            f"Medical Report Analysis\n\n"
            f"Summary:\n{payload['summary']}\n\n"
            f"Entity count: {metrics.get('entity_count', 0)}\n"
            f"Report ID: {payload.get('report_id', 'not stored')}\n"
        )
        st.download_button(
            "Download Summary",
            data=summary_text,
            file_name="medical_report_summary.txt",
            mime="text/plain",
        )
        st.download_button(
            "Download Structured JSON",
            data=json.dumps(payload, indent=2),
            file_name="medical_report_analysis.json",
            mime="application/json",
        )
        with st.expander("View raw structured JSON"):
            st.json(payload)
