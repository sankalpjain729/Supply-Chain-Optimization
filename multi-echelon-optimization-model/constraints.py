"""
05_CONSTRAINTS.PY
==================
Robust operational constraints for Multi-Echelon Supply Chain Optimization.

This version allows controlled infeasibility handling using:
- demand slack (s_demand)
- warehouse capacity slack (s_cap)

while enforcing strict production-flow consistency.
"""

import pyomo.environ as pyo
from model_initialization import model
from data_definition import data_package

# Big-M for linking constraints
M = 1e6

# Extract demand data
df_demand = data_package['df_demand']
D_total = df_demand.sum().sum()

# =====================================================================
# C1: Global Demand Coverage (soft constraint)
# =====================================================================
model.C1_DemandCov = pyo.Constraint(
    rule=lambda m:
        sum(m.X[j, c, k] for j in m.W for c in m.C for k in m.P)
        + m.s_demand >= 0.8 * D_total
)

# =====================================================================
# C2: Maximum Demand Ceiling
# =====================================================================
model.C2_MaxDemand = pyo.Constraint(
    model.C, model.P,
    rule=lambda m, c, k:
        sum(m.X[j, c, k] for j in m.W) <= m.D[c, k]
)

# =====================================================================
# C3: Warehouse Flow Balance (mass conservation)
# =====================================================================
model.C3_FlowBalance = pyo.Constraint(
    model.W, model.P,
    rule=lambda m, j, k:
        sum(m.F_flow[i, j, k] for i in m.F)
        == sum(m.X[j, c, k] for c in m.C)
)

# =====================================================================
# C4: Warehouse Capacity Constraint (soft via slack)
# =====================================================================
model.C4_WHCapacity = pyo.Constraint(
    model.W,
    rule=lambda m, j:
        sum(m.F_flow[i, j, k] for i in m.F for k in m.P)
        - m.s_cap[j] <= m.Cap[j] * m.Y[j]
)

# =====================================================================
# C5: Flow Activation Link (warehouse must be open)
# =====================================================================
model.C5_FlowLink = pyo.Constraint(
    model.F, model.W, model.P,
    rule=lambda m, i, j, k: m.F_flow[i, j, k] <= M * m.Y[j]
)

model.C5_XLink = pyo.Constraint(
    model.W, model.C, model.P,
    rule=lambda m, j, c, k: m.X[j, c, k] <= M * m.Y[j]
)

# =====================================================================
# C6: Factory Production & Logistics Balance (STRICT)
# =====================================================================
model.C6_ProdBalance = pyo.Constraint(
    model.F, model.P,
    rule=lambda m, i, k:
        sum(m.F_flow[i, j, k] for j in m.W)
        == m.R[i, k] + m.O[i, k]
)

# =====================================================================
# C7: Factory Regular Time Capacity
# =====================================================================
model.C7_RegTime = pyo.Constraint(
    model.F,
    rule=lambda m, i:
        sum(m.t[i, k] * m.R[i, k] for k in m.P) <= m.RegTime[i]
)

# =====================================================================
# C8: Factory Overtime Capacity
# =====================================================================
model.C8_OTTime = pyo.Constraint(
    model.F,
    rule=lambda m, i:
        sum(m.t[i, k] * m.O[i, k] for k in m.P) <= m.OTTime[i]
)