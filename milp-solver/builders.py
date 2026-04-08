"""
builders.py — Model Builders

Construct MILP models for Knapsack, TSP, and CVRP problems.
"""

from model import Model
from utils import compute_distance_matrix


def build_knapsack_model(instance):
    """Build a knapsack MILP model."""
    model = Model(name=instance["name"])
    n = instance["n"]
    values = instance["values"]
    weights = instance["weights"]
    capacity = instance["capacity"]

    for i in range(n):
        model.add_variable(name=f"x_{i}", var_type="binary", lower=0, upper=1)

    model.set_objective(
        {f"x_{i}": float(values[i]) for i in range(n)},
        sense="maximize"
    )

    model.add_constraint(
        {f"x_{i}": float(weights[i]) for i in range(n)},
        sense="<=",
        rhs=float(capacity),
        name="capacity"
    )

    return model


def build_tsp_model(instance):
    """Build a TSP MILP model with MTZ subtour elimination."""
    coords = instance["coords"]
    metric = instance["metric"]
    n = len(coords)
    dist = compute_distance_matrix(coords, metric=metric)

    model = Model(name=instance["name"])
    x = {}
    u = {}

    # Binary allocation variables
    for i in range(n):
        for j in range(n):
            if i != j:
                x[(i, j)] = model.add_variable(
                    name=f"x_{i}_{j}",
                    var_type="binary",
                    lower=0,
                    upper=1
                )

    # Continuous MTZ variables
    for i in range(n):
        u[i] = model.add_variable(
            name=f"u_{i}",
            var_type="continuous",
            lower=0,
            upper=n
        )

    # Objective: minimize distance
    model.set_objective(
        {f"x_{i}_{j}": float(dist[i, j]) for (i, j) in x},
        sense="minimize"
    )

    # Flow conservation: out-degree = 1
    for i in range(n):
        model.add_constraint(
            {f"x_{i}_{j}": 1.0 for j in range(n) if i != j},
            sense="==",
            rhs=1.0,
            name=f"out_{i}"
        )

    # Flow conservation: in-degree = 1
    for j in range(n):
        model.add_constraint(
            {f"x_{i}_{j}": 1.0 for i in range(n) if i != j},
            sense="==",
            rhs=1.0,
            name=f"in_{j}"
        )

    # MTZ anchor
    model.add_constraint({"u_0": 1.0}, sense="==", rhs=0.0, name="anchor_u0")

    # MTZ subtour elimination
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                model.add_constraint(
                    {f"u_{i}": 1.0, f"u_{j}": -1.0, f"x_{i}_{j}": float(n)},
                    sense="<=",
                    rhs=float(n - 1),
                    name=f"mtz_{i}_{j}"
                )

    return model


def build_cvrp_model(instance):
    """Build a CVRP MILP model."""
    coords = instance["coords"]
    demands = instance["demands"]
    capacity = instance["capacity"]
    vehicles = instance.get("vehicles", 1)
    metric = instance.get("metric", "euclidean")
    n = len(coords)
    dist = compute_distance_matrix(coords, metric=metric)

    model = Model(name=instance["name"])
    x = {}
    u = {}

    # Binary allocation variables
    for i in range(n):
        for j in range(n):
            if i != j:
                x[(i, j)] = model.add_variable(
                    name=f"x_{i}_{j}",
                    var_type="binary",
                    lower=0,
                    upper=1
                )

    # Continuous load variables
    for i in range(n):
        if i == 0:
            u[i] = model.add_variable(name="u_0", var_type="continuous", lower=0, upper=capacity)
        else:
            u[i] = model.add_variable(
                name=f"u_{i}",
                var_type="continuous",
                lower=float(demands[i]),
                upper=float(capacity)
            )

    # Objective: minimize distance
    model.set_objective(
        {f"x_{i}_{j}": float(dist[i, j]) for (i, j) in x},
        sense="minimize"
    )

    # Depot out-degree = vehicles
    model.add_constraint(
        {f"x_{0}_{j}": 1.0 for j in range(1, n)},
        sense="==",
        rhs=float(vehicles),
        name="depot_out"
    )

    # Depot in-degree = vehicles
    model.add_constraint(
        {f"x_{i}_0": 1.0 for i in range(1, n)},
        sense="==",
        rhs=float(vehicles),
        name="depot_in"
    )

    # Customer out-degree = 1
    for i in range(1, n):
        model.add_constraint(
            {f"x_{i}_{j}": 1.0 for j in range(n) if i != j},
            sense="==",
            rhs=1.0,
            name=f"out_{i}"
        )

    # Customer in-degree = 1
    for i in range(1, n):
        model.add_constraint(
            {f"x_{j}_{i}": 1.0 for j in range(n) if i != j},
            sense="==",
            rhs=1.0,
            name=f"in_{i}"
        )

    # Capacity anchor
    model.add_constraint({"u_0": 1.0}, sense="==", rhs=0.0, name="anchor_u0")

    # Capacity constraints
    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                model.add_constraint(
                    {
                        f"u_{i}": 1.0,
                        f"u_{j}": -1.0,
                        f"x_{i}_{j}": float(capacity)
                    },
                    sense="<=",
                    rhs=float(capacity - demands[j]),
                    name=f"cap_{i}_{j}"
                )

    return model
