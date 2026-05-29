"""
04_OBJECTIVE_FUNCTION.PY
=========================
Defines the objective function for the Multi-Echelon Supply Chain Optimization Model.

Objective: Minimize Total Operating Costs

Cost Components:
1. Fixed warehouse operating costs
2. Inbound shipping (Factory → Warehouse)
3. Outbound transportation (Warehouse → Customer)
4. Regular production costs
5. Overtime production costs
6. Penalties for unmet demand, logistics mismatches, and over-capacity
"""

import pyomo.environ as pyo
from model_initialization import model
from data_definition import data_package

# Extract penalty values
P1 = data_package['P1']
P2 = data_package['P2']
P3 = data_package['P3']

# =====================================================================
# 9. THE OBJECTIVE FUNCTION (Minimize Total Operating Costs)
# =====================================================================

# Math Form: min Z = Fixed Costs + Inbound + Outbound + Regular Prod + Overtime Prod + Penalties
def objective_rule(m):
    return (
        # Math Form: ∑ (OC[j] * Y[j]) for all j ∈ W
        # 1. FIXED WAREHOUSE RENT: Pay rent only if the warehouse switch is turned ON (Y[j] == 1)
        sum(m.OC_w[j] * m.Y[j] for j in m.W) +

        # Math Form: ∑ ∑ ∑ (SC[i,j,k] * F_flow[i,j,k]) for all i ∈ F, j ∈ W, k ∈ P
        # 2. INBOUND SHIPPING: Cost to move product 'k' from Factory 'i' to Warehouse 'j'
        sum(m.SC[i,j,k] * m.F_flow[i,j,k] for i in m.F for j in m.W for k in m.P) +

        # Math Form: ∑ ∑ ∑ (TC[j,c,k] * X[j,c,k]) for all j ∈ W, c ∈ C, k ∈ P
        # 3. OUTBOUND TRANSPORT: Cost to deliver product 'k' from Warehouse 'j' to Customer 'c'
        sum(m.TC[j,c,k] * m.X[j,c,k] for j in m.W for c in m.C for k in m.P) +

        # Math Form: ∑ ∑ (RC[i,k] * R[i,k]) for all i ∈ F, k ∈ P
        # 4. REGULAR PRODUCTION: Cost to manufacture product 'k' at Factory 'i' during normal hours
        sum(m.RC[i,k] * m.R[i,k] for i in m.F for k in m.P) +

        # Math Form: ∑ ∑ (OC_p[i,k] * O[i,k]) for all i ∈ F, k ∈ P
        # 5. OVERTIME PRODUCTION: Premium cost to manufacture product 'k' during extra hours
        sum(m.OC_p[i,k] * m.O[i,k] for i in m.F for k in m.P) +

        # Math Form: P1 * s_demand
        # 6. UNMET DEMAND PENALTY: Massive fine if we fail to deliver customer orders
        P1 * m.s_demand +

        # Math Form: P2 * ∑ ∑ (s_under[i,k] + s_over[i,k]) for all i ∈ F, k ∈ P
        # 7. LOGISTICS MISMATCH PENALTY: Fine if factory output doesn't match shipped logs
        P2 * sum(m.s_under[i,k] + m.s_over[i,k] for i in m.F for k in m.P) +

        # Math Form: P3 * ∑ s_cap[j] for all j ∈ W
        # 8. OVER-CAPACITY PENALTY: Massive fine for stuffing extra boxes into a full warehouse
        P3 * sum(m.s_cap[j] for j in m.W)
    )

# Activate the math blueprint in Pyomo and explicitly tell it to MINIMIZE the total
model.Obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize)

if __name__ == "__main__":
    print("=" * 60)
    print("OBJECTIVE FUNCTION DEFINED SUCCESSFULLY")
    print("=" * 60)
    print(f"\nObjective Function: {model.Obj.expr}")
    print(f"\nPenalty Values:")
    print(f"  P1 (Unmet Demand): ${P1:,}")
    print(f"  P2 (Logistics Mismatch): ${P2:,}")
    print(f"  P3 (Over-Capacity): ${P3:,}")
