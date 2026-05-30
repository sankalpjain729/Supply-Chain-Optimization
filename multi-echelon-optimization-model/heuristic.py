# =====================================================================
# GREEDY HEURISTIC SOLUTION (Beginner-Friendly Version)
# =====================================================================

from data_definition import data_package
from model_initialization import model
from objective_function import objective_function
from constraints import model
from data_definition import df_demand
from data_definition import warehouses
from data_definition import factories
from data_definition import df_warehouses
from data_definition import df_factories
from data_definition import df_production
from data_definition import sc_dict
from data_definition import tc_dict

remaining_demand = df_demand.stack().to_dict()  # (customer, product) → demand

warehouse_opened = {w: False for w in warehouses}
warehouse_used_capacity = {w: 0.0 for w in warehouses}

factory_reg_time_used = {f: 0.0 for f in factories}
factory_ot_time_used = {f: 0.0 for f in factories}

target_demand = 0.8 * df_demand.sum().sum()
fulfilled_demand = 0.0

fixed_cost = 0.0
variable_cost = 0.0

print("--- RUNNING GREEDY HEURISTIC ---")


# -----------------------------
# STEP 2: MAIN LOOP
# -----------------------------
while fulfilled_demand < target_demand:

    best_score = float('inf')
    best_action = None

    # -----------------------------
    # STEP 2A: TRY ALL POSSIBILITIES
    # -----------------------------
    for (c, k), demand_left in remaining_demand.items():

        if demand_left <= 0:
            continue

        for f in factories:
            for w in warehouses:

                # -----------------------------
                # 1. Warehouse capacity check
                # -----------------------------
                capacity_left = df_warehouses.loc[w, 'Cap'] - warehouse_used_capacity[w]
                if capacity_left <= 0:
                    continue

                # -----------------------------
                # 2. Factory time check
                # -----------------------------
                unit_time = df_production.loc[(f, k), 't_ik']

                reg_left = df_factories.loc[f, 'RegTime'] - factory_reg_time_used[f]
                ot_left = df_factories.loc[f, 'OTTime'] - factory_ot_time_used[f]

                if reg_left < unit_time and ot_left < unit_time:
                    continue

                # -----------------------------
                # 3. Compute unit cost
                # -----------------------------
                transport_cost = sc_dict[(f, w, k)] + tc_dict[(w, c, k)]

                if reg_left >= unit_time:
                    production_cost = df_production.loc[(f, k), 'RC_ik']
                else:
                    production_cost = df_production.loc[(f, k), 'OC_ik']

                base_cost = transport_cost + production_cost

                # -----------------------------
                # 4. Warehouse opening penalty
                # -----------------------------
                if not warehouse_opened[w]:
                    open_cost_penalty = df_warehouses.loc[w, 'OC'] / max(capacity_left, 1e-6)
                    score = base_cost + open_cost_penalty
                else:
                    score = base_cost

                # -----------------------------
                # 5. Track best choice
                # -----------------------------
                if score < best_score:

                    best_score = score

                    max_possible_units = (
                        (reg_left / unit_time if reg_left > 0 else 0) +
                        (ot_left / unit_time if ot_left > 0 else 0)
                    )

                    qty = min(
                        demand_left,
                        capacity_left,
                        max_possible_units,
                        target_demand - fulfilled_demand
                    )

                    if qty > 0:
                        best_action = (c, k, f, w, qty, unit_time)


    # -----------------------------
    # STEP 3: STOP CONDITION
    # -----------------------------
    if not best_action:
        print("Heuristic stopped: no feasible allocation left.")
        break

    # unpack best action
    c, k, f, w, qty, unit_time = best_action

    # -----------------------------
    # STEP 4: ALLOCATE PRODUCTION
    # -----------------------------
    remaining_qty = qty
    reg_qty = 0.0
    ot_qty = 0.0

    reg_left = df_factories.loc[f, 'RegTime'] - factory_reg_time_used[f]

    if reg_left > 0:
        reg_possible = reg_left / unit_time
        reg_qty = min(remaining_qty, reg_possible)
        factory_reg_time_used[f] += reg_qty * unit_time
        remaining_qty -= reg_qty

    if remaining_qty > 0:
        ot_left = df_factories.loc[f, 'OTTime'] - factory_ot_time_used[f]
        ot_possible = ot_left / unit_time
        ot_qty = min(remaining_qty, ot_possible)
        factory_ot_time_used[f] += ot_qty * unit_time
        remaining_qty -= ot_qty

    actual_qty = reg_qty + ot_qty

    # -----------------------------
    # STEP 5: UPDATE SYSTEM STATE
    # -----------------------------
    if not warehouse_opened[w]:
        warehouse_opened[w] = True
        fixed_cost += df_warehouses.loc[w, 'OC']

    warehouse_used_capacity[w] += actual_qty
    remaining_demand[(c, k)] -= actual_qty
    fulfilled_demand += actual_qty

    # -----------------------------
    # STEP 6: UPDATE VARIABLE COST
    # -----------------------------
    variable_cost += (
        reg_qty * df_production.loc[(f, k), 'RC_ik']
        + ot_qty * df_production.loc[(f, k), 'OC_ik']
        + actual_qty * (sc_dict[(f, w, k)] + tc_dict[(w, c, k)])
    )


# -----------------------------
# STEP 7: FINAL OUTPUT
# -----------------------------
total_cost = fixed_cost + variable_cost
open_warehouses = [w for w in warehouses if warehouse_opened[w]]

print("\n--- HEURISTIC SUMMARY ---")
print(f"Demand fulfilled       : {fulfilled_demand:.2f} / {target_demand:.2f}")
print(f"Warehouses used        : {open_warehouses}")
print(f"Fixed cost             : {fixed_cost:,.2f}")
print(f"Variable cost          : {variable_cost:,.2f}")
print(f"Total heuristic cost   : {total_cost:,.2f}")