import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

box_df = pd.read_csv("Figure7_1.tsv", sep='\t')

q3_values = box_df.groupby('subphylum_label')['relative_abundance'].quantile(0.75)
order = q3_values.sort_values(ascending=False).index

custom_colors = {
    'Saccharomycotina': "#A4B465",
    'Pucciniomycotina': "#FFEEAD",
    'Agaricomycotina': "#626F47",
    'Ustilaginomycotina': "#FFCF50",
    'Pezizomycotina': "#ECB390",
    'Taphrinomycotina': "#914F1E",
    'Entomophthoromycotina': "#D5CEA3",
    'Glomeromycotina': "#C2B280",
    'Mortierellomycotina': "#B7A57A",
    'Mucoromycotina': "#A67B5B",
    'Wallemiomycotina': "#8E806A",
    'Zoopagomycotina': "#C0A080",
    'Kickxellomycotina': "#B08B4F",
    'None': "#D3D3D3"
}
palette = {k: v for k, v in custom_colors.items() if k in box_df['subphylum_label'].unique()}

plt.figure(figsize=(10, 6))
ax = sns.boxplot(
    data=box_df,
    y='subphylum_label',
    x='relative_abundance',
    order=order,
    orient='h',
    showmeans=False,
    showfliers=False,
    hue='subphylum_label',
    palette=palette,
    dodge=False,
    linewidth=1.2,
    whis=[0, 100],
    boxprops=dict(edgecolor='black', linewidth=1.2),
    whiskerprops=dict(linewidth=1.2, color='black'),
    capprops=dict(linewidth=0),
    medianprops=dict(linewidth=1.4, color='black')
)

ax.set_ylabel('')
plt.xlabel("Relative Abundance (%)")
plt.tight_layout()
plt.show()

