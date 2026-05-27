import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

data_filtered = pd.read_csv("Figure5_b2.tsv", sep="\t", index_col=0)

order = ['Absent', 'Present']
palette = {'Absent': 'pink', 'Present': 'gold'}

fig, ax = plt.subplots(figsize=(6, 5))
sns.set(style="whitegrid", context="talk")

for i, status in enumerate(order):
    sns.boxplot(
        data=data_filtered[data_filtered['status'] == status],
        x='status',
        y='reads_length',
        color=palette[status],
        width=0.6,
        linewidth=1.5,
        showfliers=False,
        showcaps=False,
        medianprops={'color': 'black', 'linewidth': 1.2},
        boxprops={'edgecolor': 'black', 'linewidth': 1.2},
        whiskerprops={'linewidth': 1.2},
        ax=ax
    )

ax.set_xlabel("")
ax.set_ylabel("Number of reads", fontsize=13, fontweight="bold", fontname="DejaVu Sans")
ax.tick_params(axis="x", labelsize=12)
ax.tick_params(axis="y", labelsize=12)

for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontname("DejaVu Sans")
    label.set_fontsize(12)
    label.set_fontweight("bold")
ax.grid(True, axis="y", linestyle="--", alpha=0.4)

stats = data_filtered.groupby('status')['reads_length'].agg(['mean', 'std'])
quartiles = data_filtered.groupby('status')['reads_length'].quantile([0.25, 0.5, 0.75]).unstack()

y_max = ax.get_ylim()[1]
y_pos = y_max * 0.95

for i, label in enumerate(order):
    if label in stats.index:
        mu = stats.loc[label, 'mean']
        sigma = stats.loc[label, 'std']
        q1 = quartiles.loc[label, 0.25]
        median = quartiles.loc[label, 0.5]
        q3 = quartiles.loc[label, 0.75]
        ax.text(
            i, y_pos,
            fr"$\mu$ = {mu:.2e} ; $\sigma$ = {sigma:.2e}",
            ha="center", va="bottom", fontsize=9, fontweight="bold"
        )
        print(f"{label}: Q1 = {q1:.2e}, Median = {median:.2e}, Q3 = {q3:.2e}")

plt.tight_layout()
plt.show()
