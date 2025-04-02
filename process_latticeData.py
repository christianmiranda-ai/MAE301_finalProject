# process_latticeData.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import f_oneway, shapiro, levene
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# Read CSV
df = pd.read_csv("lattice_data.csv", encoding="windows-1252")

# Use all data (no max aggregation)
df_peak = df.copy()

# Convert to PSI (2" x 2" = 4 in²)
df_peak["PSI"] = df_peak["Force (kg)"] * 2.205 / 4  # kg to lbs, then PSI

# Stats
means = df_peak.groupby("Topology")["PSI"].mean()
stds = df_peak.groupby("Topology")["PSI"].std()
print("Means:\n", means)
print("Standard Deviations:\n", stds)

# Save processed data
df_peak.to_csv("lattice_processed.csv", index=False)