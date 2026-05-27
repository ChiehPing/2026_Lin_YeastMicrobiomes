import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

rel_melted = pd.read_csv("Figure7_2.tsv", sep='\t', index_col=0)

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

order = rel_melted.groupby("Subphylum")["Relative_Abundance"]\
                  .quantile(0.75).sort_values(ascending=False).index

plt.figure(figsize=(10, 6))
sns.boxplot(
    data=rel_melted,
    y="Subphylum",
    x="Relative_Abundance",
    order=order,
    palette=custom_colors,
    hue="Subphylum",
    legend=False,
    linewidth=0.8,
    fliersize=0,
    whis=[0, 100],
    dodge=False,
    whiskerprops={'color': 'black', 'linewidth': 1.2},
    capprops={'color': 'black', 'linewidth': 0},
    boxprops={'edgecolor': 'black', 'linewidth': 1.2},
    medianprops={'color': 'black', 'linewidth': 1.5}
)

plt.xlabel("")
plt.ylabel("")
plt.tight_layout()
plt.show()

summary = []
for subphylum, group in rel_melted.groupby("Subphylum"):
    if group["Relative_Abundance"].sum() == 0:
        continue
    q1 = group["Relative_Abundance"].quantile(0.25)
    median = group["Relative_Abundance"].quantile(0.5)
    q3 = group["Relative_Abundance"].quantile(0.75)
    vmax = group["Relative_Abundance"].max()
    avg_total_reads = group["Total_Reads"].mean()
    avg_reads_sub = group["Reads_Subphylum"].mean()
    n_detected_samples = group[group["Relative_Abundance"] > 0]["Sample"].nunique()

    summary.append({
        "Subphylum": subphylum,
        "Q1": q1,
        "Median": median,
        "Q3": q3,
        "Max": vmax,
        "Avg_total_reads_within_subphylum": avg_total_reads,
        "Avg_reads_for_detected_samples": avg_reads_sub,
        "N_detected_samples": n_detected_samples
    })

df_summary = pd.DataFrame(summary).round({
    "Q1": 4, "Median": 4, "Q3": 4, "Max": 4,
    "Avg_total_reads_within_subphylum": 2,
    "Avg_reads_for_detected_samples": 2
})
