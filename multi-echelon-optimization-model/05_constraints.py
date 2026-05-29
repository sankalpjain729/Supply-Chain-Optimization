"""
05_CONSTRAINTS.PY
==================
Defines all operational constraints for the Multi-Echelon Supply Chain Optimization Model.

Constraints:
C1: Global Demand Coverage Target (80% of total demand)
C2: Maximum Demand Ceiling (never exceed customer orders)
C3: Warehouse Flow Balance (conservation of mass)
C4: Warehouse Capacity & Activation Gate (binary warehouse selection)
C5: Factory Production & Logistics Balance (production matches shipments)
C6: Factory Regular Time Capacity (standard hours limit)
C7: Factory Overtime Capacity (overtime hours limit)
"""

import pyomo.environ as pyo
from model_initialization import model
from data_definition import data_package

# Extract data
df_demand = data_package['df_demand']

# Calculate the total absolute units ordered by all customers combined
D_total = df_demand.sum().sum()

# =====================================================================
# 10. THE SYSTEM CONSTRAINTS (The Operational Rules)
# =====================================================================

# ---------------------------------------------------------------------
# C1: Global Demand Coverage Target
# Math Form: ∑ ∑ ∑ X[j,c,k] + s_demand ≥ 0.8 * D_total (for all j ∈ W, c ∈ C, k ∈ P)
# Rule: The entire network MUST fulfill at least 80% of total customer demand.
# ---------------------------------------------------------------------
model.C1_DemandCov = pyo.Constraint(
    rule=lambda m: sum(m.X[j,c,k] for j in m.W for c in m.C for k in m.P) + m.s_demand >= 0.8 * D_total
)

# ---------------------------------------------------------------------
# C2: Maximum Demand Ceiling
# Math Form: ∑ X[j,c,k] ≤ D[c,k] (for each c ∈ C, k ∈ P)
# Rule: Do not over-ship! Never deliver more units of product 'k' to customer 'c' than they ordered.
# ---------------------------------------------------------------------
model.C2_MaxDemand = pyo.Constraint(
    model.C, model.P,
    rule=lambda m, c, k: sum(m.X[j,c,k] for j in m.W) <= m.D[c,k]
)

# ---------------------------------------------------------------------
# C3: Warehouse Flow Balance
# Math Form: ∑ F_flow[i,j,k] ≡ ∑ X[j,c,k] (for each j ∈ W, k ∈ P)
# Rule: Conservation of mass! Total units entering a warehouse from factories
# must exactly equal total units leaving that warehouse to customers.
# ---------------------------------------------------------------------
model.C3_FlowBalance = pyo.Constraint(
    model.W, model.P,
    rule=lambda m, j, k: sum(m.F_flow[i,j,k] for i in m.F) == sum(m.X[j,c,k] for c in m.C)
)

# ---------------------------------------------------------------------
# C4: Warehouse Capacity & Activation Gate
# Math Form: ∑ ∑ F_flow[i,j,k] - s_cap[j] ≤ Cap[j] * Y[j] (for each j ∈ W, across all i ∈ F, k ∈ P)
# Rule: If a warehouse is closed (Y[j]=0), its capacity is 0. If open (Y[j]=1),
# total inbound volume cannot exceed its physical cap limit.
# ---------------------------------------------------------------------
model.C4_WHCapacity = pyo.Constraint(
    model.W,
    rule=lambda m, j: sum(m.F_flow[i,j,k] for i in m.F for k in m.P) - m.s_cap[j] <= m.Cap[j] * m.Y[j]
)

# ---------------------------------------------------------------------
# C5: Factory Production & Logistics Balance
# Math Form: ∑ F_flow[i,j,k] + s_under[i,k] - s_over[i,k] ≡ R[i,k] + O[i,k] (for each i ∈ F, k ∈ P)
# Rule: Everything manufactured in regular time (R) + overtime (O) at a factory
# must perfectly match the total physical logs shipped out to the warehouses.
# ---------------------------------------------------------------------
model.C5_ProdBalance = pyo.Constraint(
    model.F, model.P,
    rule=lambda m, i, k: sum(m.F_flow[i,j,k] for j in m.W) + m.s_under[i,k] - m.s_over[i,k] == m.R[i,k] + m.O[i,k]
)

# ---------------------------------------------------------------------
# C6: Factory Regular Time Capacity
# Math Form: ∑ (t[i,k] * R[i,k]) ≤ RegTime[i] (for each i ∈ F, across all k ∈ P)
# Rule: Total hours spent producing items cannot exceed the factory's standard calendar hours.
# ---------------------------------------------------------------------
model.C6_RegTime = pyo.Constraint(
    model.F,
    rule=lambda m, i: sum(m.t[i,k] * m.R[i,k] for k in m.P) <= m.RegTime[i]
)

# ---------------------------------------------------------------------
# C7: Factory Overtime Capacity
# Math Form: ∑ (t[i,k] * O[i,k]) ≤ OTTime[i] (for each i ∈ F, across all k ∈ P)
# Rule: Total extra hours spent manufacturing cannot exceed the factory's strict overtime limit.
# ---------------------------------------------------------------------
model.C7_OTTime = pyo.Constraint(
    model.F,
    rule=lambda m, i: sum(m.t[i,k] * m.O[i,k] for k in m.P) <= m.OTTime[i]
)

if __name__ == "__main__":
    print("=" * 60)
    print("CONSTRAINTS DEFINED SUCCESSFULLY")
    print("=" * 60)
    print(f"\nTotal Demand (D_total): {D_total} units")
    print(f"Minimum Coverage Target: {0.8 * D_total} units (80%)")
    print(f"\nConstraints Added:")
    print(f"  C1: Global Demand Coverage")
    print(f"  C2: Maximum Demand Ceiling")
    print(f"  C3: Warehouse Flow Balance")
    print(f"  C4: Warehouse Capacity & Activation")
    print(f"  C5: Factory Production & Logistics Balance")
    print(f"  C6: Factory Regular Time Capacity")
    print(f"  C7: Factory Overtime Capacity")
    print(f"\nTotal Constraints: {len(model.component_map(pyo.Constraint))}")
