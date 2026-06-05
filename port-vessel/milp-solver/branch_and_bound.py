"""
branch_and_bound.py — Branch-and-Bound MILP Solver Core

Implements the standard branch-and-bound algorithm:
1. Solve the root LP relaxation
2. If integer-feasible, return solution
3. Otherwise, branch on most fractional variable
4. Prune nodes with bounds worse than current incumbent
5. Continue until all nodes are explored or pruned
"""

import math
import heapq
from types import SimpleNamespace
from lp_solver import solve_lp


TOL = 1e-5


def _choose_branch_var(x, int_vars, tol=TOL):
    """Find the most fractional integer variable."""
    best_idx = None
    best_frac = tol

    for idx in int_vars:
        frac = abs(x[idx] - round(x[idx]))
        if frac > best_frac:
            best_frac = frac
            best_idx = idx

    return best_idx


def _apply_bounds(base_bounds, fixed_bounds):
    """Apply variable bounds tightening."""
    bounds = list(base_bounds)
    for idx, (lb, ub) in fixed_bounds.items():
        bounds[idx] = (lb, ub)
    return bounds


def _solve_node(sf, fixed_bounds):
    """Solve LP relaxation with tightened bounds."""
    node_sf = dict(sf)
    node_sf["bounds"] = _apply_bounds(sf["bounds"], fixed_bounds)
    return solve_lp(node_sf)


def _reported_objective(model, internal_obj):
    """Convert internal objective to reported form (maximize if needed)."""
    if model.sense == "maximize":
        return -internal_obj
    return internal_obj


def push_child(fixed_bounds, sf, heap, counter, nodes,
               best_internal_obj, best_x, max_nodes, tol=TOL):
    """Create and enqueue a child node if promising."""
    if nodes >= max_nodes:
        return counter, nodes

    child = _solve_node(sf, fixed_bounds)
    nodes += 1

    if not child.success:
        return counter, nodes

    if best_x is not None and child.fun >= best_internal_obj - tol:
        return counter, nodes

    counter += 1
    heapq.heappush(heap, (child.fun, counter, fixed_bounds, child))

    return counter, nodes


def branch_on_var(var_idx, val, fixed_bounds, model, sf, heap,
                  counter, nodes, best_internal_obj, best_x, max_nodes, tol=TOL):
    """Branch on a single variable, creating child nodes."""
    var_obj = model.variables[model.var_order[var_idx]]
    lb, ub = sf["bounds"][var_idx]

    if var_obj.var_type == "binary":
        # Binary: branch into x = 0 and x = 1
        if lb <= 0 <= ub:
            left = dict(fixed_bounds)
            left[var_idx] = (0, 0)
            counter, nodes = push_child(
                left, sf, heap, counter, nodes,
                best_internal_obj, best_x, max_nodes, tol
            )

        if lb <= 1 <= ub:
            right = dict(fixed_bounds)
            right[var_idx] = (1, 1)
            counter, nodes = push_child(
                right, sf, heap, counter, nodes,
                best_internal_obj, best_x, max_nodes, tol
            )

    elif var_obj.var_type == "integer":
        # Integer: branch using floor and ceil
        fl = math.floor(val)
        ce = math.ceil(val)

        if lb <= fl:
            left = dict(fixed_bounds)
            left[var_idx] = (lb, fl)
            counter, nodes = push_child(
                left, sf, heap, counter, nodes,
                best_internal_obj, best_x, max_nodes, tol
            )

        if ub is None or ce <= ub:
            right = dict(fixed_bounds)
            right[var_idx] = (ce, ub)
            counter, nodes = push_child(
                right, sf, heap, counter, nodes,
                best_internal_obj, best_x, max_nodes, tol
            )

    # Continuous: do not branch
    return counter, nodes


def solve_model(model, max_nodes=10000, tol=TOL):
    """
    Solve a MILP using branch-and-bound.
    
    Args:
        model : Model object
        max_nodes : maximum nodes to explore
        tol : tolerance for integrality
    
    Returns:
        SimpleNamespace with success, message, x, fun, nodes
    """
    sf = model.to_standard_form()
    int_vars = sf["int_vars"]

    # Pure LP: no integer variables
    if not int_vars:
        res = solve_lp(sf)
        if not res.success:
            return SimpleNamespace(
                success=False,
                message=res.message,
                x=None,
                fun=None,
                nodes=1,
            )

        return SimpleNamespace(
            success=True,
            message="LP solved successfully.",
            x=res.x,
            fun=_reported_objective(model, res.fun),
            nodes=1,
        )

    # Solve root node
    root = _solve_node(sf, {})
    nodes = 1

    if not root.success:
        return SimpleNamespace(
            success=False,
            message="Root LP infeasible or unbounded.",
            x=None,
            fun=None,
            nodes=nodes,
        )

    # Check if root is already integer-feasible
    root_branch_var = _choose_branch_var(root.x, int_vars, tol)

    if root_branch_var is None:
        return SimpleNamespace(
            success=True,
            message="Integer-feasible solution found at root.",
            x=root.x.copy(),
            fun=_reported_objective(model, root.fun),
            nodes=nodes,
        )

    # Initialize branch-and-bound
    heap = []
    counter = 0
    best_internal_obj = math.inf
    best_x = None

    # Branch root node
    counter, nodes = branch_on_var(
        root_branch_var, root.x[root_branch_var], {},
        model, sf, heap, counter, nodes,
        best_internal_obj, best_x, max_nodes, tol
    )

    # Main loop: explore nodes
    while heap and nodes < max_nodes:
        # Global pruning: if best node cannot improve incumbent, stop
        if best_x is not None and heap[0][0] >= best_internal_obj - tol:
            break

        # Pop most promising node
        node_bound, _, fixed_bounds, node = heapq.heappop(heap)

        # Local pruning
        if best_x is not None and node_bound >= best_internal_obj - tol:
            continue

        # Find fractional variable
        frac_var = _choose_branch_var(node.x, int_vars, tol)

        # If integer-feasible, update incumbent
        if frac_var is None:
            if node.fun < best_internal_obj - tol:
                best_internal_obj = node.fun
                best_x = node.x.copy()
            continue

        # Branch on fractional variable
        counter, nodes = branch_on_var(
            frac_var, node.x[frac_var], fixed_bounds, model, sf, heap,
            counter, nodes, best_internal_obj, best_x, max_nodes, tol
        )

    if best_x is None:
        return SimpleNamespace(
            success=False,
            message="No integer-feasible solution found.",
            x=None,
            fun=None,
            nodes=nodes,
        )

    return SimpleNamespace(
        success=True,
        message="Integer-feasible solution found.",
        x=best_x,
        fun=_reported_objective(model, best_internal_obj),
        nodes=nodes,
    )


def solution_dict(model, x):
    """Convert solution array to dict {var_name: value}."""
    if x is None:
        return None
    return {name: x[idx] for idx, name in enumerate(model.var_order)}
