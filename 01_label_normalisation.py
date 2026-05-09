"""
THESIS PIPELINE — STEP 1: LABEL NORMALISATION
==============================================
Author : Ali Ahson
Thesis : Latency-Aware Network Protection — ML Middle Layer for IDS Orchestration

PURPOSE
-------
Both CICIDS-2017 and CSE-CIC-IDS-2018 use different raw label strings for
the same attack type. Before we can merge and train on them together, every
row must be mapped to ONE of our 6 unified classes.

UNIFIED 6-CLASS TAXONOMY
-------------------------
  0 → BENIGN
  1 → DoS_DDoS
  2 → BOTNET
  3 → BRUTE_FORCE
  4 → WEB_ATTACK
  5 → INFILTRATION

HOW THIS SCRIPT WORKS (read this before editing)
-------------------------------------------------
1. Load ONLY the Label column of each dataset (fast — avoids loading 18M rows twice).
2. Strip whitespace and lowercase every label (raw data is inconsistent).
3. Apply the mapping dictionary → produces a new column "Unified_Label".
4. Report any labels that did NOT match (unmapped_labels). Fix the dict if any appear.
5. Save a lightweight CSV containing ONLY the index + Unified_Label for each dataset.
   → We attach these columns when we merge in Step 2, avoiding a full re-read here.

WHY WE SAVE INDEX + LABEL ONLY
--------------------------------
The full merged dataset is ~18M rows × 80 columns. Loading it twice (once here,
once in Step 2) wastes ~8 GB of RAM. Instead, we produce a "label patch" file
and join it by index in the next step.
"""

import pandas as pd
import os

# ============================================================
# CONFIGURATION — adjust paths to match your machine
# ============================================================

PATH_2017 = r"C:\Users\wajiz.pk\OneDrive\Documents\Master's Documents\AThesis WORK\CVS2017CVS\combined_CIDS2017csv.csv"
PATH_2018 = r"C:\Users\wajiz.pk\OneDrive\Documents\Master's Documents\AThesis WORK\combined_CIDS2018csv.csv"  # use the RENAMED version

OUTPUT_DIR = r"C:\Users\wajiz.pk\OneDrive\Documents\Master's Documents\AThesis WORK\pipeline"
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUT_LABELS_2017 = os.path.join(OUTPUT_DIR, "labels_2017.csv")
OUT_LABELS_2018 = os.path.join(OUTPUT_DIR, "labels_2018.csv")
OUT_REPORT      = os.path.join(OUTPUT_DIR, "label_normalisation_report.txt")

# ============================================================
# UNIFIED LABEL MAP
# ============================================================
# Key   = raw label string (lowercased, stripped)
# Value = unified class name
#
# How to read this:
#   "dos hulk" is what CICIDS-2017 calls this attack.
#   We map it to "DoS_DDoS" because it belongs to that family.
#   The model will then learn ONE concept, not 12 slightly different ones.

LABEL_MAP = {
    # ── BENIGN ────────────────────────────────────────────────────────
    "benign"                          : "BENIGN",

    # ── DoS / DDoS ────────────────────────────────────────────────────
    # 2017 labels
    "dos hulk"                        : "DoS_DDoS",
    "dos goldeneye"                   : "DoS_DDoS",
    "dos slowloris"                   : "DoS_DDoS",
    "dos slowhttptest"                : "DoS_DDoS",
    "heartbleed"                      : "DoS_DDoS",   # exploits OpenSSL — grouped here
    "ddos"                            : "DoS_DDoS",
    # 2018 labels
    "ddos attack-hoic"                : "DoS_DDoS",
    "ddos attack-loic-http"           : "DoS_DDoS",
    "ddos attack-loic-udp"            : "DoS_DDoS",
    "dos attack-hulk"                 : "DoS_DDoS",
    "dos attack-goldeneye"            : "DoS_DDoS",
    "dos attack-slowloris"            : "DoS_DDoS",
    "dos attack-slowhttptest"         : "DoS_DDoS",

    # ── BOTNET ────────────────────────────────────────────────────────
    "bot"                             : "BOTNET",
    "botnet ares"                     : "BOTNET",

    # ── BRUTE FORCE ───────────────────────────────────────────────────
    # 2017 labels
    "ftp-patator"                     : "BRUTE_FORCE",
    "ssh-patator"                     : "BRUTE_FORCE",
    # 2018 labels
    "brute force -web"                : "BRUTE_FORCE",
    "brute force -xss"                : "BRUTE_FORCE",   # XSS via brute force — grouped
    "ftp-bruteforce"                  : "BRUTE_FORCE",
    "ssh-bruteforce"                  : "BRUTE_FORCE",

    # ── WEB ATTACK ────────────────────────────────────────────────────
    # 2017 labels
    "web attack \x96 brute force"     : "WEB_ATTACK",   # encoding artefact in raw CSV
    "web attack – brute force"        : "WEB_ATTACK",
    "web attack - brute force"        : "WEB_ATTACK",
    "web attack \x96 xss"             : "WEB_ATTACK",
    "web attack – xss"                : "WEB_ATTACK",
    "web attack - xss"                : "WEB_ATTACK",
    "web attack \x96 sql injection"   : "WEB_ATTACK",
    "web attack – sql injection"      : "WEB_ATTACK",
    "web attack - sql injection"      : "WEB_ATTACK",
    # 2018 labels
    "sql injection"                   : "WEB_ATTACK",
    "xss"                             : "WEB_ATTACK",

    # ── INFILTRATION ──────────────────────────────────────────────────
    "infiltration"                    : "INFILTRATION",
}

# ============================================================
# HELPER: apply map and report unmapped rows
# ============================================================

def normalise_labels(raw_series: pd.Series, dataset_name: str) -> pd.Series:
    """
    Takes a Series of raw label strings.
    Returns a Series of unified label strings.
    Prints a warning for anything that didn't match the map.
    """
    # Clean: strip whitespace, lowercase
    cleaned = raw_series.str.strip().str.lower()

    # Map to unified label
    unified = cleaned.map(LABEL_MAP)

    # Find unmapped rows
    unmapped_mask  = unified.isna()
    unmapped_count = unmapped_mask.sum()

    if unmapped_count > 0:
        unmapped_labels = cleaned[unmapped_mask].unique()
        print(f"\n⚠  [{dataset_name}] {unmapped_count} rows had UNMAPPED labels:")
        for lbl in unmapped_labels:
            print(f"      → '{lbl}'")
        print("   Add these to LABEL_MAP before proceeding.\n")
    else:
        print(f"✅  [{dataset_name}] All labels mapped successfully.")

    return unified


# ============================================================
# STEP 1A: normalise 2017 labels
# ============================================================

print("=" * 60)
print("Loading 2017 Label column ...")

# WHY we load the full header first:
# The 2017 CSV has leading spaces on almost every column name (' Label' not 'Label').
# We read the header, strip all column names, then find where 'Label' ended up.
# Only THEN do we tell pandas which column index to load — avoiding the usecols mismatch.

raw_cols_2017 = pd.read_csv(PATH_2017, nrows=0, engine="python", on_bad_lines="skip").columns
clean_cols_2017 = raw_cols_2017.str.strip()
label_col_2017 = raw_cols_2017[clean_cols_2017 == "Label"][0]   # original name with spaces
print(f"  Found label column in 2017 as: {repr(label_col_2017)}")

df17_labels = pd.read_csv(PATH_2017, usecols=[label_col_2017], engine="python", on_bad_lines="skip")
df17_labels.columns = ["Label"]   # rename to clean version

print(f"  2017 raw label distribution:\n{df17_labels['Label'].value_counts()}\n")

df17_labels["Unified_Label"] = normalise_labels(df17_labels["Label"], "2017")
df17_labels["Source_Year"]   = 2017   # track origin after merge

df17_labels.drop(columns=["Label"]).to_csv(OUT_LABELS_2017, index=True)   # index = row number (used for join)
print(f"  Saved → {OUT_LABELS_2017}")


# ============================================================
# STEP 1B: normalise 2018 labels
# ============================================================

print("\n" + "=" * 60)
print("Loading 2018 Label column ...")

# 2018 has no leading spaces — 'Label' loads fine directly
# But we apply the same safe pattern for consistency
raw_cols_2018 = pd.read_csv(PATH_2018, nrows=0, engine="python", on_bad_lines="skip").columns
clean_cols_2018 = raw_cols_2018.str.strip()
label_col_2018 = raw_cols_2018[clean_cols_2018 == "Label"][0]
print(f"  Found label column in 2018 as: {repr(label_col_2018)}")

df18_labels = pd.read_csv(PATH_2018, usecols=[label_col_2018], engine="python", on_bad_lines="skip")
df18_labels.columns = ["Label"]

print(f"  2018 raw label distribution:\n{df18_labels['Label'].value_counts()}\n")

df18_labels["Unified_Label"] = normalise_labels(df18_labels["Label"], "2018")
df18_labels["Source_Year"]   = 2018

df18_labels.drop(columns=["Label"]).to_csv(OUT_LABELS_2018, index=True)
print(f"  Saved → {OUT_LABELS_2018}")


# ============================================================
# STEP 1C: summary report
# ============================================================

print("\n" + "=" * 60)
print("UNIFIED LABEL DISTRIBUTION ACROSS BOTH DATASETS")
print("=" * 60)

all_labels = pd.concat([df17_labels["Unified_Label"], df18_labels["Unified_Label"]], ignore_index=True)

dist = all_labels.value_counts()
total = len(all_labels)

report_lines = []
report_lines.append("LABEL NORMALISATION REPORT\n")
report_lines.append(f"Total rows (2017 + 2018): {total:,}\n\n")
report_lines.append(f"{'Class':<20} {'Count':>10} {'%':>8}\n")
report_lines.append("-" * 42 + "\n")

for label, count in dist.items():
    line = f"{label:<20} {count:>10,} {count/total*100:>7.2f}%"
    print(line)
    report_lines.append(line + "\n")

null_count = all_labels.isna().sum()
report_lines.append(f"\nUnmapped (NaN) rows: {null_count:,}\n")
print(f"\nUnmapped (NaN) rows: {null_count:,}")

with open(OUT_REPORT, "w") as f:
    f.writelines(report_lines)

print(f"\nFull report saved → {OUT_REPORT}")
print("\n✅  STEP 1 COMPLETE. Run 02_merge_and_clean.py next.")