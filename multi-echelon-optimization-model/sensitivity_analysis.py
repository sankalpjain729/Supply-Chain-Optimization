# =====================================================================
# 9. SENSITIVITY ANALYSIS SCENARIOS
# =====================================================================

import pyomo.environ as pyo
import pandas as pd
from data_definition import data_package, P1, P2
from model_initialization import model
import objective_function  # noqa: F401 — registers Obj on model
from constraints import model
from solver import solve_model

scenarios = {
    "Low Demand (85%)": 0.85,
    "Baseline Demand (100%)": 1.00,
    "High Stress Demand (125%)": 1.25
}

# Dictionary to hold summary comparison data
sensitivity_summary = {}

print("--- STARTING MILP SENSITIVITY RUNS ---")

for sc_name, multiplier in scenarios.items():
    print(f"\n{'=' * 60}")
    print(f"  SCENARIO: {sc_name}")
    print(f"{'=' * 60}")

    scaled_demand_df = data_package['df_demand'] * multiplier
    D_scenario_total = scaled_demand_df.sum().sum()

    model.del_component('D')
    model.D = pyo.Param(
        model.C, model.P,
        initialize=scaled_demand_df.stack().to_dict()
    )

    model.del_component('C1_DemandCov')
    model.C1_DemandCov = pyo.Constraint(
        rule=lambda m: sum(m.X[j, c, k] for j in m.W for c in m.C for k in m.P) + m.s_demand >= 0.8 * D_scenario_total
    )

    results = solve_model(verbose=False)

    # Extract Metrics Safely
    if results.solver.termination_condition == pyo.TerminationCondition.optimal:
        opened_whs = [j for j in model.W if pyo.value(model.Y[j]) > 0.5]
        total_delivered = sum(pyo.value(model.X[j,c,k]) for j in model.W for c in model.C for k in model.P)
        unmet_demand_slack = pyo.value(model.s_demand)
        capacity_overflow_slack = sum(pyo.value(model.s_cap[j]) for j in model.W)

        penalty_costs = (P1 * unmet_demand_slack) + (P2 * capacity_overflow_slack)
        true_network_cost = pyo.value(model.Obj) - penalty_costs
        target_80 = 0.8 * D_scenario_total
        fill_rate = (total_delivered / D_scenario_total * 100) if D_scenario_total > 0 else 0.0
        target_achievement = (total_delivered / target_80 * 100) if target_80 > 0 else 0.0

        print(f"  Demand Multiplier     : {multiplier:.0%}")
        print(f"  Total Demand          : {D_scenario_total:,.1f} units")
        print(f"  Delivered / Target    : {total_delivered:,.1f} / {target_80:,.1f} units")
        print(f"  Fill Rate             : {fill_rate:.1f}%")
        print(f"  Target Achievement    : {target_achievement:.1f}%")
        print(f"  Opened Hubs ({len(opened_whs)})     : {', '.join(opened_whs)}")
        print(f"  True Network Cost     : ${true_network_cost:,.2f}")
        print(f"  Penalty Cost          : ${penalty_costs:,.2f}")
        print(f"  Capacity Violations   : {capacity_overflow_slack:,.1f} units")

        sensitivity_summary[sc_name] = {
            "Status": "Optimal",
            "Target 80% Vol": round(target_80, 1),
            "Actual Delivered": round(total_delivered, 1),
            "Opened Hubs": opened_whs,
            "Hub Count": len(opened_whs),
            "True Network Cost": f"${true_network_cost:,.2f}",
            "Unmet Penalty Vol": round(unmet_demand_slack, 1),
            "Capacity Violations": round(capacity_overflow_slack, 1)
        }
    else:
        sensitivity_summary[sc_name] = {"Status": "Infeasible/Failed", "Target 80% Vol": "-", "Actual Delivered": "-", "Opened Hubs": "-", "Hub Count": "-", "True Network Cost": "-", "Unmet Penalty Vol": "-", "Capacity Violations": "-"}
        print(f"  Status                : Infeasible/Failed")

# --- DISPLAY RESILIENCY REPORT ---
df_report = pd.DataFrame(sensitivity_summary).T
print("\n" + "="*60)
print("             SUPPLY CHAIN RESILIENCY REPORT             ")
print("="*60)
print(df_report[["Status", "Target 80% Vol", "Actual Delivered", "Hub Count", "Opened Hubs", "True Network Cost", "Capacity Violations"]])
