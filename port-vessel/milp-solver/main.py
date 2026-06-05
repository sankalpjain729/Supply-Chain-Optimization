"""
main.py — MILP Solver Benchmark Entry Point

Run the full benchmark suite and generate results.
"""

import pandas as pd
from benchmarks import ALL_BENCHMARK_CASES
from benchmark_runner import run_benchmark_suite


def main():
    """Run benchmark suite and display results."""
    print("=" * 80)
    print("MILP SOLVER BENCHMARK")
    print("Custom Branch-and-Bound Solver vs. PuLP/CBC")
    print("=" * 80)
    print()

    df, summary = run_benchmark_suite(ALL_BENCHMARK_CASES)

    # Configure pandas display
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 220)

    print("\n" + "=" * 80)
    print("FULL BENCHMARK TABLE")
    print("=" * 80 + "\n")
    print(df.to_string(index=False))

    print("\n\n" + "=" * 80)
    print("FAMILY SUMMARY")
    print("=" * 80 + "\n")
    print(summary.to_string(index=False))

    # Save results
    df.to_csv("results.csv", index=False)
    summary.to_csv("results_summary.csv", index=False)
    print("\n\nResults saved to results.csv and results_summary.csv")

    return df, summary


if __name__ == "__main__":
    df, summary = main()
