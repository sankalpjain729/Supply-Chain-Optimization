"""
lp_solver.py — LP Solver wrapper using SciPy

Flow:
    model.to_standard_form()  →  linprog()  →  answer
"""

from scipy.optimize import linprog


def solve_lp(sf):
    """
    Pass standard form arrays to scipy and return the result.
    
    Args:
        sf (dict): Standard form representation with keys:
            - c: objective coefficients
            - A_ub: inequality constraint matrix
            - b_ub: inequality constraint RHS
            - A_eq: equality constraint matrix
            - b_eq: equality constraint RHS
            - bounds: variable bounds
    
    Returns:
        OptimizeResult: scipy linprog result object
    """
    result = linprog(
        sf["c"],
        A_ub=sf["A_ub"],
        b_ub=sf["b_ub"],
        A_eq=sf["A_eq"],
        b_eq=sf["b_eq"],
        bounds=sf["bounds"],
        method="highs",
    )
    return result
