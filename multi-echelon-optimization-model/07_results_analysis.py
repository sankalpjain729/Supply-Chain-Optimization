"""
07_RESULTS_ANALYSIS.PY
=======================
Analyzes and displays the optimization results in a human-readable format.

Output Sections:
- Solution status and total cost
- Opened warehouses
- Factory production plan (regular and overtime)
- Shipping routine (Factory → Warehouse)
- Delivery routine (Warehouse → Customer)
"""

import pyomo.environ as pyo
from solver import solve_model, model

# Solve the model
results = solve_model()

# =====================================================================
# OUTPUT SUMMARY VERIFICATION
# =====================================================================

print("\n" + "=" * 60)
print("SOLUTION RESULTS")
print("=" * 60)

opened_warehouses = [j for j in model.W if pyo.value(model.Y[j]) > 0.5]
print(f"\nSolver Status           : {results.solver.status}")
print(f"Termination Condition   : {results.solver.termination_condition}")
print(f"Opened Warehouses       : {opened_warehouses}")
print(f"Total Network Cost      : ${pyo.value(model.Obj):,.2f}")

print("\n" + "=" * 60)
print("FACTORY PRODUCTION PLAN")
print("=" * 60)

for i in model.F:
    for k in model.P:
        reg_val = pyo.value(model.R[i,k])
        ot_val = pyo.value(model.O[i,k])
        
        if reg_val > 0.1:
            print(f"{i} produces {reg_val:.1f} units of {k} (Regular Time)")
        if ot_val > 0.1:
            print(f"{i} produces {ot_val:.1f} units of {k} (Overtime)")

print("\n" + "=" * 60)
print("FACTORY TO WAREHOUSE SHIPMENTS")
print("=" * 60)

for i in model.F:
    for j in model.W:
        for k in model.P:
            val = pyo.value(model.F_flow[i,j,k])
            if val > 0.1:
                print(f"Ship {val:.1f} units of {k} from {i} → {j}")

print("\n" + "=" * 60)
print("WAREHOUSE TO CUSTOMER DELIVERIES")
print("=" * 60)

for j in model.W:
    for c in model.C:
        for k in model.P:
            val = pyo.value(model.X[j,c,k])
            if val > 0.1:
                print(f"Deliver {val:.1f} units of {k} from {j} → {c}")

print("\n" + "=" * 60)
print("PENALTY & SLACK ANALYSIS")
print("=" * 60)

unmet_demand = pyo.value(model.s_demand)
total_under = sum(pyo.value(model.s_under[i,k]) for i in model.F for k in model.P)
total_over = sum(pyo.value(model.s_over[i,k]) for i in model.F for k in model.P)
total_cap_violation = sum(pyo.value(model.s_cap[j]) for j in model.W)

print(f"\nUnmet Demand            : {unmet_demand:.1f} units")
print(f"Logistics Under-shipment: {total_under:.1f} units")
print(f"Logistics Over-shipment : {total_over:.1f} units")
print(f"Warehouse Over-capacity : {total_cap_violation:.1f} units")

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("RESULTS ANALYSIS COMPLETE")
    print("=" * 60)
