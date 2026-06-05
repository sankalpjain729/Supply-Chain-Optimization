"""
benchmark_runner.py — Benchmark Orchestration

Run full benchmark suite comparing custom solver against baseline.
"""

import time
import pandas as pd
from branch_and_bound import solve_model, solution_dict
from builders import build_knapsack_model, build_tsp_model, build_cvrp_model
from baselines import run_pulp_knapsack, run_pulp_tsp, run_pulp_cvrp
from validators import validate_knapsack_solution, validate_tsp_solution, validate_cvrp_solution
from utils import compute_gap_pct
from branch_and_bound import TOL


def run_one_case(case):
    """
    Run a single benchmark case.
    
    Returns:
        dict with results: Family, Instance, Success, Gap, etc.
    """
    family = case["family"]
    max_nodes = case.get("max_nodes", 50000)
    tol = TOL

    if family.startswith("Knapsack"):
        # Knapsack problem
        model = build_knapsack_model(case)
        start = time.perf_counter()
        your_res = solve_model(model, max_nodes=max_nodes, tol=tol)
        your_time = time.perf_counter() - start

        base_start = time.perf_counter()
        base_res = run_pulp_knapsack(case)
        base_time = time.perf_counter() - base_start

        valid, remark = validate_knapsack_solution(
            solution_dict(model, your_res.x) if your_res.success else None, case
        )

    elif family == "TSPLIB":
        # TSP problem
        model = build_tsp_model(case)
        start = time.perf_counter()
        your_res = solve_model(model, max_nodes=5000, tol=tol)
        your_time = time.perf_counter() - start

        base_start = time.perf_counter()
        base_res = run_pulp_tsp(case)
        base_time = time.perf_counter() - base_start

        valid, remark = validate_tsp_solution(
            solution_dict(model, your_res.x) if your_res.success else None,
            len(case["coords"])
        )

    elif family == "CVRPLIB":
        # CVRP problem
        model = build_cvrp_model(case)
        start = time.perf_counter()
        your_res = solve_model(model, max_nodes=max_nodes, tol=tol)
        your_time = time.perf_counter() - start

        base_start = time.perf_counter()
        base_res = run_pulp_cvrp(case)
        base_time = time.perf_counter() - base_start

        valid, remark = validate_cvrp_solution(
            solution_dict(model, your_res.x) if your_res.success else None, case
        )

    else:
        raise ValueError(f"Unknown family: {family}")

    your_obj = getattr(your_res, "fun", None)
    baseline_obj = base_res["obj"]
    gap_pct = compute_gap_pct(case["sense"], your_obj, baseline_obj)

    return {
        "Family": family,
        "Instance": case["name"],
        "n": case.get("n", len(case.get("coords", []))),
        "Success": bool(getattr(your_res, "success", False)),
        "Your Obj": your_obj,
        "Baseline Obj": baseline_obj,
        "Gap %": gap_pct,
        "Your Time (s)": round(your_time, 4),
        "Baseline Time (s)": round(base_time, 4),
        "Nodes": getattr(your_res, "nodes", None),
        "Valid": valid,
        "Remark": remark,
        "Baseline Status": base_res["status"],
    }


def run_benchmark_suite(benchmark_cases):
    """
    Run full benchmark suite.
    
    Args:
        benchmark_cases : list of case dicts
    
    Returns:
        pandas DataFrame with results
    """
    results = []

    for case in benchmark_cases:
        print(f"Running {case['family']}: {case['name']}")
        try:
            results.append(run_one_case(case))
        except Exception as e:
            results.append({
                "Family": case["family"],
                "Instance": case["name"],
                "n": case.get("n", len(case.get("coords", []))),
                "Success": False,
                "Your Obj": None,
                "Baseline Obj": None,
                "Gap %": None,
                "Your Time (s)": None,
                "Baseline Time (s)": None,
                "Nodes": None,
                "Valid": False,
                "Remark": f"ERROR: {e}",
                "Baseline Status": None,
            })

    df = pd.DataFrame(results)

    # Sort by family and instance size
    sort_cols = ["Family", "n", "Instance"]
    for col in sort_cols:
        if col not in df.columns:
            df[col] = None

    df = df.sort_values(by=["Family", "n", "Instance"]).reset_index(drop=True)

    # Summary by family
    summary = (
        df.assign(
            GapPctNum=pd.to_numeric(df["Gap %"], errors="coerce"),
            YourTimeNum=pd.to_numeric(df["Your Time (s)"], errors="coerce"),
            BaseTimeNum=pd.to_numeric(df["Baseline Time (s)"], errors="coerce"),
            NodesNum=pd.to_numeric(df["Nodes"], errors="coerce"),
        )
        .groupby("Family", dropna=False)
        .agg(
            Cases=("Instance", "count"),
            Successes=("Success", "sum"),
            AvgGapPct=("GapPctNum", "mean"),
            AvgYourTime=("YourTimeNum", "mean"),
            AvgBaseTime=("BaseTimeNum", "mean"),
            AvgNodes=("NodesNum", "mean"),
        )
        .reset_index()
    )

    return df, summary
