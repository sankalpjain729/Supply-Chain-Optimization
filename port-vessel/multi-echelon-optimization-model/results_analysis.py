import pyomo.environ as pyo
from solver import solve_model, model
from objective_function import objective_rule

results = solve_model()

print("\n" + "=" * 60)
print("SOLUTION RESULTS")
print("=" * 60)

opened_warehouses = [j for j in model.W if pyo.value(model.Y[j]) > 0.5]

# ---Calculations for Demand Fulfillment ---
total_fulfilled = sum(pyo.value(model.X[j, c, k]) for j in model.W for c in model.C for k in model.P)
unmet_demand_val = pyo.value(model.s_demand)
total_demand = total_fulfilled + unmet_demand_val
fulfillment_pct = (total_fulfilled / total_demand * 100) if total_demand > 0 else 0.0
# -----------------------------------------------

print(f"\nSolver Status           : {results.solver.status}")
print(f"Termination Condition   : {results.solver.termination_condition}")
print(f"Opened Warehouses       : {opened_warehouses}")
print(f"Total Network Cost      : ${pyo.value(objective_rule(model)):,.2f}")
print(f"Demand Fulfillment      : {total_fulfilled:.1f} / {total_demand:.1f} units ({fulfillment_pct:.2f}%)")

print("\n" + "=" * 60)
print("FACTORY PRODUCTION PLAN")
print("=" * 60)

for i in model.F:
    for k in model.P:
        reg_val = pyo.value(model.R[i, k])
        ot_val = pyo.value(model.O[i, k])

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
            val = pyo.value(model.F_flow[i, j, k])
            if val > 0.1:
                print(f"Ship {val:.1f} units of {k} from {i} → {j}")

print("\n" + "=" * 60)
print("WAREHOUSE TO CUSTOMER DELIVERIES")
print("=" * 60)

for j in model.W:
    for c in model.C:
        for k in model.P:
            val = pyo.value(model.X[j, c, k])
            if val > 0.1:
                print(f"Deliver {val:.1f} units of {k} from {j} → {c}")

print("\n" + "=" * 60)
print("PENALTY & SLACK ANALYSIS")
print("=" * 60)

unmet_demand = pyo.value(model.s_demand)
total_cap_violation = sum(pyo.value(model.s_cap[j]) for j in model.W)

print(f"\nUnmet Demand            : {unmet_demand:.1f} units")
print(f"Warehouse Over-capacity : {total_cap_violation:.1f} units")