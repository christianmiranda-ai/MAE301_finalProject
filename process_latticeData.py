# process_latticeData.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import f_oneway, shapiro, levene
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# Read CSV
df = pd.read_csv("lattice_data.csv", encoding="windows-1252")

# Convert to PSI (2" x 2" = 4 in²)
df["PSI"] = df["Force (kg)"] * 2.205 / 4  # kg to lbs, then PSI

# Stats
means = df.groupby("Topology")["PSI"].mean()
stds = df.groupby("Topology")["PSI"].std()
print("Means:\n", means)
print("Standard Deviations:\n", stds)

# Normality Test (Shapiro-Wilk)
for topology in df["Topology"].unique():
    stat, p = shapiro(df[df["Topology"] == topology]["PSI"])
    print(f"Shapiro-Wilk Test for {topology}: W={stat:.4f}, p={p:.4f}")

# Variance Homogeneity Test (Levene's)
levene_stat, levene_p = levene(*[df[df["Topology"] == t]["PSI"] for t in df["Topology"].unique()])
print(f"Levene's Test: Stat={levene_stat:.4f}, p={levene_p:.4f}")

# ANOVA
anova_stat, anova_p = f_oneway(*[df[df["Topology"] == t]["PSI"] for t in df["Topology"].unique()])
print(f"ANOVA: Stat={anova_stat:.4f}, p={anova_p:.4f}")

# Post-hoc Tukey HSD if ANOVA is significant
if anova_p < 0.05:
    tukey_results = pairwise_tukeyhsd(df["PSI"], df["Topology"], alpha=0.05)
    print(tukey_results)

# Compute Stiffness (Elastic Modulus Approximation)
df["Stress"] = df["PSI"]  # Assuming PSI as stress
df["Strain"] = df["Time (ms)"] / max(df["Time (ms)"])  # Normalize time as proxy for strain

# Linear Fit (Stiffness Calculation)
stiffness = {}
for topology in df["Topology"].unique():
    subset = df[df["Topology"] == topology]
    slope, intercept = np.polyfit(subset["Strain"], subset["Stress"], 1)
    stiffness[topology] = slope
    print(f"Estimated Stiffness for {topology}: {slope:.4f} PSI/strain")

# Visualization
plt.figure(figsize=(10, 6))
sns.boxplot(x="Topology", y="PSI", data=df, palette="Set2")
plt.title("PSI Distribution by Topology")
plt.ylabel("PSI")
plt.xlabel("Topology")
plt.show()

# Save processed data
df.to_csv("lattice_processed.csv", index=False)
