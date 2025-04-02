# MAE301_finalProject
Final project for my statistics for engineers course.

# Lattice Strength Project
The goal of this project is to investigate how different 3D-printed lattice topologies (04/02/25 TBD) affect the compressive strength of resin-printed parts using Elegoo ABS-like V2.0 and my Elegoo Saturn 3 Ultra printer. I plan to test samples with a 20-ton hydraulic press available to students via the ASU Chandler Innovation Center (ACIC). Alternatively, if the capabilities of the press and its pressure gauge exceed the resolution we seek, I'll switch to a more manual approach -- that is, a 500 kg load cell with manual load case implementation (i.e. weights). Regardless of the methodology at hand, the fundamental idea is to measure force at failure and use various analytical tools to present the data with.

- **Arduino**: `x.ino` - Logs force data
- **Data Processing**: `y.ino` - Converts to PSI, runs stats
- **Visualization**: `z.py` → `a.html` - Interactive plots
