"""
06_SOLVER.PY
=============
Solves the Multi-Echelon Supply Chain Optimization Model using GLPK solver.

This module:
- Initializes the GLPK solver
- Solves the optimization problem
- Displays basic solution status
"""

import pyomo.environ as pyo
from constraints import model

# =====================================================================
# SOLVER RUN
# =====================================================================

def solve_model():
    """Solve the optimization model"""
    
    print("\n" + "=" * 60)
    print("SOLVING OPTIMIZATION MODEL...")
    print("=" * 60)
    
    solver = pyo.SolverFactory('highs')
    solver = pyo.SolverFactory("appsi_highs")
    solver.options["random_seed"] = 42
    # solver.options["time_limit"] = 60
    results = solver.solve(model)
    
    return results

if __name__ == "__main__":
    results = solve_model()
    
    print(f"\nSolver Status: {results.solver.status}")
    print(f"Termination Condition: {results.solver.termination_condition}")
    print(f"Total Objective Value: ${pyo.value(model.Obj):,.2f}")
