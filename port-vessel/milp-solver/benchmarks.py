"""
benchmarks.py — Benchmark Problem Instances

Generate and load test instances for Knapsack, TSP, and CVRP.
"""

import os
import numpy as np

try:
    import vrplib
except ImportError:
    vrplib = None


# ===================================================
# Knapsack Generators
# ===================================================

def generate_knapsack_instance(n, seed=0,
                               value_low=10, value_high=100,
                               weight_low=5, weight_high=30,
                               capacity_ratio=0.5):
    """Generate random knapsack instance."""
    rng = np.random.default_rng(seed)
    values = rng.integers(value_low, value_high + 1, size=n)
    weights = rng.integers(weight_low, weight_high + 1, size=n)
    capacity = int(capacity_ratio * weights.sum())

    return {
        "family": "Knapsack",
        "name": f"kp_n{n}_seed{seed}",
        "n": n,
        "values": values,
        "weights": weights,
        "capacity": capacity,
        "sense": "maximize",
        "max_nodes": 20000,
    }


def generate_hard_knapsack(n, seed=0):
    """Generate hard knapsack instance (correlated values/weights)."""
    rng = np.random.default_rng(seed)
    weights = rng.integers(10, 50, size=n)
    values = weights + rng.integers(-3, 3, size=n)
    capacity = int(0.5 * weights.sum())

    return {
        "family": "Knapsack-Hard",
        "name": f"hard_kp_n{n}_seed{seed}",
        "n": n,
        "values": values,
        "weights": weights,
        "capacity": capacity,
        "sense": "maximize",
        "max_nodes": 50000,
    }


def generate_tight_knapsack(n, seed=0):
    """Generate tight knapsack (tight capacity constraint)."""
    rng = np.random.default_rng(seed)
    values = rng.integers(10, 100, size=n)
    weights = rng.integers(10, 100, size=n)
    capacity = int(0.3 * weights.sum())

    return {
        "family": "Knapsack-Tight",
        "name": f"tight_kp_n{n}_seed{seed}",
        "n": n,
        "values": values,
        "weights": weights,
        "capacity": capacity,
        "sense": "maximize",
        "max_nodes": 50000,
    }


# Easy knapsack cases
EASY_KNAPSACK_CASES = [
    generate_knapsack_instance(8, seed=1),
    generate_knapsack_instance(10, seed=2),
    generate_knapsack_instance(12, seed=3),
]

# Hard knapsack cases
HARD_KNAPSACK_CASES = [
    generate_hard_knapsack(12, seed=1),
    generate_hard_knapsack(14, seed=2),
    generate_hard_knapsack(16, seed=3),
    generate_hard_knapsack(18, seed=4),
]

# Tight knapsack cases
TIGHT_KNAPSACK_CASES = [
    generate_tight_knapsack(12, seed=1),
    generate_tight_knapsack(14, seed=2),
    generate_tight_knapsack(16, seed=3),
    generate_tight_knapsack(18, seed=4),
]

# ===================================================
# TSPLIB Instances
# ===================================================

TSPLIB_CASES = [
    {
        "family": "TSPLIB",
        "name": "burma14",
        "metric": "geo",
        "coords": [
            (16.47, 96.10), (16.47, 94.44), (20.09, 92.54), (22.39, 93.37),
            (25.23, 97.24), (22.00, 96.05), (20.47, 97.02), (17.20, 96.29),
            (16.30, 97.38), (14.05, 98.12), (16.53, 97.38), (21.52, 95.59),
            (19.41, 97.13), (20.09, 94.55),
        ],
        "sense": "minimize",
        "max_nodes": 50000,
    },
    {
        "family": "TSPLIB",
        "name": "ulysses22",
        "metric": "geo",
        "coords": [
            (38.24, 20.42), (39.57, 26.15), (40.56, 25.32), (36.26, 23.12),
            (33.48, 10.54), (37.56, 12.19), (38.42, 13.11), (37.52, 20.44),
            (41.23, 9.10), (41.17, 13.05), (36.08, -5.21), (38.47, 15.13),
            (38.15, 15.35), (37.51, 15.17), (35.49, 14.32), (39.36, 19.56),
            (38.09, 24.36), (36.09, 23.00), (40.44, 13.57), (40.33, 14.15),
            (40.37, 14.23), (37.57, 22.56),
        ],
        "sense": "minimize",
        "max_nodes": 50000,
    },
]

# ===================================================
# CVRPLIB Loader
# ===================================================

def _pick(raw, *keys, default=None):
    """Helper to find a key in case-insensitive dict."""
    for k in keys:
        if k in raw:
            return raw[k]
        kl = str(k).lower()
        ku = str(k).upper()
        if kl in raw:
            return raw[kl]
        if ku in raw:
            return raw[ku]
    return default


def normalize_vrplib_instance(raw, name):
    """Normalize VRPLib instance to standard format."""
    coords = _pick(raw, "node_coord", "NODE_COORD_SECTION", "coordinates", "coord")
    demands = _pick(raw, "demand", "DEMAND_SECTION", "demands")
    capacity = _pick(raw, "capacity", "CAPACITY")
    vehicles = _pick(raw, "vehicles", "VEHICLES", default=1)

    if coords is None or demands is None or capacity is None:
        return None

    coords = np.asarray(coords, dtype=float)
    demands = np.asarray(demands, dtype=float).reshape(-1)

    if len(demands) == len(coords) and len(demands) > 0:
        demands[0] = 0.0

    return {
        "family": "CVRPLIB",
        "name": name,
        "coords": coords,
        "demands": demands,
        "capacity": int(capacity),
        "vehicles": int(vehicles) if vehicles is not None else 1,
        "metric": "euclidean",
        "sense": "minimize",
        "max_nodes": 50000,
    }


def load_cvrplib_case(case_name, folder="cvrplib_instances"):
    """Load a CVRPLIB instance (downloads if needed)."""
    if vrplib is None:
        return None

    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{case_name}.vrp")

    if not os.path.exists(path):
        try:
            vrplib.download_instance(case_name, folder)
        except Exception:
            return None

    try:
        raw = vrplib.read_instance(path)
    except Exception:
        return None

    return normalize_vrplib_instance(raw, case_name)


CVRPLIB_TARGETS = ["E-n13-k4", "P-n16-k8"]
CVRPLIB_CASES = []
for nm in CVRPLIB_TARGETS:
    inst = load_cvrplib_case(nm)
    if inst is not None:
        CVRPLIB_CASES.append(inst)


# ===================================================
# Combined benchmark set
# ===================================================

ALL_BENCHMARK_CASES = []
ALL_BENCHMARK_CASES.extend(EASY_KNAPSACK_CASES)
ALL_BENCHMARK_CASES.extend(HARD_KNAPSACK_CASES)
ALL_BENCHMARK_CASES.extend(TIGHT_KNAPSACK_CASES)
ALL_BENCHMARK_CASES.extend(TSPLIB_CASES)
ALL_BENCHMARK_CASES.extend(CVRPLIB_CASES)
