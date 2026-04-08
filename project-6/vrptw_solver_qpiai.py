# -*- coding: utf-8 -*-
"""VRPTW Solver for QPIAI assignment.

This script builds a Vehicle Routing Problem with Time Windows (VRPTW)
using Pyomo and solves it with the open-source CBC solver.
"""

import math
import random

try:
    import pyomo.environ as pyo
except ImportError:
    pyo = None


def generate_dataset(n_customers=10, vehicle_capacity=100, n_vehicles=4, seed=42):
    """Generate a synthetic VRPTW dataset."""
    random.seed(seed)

    depot_x = 50
    depot_y = 50
    customers = []

    for i in range(1, n_customers + 1):
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        demand = random.randint(5, 30)
        service_time = random.randint(5, 15)
        tw_start = random.randint(0, 150)
        tw_end = tw_start + random.randint(30, 80)

        customers.append({
            "id": i,
            "x": x,
            "y": y,
            "demand": demand,
            "tw_start": tw_start,
            "tw_end": tw_end,
            "service_time": service_time,
        })

    return {
        "depot": {"x": depot_x, "y": depot_y},
        "customers": customers,
        "vehicle_capacity": vehicle_capacity,
        "n_vehicles": n_vehicles,
    }


def print_dataset(dataset):
    """Print the dataset in a readable table."""
    depot = dataset["depot"]
    print(f"Depot: ({depot['x']}, {depot['y']})")
    print(f"Vehicle capacity: {dataset['vehicle_capacity']}")
    print(f"Number of vehicles: {dataset['n_vehicles']}")
    print()
    print(f"{'ID':>4}  {'X':>4}  {'Y':>4}  {'Demand':>6}  {'TW_Start':>8}  {'TW_End':>6}  {'Service':>7}")
    print("-" * 55)
    for c in dataset["customers"]:
        print(f"{c['id']:>4}  {c['x']:>4}  {c['y']:>4}  {c['demand']:>6}  {c['tw_start']:>8}  {c['tw_end']:>6}  {c['service_time']:>7}")


def compute_distance_matrix(dataset):
    """Compute Euclidean distances between nodes."""
    depot = dataset["depot"]
    customers = dataset["customers"]
    coords = [(depot["x"], depot["y"])] + [(c["x"], c["y"]) for c in customers]

    dist = {}
    for i in range(len(coords)):
        for j in range(len(coords)):
            dx = coords[i][0] - coords[j][0]
            dy = coords[i][1] - coords[j][1]
            dist[i, j] = round(math.hypot(dx, dy), 2)

    return dist


def build_model(dataset, M=1000):
    """Build the VRPTW MILP model using Pyomo."""
    if pyo is None:
        raise ImportError("Pyomo is required to build the model. Install pyomo with pip.")

    customers = dataset["customers"]
    n = len(customers)
    m = dataset["n_vehicles"]
    Q = dataset["vehicle_capacity"]
    dist = compute_distance_matrix(dataset)

    N = list(range(n + 1))
    C = list(range(1, n + 1))
    K = list(range(m))

    q = {0: 0}
    for c in customers:
        q[c["id"]] = c["demand"]

    a = {0: 0}
    b = {0: 500}
    for c in customers:
        a[c["id"]] = c["tw_start"]
        b[c["id"]] = c["tw_end"]

    s = {0: 0}
    for c in customers:
        s[c["id"]] = c["service_time"]

    model = pyo.ConcreteModel("VRPTW")
    model.N = pyo.Set(initialize=N)
    model.C = pyo.Set(initialize=C)
    model.K = pyo.Set(initialize=K)

    model.x = pyo.Var(model.N, model.N, model.K, domain=pyo.Binary)
    model.T = pyo.Var(model.N, domain=pyo.NonNegativeReals)
    model.late = pyo.Var(model.C, domain=pyo.NonNegativeReals)
    model.overload = pyo.Var(model.K, domain=pyo.NonNegativeReals)
    model.skip = pyo.Var(model.C, domain=pyo.Binary)

    def obj_rule(m):
        total_dist = sum(dist[i, j] * m.x[i, j, k] for k in m.K for i in m.N for j in m.N)
        total_late = sum(100 * m.late[i] for i in m.C)
        total_overload = sum(500 * m.overload[k] for k in m.K)
        total_skip = sum(10000 * m.skip[i] for i in m.C)
        return total_dist + total_late + total_overload + total_skip

    model.objective = pyo.Objective(rule=obj_rule, sense=pyo.minimize)

    def visit_once_rule(m, j):
        return sum(m.x[i, j, k] for k in m.K for i in m.N if i != j) + m.skip[j] == 1

    model.visit_once = pyo.Constraint(model.C, rule=visit_once_rule)

    def flow_rule(m, j, k):
        return sum(m.x[i, j, k] for i in m.N) == sum(m.x[j, i, k] for i in m.N)

    model.flow = pyo.Constraint(model.C, model.K, rule=flow_rule)

    def start_depot_rule(m, k):
        return sum(m.x[0, j, k] for j in m.N) == 1

    model.start_depot = pyo.Constraint(model.K, rule=start_depot_rule)

    def end_depot_rule(m, k):
        return sum(m.x[i, 0, k] for i in m.N) == 1

    model.end_depot = pyo.Constraint(model.K, rule=end_depot_rule)

    def capacity_rule(m, k):
        return sum(q[i] * sum(m.x[i, j, k] for j in m.N) for i in m.C) <= Q + m.overload[k]

    model.capacity = pyo.Constraint(model.K, rule=capacity_rule)

    def tw_start_rule(m, i):
        return m.T[i] >= a[i]

    def tw_end_rule(m, i):
        return m.T[i] <= b[i] + m.late[i]

    model.tw_start = pyo.Constraint(model.C, rule=tw_start_rule)
    model.tw_end = pyo.Constraint(model.C, rule=tw_end_rule)

    def time_continuity_rule(m, i, j, k):
        if i == j:
            return pyo.Constraint.Skip
        return m.T[i] + s[i] + dist[i, j] - M * (1 - m.x[i, j, k]) <= m.T[j]

    model.time_cont = pyo.Constraint(model.N, model.C, model.K, rule=time_continuity_rule)

    def no_self_loop_rule(m, i, k):
        return m.x[i, i, k] == 0

    model.no_self_loop = pyo.Constraint(model.N, model.K, rule=no_self_loop_rule)

    return model


def solve_model(model, solver_name="cbc", time_limit=300):
    """Solve the model using the specified solver."""
    if pyo is None:
        raise ImportError("Pyomo is required to solve the model. Install pyomo with pip.")

    solver = pyo.SolverFactory(solver_name)
    if not solver.available(False):
        raise RuntimeError(f"Solver '{solver_name}' is not available. Install it and make it available to Pyomo.")

    if solver_name == "cbc":
        solver.options["seconds"] = time_limit

    print(f"Solving with {solver_name}...")
    results = solver.solve(model, tee=False)
    status = results.solver.termination_condition
    print(f"Solver status: {status}")
    return status in {pyo.TerminationCondition.optimal, pyo.TerminationCondition.feasible}


def extract_routes(model, dataset):
    """Extract routes from the solved model."""
    if pyo is None:
        raise ImportError("Pyomo is required to inspect the model after solving.")

    n = len(dataset["customers"])
    routes = {}
    for k in model.K:
        current = 0
        route = []
        while True:
            next_node = None
            for j in model.N:
                if j != current and pyo.value(model.x[current, j, k]) > 0.5:
                    next_node = j
                    break
            if next_node is None or next_node == 0:
                break
            route.append({"customer": next_node, "arrival_time": round(pyo.value(model.T[next_node]), 1)})
            current = next_node
        if route:
            routes[k] = route
    return routes


def print_routes(routes, dataset):
    """Print optimized routes."""
    dist = compute_distance_matrix(dataset)
    print("\n" + "=" * 60)
    print("OPTIMIZED ROUTES")
    print("=" * 60)
    total_distance = 0

    for k, route in routes.items():
        path = [0] + [stop["customer"] for stop in route] + [0]
        route_dist = sum(dist[path[i], path[i + 1]] for i in range(len(path) - 1))
        total_distance += route_dist
        print(f"\nVehicle {k + 1} route: {path}")
        print(f"  Distance = {route_dist:.2f}")
        print(f"  Arrival times: {[stop['arrival_time'] for stop in route]}")

    print(f"\nTotal distance: {total_distance:.2f}")


def print_violations(model, dataset):
    """Print slack variable violations."""
    if pyo is None:
        return

    print("\n" + "=" * 60)
    print("CONSTRAINT VIOLATIONS")
    print("=" * 60)
    any_violation = False

    for i in model.C:
        if pyo.value(model.late[i]) > 0.01:
            any_violation = True
            print(f"Late arrival at customer {i}: {pyo.value(model.late[i]):.1f}")

    for k in model.K:
        if pyo.value(model.overload[k]) > 0.01:
            any_violation = True
            print(f"Vehicle {k + 1} overload: {pyo.value(model.overload[k]):.1f}")

    for i in model.C:
        if pyo.value(model.skip[i]) > 0.5:
            any_violation = True
            print(f"Customer {i} was skipped.")

    if not any_violation:
        print("No violations detected.")


if __name__ == "__main__":
    dataset = generate_dataset(n_customers=10, vehicle_capacity=100, n_vehicles=4, seed=42)
    print_dataset(dataset)

    if pyo is None:
        print("\nPyomo is not installed. Install with `pip install pyomo` to run the solver.")
    else:
        model = build_model(dataset)
        try:
            solved = solve_model(model, solver_name="cbc")
            if solved:
                routes = extract_routes(model, dataset)
                print_routes(routes, dataset)
                print_violations(model, dataset)
            else:
                print("Solver did not return a feasible solution.")
        except Exception as exc:
            print(f"Solver execution failed: {exc}")
