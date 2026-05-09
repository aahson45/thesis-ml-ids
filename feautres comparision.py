import pandas as pd

# ==============================
# 1. File paths
# ==============================
file_2017 = "C:\\Users\\wajiz.pk\\OneDrive\\Documents\\Master's Documents\\AThesis WORK\\combined_CIDS2017csv.csv"
file_2018 = "C:\\Users\\wajiz.pk\\OneDrive\\Documents\\Master's Documents\\AThesis WORK\\combined_CIDS2018csv.csv"


# ==============================
# 2. Load datasets
# ==============================
df2017 = pd.read_csv(file_2017, nrows=1)  # only header needed
df2018 = pd.read_csv(file_2018, nrows=1)

features_2017 = list(df2017.columns)
features_2018 = list(df2018.columns)

# Remove label from comparison
if "Label" in features_2017:
    features_2017.remove("Label")
if "Label" in features_2018:
    features_2018.remove("Label")

# ==============================
# 3. Compare features
# ==============================

set_2017 = set(features_2017)
set_2018 = set(features_2018)

common_features = list(set_2017.intersection(set_2018))
missing_in_2018 = list(set_2017 - set_2018)
missing_in_2017 = list(set_2018 - set_2017)

# ==============================
# 4. Order comparison
# ==============================

order_match = features_2017 == features_2018

# ==============================
# 5. Print results
# ==============================

print("===== FEATURE COMPARISON REPORT =====\n")

print("Features in CIC-IDS2017:", len(features_2017))
print("Features in CIC-IDS2018:", len(features_2018))
print("Common features:", len(common_features))
print("\n")

print("Missing in CIC-IDS2018:")
print(missing_in_2018)
print("\n")

print("Missing in CIC-IDS2017:")
print(missing_in_2017)
print("\n")

print("Feature order identical:", order_match)

# ==============================
# 6. Merge feasibility decision
# ==============================

if len(missing_in_2018) == 0 and len(missing_in_2017) == 0:
    print("\nDatasets have identical feature sets.")
    print("MERGE POSSIBLE: YES")
else:
    print("\nDatasets differ in features.")
    print("MERGE POSSIBLE: NEED FEATURE ALIGNMENT")

# ==============================
# 7. Export comparison report
# ==============================

comparison_df = pd.DataFrame({
    "Common_Features": pd.Series(common_features),
    "Missing_in_2018": pd.Series(missing_in_2018),
    "Missing_in_2017": pd.Series(missing_in_2017)
})

comparison_df.to_csv("feature_comparison_report.csv", index=False)

print("\nFeature comparison report saved as feature_comparison_report.csv")
