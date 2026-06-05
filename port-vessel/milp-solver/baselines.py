"""
baselines.py — Baseline Solvers (PuLP/CBC)

Implementations using PuLP and CBC for comparison benchmarking.
"""

import time
import numpy as np
from pulp import (
    LpProblem, LpVariable, lpSum,
    LpMinimize, LpMaximize, PULP_CBC_CMD,
    LpStatus, value
)
from utils import compute_distance_matrix


def run_pulp_knapsack(instance):
    """Solve knapsack using PuLP/CBC."""
    n = instance["n"]
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]

    prob = LpProblem(instance["name"], LpMaximize)
    x = [LpVariable(f"x_{i}", lowBound=0, upBound=1, cat="Binary") for i in range(n)]

    prob += lpSum(values[i] * x[i] for i in range(n))
    prob += lpSum(weights[i] * x[i] for i in range(n)) <= capacity

    start = time.perf_counter()
    prob.solve(PULP_CBC_CMD(msg=0, timeLimit=60))
    elapsed = time.perf_counter() - start

    status = LpStatus[prob.status]
    obj = value(prob.objective) if prob.status == 1 else None

    return {"status": status, "obj": obj, "time": elapsed}


def run_pulp_tsp(instance):
    """Solve TSP using PuLP/CBC with MTZ subtour elimination."""
    coords = instance["coords"]
    metric = instance["metric"]
    n = len(coords)
    dist = compute_distance_matrix(coords, metric=metric)

    prob = LpProblem(instance["name"], LpMinimize)
    x = {(i, j): LpVariable(f"x_{i}_{j}", lowBound=0, upBound=1, cat="Binary")
         for i in range(n) for j in range(n) if i != j}
    u = {i: LpVariable(f"u_{i}", lowBound=0, upBound=n, cat="Continuous") for i in range(n)}

    prob += lpSum(dist[i, j] * x[i, j] for (i, j) in x)

    for i in range(n):
        prob += lpSum(x[i, j] for j in range(n) if i != j) == 1
    for j in range(n):
        prob += lpSum(x[i, j] for i in range(n) if i != j) == 1

    prob += u[0] == 0
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                prob += u[i] - u[j] + n * x[i, j] <= n - 1

    start = time.perf_counter()
    prob.solve(PULP_CBC_CMD(msg=0, timeLimit=60))
    elapsed = time.perf_counter() - start

    status = LpStatus[prob.status]
    obj = value(prob.objective) if prob.status == 1 else None

    return {"status": status, "obj": obj, "time": elapsed}


def run_pulp_cvrp(instance):
    """Solve CVRP using PuLP/CBC with flow relaxation."""
    coords = instance["coords"]
    demands = instance["demands"]
    capacity = instance["capacity"]
    vehicles = instance.get("vehicles", 1)
    metric = instance.get("metric", "euclidean")
    n = len(coords)
    dist = compute_distance_matrix(coords, metric=metric)

    prob = LpProblem(instance["name"], LpMinimize)

    x = {(i, j): LpVariable(f"x_{i}_{j}", lowBound=0, upBound=1, cat="Binary")
         for i in range(n) for j in range(n) if i != j}
    u = {i: LpVariable(f"u_{i}", lowBound=0, upBound=capacity, cat="Continuous") for i in range(n)}

    prob += lpSum(dist[i, j] * x[i, j] for (i, j) in x)

    # Depot constraints
    prob += lpSum(x[0, j] for j in range(1, n)) == vehicles
    prob += lpSum(x[i, 0] for i in range(1, n)) == vehicles

    # Customer constraints
    for i in range(1, n):
        prob += lpSum(x[i, j] for j in range(n) if i != j) == 1
        prob += lpSum(x[j, i] for j in range(n) if i != j) == 1

    # Capacity constraints
    prob += u[0] == 0
    for i in range(1, n):
        prob += u[i] >= demands[i]
        prob += u[i] <= capacity

    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                prob += u[i] - u[j] + capacity * x[i, j] <= capacity - demands[j]

    start = time.perf_counter()
    prob.solve(PULP_CBC_CMD(msg=0, timeLimit=60))
    elapsed = time.perf_counter() - start

    status = LpStatus[prob.status]
    obj = value(prob.objective) if prob.status == 1 else None

    return {"status": status, "obj": obj, "time": elapsed}
