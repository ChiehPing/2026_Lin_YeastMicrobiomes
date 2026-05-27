import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_plot = pd.read_csv("Figure5_a1.tsv", sep='\t', index_col=0)

colors = {
    "None": "green",
    "Other Fungi": "#d62728",
    "Yeast": "#ffcc00"
}

x = np.arange(len(df_plot))
labels = df_plot['label']

none_vals = df_plot['None']
other_vals = df_plot['Other Fungi']
yeast_vals = df_plot['Yeast']

fig, ax = plt.subplots(figsize=(10, 6))

ax.bar(x, none_vals, color=colors["None"], label="None", width=0.8)
ax.bar(x, other_vals, bottom=none_vals, color=colors["Other Fungi"], label="Other Fungi", width=0.8)
ax.bar(x, yeast_vals, bottom=none_vals + other_vals, color=colors["Yeast"], label="Yeast", width=0.8)

ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
ax.set_ylabel("Occurrence (%)", fontsize=10)
ax.set_xlabel("Category", fontsize=10)
ax.set_title("Kraken2+Bracken", fontsize=12)
ax.grid(False)

ax.legend(
    bbox_to_anchor=(1.05, 0.5),
    loc="center left",
    borderaxespad=0.0,
    frameon=False
)

plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.show()
