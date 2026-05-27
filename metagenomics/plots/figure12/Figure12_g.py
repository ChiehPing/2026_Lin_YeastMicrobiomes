import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_abundance = pd.read_csv("Figure12_g.tsv", sep='\t', index_col=0)

top10_genus = [col for col in df_abundance.columns if col != 'n_samples']

plt.figure(figsize=(12, 7))

colors = plt.cm.tab10(np.linspace(0, 1, len(top10_genus)))
genus_color_map = dict(zip(top10_genus, colors))

bottom = np.zeros(len(df_abundance))

for genus in top10_genus:
    vals = df_abundance[genus].values
    plt.bar(df_abundance.index, vals, bottom=bottom, label=genus,
            color=genus_color_map[genus])
    bottom += vals

labels = [f"{cat} (n={df_abundance.loc[cat,'n_samples']})" for cat in df_abundance.index]

plt.ylabel("Absolute Abundance")
plt.xlabel("")
plt.xticks(range(len(df_abundance.index)), labels, rotation=90, ha='right')

plt.legend(
    title="Genus",
    loc="upper right",
    frameon=True,
    facecolor='white',
    framealpha=0.6,
    fontsize=9
)

plt.tight_layout()
plt.show()
