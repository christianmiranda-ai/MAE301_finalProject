# process_latticeData.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import f_oneway, shapiro, levene
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from bokeh.plotting import figure, output_file, save
from bokeh.models import HoverTool

# begin reading the data from the csv
df = pd.read_csv("lattice_data.csv", encoding="windows-1252")

# convert force values to PSI based on the boundary conditions (surface area)
# of the where the load is applied (2" x 2" = 4 in²)
df["PSI"] = df["Force (kg)"] * 2.205 / 4  # kg to lbs, then PSI

# simple stats, mean (x bar) and stdev (sigma)
means = df.groupby("Topology")["PSI"].mean()
stds = df.groupby("Topology")["PSI"].std()
print("Means:\n", means)
print("Standard Deviations:\n", stds)

# checking to see if the data follows normal distribution via Shapiro-Wilk's test
for topology in df["Topology"].unique():
    stat, p = shapiro(df[df["Topology"] == topology]["PSI"])
    print(f"Shapiro-Wilk Test for {topology}: W={stat:.4f}, p={p:.4f}")

# checking to see if variance is equal across all topologies via Levene's test
levene_stat, levene_p = levene(*[df[df["Topology"] == t]["PSI"] for t in df["Topology"].unique()])
print(f"Levene's Test: Stat={levene_stat:.4f}, p={levene_p:.4f}")

# using one-way ANOVA to check if at least one group's mean differs from the rest (testing null hypothesis)
anova_stat, anova_p = f_oneway(*[df[df["Topology"] == t]["PSI"] for t in df["Topology"].unique()])
print(f"ANOVA: Stat={anova_stat:.4f}, p={anova_p:.4f}")

# if ANOVA IS significant, applying tukey's HSD test to see WHICH differ from the rest
if anova_p < 0.05:
    tukey_results = pairwise_tukeyhsd(df["PSI"], df["Topology"], alpha=0.05)
    print(tukey_results)

# estimating the elastic modulus calculation, ASSUMING that deformation is linear and thus
# the displacement is proportionate to the time
df["Stress"] = df["PSI"]  # using previous calcs/data to develop the stress side of the curve
df["Strain"] = df["Time (ms)"] / max(df["Time (ms)"])  # 

# stiffness calculation for each topology
stiffness = {}
for topology in df["Topology"].unique():
    subset = df[df["Topology"] == topology]
    slope, intercept = np.polyfit(subset["Strain"], subset["Stress"], 1)
    stiffness[topology] = slope
    print(f"Estimated Stiffness for {topology}: {slope:.4f} PSI/strain")

# end calcs! ---------- ---------- ---------- ---------- ----------
# bokeh stuff

output_file("docs/interactive_plot.html") #generating file for static interactive github pages

# plotting graph framework
figurePlot = figure(title="Stress-Strain Curve", x_axis_label="Strain", y_axis_label="Stress (PSI)", width=800, height=500)

# hover tool addition (consider removing if needed)
hover = HoverTool(tooltips=[("Topology", "@Topology"),("Stress", "@y"),("Strain","@x")])
figurePlot.add_tools(hover)

for topology in df["Topology"].unique(): # plots the relative stress-strain curve of a given topology type
    subset = df[df["Topology"] == topology]
    figurePlot.line(subset["Strain"], subset["Stress"], legend_label=topology, line_width=2)

save(figurePlot)

df.to_csv("lattice_processed.csv", index=False) #resave processed data to overwrite original file

