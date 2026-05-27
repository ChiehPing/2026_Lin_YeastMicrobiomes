import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plot_df = pd.read_csv("Figure12_a.tsv", sep="\t")

empo_3_order = [
    'Sediment (non-saline)', 'Soil (non-saline)', 'Water (non-saline)',
    'Sediment (saline)', 'Water (saline)', 'Animal corpus',
    'Animal distal gut', 'Animal proximal gut', 'Animal secretion',
    'Fungus corpus', 'Plant corpus', 'Plant surface'
]

category_order = [cat for cat in empo_3_order if cat in plot_df["category"].unique()]

source_colors = {
    "ITS": "green",
    "Euk": "darkgray",
    "Kraken": "blue"
}

plt.figure(figsize=(10, 8))
ax = sns.stripplot(
    data=plot_df,
    x="category",
    y="Yeast Percentage",
    hue="Source",
    order=category_order,
    palette=source_colors,
    size=8,
    jitter=True,
    edgecolor="0.3",
    linewidth=1,
    dodge=True
)

for i in range(len(category_order)):
    color = "#f0f0f0" if i % 2 == 0 else "#d9d9d9"
    ax.axvspan(i - 0.5, i + 0.5, facecolor=color, alpha=0.4, zorder=-1)

if "n_samples" in plot_df.columns:
    sample_map = dict(zip(
        plot_df[plot_df["Source"] == "ITS"]["category"],
        plot_df[plot_df["Source"] == "ITS"]["n_samples"]
    ))
    xtick_labels = [f"{cat} ({int(sample_map.get(cat, 0))})" for cat in category_order]
else:
    xtick_labels = category_order

ax.set_xticks(range(len(xtick_labels)))
ax.set_xticklabels(xtick_labels, rotation=90, ha="right")

ax.set_ylim(0, 100)
plt.ylabel("Percentage of samples with Yeasts (%)", fontsize=11)
plt.xlabel("")
ax.grid(False)

leg = plt.legend(
    title="Source",
    loc="upper right",
    frameon=False,
    fontsize=9,
    title_fontsize=9,
    bbox_to_anchor=(0.999, 0.999)
)

for lh in leg.legend_handles:
    lh.set_alpha(0.8)

plt.tight_layout()
plt.show()
