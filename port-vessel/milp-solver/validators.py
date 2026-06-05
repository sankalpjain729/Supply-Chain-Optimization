"""
validators.py — Solution Validation

Verify that solutions satisfy all constraints and are feasible.
"""


def validate_knapsack_solution(sol, instance, tol=1e-5):
    """Validate a knapsack solution."""
    if sol is None:
        return False, "No solution"
    total_weight = 0.0
    total_value = 0.0
    for i in range(instance["n"]):
        xi = sol.get(f"x_{i}", 0.0)
        if xi < -tol or xi > 1.0 + tol:
            return False, f"x_{i} out of bounds"
        total_weight += instance["weights"][i] * xi
        total_value += instance["values"][i] * xi

    if total_weight > instance["capacity"] + tol:
        return False, "Capacity violated"

    return True, f"Valid knapsack (value={total_value:.3f}, weight={total_weight:.3f})"


def validate_tsp_solution(sol, n, tol=1e-5):
    """Validate a TSP solution (tour structure)."""
    if sol is None:
        return False, "No solution"

    edges = [(i, j) for i in range(n) for j in range(n)
             if i != j and sol.get(f"x_{i}_{j}", 0.0) > 0.5]

    outdeg = {i: 0 for i in range(n)}
    indeg = {i: 0 for i in range(n)}
    for i, j in edges:
        outdeg[i] += 1
        indeg[j] += 1

    if any(outdeg[i] != 1 for i in range(n)):
        return False, "Out-degree violation"
    if any(indeg[i] != 1 for i in range(n)):
        return False, "In-degree violation"

    nxt = {}
    for i, j in edges:
        nxt[i] = j

    tour = [0]
    cur = 0
    for _ in range(n):
        cur = nxt.get(cur, None)
        if cur is None:
            return False, "Broken tour"
        tour.append(cur)
        if cur == 0:
            break

    if len(tour) != n + 1 or len(set(tour[:-1])) != n or tour[-1] != 0:
        return False, "Subtour / incomplete tour"

    return True, "Valid tour"


def validate_cvrp_solution(sol, instance, tol=1e-5):
    """Validate a CVRP solution (flow conservation)."""
    if sol is None:
        return False, "No solution"

    n = len(instance["coords"])
    vehicles = instance.get("vehicles", 1)

    outdeg = {i: 0 for i in range(n)}
    indeg = {i: 0 for i in range(n)}
    for i in range(n):
        for j in range(n):
            if i != j and sol.get(f"x_{i}_{j}", 0.0) > 0.5:
                outdeg[i] += 1
                indeg[j] += 1

    if outdeg[0] != vehicles or indeg[0] != vehicles:
        return False, "Depot degree violation"

    for i in range(1, n):
        if outdeg[i] != 1 or indeg[i] != 1:
            return False, f"Customer degree violation at {i}"

    return True, "Valid CVRP degrees"
