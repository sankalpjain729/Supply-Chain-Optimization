"""
03_MODEL_INITIALIZATION.PY
===========================
Initializes the Pyomo optimization model with all sets, parameters, decision variables, 
and slack variables for the Multi-Echelon Supply Chain Optimization.

This module:
- Creates the Pyomo ConcreteModel
- Defines all sets (Factories, Warehouses, Customers, Products)
- Initializes all parameters from the data package
- Creates decision variables (production, flows, binary warehouse selection)
- Defines slack variables for constraint relaxation
"""

import pyomo.environ as pyo
from data_definition import data_package

# =====================================================================
# 7. PYOMO MODEL INITIALIZATION
# =====================================================================

# Open up a blank canvas for our mathematical model
model = pyo.ConcreteModel()

# Extract data from package
factories = data_package['factories']
warehouses = data_package['warehouses']
customers = data_package['customers']
products = data_package['products']
df_factories = data_package['df_factories']
df_warehouses = data_package['df_warehouses']
df_production = data_package['df_production']
df_demand = data_package['df_demand']
sc_dict = data_package['sc_dict']
tc_dict = data_package['tc_dict']

# ---------------------------------------------------------------------
# A. SETS (The Dimensions of our Problem)
# ---------------------------------------------------------------------

# Math Form: i ∈ F
model.F = pyo.Set(initialize=factories)

# Math Form: j ∈ W
model.W = pyo.Set(initialize=warehouses)

# Math Form: c ∈ C
model.C = pyo.Set(initialize=customers)

# Math Form: k ∈ P
model.P = pyo.Set(initialize=products)


# ---------------------------------------------------------------------
# B. PARAMETERS (The Fixed Business Data)
# ---------------------------------------------------------------------

# Math Form: RegTime[i]
model.RegTime = pyo.Param(model.F, initialize=df_factories['RegTime'].to_dict())

# Math Form: OTTime[i]
model.OTTime = pyo.Param(model.F, initialize=df_factories['OTTime'].to_dict())

# Math Form: OC[j]
model.OC_w = pyo.Param(model.W, initialize=df_warehouses['OC'].to_dict())

# Math Form: Cap[j]
model.Cap = pyo.Param(model.W, initialize=df_warehouses['Cap'].to_dict())

# Math Form: t[i,k]
model.t = pyo.Param(model.F, model.P, initialize=df_production['t_ik'].to_dict())

# Math Form: RC[i,k]
model.RC = pyo.Param(model.F, model.P, initialize=df_production['RC_ik'].to_dict())

# Math Form: OC_p[i,k]
model.OC_p = pyo.Param(model.F, model.P, initialize=df_production['OC_ik'].to_dict())

# Math Form: D[c,k]
model.D = pyo.Param(model.C, model.P, initialize=df_demand.stack().to_dict())

# Math Form: SC[i,j,k]
model.SC = pyo.Param(model.F, model.W, model.P, initialize=sc_dict)

# Math Form: TC[j,c,k]
model.TC = pyo.Param(model.W, model.C, model.P, initialize=tc_dict)


# ---------------------------------------------------------------------
# C. DECISION VARIABLES (The Choices the Solver Must Make)
# ---------------------------------------------------------------------

# Math Form: R[i,k] ≥ 0
model.R = pyo.Var(model.F, model.P, domain=pyo.NonNegativeReals)

# Math Form: O[i,k] ≥ 0
model.O = pyo.Var(model.F, model.P, domain=pyo.NonNegativeReals)

# Math Form: F_flow[i,j,k] ≥ 0
model.F_flow = pyo.Var(model.F, model.W, model.P, domain=pyo.NonNegativeReals)

# Math Form: X[j,c,k] ≥ 0
model.X = pyo.Var(model.W, model.C, model.P, domain=pyo.NonNegativeReals)

# Math Form: Y[j] ∈ {0, 1}
model.Y = pyo.Var(model.W, domain=pyo.Binary)

# =====================================================================
# 8. SLACK VARIABLES (The Mathematical Safety Valves)
# =====================================================================

# Math Form: s_demand ≥ 0
# Captures how many units of customer demand we completely failed to deliver.
model.s_demand = pyo.Var(domain=pyo.NonNegativeReals)

# Math Form: s_under[i,k] ≥ 0
# Captures if we shipped LESS units out of factory 'i' than we actually manufactured.
model.s_under = pyo.Var(model.F, model.P, domain=pyo.NonNegativeReals)

# Math Form: s_over[i,k] ≥ 0
# Captures if we tried to ship MORE units out of factory 'i' than we actually manufactured.
model.s_over = pyo.Var(model.F, model.P, domain=pyo.NonNegativeReals)

# Math Form: s_cap[j] ≥ 0
# Captures exactly how many extra units we packed into warehouse 'j' past its real limit.
model.s_cap = pyo.Var(model.W, domain=pyo.NonNegativeReals)

# =====================================================================
# EXPORT MODEL FOR USE IN OBJECTIVE AND CONSTRAINTS
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MODEL INITIALIZATION COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"\nModel Type: {type(model).__name__}")
    print(f"Number of Sets: {len(model.component_map(pyo.Set))}")
    print(f"Number of Parameters: {len(model.component_map(pyo.Param))}")
    print(f"Number of Variables: {len(model.component_map(pyo.Var))}")
    print(f"\nSets defined: F, W, C, P")
    print(f"Decision variables defined: R, O, F_flow, X, Y")
    print(f"Slack variables defined: s_demand, s_under, s_over, s_cap")
