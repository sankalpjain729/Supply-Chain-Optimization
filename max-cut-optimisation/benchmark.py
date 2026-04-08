import os
import pandas as pd

from utils import load_graph, SAParams
from sa import multi_start_sa

"""
Benchmark runner for Max-Cut SA solver.
Compares our results against Toshiba Simulated Bifurcation Machine (SBM) values.
"""

# ---------------------------------------------------------------------------
# Toshiba SBM reported values (from their benchmark papers)
# ---------------------------------------------------------------------------

TOSHIBA_SBM = {
    "G1": 11624,
    "G2": 11620,
    "G3": 11622,
    "G4": 11646,
    "G5": 11631,
    "G6": 2178,
    "G7": 2006,
    "G8": 2005,
    "G9": 2054,
    "G10": 2000,
    "G11": 564,
    "G12": 556,
    "G13": 582,
    "G14": 3064,
    "G15": 3050,
    "G16": 3052,
    "G17": 3047,
    "G18": 992,
    "G19": 906,
    "G20": 941,
    "G21": 931,
    "G22": 13359,
    "G23": 13344,
    "G24": 13337,
    "G25": 13340,
    "G26": 13328,
    "G27": 3341,
    "G28": 3298,
    "G29": 3405,
    "G30": 3413,
    "G31": 3310,
    "G32": 1410,
    "G33": 1382,
    "G34": 1384,
    "G35": 7687,
    "G36": 7680,
    "G37": 7691,
    "G38": 7688,
    "G39": 2408,
    "G40": 2400,
    "G41": 2405,
    "G42": 2481,
    "G43": 6660,
    "G44": 6650,
    "G45": 6654,
    "G46": 6649,
    "G47": 6657,
    "G48": 6000,
    "G49": 6000,
    "G50": 5880,
    "G51": 3848,
    "G52": 3851,
    "G53": 3850,
    "G54": 3852,
    "G55": 10299,
    "G56": 4017,
    "G57": 3494,
    "G58": 19293,
    "G59": 6086,
    "G60": 14188,
    "G61": 5796,
    "G62": 4870,
    "G63": 27045,
    "G64": 8751,
    "G65": 5562,
    "G66": 6364,
    "G67": 6950,
    "G70": 9591,
    "G72": 7006,
}


def run_benchmark(
    graph_names=None,
    n_starts=5,
    alpha=0.999995,
):
    """Run SA on specified GSET graphs and compare with Toshiba SBM."""
    if graph_names is None:
        graph_names = ["G1", "G2", "G3", "G4", "G5"]

    results = []
    params = SAParams(T_init=0, alpha=alpha, seed=42)

    for name in graph_names:
        print(f"\n{'='*60}")
        print(f"Running {name}...")
        print(f"{'='*60}")

        base_dir = os.path.dirname(os.path.abspath(__file__))  # Use local repo root
        filepath = os.path.join(base_dir, "Graph_Data", f"{name}.txt")

        if not os.path.exists(filepath):
            print(f"  Skipping {name} (file not found)")
            continue

        n, edges, adj = load_graph(filepath)
        print(f"  Loaded: {n} vertices, {len(edges)} edges")

        result = multi_start_sa(n, edges, adj, n_starts=n_starts, params=params)

        toshiba = TOSHIBA_SBM.get(name, None)

        gap = None
        if toshiba:
            gap = (toshiba - result.best_cut) / toshiba * 100

        row = {
            "graph": name,
            "n": n,
            "edges": len(edges),
            "our_cut": result.best_cut,
            "toshiba_sbm": toshiba,
            "gap_%": round(gap, 2) if gap is not None else None,
            "time_s": round(result.elapsed, 2),
            "history": result.history,
        }
        results.append(row)
        # SAVE PROGRESS AFTER EACH GRAPH
        temp_df = pd.DataFrame(results)
        temp_df = temp_df.drop(columns=["history"], errors="ignore")

        RESULTS_DIR = os.path.join(base_dir, "results")  # Adjust
        os.makedirs(RESULTS_DIR, exist_ok=True)
        temp_path = os.path.join(RESULTS_DIR, "benchmark_progress.csv")
        temp_df.to_csv(temp_path, index=False)

        print(f"  Progress saved ({len(results)} graphs)")

        print(f"\n  Our cut:     {result.best_cut}")
        if toshiba:
            print(f"  Toshiba SBM: {toshiba}")
            print(f"  Gap:         {gap:.2f}%")
        print(f"  Time:        {result.elapsed:.2f}s")

    return results


def save_results(results, RESULTS_DIR):
    """Convert results to a DataFrame, print it, and save as CSV."""
    os.makedirs(RESULTS_DIR, exist_ok=True)

    df = pd.DataFrame(results)
    df = df.drop(columns=["history"])

    print("\n")
    print(df.head(5))

    filepath = os.path.join(RESULTS_DIR, "benchmark_results.csv")
    df.to_csv(filepath, index=False)
    print(f"\nResults saved to {filepath}")

    return df