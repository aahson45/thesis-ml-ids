import pandas as pd

# ---- LOAD ONLY COLUMN NAMES FIRST (FAST) ----

df17_cols = pd.read_csv(r"C:\\Users\\wajiz.pk\\OneDrive\\Documents\\Master's Documents\\AThesis WORK\\combined_CIDS2018csv.csv", nrows=0).columns
df18 = pd.read_csv(r"C:\\Users\\wajiz.pk\\OneDrive\\Documents\\Master's Documents\\AThesis WORK\\combined_CIDS2018csv.csv", engine="python", on_bad_lines="skip")

df18.columns = df18.columns.str.strip()

# ---- FIXED MAPPING (added missing comma) ----

col_map = {
"ACK Flag Cnt": "ACK Flag Count",
"Bwd Blk Rate Avg": "Bwd Avg Bulk Rate",
"Bwd Byts/b Avg": "Bwd Avg Bytes/Bulk",
"Bwd Header Len": "Bwd Header Length",
"Bwd IAT Tot": "Bwd IAT Total",
"Bwd Pkt Len Max": "Bwd Packet Length Max",
"Bwd Pkt Len Mean": "Bwd Packet Length Mean",
"Bwd Pkt Len Min": "Bwd Packet Length Min",
"Bwd Pkt Len Std": "Bwd Packet Length Std",
"Bwd Pkts/b Avg": "Bwd Avg Packets/Bulk",
"Bwd Pkts/s": "Bwd Packets/s",
"Bwd Seg Size Avg": "Avg Bwd Segment Size",
"Dst Port": "Destination Port",
"ECE Flag Cnt": "ECE Flag Count",
"FIN Flag Cnt": "FIN Flag Count",
"Flow Byts/s": "Flow Bytes/s",
"Flow Pkts/s": "Flow Packets/s",
"Fwd Act Data Pkts": "act_data_pkt_fwd",
"Fwd Blk Rate Avg": "Fwd Avg Bulk Rate",
"Fwd Byts/b Avg": "Fwd Avg Bytes/Bulk",
"Fwd Header Len": "Fwd Header Length",
"Fwd IAT Tot": "Fwd IAT Total",
"Fwd Pkt Len Max": "Fwd Packet Length Max",
"Fwd Pkt Len Mean": "Fwd Packet Length Mean",
"Fwd Pkt Len Min": "Fwd Packet Length Min",
"Fwd Pkt Len Std": "Fwd Packet Length Std",
"Fwd Pkts/b Avg": "Fwd Avg Packets/Bulk",
"Fwd Pkts/s": "Fwd Packets/s",
"Fwd Seg Size Avg": "Avg Fwd Segment Size",
"Fwd Seg Size Min": "min_seg_size_forward",
"Init Bwd Win Byts": "Init_Win_bytes_backward",
"Init Fwd Win Byts": "Init_Win_bytes_forward",
"PSH Flag Cnt": "PSH Flag Count",
"Pkt Len Max": "Max Packet Length",
"Pkt Len Mean": "Packet Length Mean",
"Pkt Len Min": "Min Packet Length",
"Pkt Len Std": "Packet Length Std",
"Pkt Len Var": "Packet Length Variance",
"Pkt Size Avg": "Average Packet Size",
"RST Flag Cnt": "RST Flag Count",
"SYN Flag Cnt": "SYN Flag Count",
"Subflow Bwd Byts": "Subflow Bwd Bytes",
"Subflow Bwd Pkts": "Subflow Bwd Packets",
"Subflow Fwd Byts": "Subflow Fwd Bytes",
"Subflow Fwd Pkts": "Subflow Fwd Packets",
"Tot Bwd Pkts": "Total Backward Packets",
"Tot Fwd Pkts": "Total Fwd Packets",
"TotLen Bwd Pkts": "Total Length of Bwd Packets",
"TotLen Fwd Pkts": "Total Length of Fwd Packets",
"URG Flag Cnt": "URG Flag Count"
}

# ---- RENAME ----

df18.rename(columns=col_map, inplace=True)


# ---- SAVE FAST ----

df18.to_csv(r"C:\\Users\\wajiz.pk\\OneDrive\\Documents\\Master's Documents\\AThesis WORK\\combined_CIDS2018_renamed.csv", index=False)

print("DONE - Saved aligned dataset")