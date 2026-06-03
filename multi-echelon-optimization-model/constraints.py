"""
05_CONSTRAINTS.PY
==================
Robust operational constraints for Multi-Echelon Supply Chain Optimization.

Infeasibility handling using:
- demand slack (s_demand)
- warehouse capacity slack (s_cap)

while enforcing strict production-flow consistency.
"""

import pyomo.environ as pyo
from model_initialization import model
from data_definition import data_package

# Big-M for linking constraints (REVERTED TO ORIGINAL)
M = 200

# Extract demand data
df_demand = data_package["df_demand"]
D_total = df_demand.sum().sum()

# =====================================================================
# C1: Global Demand Coverage (soft constraint)
# =====================================================================
def c1_global_demand_rule(model):
    total_delivery = sum(
        model.X[j, c, k] for j in model.W for c in model.C for k in model.P
    )
    return total_delivery + model.s_demand >= 0.8 * D_total

model.C1_DemandCov = pyo.Constraint(rule=c1_global_demand_rule)


# =====================================================================
# C2: Maximum Demand Ceiling
# =====================================================================
def c2_customer_demand_cap_rule(model, c, k):
    total_customer_delivery = sum(model.X[j, c, k] for j in model.W)
    return total_customer_delivery <= model.D[c, k]

model.C2_MaxDemand = pyo.Constraint(
    model.C, model.P, rule=c2_customer_demand_cap_rule
)

# =====================================================================
# C3: Warehouse Flow Balance (mass conservation)
# =====================================================================
def c3_warehouse_flow_balance_rule(model, j, k):
    inflow = sum(model.F_flow[i, j, k] for i in model.F)
    outflow = sum(model.X[j, c, k] for c in model.C)
    return inflow == outflow

model.C3_FlowBalance = pyo.Constraint(
    model.W, model.P, rule=c3_warehouse_flow_balance_rule
)

# =====================================================================
# C4: Warehouse Capacity Constraint (soft via slack)
# =====================================================================
def c4_wh_capacity_rule(model, j):
    total_inflow = sum(
        model.F_flow[i, j, k] for i in model.F for k in model.P
    )
    return total_inflow - model.s_cap[j] <= model.Cap[j] * model.Y[j]

model.C4_WHCapacity = pyo.Constraint(model.W, rule=c4_wh_capacity_rule)

# =====================================================================
# C5: Flow Activation Link (warehouse must be open)
# =====================================================================
def c5_flow_link_rule(model, i, j, k):
    return model.F_flow[i, j, k] <= M * model.Y[j]

model.C5_FlowLink = pyo.Constraint(
    model.F, model.W, model.P, rule=c5_flow_link_rule
)

def c5_xlink_rule(model, j, c, k):
    return model.X[j, c, k] <= M * model.Y[j]

model.C5_XLink = pyo.Constraint(
    model.W, model.C, model.P, rule=c5_xlink_rule
)

# =====================================================================
# C6: Factory Production & Logistics Balance (STRICT)
# =====================================================================
def c6_prod_balance_rule(model, i, k):
    # Total outbound flow from factory i to all warehouses j for product k
    total_factory_outflow = sum(model.F_flow[i, j, k] for j in model.W)

    # Must equal total regular time production + overtime production
    return total_factory_outflow == model.R[i, k] + model.O[i, k]


model.C6_ProdBalance = pyo.Constraint(
    model.F, model.P, rule=c6_prod_balance_rule
)

# =====================================================================
# C7: Factory Regular Time Capacity
# =====================================================================
def c7_reg_time_rule(model, i):
    # Total time used for regular production across all products at factory i
    total_reg_time_used = sum(model.t[i, k] * model.R[i, k] for k in model.P)

    return total_reg_time_used <= model.RegTime[i]

model.C7_RegTime = pyo.Constraint(model.F, rule=c7_reg_time_rule)

# =====================================================================
# C8: Factory Overtime Capacity
# =====================================================================
def c8_ot_time_rule(model, i):
    # Total time used for overtime production across all products at factory i
    total_ot_time_used = sum(model.t[i, k] * model.O[i, k] for k in model.P)

    return total_ot_time_used <= model.OTTime[i]

model.C8_OTTime = pyo.Constraint(model.F, rule=c8_ot_time_rule)