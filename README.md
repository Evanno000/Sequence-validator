# 🧬 BioSeq Validator Pro

An automated, Excel-driven bioinformatics quality control web application and CLI pipeline built with **Python, Biopython, Pandas, OpenPyXL, and Streamlit**.

---

## 🚀 Features
- **Batch Excel Validator (`app.py`):** Upload an `.xlsx` workbook containing `Sequences` and `Rules` tabs to dynamically validate GC% bounds, length thresholds, primer melting temperatures ($T_m$), forbidden motifs, start/stop codons, and 3' GC clamps.
- **Live Rule Overrides & In-Browser Editor:** Tweak biological validation thresholds via sidebar sliders or edit DNA sequences directly in the browser without re-uploading Excel.
- **Automated Multi-Format Outputs:** Exports a filtered `.fasta` file of passing sequences alongside a color-coded, auto-formatted `.xlsx` audit report (`Audit_Results` and `Summary_Stats`).
- **Quick Sequence Lab:** Single-sequence nucleotide composition bar chart, reverse complement generator, and Frame 1 amino acid translation with `.faa` export.
- **PCR Primer-Pair Analyzer:** Pairwise forward/reverse primer evaluation for $\Delta T_m$, annealing temperature ($T_a$), 3' GC clamps, and 3' cross-dimer risk.
- **FASTA-to-Excel Converter:** Converts raw `.fasta` / `.fa` files into ready-to-validate Excel workbooks.

---

## 📂 Project Structure
- `.streamlit/config.toml` — Custom dark-oceanic biotech UI theme
- `pages/1_Quick_Sequence_Lab.py` — Single-sequence metrics & translation
- `pages/2_Rules_and_Schema_Guide.py` — Excel workbook schema documentation
- `pages/3_Primer_Pair_Analyzer.py` — Forward/Reverse PCR primer checker
- `pages/4_FASTA_to_Excel_Converter.py` — Raw FASTA to Excel input builder
- `app.py` — Main Streamlit web application
- `validator.py` — Standalone CLI batch validator
- `input_data.xlsx` — Sample Excel configuration & test data
- `requirements.txt` — Python dependencies
- `.gitignore` — Excludes temporary Office & cache files

---

## 💻 Running Locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the web application:
   ```bash
   streamlit run app.py
   ```

---

## 👨‍💻 Author
**Evans Ukiiti Kioko**  
 
- 💻 **GitHub:** [github.com](https://github.com)
