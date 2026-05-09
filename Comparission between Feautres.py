import matplotlib.pyplot as plt
import pandas as pd

file17 = r"C:\\Users\\wajiz.pk\\OneDrive\\Documents\\Master's Documents\\AThesis WORK\\combined_CIDS2017csv.csv"
file18 = r"C:\\Users\\wajiz.pk\\OneDrive\\Documents\\Master's Documents\\AThesis WORK\\combined_CIDS2018csv.csv"

df17_head = pd.read_csv(file17, nrows=5)
df18_head = pd.read_csv(file18, nrows=5)

# Get feature lists
features17 = list(df17_head.columns.str.strip())
features18 = list(df18_head.columns.str.strip())

# Compute counts
common = set(features17).intersection(features18)
only17 = set(features17) - set(features18)
only18 = set(features18) - set(features17)

# Prepare DataFrame for graphical table
summary_df = pd.DataFrame({
    "Category": ["TOTAL Features in 2017", "TOTAL Features in 2018", "Common Features", "Remaining features in 2017", "Remaining common Features in 2018"],
    "Count": [len(features17), len(features18), len(common), len(only17), len(only18)]
})

# Plot as graphical table
fig, ax = plt.subplots(figsize=(8, len(summary_df)*0.8))  # increase height per row
ax.axis('tight')
ax.axis('off')

table = ax.table(cellText=summary_df.values,
                 colLabels=summary_df.columns,
                 cellLoc='center',
                 loc='center')

# Adjust font size and scaling
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 2)  # scale(width, height)

plt.title("Feature Comparison: CICIDS2017 vs CICIDS2018", fontsize=14, pad=15)
plt.show()