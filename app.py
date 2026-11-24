import io
import streamlit as st
import pandas as pd
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction, MeltingTemp as mt
from openpyxl.styles import PatternFill, Font
from openpyxl.utils import get_column_letter


st.set_page_config(page_title="BioSeq Validator Pro", page_icon="🧬", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #0B132B 0%, #152238 50%, #1C2541 100%);
        color: #F0F4F8;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090F21 0%, #131E3A 100%);
        border-right: 1px solid #2A3B5C;
    }
    .hero-banner {
        background: linear-gradient(90deg, #0077B6 0%, #00B4D8 50%, #00F5D4 100%);
        padding: 2rem;
        border-radius: 15px;
        color: #0B132B;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(0, 245, 212, 0.2);
    }
    .hero-banner h1 {
        color: #0B132B !important;
        margin-bottom: 0.3rem;
        font-weight: 800;
    }
    .hero-banner p {
        color: #0B132B !important;
        font-size: 1.1rem;
        font-weight: 500;
        margin: 0;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(28, 37, 65, 0.85);
        border: 1px solid #2E4068;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    div[data-testid="stMetricValue"] {
        color: #00F5D4 !important;
        font-weight: 700;
    }
    .stDownloadButton > button {
        background: linear-gradient(90deg, #00B4D8 0%, #00F5D4 100%) !important;
        color: #0B132B !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 1.2rem !important;
    }
    .custom-footer {
        margin-top: 3rem;
        padding: 1.2rem;
        text-align: center;
        background-color: rgba(9, 15, 33, 0.9);
        border-top: 1px solid #2A3B5C;
        border-radius: 10px;
        color: #A0B2C6;
        font-size: 0.9rem;
    }
    .custom-footer span {
        color: #00F5D4;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def generate_sample_excel():
    sample_seq_df = pd.DataFrame({
        "Sample_ID": ["SEQ_001", "SEQ_002", "SEQ_003", "SEQ_004"],
        "Type": ["Gene", "Primer", "Gene", "Primer"],
        "Sequence": [
            "ATGGCTAGCTAGCTACGATCGATCGATCGATAA",
            "GCTAGCTAGCATCGATCGC",
            "ATGCGATCGNNNNATCG",
            "GCTAGCTAGCATCGATCGA"
        ]
    })
    sample_rules_df = pd.DataFrame({
        "Parameter": [
            "Min_GC_Percent", "Max_GC_Percent", "Min_Gene_Length",
            "Max_Primer_Tm", "Forbidden_Motif", "Require_Start_Codon",
            "Require_Stop_Codon", "Require_GC_Clamp"
        ],
        "Value": [40, 60, 25, 65, "NNNN", True, True, True]
    })
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        sample_seq_df.to_excel(writer, sheet_name="Sequences", index=False)
        sample_rules_df.to_excel(writer, sheet_name="Rules", index=False)
    return buffer.getvalue()

with st.sidebar:
    st.markdown("## 🧬 BioSeq Validator Pro")
    st.caption("Automated Bioinformatics QC Pipeline")
    st.divider()
    st.subheader("🧪 Sample Input File")
    st.caption("Download a pre-formatted Excel file to test the batch validator:")
    st.download_button(
        label="📥 Download Sample .xlsx",
        data=generate_sample_excel(),
        file_name="sample_input_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.markdown(
    """
    <div class="hero-banner">
        <h1>🧬 Batch Sequence & Primer Validator</h1>
        <p>Excel-Driven Quality Control • Automated FASTA Filtering • Color-Coded Audit Reporting</p>
    </div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload your Excel workbook (.xlsx with 'Sequences' and 'Rules' tabs)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df_sequences = pd.read_excel(uploaded_file, sheet_name="Sequences")
        df_rules = pd.read_excel(uploaded_file, sheet_name="Rules")
    except Exception as e:
        st.error(f"Error reading Excel workbook: {e}")
        st.stop()

    required_seq_cols = {"Sample_ID", "Type", "Sequence"}
    if not required_seq_cols.issubset(df_sequences.columns):
        st.error(f"The 'Sequences' tab must contain columns: {', '.join(required_seq_cols)}")
        st.stop()

    with st.expander("✏️ Edit Input Sequences Live in Browser (Click to Expand)", expanded=False):
        st.caption("Fix typos, change Gene/Primer types, or add new rows below—validation updates automatically.")
        df_sequences = st.data_editor(
            df_sequences,
            num_rows="dynamic",
            use_container_width=True,
            key="sequence_editor"
        )
    rules = dict(zip(df_rules["Parameter"], df_rules["Value"]))

    def parse_bool(val):
        return str(val).strip().lower() in ["true", "yes", "1"]

    min_gc = float(rules.get("Min_GC_Percent", 40))
    max_gc = float(rules.get("Max_GC_Percent", 60))
    min_gene_len = int(rules.get("Min_Gene_Length", 25))
    max_primer_tm = float(rules.get("Max_Primer_Tm", 65))
    forbidden_motif = str(rules.get("Forbidden_Motif", "NNNN")).strip()
    req_start = parse_bool(rules.get("Require_Start_Codon", True))
    req_stop = parse_bool(rules.get("Require_Stop_Codon", True))
    req_gc_clamp = parse_bool(rules.get("Require_GC_Clamp", True))

    with st.sidebar:
        st.divider()
        st.subheader("🎛️ Live Rule Overrides")
        override_active = st.toggle("Override Excel Rules Live", value=False)

        if override_active:
            st.caption("Adjusting sliders updates results immediately without editing Excel.")
            gc_range = st.slider("GC Content Bounds (%)", 0.0, 100.0, (min_gc, max_gc), step=1.0)
            min_gc, max_gc = gc_range, gc_range
            min_gene_len = st.number_input("Min Gene Length (bp)", min_value=1, max_value=10000, value=min_gene_len)
            max_primer_tm = st.slider("Max Primer Tm (°C)", 30.0, 95.0, max_primer_tm, step=0.5)
            forbidden_motif = st.text_input("Forbidden Motif", value=forbidden_motif).strip().upper()
            req_start = st.checkbox("Require Start Codon (ATG)", value=req_start)
            req_stop = st.checkbox("Require Stop Codon (TAA/TAG/TGA)", value=req_stop)
            req_gc_clamp = st.checkbox("Require 3' GC Clamp (G/C)", value=req_gc_clamp)

    if override_active:
        st.warning("⚡ **Live Override Mode Active:** Using your interactive sidebar thresholds instead of the Excel `Rules` tab.")

    with st.expander("⚙️ View Active Validation Rules", expanded=False):
        active_rules_df = pd.DataFrame({
            "Parameter": [
                "Min_GC_Percent", "Max_GC_Percent", "Min_Gene_Length",
                "Max_Primer_Tm", "Forbidden_Motif", "Require_Start_Codon",
                "Require_Stop_Codon", "Require_GC_Clamp"
            ],
            "Active_Value": [
                str(min_gc), str(max_gc), str(min_gene_len),
                str(max_primer_tm), forbidden_motif or "None",
                str(req_start), str(req_stop), str(req_gc_clamp)
            ],
            "Source": ["Live Override" if override_active else "Excel File"] * 8
        })
        st.dataframe(active_rules_df, use_container_width=True, hide_index=True)

    passed_sequences = []
    audit_records = []
    stop_codons = ("TAA", "TAG", "TGA")
    valid_bases = set("ATCGN")

    for index, row in df_sequences.iterrows():
        if pd.isna(row["Sample_ID"]) and pd.isna(row["Sequence"]):
            continue

        sample_id = str(row["Sample_ID"]).strip() if not pd.isna(row["Sample_ID"]) else f"ROW_{index+2}"
        seq_type = str(row["Type"]).strip().capitalize() if not pd.isna(row["Type"]) else "Unknown"
        raw_seq = str(row["Sequence"]).strip().upper() if not pd.isna(row["Sequence"]) else ""

        reasons = []
        seq_len = len(raw_seq)
        gc_percent = 0.0
        tm_val = "N/A"

        invalid_chars = set(raw_seq) - valid_bases
        if not raw_seq:
            reasons.append("Empty sequence cell")
        elif invalid_chars:
            reasons.append(f"Invalid nucleotide characters: {', '.join(sorted(invalid_chars))}")
        else:
            seq_obj = Seq(raw_seq)
            gc_percent = round(gc_fraction(seq_obj) * 100, 2)

            if forbidden_motif and forbidden_motif in raw_seq:
                reasons.append(f"Contains forbidden motif ({forbidden_motif})")

            if not (min_gc <= gc_percent <= max_gc):
                reasons.append(f"GC% ({gc_percent}%) out of range ({min_gc}-{max_gc}%)")

            if seq_type == "Gene":
                if seq_len < min_gene_len:
                    reasons.append(f"Gene too short ({seq_len} bp < {min_gene_len} bp)")
                if req_start and not raw_seq.startswith("ATG"):
                    reasons.append("Missing start codon (ATG)")
                if req_stop and not raw_seq.endswith(stop_codons):
                    reasons.append("Missing valid stop codon (TAA/TAG/TGA)")

            elif seq_type == "Primer":
                tm_val = round(mt.Tm_Wallace(seq_obj), 2)
                if tm_val > max_primer_tm:
                    reasons.append(f"Primer Tm too high ({tm_val}°C > {max_primer_tm}°C)")
                if req_gc_clamp and not raw_seq.endswith(("G", "C")):
                    reasons.append("Missing 3' GC clamp (must end in G or C)")
            else:
                reasons.append(f"Unknown sequence Type '{seq_type}' (expected 'Gene' or 'Primer')")

        if not reasons:
            status = "PASS"
            failure_summary = "None"
            passed_sequences.append(f">{sample_id}_{seq_type}\n{raw_seq}")
        else:
            status = "FAIL"
            failure_summary = "; ".join(reasons)

        audit_records.append({
            "Sample_ID": sample_id,
            "Type": seq_type,
            "Status": status,
            "Length_bp": seq_len,
            "GC_Percent": gc_percent,
            "Primer_Tm_C": tm_val,
            "Failure_Reasons": failure_summary,
            "Sequence": raw_seq
        })

    df_audit = pd.DataFrame(audit_records)

    total_count = len(df_audit)
    pass_count = len(df_audit[df_audit["Status"] == "PASS"])
    fail_count = len(df_audit[df_audit["Status"] == "FAIL"])
    pass_rate = round((pass_count / total_count) * 100, 1) if total_count > 0 else 0

    st.subheader("📈 Validation Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sequences", total_count)
    c2.metric("Passed QC", pass_count)
    c3.metric("Failed QC", fail_count)
    c4.metric("Pass Rate", f"{pass_rate}%")

    tab_table, tab_chart = st.tabs(["📋 Audit Table", "📊 QC Breakdown Chart"])

    with tab_table:
        status_filter = st.selectbox("Filter Results by Status:", ["All", "PASS", "FAIL"])
        filtered_df = df_audit if status_filter == "All" else df_audit[df_audit["Status"] == status_filter]

        def highlight_status(val):
            if val == "PASS":
                return "background-color: #C6EFCE; color: #006100; font-weight: bold;"
            elif val == "FAIL":
                return "background-color: #FFC7CE; color: #9C0006; font-weight: bold;"
            return ""

        st.dataframe(
            filtered_df.style.map(highlight_status, subset=["Status"]).format({"GC_Percent": "{:.2f}"}),
            use_container_width=True,
            hide_index=True
        )

    with tab_chart:
        st.bar_chart(df_audit["Status"].value_counts(), color="#00F5D4")

    fasta_content = "\n".join(passed_sequences)
    df_summary = pd.DataFrame({
        "Metric": ["Total Sequences Processed", "Passed Sequences", "Failed Sequences", "Overall Pass Rate (%)"],
        "Value": [total_count, pass_count, fail_count, pass_rate]
    })

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df_audit.to_excel(writer, sheet_name="Audit_Results", index=False)
        df_summary.to_excel(writer, sheet_name="Summary_Stats", index=False)

        pass_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        pass_font = Font(color="006100", bold=True)
        fail_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        fail_font = Font(color="9C0006", bold=True)

        for sheet_name in writer.sheets:
            ws = writer.sheets[sheet_name]
            for idx, col in enumerate(ws.columns, start=1):
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[get_column_letter(idx)].width = max_len + 4

            if sheet_name == "Audit_Results":
                for row in range(2, ws.max_row + 1):
                    cell = ws.cell(row=row, column=3)
                    if cell.value == "PASS":
                        cell.fill = pass_fill
                        cell.font = pass_font
                    elif cell.value == "FAIL":
                        cell.fill = fail_fill
                        cell.font = fail_font

    st.subheader("⬇️ Export Validated Files")
    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button("📄 Download Validated FASTA (.fasta)", fasta_content, "validated_sequences.fasta", "text/plain", use_container_width=True)
    with dl2:
        st.download_button("📊 Download Excel Audit Report (.xlsx)", excel_buffer.getvalue(), "validation_report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
else:
    st.info("👆 Upload your `input_data.xlsx` file above—or grab the **Sample .xlsx** from the left sidebar to try it out!")

st.markdown(
    """
    <div class="custom-footer">
        🧬 <span>BioSeq Validator Pro</span> • Developed by <span>Evans Kioko</span> • Automated Bioinformatics Sequence Quality Control
    </div>
    """,
    unsafe_allow_html=True
)
