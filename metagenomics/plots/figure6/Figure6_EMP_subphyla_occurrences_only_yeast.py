import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

df_plot = pd.read_csv("Figure6_EMP_subphyla_occurrences_only_yeast.tsv", sep='\t', index_col=0)

categories = df_plot.index.tolist()
subphyla = [col for col in df_plot.columns if col not in ['n_samples','label']]

custom_colors = {
    'Saccharomycotina': "#A4B465",
    'Pucciniomycotina': "#FFEEAD",
    'Agaricomycotina': "#626F47",
    'Ustilaginomycotina': "#FFCF50",
    'Pezizomycotina': "#ECB390",
    'Taphrinomycotina': "#914F1E",
    'Non Yeast': "#6A7FDB",
    'Wallemiomycotina': "#8E806A",
    'None': "#D3D3D3"
}

for sp in subphyla:
    if sp not in custom_colors:
        custom_colors[sp] = "#CCCCCC"

subphyla_ordered = [sp for sp in custom_colors.keys() if sp in df_plot.columns]

fig, ax = plt.subplots(figsize=(12, 7))
x = np.arange(len(df_plot))
bottom = np.zeros(len(df_plot))

for sp in subphyla_ordered:
    vals = df_plot[sp] if sp in df_plot.columns else np.zeros(len(df_plot))
    ax.bar(x, vals, bottom=bottom, label=sp, color=custom_colors[sp], width=0.8)
    bottom += vals

ax.set_xticks(x)
ax.set_xticklabels(df_plot['label'] if 'label' in df_plot.columns else categories, rotation=45, ha='right', fontsize=8)
ax.set_ylabel("Subphylum occurrence (%)", fontsize=10)
ax.grid(False)

handles, labels = ax.get_legend_handles_labels()
handles_filtered, labels_filtered = [], []

for h, l in zip(handles, labels):
    if l in custom_colors:
        handles_filtered.append(h)
        labels_filtered.append(l)

BASE_FONT_SIZE = 10
legend = ax.legend(
    handles_filtered,
    labels_filtered,
    bbox_to_anchor=(1.05, 0.5),
    loc="center left",
    borderaxespad=0.0,
    frameon=False,
    title="Subphylum"
)

legend.set_title("Subphylum", prop=FontProperties(size=BASE_FONT_SIZE))
for text in legend.get_texts():
    text.set_fontsize(BASE_FONT_SIZE - 1)

plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.show()
