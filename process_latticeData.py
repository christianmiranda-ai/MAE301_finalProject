# to be used for processing the data we wrote from Arduino IDE to Excel and now into Python for data visualization later on
import pandas as pd
import numpy as np
from scipy.stats import f_oneway

# Read CSV (exported from Excel or PLX-DAQ)
df = pd.read_csv("lattice_data.csv", encoding="windows-1252")  # adjusted with new encoding due to error

# Assume you manually add a "Topology" column (cubic, octet, gyroid) in Excel
# Example data structure: Time (ms), Force (kg), Topology
# Find peak force per test (simplified: max force per topology group)
df_peak = df.groupby("Topology").agg({"Force (kg)": "max"}).reset_index()

# Convert to PSI (assuming 2 cm x 2 cm = 0.62 in²; adjust area later)
df_peak["PSI"] = df_peak["Force (kg)"] * 2.205 / 0.62  # kg to lbs, then PSI

# Stats
means = df_peak.groupby("Topology")["PSI"].mean()
stds = df_peak.groupby("Topology")["PSI"].std()
print("Means:\n", means)
print("Standard Deviations:\n", stds)

# ANOVA
cubic = df_peak[df_peak["Topology"] == "cubic"]["PSI"]
octet = df_peak[df_peak["Topology"] == "octet"]["PSI"]
gyroid = df_peak[df_peak["Topology"] == "gyroid"]["PSI"]
f_stat, p_val = f_oneway(cubic, octet, gyroid)
print(f"ANOVA: F={f_stat}, p={p_val}")

# Save processed data
df_peak.to_csv("lattice_processed.csv", index=False)
