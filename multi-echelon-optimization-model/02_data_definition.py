"""
02_DATA_DEFINITION.PY
=====================
Defines all sets, parameters, and data structures for the Multi-Echelon Supply Chain Optimization Model.

Sets Defined:
- Factories (F)
- Warehouses (W)
- Customers (C)
- Products (P)

Parameters Defined:
- Factory capacities and time constraints
- Warehouse storage and operating costs
- Production parameters (time, regular cost, overtime cost)
- Customer demand
- Shipping and transportation costs
"""

import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)

# ==========================================
# 1. DEFINE SETS
# ==========================================
factories = ['F1', 'F2', 'F3', 'F4']
warehouses = ['W1', 'W2', 'W3', 'W4', 'W5']
customers = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
products = ['P1', 'P2', 'P3']

# ==========================================
# 2. FACTORY PARAMETERS
# ==========================================
df_factories = pd.DataFrame({
    'RegTime': [160, 160, 160, 160],
    'OTTime': [40, 40, 40, 40]
}, index=factories)

# ==========================================
# 3. WAREHOUSE PARAMETERS (Restricted Capacities)
# ==========================================
df_warehouses = pd.DataFrame({
    'OC': [5000, 4500, 6000, 4800, 5200],
    'Cap': [150, 120, 160, 110, 140]
}, index=warehouses)

# ==========================================
# 4. PRODUCTION PARAMETERS (Simplified)
# ==========================================

simple_prod_data = [
    # Factory, Product, Time(t_ik), RegCost(RC_ik), OvertimeCost(OC_ik)
    ['F1', 'P1', 2.0, 10.0, 15.0],
    ['F1', 'P2', 3.0, 12.0, 18.0],
    ['F1', 'P3', 1.5,  8.0, 12.0],

    ['F2', 'P1', 2.5, 11.0, 16.0],
    ['F2', 'P2', 2.8, 11.0, 17.0],
    ['F2', 'P3', 1.8,  9.0, 13.0],

    ['F3', 'P1', 2.0, 10.0, 15.0],
    ['F3', 'P2', 3.2, 13.0, 19.0],
    ['F3', 'P3', 1.5,  8.0, 12.0],

    ['F4', 'P1', 2.2, 10.5, 15.5],
    ['F4', 'P2', 3.0, 12.0, 18.0],
    ['F4', 'P3', 1.6,  8.5, 12.5]
]

# 2. Turn it into a pandas table and name the columns
df_production = pd.DataFrame(simple_prod_data, columns=['Factory', 'Product', 't_ik', 'RC_ik', 'OC_ik'])

# 3. Tell pandas to group the table by Factory and Product
df_production.set_index(['Factory', 'Product'], inplace=True)

# ==========================================
# 5. CUSTOMER DEMAND (Simplified)
# ==========================================

# 1. Create a simple dictionary representing the columns of an order sheet
simple_demand_data = {
    # Product 1 Orders (for C1, C2, C3, C4, C5, C6)
    'P1': [22, 25, 30, 21, 28, 34],

    # Product 2 Orders
    'P2': [31, 20, 24, 29, 23, 27],

    # Product 3 Orders
    'P3': [25, 32, 21, 26, 30, 22]
}

# 2. Turn it into a table and explicitly label the rows with the Customer names
df_demand = pd.DataFrame(simple_demand_data, index=customers)

# ==========================================
# 6. PENALTIES & COST RULES (Simplified)
# ==========================================

# 1. Penalties (Think of these as massive fines for breaking contracts)
P1 = 10000  # Penalty fine if we fail to deliver what a customer ordered
P2 = 50     # Penalty fine if factory production doesn't match shipping logs
P3 = 10000  # Penalty fine if we stuff more boxes into a warehouse than it can hold

# 2. Factory -> Warehouse Shipping Rate Card
# Just like reading a map chart: to find the cost from Factory 1 to Warehouse 2,
# look at the 'F1' row, second number ($6.00).
sc_rate_card = {
    #      W1    W2    W3    W4    W5
    'F1': [4.0,  6.0,  5.0,  7.0,  3.0],
    'F2': [5.0,  4.0,  6.0,  5.0,  4.0],
    'F3': [6.0,  5.0,  4.0,  6.0,  5.0],
    'F4': [3.0,  7.0,  5.0,  4.0,  6.0]
}

# Convert our easy-to-read chart into the format Pyomo needs
sc_dict = {}
for f in factories:
    for w_index, w in enumerate(warehouses):
        for p in products:
            # Applies the route cost from our chart to every product shipped on that route
            sc_dict[(f, w, p)] = sc_rate_card[f][w_index]

# 3. Warehouse -> Customer Transportation Rate Card
tc_rate_card = {
    #      C1    C2    C3    C4    C5    C6
    'W1': [6.0,  8.0,  7.0,  5.0,  9.0,  6.0],
    'W2': [7.0,  5.0,  6.0,  8.0,  6.0,  7.0],
    'W3': [5.0,  7.0,  8.0,  6.0,  5.0,  8.0],
    'W4': [8.0,  6.0,  5.0,  7.0,  8.0,  5.0],
    'W5': [6.0,  9.0,  6.0,  5.0,  7.0,  8.0]
}

# Convert this chart into Pyomo's format
tc_dict = {}
for w in warehouses:
    for c_index, c in enumerate(customers):
        for p in products:
            tc_dict[(w, c, p)] = tc_rate_card[w][c_index]

# =====================================================================
# EXPORT DATA FOR USE IN OTHER MODULES
# =====================================================================

data_package = {
    'factories': factories,
    'warehouses': warehouses,
    'customers': customers,
    'products': products,
    'df_factories': df_factories,
    'df_warehouses': df_warehouses,
    'df_production': df_production,
    'df_demand': df_demand,
    'P1': P1,
    'P2': P2,
    'P3': P3,
    'sc_dict': sc_dict,
    'tc_dict': tc_dict
}

if __name__ == "__main__":
    print("=" * 60)
    print("DATA DEFINITION LOADED SUCCESSFULLY")
    print("=" * 60)
    print(f"\nFactories: {factories}")
    print(f"Warehouses: {warehouses}")
    print(f"Customers: {customers}")
    print(f"Products: {products}")
    print(f"\nFactory Parameters:\n{df_factories}")
    print(f"\nWarehouse Parameters:\n{df_warehouses}")
    print(f"\nProduction Parameters:\n{df_production}")
    print(f"\nCustomer Demand:\n{df_demand}")
