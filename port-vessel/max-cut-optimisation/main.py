import os
import pandas as pd

"""
Max-Cut QUBO Solver — Main entry point.
Run: python main.py
"""

# Define directories relative to this repository root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Graph_Data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

# Create folders if not exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Check if data exists
files = os.listdir(DATA_DIR)

if len(files) == 0:
    raise Exception(
        "❌ Graph_Data folder is EMPTY.\n\n"
        "👉 Upload GSET .txt files into:\n"
        f"{DATA_DIR}\n\n"
        "Then re-run the notebook."
    )
else:
    print("✅ Data files found:", files[:5])

from benchmark import run_benchmark, save_results

print("=" * 60)
print("BENCHMARK: Our SA vs Toshiba SBM")
print("=" * 60)

# graph_names = ["G1", "G2", "G3", "G4", "G5"]
graph_names = ["G1"]
# graph_names = [
#     "G1","G2","G3","G4","G5","G6","G7","G8","G9","G10",
#     "G11","G12","G13","G14","G15","G16","G17","G18","G19","G20",
#     "G21","G22","G23","G24","G25","G26","G27","G28","G29","G30",
#     "G31","G32","G33","G34","G35","G36","G37","G38","G39","G40",
#     "G41","G42","G43","G44","G45","G46","G47","G48","G49","G50",
#     "G51","G52","G53","G54","G55","G56","G57","G58","G59","G60",
#     "G61","G62","G63","G64","G65","G66","G67","G70", "G72"
# ]

results = run_benchmark(graph_names=graph_names)
df = save_results(results, RESULTS_DIR)

print(df.head(40))

print("Total gap sum:", df['gap_%'].sum())