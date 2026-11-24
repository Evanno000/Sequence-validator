import sys
import pandas as pd
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction, MeltingTemp as mt
from openpyxl.styles import PatternFill, Font

excel_file = "input_data.xlsx"
report_file = "validation_report.xlsx"

# 1. Defensive File & Sheet Loading
try:
    df_sequences = pd.read_excel(excel_file, sheet_name="Sequences")
    df_rules = pd.read_excel(excel_file, sheet_name="Rules")
except FileNotFoundError:
    print(f"[ERROR] Could not find '{excel_file}'. Make sure it is in the same folder as this script.")
    sys.exit(1)
except ValueError as e:
    print(f"[ERROR] Missing required tab in '{excel_file}': {e}")
    sys.exit(1)
except PermissionError:
    print(f"[ERROR] '{excel_file}' is currently open in another program. Close it and try again.")
    sys.exit(1)

# Validate required columns exist
required_seq_cols = {"Sample_ID", "Type", "Sequence"}
if not required_seq_cols.issubset(df_sequences.columns):
    print(f"[ERROR] 'Sequences' tab must contain columns: {required_seq_cols}")
    sys.exit(1)

rules = dict(zip(df_rules["Parameter"], df_rules["Value"]))

def is_rule_enabled(param_name):
    val = str(rules.get(param_name, "False")).strip().lower()
    return val in ["true", "yes", "1"]

print("--- Loaded Validation Rules ---")
for k, v in rules.items():
    print(f"{k}: {v}")
print("\n--- Running Sequence Validation ---")

passed_sequences = []
audit_records = []
stop_codons = ("TAA", "TAG", "TGA")
valid_bases = set("ATCGN")

# 2. Iterate through rows with row-level error protection
for index, row in df_sequences.iterrows():
    # Skip completely empty rows
    if pd.isna(row["Sample_ID"]) and pd.isna(row["Sequence"]):
        continue

    sample_id = str(row["Sample_ID"]).strip() if not pd.isna(row["Sample_ID"]) else f"ROW_{index+2}"
    seq_type = str(row["Type"]).strip().capitalize() if not pd.isna(row["Type"]) else "Unknown"
    raw_seq = str(row["Sequence"]).strip().upper() if not pd.isna(row["Sequence"]) else ""

    reasons = []
    seq_len = len(raw_seq)
    gc_percent = 0.0
    tm_val = "N/A"

    # Check for empty sequence or invalid DNA characters
    invalid_chars = set(raw_seq) - valid_bases
    if not raw_seq:
        reasons.append("Empty sequence cell")
    elif invalid_chars:
        reasons.append(f"Invalid nucleotide characters found: {', '.join(sorted(invalid_chars))}")
    else:
        seq_obj = Seq(raw_seq)
        gc_percent = round(gc_fraction(seq_obj) * 100, 2)

        # Universal Check 1: Forbidden Motifs
        forbidden = str(rules.get("Forbidden_Motif", ""))
        if forbidden and forbidden in raw_seq:
            reasons.append(f"Contains forbidden motif ({forbidden})")

        # Universal Check 2: GC Content Bounds
        if not (rules["Min_GC_Percent"] <= gc_percent <= rules["Max_GC_Percent"]):
            reasons.append(f"GC% ({gc_percent}%) out of range ({rules['Min_GC_Percent']}-{rules['Max_GC_Percent']}%)")

        # Gene-Specific Checks
        if seq_type == "Gene":
            if seq_len < rules["Min_Gene_Length"]:
                reasons.append(f"Gene too short ({seq_len} bp < {rules['Min_Gene_Length']} bp)")
            if is_rule_enabled("Require_Start_Codon") and not raw_seq.startswith("ATG"):
                reasons.append("Missing start codon (ATG)")
            if is_rule_enabled("Require_Stop_Codon") and not raw_seq.endswith(stop_codons):
                reasons.append("Missing valid stop codon (TAA/TAG/TGA)")

        # Primer-Specific Checks
        elif seq_type == "Primer":
            tm_val = round(mt.Tm_Wallace(seq_obj), 2)
            if tm_val > rules["Max_Primer_Tm"]:
                reasons.append(f"Primer Tm too high ({tm_val}°C > {rules['Max_Primer_Tm']}°C)")
            if is_rule_enabled("Require_GC_Clamp") and not raw_seq.endswith(("G", "C")):
                reasons.append("Missing 3' GC clamp (must end in G or C)")
        else:
            reasons.append(f"Unknown sequence Type '{seq_type}' (expected 'Gene' or 'Primer')")

    # 3. Record Results
    if not reasons:
        status = "PASS"
        failure_summary = "None"
        print(f"[PASS] {sample_id} ({seq_type}) | Length: {seq_len} | GC: {gc_percent}%")
        passed_sequences.append(f">{sample_id}_{seq_type}\n{raw_seq}")
    else:
        status = "FAIL"
        failure_summary = "; ".join(reasons)
        print(f"[FAIL] {sample_id} ({seq_type}) -> {failure_summary}")

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

# 4. Save passing sequences to FASTA
with open("validated_sequences.fasta", "w") as fasta_out:
    fasta_out.write("\n".join(passed_sequences))

# 5. Export & Format Excel Report
df_audit = pd.DataFrame(audit_records)
total_count = len(df_audit)
pass_count = len(df_audit[df_audit["Status"] == "PASS"])
fail_count = len(df_audit[df_audit["Status"] == "FAIL"])
pass_rate = round((pass_count / total_count) * 100, 1) if total_count > 0 else 0

df_summary = pd.DataFrame({
    "Metric": ["Total Sequences Processed", "Passed Sequences", "Failed Sequences", "Overall Pass Rate (%)"],
    "Value": [total_count, pass_count, fail_count, pass_rate]
})

try:
    with pd.ExcelWriter(report_file, engine="openpyxl") as writer:
        df_audit.to_excel(writer, sheet_name="Audit_Results", index=False)
        df_summary.to_excel(writer, sheet_name="Summary_Stats", index=False)

        # Auto-fit column widths & color-code Status cells
        pass_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        pass_font = Font(color="006100", bold=True)
        fail_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        fail_font = Font(color="9C0006", bold=True)

        for sheet_name in writer.sheets:
            ws = writer.sheets[sheet_name]
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[col[0].column_letter].width = max_len + 4

            if sheet_name == "Audit_Results":
                for row_cells in ws.iter_rows(min_row=2, min_col=3, max_col=3):
                    cell = row_cells[0]
                    if cell.value == "PASS":
                        cell.fill = pass_fill
                        cell.font = pass_font
                    elif cell.value == "FAIL":
                        cell.fill = fail_fill
                        cell.font = fail_font

    print(f"\nDone! Saved FASTA to 'validated_sequences.fasta' and formatted report to '{report_file}'.")
except PermissionError:
    print(f"\n[ERROR] Could not save '{report_file}' because it is currently open in WPS Office. Close it and re-run.")
