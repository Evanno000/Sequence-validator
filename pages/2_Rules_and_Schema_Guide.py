import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rules & Schema Guide", page_icon="📖", layout="wide")

st.markdown(
    """
    <div style="background: linear-gradient(90deg, #0077B6, #00F5D4); padding: 1.5rem; border-radius: 12px; color: #0B132B; margin-bottom: 1.5rem;">
        <h1 style="margin:0; color:#0B132B;">📖 Rules & Excel Schema Guide</h1>
        <p style="margin:0; font-weight:500;">How to Structure Your Excel Input Workbook & Configure Biological Thresholds</p>
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ Tab 1: Sequences")
    st.write("Your Excel workbook must have a tab named **`Sequences`** with these three columns:")
    st.table(pd.DataFrame({
        "Column": ["Sample_ID", "Type", "Sequence"],
        "Description": [
            "Unique sample identifier (e.g., SEQ_001)",
            "Must be either 'Gene' or 'Primer'",
            "Raw 5' -> 3' nucleotide string (A, T, C, G, N)"
        ]
    }))

with col2:
    st.subheader("2️⃣ Tab 2: Rules")
    st.write("Your Excel workbook must have a second tab named **`Rules`** with `Parameter` and `Value` columns:")
    st.table(pd.DataFrame({
        "Parameter": [
            "Min_GC_Percent / Max_GC_Percent",
            "Min_Gene_Length",
            "Max_Primer_Tm",
            "Forbidden_Motif",
            "Require_Start_Codon",
            "Require_Stop_Codon",
            "Require_GC_Clamp"
        ],
        "Behavior": [
            "Flags sequences outside acceptable GC% bounds.",
            "Flags 'Gene' sequences shorter than minimum bp.",
            "Flags 'Primer' sequences exceeding Wallace Tm (°C).",
            "Flags any sequence containing a banned motif (e.g., NNNN).",
            "True/False: Requires 'Gene' sequences to start with ATG.",
            "True/False: Requires 'Gene' sequences to end in TAA/TAG/TGA.",
            "True/False: Requires 'Primer' sequences to end in G or C."
        ]
    }))

st.markdown(
    """
    <div style="margin-top:3rem; padding:1.2rem; text-align:center; background-color:rgba(9,15,33,0.9); border-top:1px solid #2A3B5C; border-radius:10px; color:#A0B2C6; font-size:0.9rem;">
        🧬 <span style="color:#00F5D4; font-weight:600;">BioSeq Validator Pro</span> • Developed by <span style="color:#00F5D4; font-weight:600;">Evans Kioko</span> • Automated Bioinformatics Sequence Quality Control
    </div>
    """,
    unsafe_allow_html=True
)

