import pandas as pd
import glob
import os

path18 = r"C:\Users\wajiz.pk\Downloads\Raw data\*TrafficForML_CICFlowMeter.csv"

files18 = glob.glob(path18)

output_file = r"C:\\Users\wajiz.pk\\OneDrive\Documents\\Master's Documents\\AThesis WORK\\combined_CIDS2018csv.csv"

first_file = True

for file in files18:
    print("Processing:", os.path.basename(file))
    
    df = pd.read_csv(file, low_memory=False)
    
    if first_file:
        df.to_csv(output_file, index=False, mode='w')
        first_file = False
    else:
        df.to_csv(output_file, index=False, header=False, mode='a')

print("Merging completed!")