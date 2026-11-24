import io
import streamlit as st
import pandas as pd
from Bio import SeqIO

st.set_page_config(page_title="FASTA to Excel Converter", page_icon="🔄", layout="wide")

st.markdown(
    """
    <div style="background: linear-gradient(90deg, #0077B6, #00F5D4); padding: 1.5rem; border-radius: 12px; color: #0B132B; margin-bottom: 1.5rem;">
        <h1 style="margin:0; color:#0B132B;">🔄 FASTA to Excel Input Converter</h1>
        <p style="margin:0; font-weight:500;">Convert Raw .fasta / .fa Sequence Files into Ready-to-Validate Excel Workbooks</p>
    </div>
    """,
    unsafe_allow_html=True
)

type_mode = st.radio(
    "How should sequence types be assigned?",
    ["Auto-Detect (≤ 35 bp = Primer, > 35 bp = Gene)", "Assign All as Gene", "Assign All as Primer"],
    horizontal=True
)

fasta_file = st.file_uploader("Upload a FASTA file (.fasta, .fa, .fna)", type=["fasta", "fa", "fna", "txt"])

if fasta_file is not None:
    try:
        string_io = io.StringIO(fasta_file.getvalue().decode("utf-8"))
        records = list(SeqIO.parse(string_io, "fasta"))
    except Exception as e:
        st.error(f"Could not parse FASTA file: {e}")
        st.stop()

    if not records:
        st.warning("No valid FASTA records found (make sure headers start with '>').")
        st.stop()

    rows = []
    for rec in records:
        seq_str = str(rec.seq).strip().upper()
        if "Auto-Detect" in type_mode:
            seq_type = "Primer" if len(seq_str) <= 35 else "Gene"
        elif "Gene" in type_mode:
            seq_type = "Gene"
        else:
            seq_type = "Primer"

        rows.append({
            "Sample_ID": rec.id,
            "Type": seq_type,
            "Sequence": seq_str
        })

    df_seq = pd.DataFrame(rows)
    df_rules = pd.DataFrame({
        "Parameter": [
            "Min_GC_Percent", "Max_GC_Percent", "Min_Gene_Length",
            "Max_Primer_Tm", "Forbidden_Motif", "Require_Start_Codon",
            "Require_Stop_Codon", "Require_GC_Clamp"
        ],
        "Value": [40, 60, 25, 65, "NNNN", True, True, True]
    })

    st.success(f"✅ Parsed **{len(df_seq)}** sequences from `{fasta_file.name}`!")
    st.subheader("👀 Preview Converted `Sequences` Tab")
    st.dataframe(df_seq, use_container_width=True, hide_index=True)

    excel_out = io.BytesIO()
    with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
        df_seq.to_excel(writer, sheet_name="Sequences", index=False)
        df_rules.to_excel(writer, sheet_name="Rules", index=False)

    st.download_button(
        label="📥 Download Ready-to-Validate Excel Workbook (.xlsx)",
        data=excel_out.getvalue(),
        file_name="converted_input_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
else:
    st.info("💡 Tip: You can test this right away by uploading the `validated_sequences.fasta` file you generated earlier!")

st.markdown(
    """
    <div style="margin-top:3rem; padding:1.2rem; text-align:center; background-color:rgba(9,15,33,0.9); border-top:1px solid #2A3B5C; border-radius:10px; color:#A0B2C6; font-size:0.9rem;">
        🧬 <span style="color:#00F5D4; font-weight:600;">BioSeq Validator Pro</span> • Developed by <span style="color:#00F5D4; font-weight:600;">Evans Kioko</span> • Automated Bioinformatics Sequence Quality Control
    </div>
    """,
    unsafe_allow_html=True
)

