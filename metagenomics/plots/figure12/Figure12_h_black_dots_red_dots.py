import pandas as pd
import matplotlib.pyplot as plt

scatter_saccharo_df = pd.read_csv("Figure12_h_black_dots.tsv", sep='\t')
scatter_non_yeast_df = pd.read_csv("Figure12_h_red_dots.tsv", sep='\t')

scatter_non_yeast_top3 = scatter_non_yeast_df.nlargest(3, 'abundance')

category_order = [
    'dairy', 'alcohol', 'fermented_beverages', 'meat',
    'fermented_seeds', 'fermented_grains', 'fermented_fruits_and_vegetables',
    'fermented_tubers_and_roots', 'probiotics', 'fermented_meat',
    'fish', 'fruits_and_vegetables', 'fermented_legumes', 'fermented_fish', 'other'
]

scatter_saccharo_df['category'] = pd.Categorical(scatter_saccharo_df['category'], categories=category_order, ordered=True)
scatter_non_yeast_top3['category'] = pd.Categorical(scatter_non_yeast_top3['category'], categories=category_order, ordered=True)

plt.figure(figsize=(14,7))

plt.scatter([], [], facecolors='none', edgecolors='black', s=50, label="Number of reads of genus Saccharomyces in a sample")
plt.scatter([], [], color='red', s=70, label="Top 3 non-yeast sample (by assigned number of reads)")

for cat in category_order:
    df_cat_black = scatter_saccharo_df[scatter_saccharo_df['category'] == cat]
    if not df_cat_black.empty:
        plt.scatter([cat]*len(df_cat_black), df_cat_black['abundance'], facecolors='none', edgecolors='black', s=50)

    df_cat_red = scatter_non_yeast_top3[scatter_non_yeast_top3['category'] == cat]
    if not df_cat_red.empty:
        plt.scatter([cat]*len(df_cat_red), df_cat_red['abundance'], color='red', s=70)

plt.xticks(rotation=90)
plt.ylabel("Absolute Abundance (number of reads)")
plt.legend(loc="best", facecolor='lightgray', edgecolor='dimgray', framealpha=0.9, frameon=True)
plt.xlabel("")

plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
plt.tight_layout()
plt.show()
