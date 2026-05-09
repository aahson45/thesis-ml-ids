"""
DIAGNOSTIC — find exact column names in both datasets
Run this first, paste the output back to Claude.
"""
import pandas as pd
 
PATH_2017 = r"C:\Users\wajiz.pk\OneDrive\Documents\Master's Documents\AThesis WORK\CVS2017CVS\combined_CIDS2017csv.csv"
PATH_2018 = r"C:\Users\wajiz.pk\OneDrive\Documents\Master's Documents\AThesis WORK\combined_CIDS2018csv.csv"
 
for path, name in [(PATH_2017, "2017"), (PATH_2018, "2018")]:
    cols = pd.read_csv(path, nrows=0, engine="python", on_bad_lines="skip").columns.tolist()
    print(f"\n{'='*50}")
    print(f"Dataset: {name}")
    print(f"Total columns: {len(cols)}")
    print(f"\nAll column names (repr shows hidden spaces/chars):")
    for col in cols:
        print(f"  {repr(col)}")