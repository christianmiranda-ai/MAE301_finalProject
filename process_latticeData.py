# process_latticeData.py

# library import:
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

# checking to see if the data follows normal distribution via Shapiro-Wilk's test (STEP 1A)
for topology in df["Topology"].unique():
    stat, p = shapiro(df[df["Topology"] == topology]["PSI"])
    print(f"Shapiro-Wilk Test for {topology}: W={stat:.4f}, p={p:.4f}")

# checking to see if variance is equal across all topologies via Levene's test (STEP 1B)
levene_stat, levene_p = levene(*[df[df["Topology"] == t]["PSI"] for t in df["Topology"].unique()])
print(f"Levene's Test: Stat={levene_stat:.4f}, p={levene_p:.4f}")

# using one-way ANOVA to check if at least one group's mean differs from the rest (testing null hypothesis)
# this is (STEP 2)
anova_stat, anova_p = f_oneway(*[df[df["Topology"] == t]["PSI"] for t in df["Topology"].unique()])
print(f"ANOVA: Stat={anova_stat:.4f}, p={anova_p:.4f}")

# if ANOVA IS significant, applying tukey's HSD test to see WHICH differ from the rest (STEP 3)
if anova_p < 0.05:
    tukey_results = pairwise_tukeyhsd(df["PSI"], df["Topology"], alpha=0.05)
    print(tukey_results)

# estimating the elastic modulus calculation, ASSUMING that deformation is linear and thus
# the displacement is proportionate to the time (STEP 5)
df["Stress"] = df["PSI"]  # using previous calcs/data to develop the stress side of the curve
df["Strain"] = df["Time (ms)"] / max(df["Time (ms)"])  # now using "linear time/displacement" idea 4 strain

# stiffness calculation for each topology
stiffness = {}
for topology in df["Topology"].unique():
    subset = df[df["Topology"] == topology]
    slope, intercept = np.polyfit(subset["Strain"], subset["Stress"], 1)
    stiffness[topology] = slope
    print(f"Estimated Stiffness for {topology}: {slope:.4f} PSI/strain")

# end calcs! ---------- ---------- ---------- ---------- ----------
# bokeh stuff

# 1. Bar Plot: Mean PSI with Error Bars
output_file("mean_strength.html")
bar_plot = figure(title="Mean Compressive Strength by Topology", 
                  x_axis_label="Topology", y_axis_label="Mean PSI", 
                  width=800, height=500, x_range=df["Topology"].unique())
bar_plot.vbar(x=df["Topology"].unique(), top=means, width=0.5, fill_color="blue", legend_label="Mean PSI")
bar_plot.segment(x0=df["Topology"].unique(), y0=means-stds, x1=df["Topology"].unique(), y1=means+stds, 
                 color="black", line_width=2, legend_label="Std Dev")
bar_plot.add_tools(HoverTool(tooltips=[("Topology", "@x"), ("Mean PSI", "@top"), ("SD", f"{stds.values[0]:.2f}")]))
bar_plot.legend.click_policy = "hide"
save(bar_plot)

# 2. Box Plot: PSI Distribution
output_file("box_strength.html")
box_plot = figure(title="PSI Distribution by Topology", 
                  x_axis_label="Topology", y_axis_label="PSI", 
                  width=800, height=500, x_range=df["Topology"].unique())
for i, topology in enumerate(df["Topology"].unique()):
    subset = df[df["Topology"] == topology]["PSI"]
    q1, q2, q3 = subset.quantile([0.25, 0.5, 0.75])
    iqr = q3 - q1
    upper = q3 + 1.5 * iqr
    lower = q1 - 1.5 * iqr
    outliers = subset[(subset < lower) | (subset > upper)]
    box_plot.vbar(x=[topology], bottom=q1, top=q3, width=0.4, fill_color="lightblue")
    box_plot.segment(x0=[topology], y0=q3, x1=[topology], y1=upper, color="black")
    box_plot.segment(x0=[topology], y0=q1, x1=[topology], y1=lower, color="black")
    box_plot.scatter(x=[topology]*len(outliers), y=outliers, size=10, color="red", legend_label="Outliers")
box_plot.add_tools(HoverTool(tooltips=[("Topology", "@x"), ("Median", f"{q2:.2f}"), ("Q1", f"{q1:.2f}"), ("Q3", f"{q3:.2f}")]))
save(box_plot)

# 3. Scatter Plot: Individual PSI
from bokeh.palettes import Category10
output_file("scatter_strength.html")
scatter_plot = figure(title="Individual Compressive Strengths", 
                      x_axis_label="Topology", y_axis_label="PSI", 
                      width=800, height=500, x_range=df["Topology"].unique())
colors = Category10[5]
for i, topology in enumerate(df["Topology"].unique()):
    subset = df[df["Topology"] == topology]
    scatter_plot.scatter(x=[topology]*len(subset), y=subset["PSI"], size=10, color=colors[i], 
                         legend_label=topology, alpha=0.6)
scatter_plot.add_tools(HoverTool(tooltips=[("Topology", "@legend"), ("PSI", "@y"), ("Time", "@{Time (ms)}")]))
scatter_plot.legend.click_policy = "hide"
save(scatter_plot)

# 4. Enhanced Stress-Strain (replace current)
output_file("stress_strain.html")
stress_plot = figure(title="Stress-Strain Curves by Topology", 
                     x_axis_label="Strain", y_axis_label="Stress (PSI)", 
                     width=800, height=500)
stress_plot.add_tools(HoverTool(tooltips=[("Topology", "@Topology"), ("Stress", "@y"), ("Strain", "@x")]))
for i, topology in enumerate(df["Topology"].unique()):
    subset = df[df["Topology"] == topology]
    stress_plot.line(subset["Strain"], subset["Stress"], legend_label=topology, line_width=3, color=colors[i])
    stress_plot.scatter(subset["Strain"], subset["Stress"], size=10, color=colors[i], legend_label=topology)
stress_plot.legend.click_policy = "hide"
save(stress_plot)

print("All Bokeh plots saved: mean_strength.html, box_strength.html, scatter_strength.html, stress_strain.html")