import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_plot = pd.read_csv("Figure12_b.tsv", sep='\t')

df_plot = df_plot.rename(columns={
    "Yeast": "Samples with Yeast (RA)",
    "Other Fungi": "Samples with Only Fungus (RA)",
    "None": "Nofungal (RA)"
})

category_order = df_plot['label'].tolist()
df_plot = df_plot.set_index('label').reindex(category_order)

columns_to_plot = ['Samples with Yeast (RA)',
                   'Samples with Only Fungus (RA)',
                   'Nofungal (RA)']
colors = ['gold', 'gray', 'darkred']

fig, ax = plt.subplots(figsize=(10, 6))
bottom = np.zeros(len(df_plot))

for col, color in zip(columns_to_plot, colors):
    values = df_plot[col].values
    ax.bar(df_plot.index, values, bottom=bottom, color=color, width=0.8, label=col)
    bottom += values

ax.set_xticks(range(len(df_plot)))
ax.set_xticklabels(df_plot.index, rotation=45, ha='right', fontsize=8)
ax.set_ylabel("Occurrence (%)", fontsize=10)
ax.set_xlabel("")
ax.grid(False, axis='y')

ax.legend(
    title='Sample Type',
    loc='lower right',
    frameon=True,
    facecolor='white',
    framealpha=0.5,
    title_fontsize=10,
    fontsize=9
)

plt.tight_layout()
plt.show()
