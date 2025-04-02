# final stage where we integrate processed data into Bokeh for easy visualization on behalf of the end user

from bokeh.plotting import figure, show
from bokeh.io import output_file
import pandas as pd

# Load processed data
df = pd.read_csv("lattice_processed.csv")

# Bokeh plot
output_file("lattice_strength.html")  # Saves to local HTML
p = figure(title="Lattice Compressive Strength by Topology",
           x_axis_label="Topology",
           y_axis_label="PSI",
           width=600, height=400)

# Bar plot of means
topologies = df["Topology"]
psi_values = df["PSI"]
p.vbar(x=topologies, top=psi_values, width=0.5, fill_color="blue", legend_label="PSI")

# Style
p.xgrid.grid_line_color = None
p.y_range.start = 0
p.legend.location = "top_right"

show(p)
