import streamlit as st
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction, MeltingTemp as mt

st.set_page_config(page_title="Primer-Pair Analyzer", page_icon="🧪", layout="wide")

st.markdown(
    """
    <div style="background: linear-gradient(90deg, #0077B6, #00F5D4); padding: 1.5rem; border-radius: 12px; color: #0B132B; margin-bottom: 1.5rem;">
        <h1 style="margin:0; color:#0B132B;">🧪 PCR Primer-Pair Compatibility Analyzer</h1>
        <p style="margin:0; font-weight:500;">Check Melting Temperature Delta (ΔTm), 3' GC Clamps & Cross-Dimer Risk</p>
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)
with col1:
    fwd_input = st.text_input("Forward Primer (5' -> 3'):", value="ATGGCTAGCTAGCTACGATC").strip().upper()
with col2:
    rev_input = st.text_input("Reverse Primer (5' -> 3'):", value="TTATCGATCGATCGATCGTC").strip().upper()

def analyze_primer(seq_str):
    s = Seq(seq_str)
    gc = round(gc_fraction(s) * 100, 2)
    tm = round(mt.Tm_Wallace(s), 2)
    clamp = seq_str.endswith(("G", "C"))
    return len(s), gc, tm, clamp

if fwd_input and rev_input:
    valid_bases = set("ATCG")
    if (set(fwd_input) - valid_bases) or (set(rev_input) - valid_bases):
        st.error("Primers must contain only standard DNA bases (A, T, C, G).")
        st.stop()

    f_len, f_gc, f_tm, f_clamp = analyze_primer(fwd_input)
    r_len, r_gc, r_tm, r_clamp = analyze_primer(rev_input)
    tm_diff = round(abs(f_tm - r_tm), 2)
    annealing_temp = round(min(f_tm, r_tm) - 5.0, 1)

    st.subheader("📊 Pairwise Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Forward Tm", f"{f_tm} °C", f"GC: {f_gc}%")
    m2.metric("Reverse Tm", f"{r_tm} °C", f"GC: {r_gc}%")
    m3.metric("ΔTm Difference", f"{tm_diff} °C", "Ideal ≤ 5°C")
    m4.metric("Suggested Annealing Ta", f"{annealing_temp} °C")

    st.subheader("🔬 Compatibility Diagnostics")
    if tm_diff <= 5.0:
        st.success(f"✅ **Good Tm Match:** ΔTm is {tm_diff}°C (within the recommended ≤ 5.0°C window).")
    else:
        st.warning(f"⚠️ **High Tm Mismatch:** ΔTm is {tm_diff}°C (> 5.0°C). Primers may anneal unevenly during PCR.")

    if f_clamp and r_clamp:
        st.success("✅ **3' GC Clamps Present:** Both primers end in G or C for stable polymerase binding.")
    else:
        st.warning("⚠️ **Missing 3' GC Clamp:** One or both primers end in A/T, which can reduce priming efficiency.")

    # Check 3'-end cross-dimer risk (last 4 bases of Forward vs Reverse Complement of Reverse)
    fwd_3_end = fwd_input[-4:]
    rev_rc = str(Seq(rev_input).reverse_complement())
    if fwd_3_end in rev_rc:
        st.error(f"🚨 **3' Cross-Dimer Risk Detected:** Forward 3' end (`{fwd_3_end}`) is complementary to Reverse primer!")
    else:
        st.success("✅ **Low 3' Dimer Risk:** No exact 4-bp 3'-end complementarity detected between primers.")

st.markdown(
    """
    <div style="margin-top:3rem; padding:1.2rem; text-align:center; background-color:rgba(9,15,33,0.9); border-top:1px solid #2A3B5C; border-radius:10px; color:#A0B2C6; font-size:0.9rem;">
        🧬 <span style="color:#00F5D4; font-weight:600;">BioSeq Validator Pro</span> • Developed by <span style="color:#00F5D4; font-weight:600;">Evans Kioko</span> • Automated Bioinformatics Sequence Quality Control
    </div>
    """,
    unsafe_allow_html=True
)

