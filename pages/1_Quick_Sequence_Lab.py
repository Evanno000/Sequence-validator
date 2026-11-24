import streamlit as st
import pandas as pd
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction, MeltingTemp as mt

st.set_page_config(page_title="Quick Sequence Lab", page_icon="🔬", layout="wide")

st.markdown(
    """
    <div style="background: linear-gradient(90deg, #0077B6, #00F5D4); padding: 1.5rem; border-radius: 12px; color: #0B132B; margin-bottom: 1.5rem;">
        <h1 style="margin:0; color:#0B132B;">🔬 Quick Single-Sequence Lab</h1>
        <p style="margin:0; font-weight:500;">Nucleotide Composition • Reverse Complement • In-Silico Protein Translation & Export</p>
    </div>
    """,
    unsafe_allow_html=True
)

seq_name = st.text_input("Sequence Label (for FASTA export):", value="Custom_Gene_01").strip()
seq_input = st.text_area("Paste a DNA Sequence (5' -> 3'):", value="ATGGCTAGCTAGCTACGATCGATCGATCGATAA", height=120).strip().upper()

if seq_input:
    invalid = set(seq_input) - set("ATCGN")
    if invalid:
        st.error(f"Invalid characters detected: {', '.join(sorted(invalid))}")
    else:
        dna_obj = Seq(seq_input)
        c1, c2, c3 = st.columns(3)
        c1.metric("Sequence Length", f"{len(dna_obj)} bp")
        c2.metric("GC Content", f"{round(gc_fraction(dna_obj) * 100, 2)}%")
        c3.metric("Wallace Tm", f"{round(mt.Tm_Wallace(dna_obj), 2)} °C")

        # Nucleotide Composition Breakdown Chart
        st.subheader("📊 Nucleotide Composition")
        base_counts = pd.DataFrame({
            "Base": ["Adenine (A)", "Thymine (T)", "Cytosine (C)", "Guanine (G)"],
            "Count": [seq_input.count("A"), seq_input.count("T"), seq_input.count("C"), seq_input.count("G")]
        }).set_index("Base")
        st.bar_chart(base_counts, color="#00F5D4")

        st.subheader("🧬 Sequence Transformations")
        st.markdown("**Complement (3' -> 5'):**")
        st.code(str(dna_obj.complement()))

        st.markdown("**Reverse Complement (5' -> 3'):**")
        st.code(str(dna_obj.reverse_complement()))

        st.markdown("**Amino Acid Translation (Frame 1):**")
        trim_len = len(dna_obj) - (len(dna_obj) % 3)
        if trim_len >= 3:
            protein_str = str(dna_obj[:trim_len].translate())
            st.code(protein_str)
            faa_content = f">{seq_name}_protein\n{protein_str}\n"
            st.download_button(
                label="📥 Download Translated Protein (.faa)",
                data=faa_content,
                file_name=f"{seq_name or 'translated'}.faa",
                mime="text/plain"
            )
        else:
            st.warning("Sequence must be at least 3 bases long to translate.")

st.markdown(
    """
    <div style="margin-top:3rem; padding:1.2rem; text-align:center; background-color:rgba(9,15,33,0.9); border-top:1px solid #2A3B5C; border-radius:10px; color:#A0B2C6; font-size:0.9rem;">
        🧬 <span style="color:#00F5D4; font-weight:600;">BioSeq Validator Pro</span> • Developed by <span style="color:#00F5D4; font-weight:600;">Evans Kioko</span> • Automated Bioinformatics Sequence Quality Control
    </div>
    """,
    unsafe_allow_html=True
)

