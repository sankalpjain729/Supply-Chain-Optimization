import pandas as pd
import numpy as np

np.random.seed(42)

# Sets
factories = ['F1', 'F2', 'F3', 'F4']
warehouses = ['W1', 'W2', 'W3', 'W4', 'W5']
customers = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']
products = ['P1', 'P2', 'P3']

# Factory parameters
df_factories = pd.DataFrame({
    'RegTime': [160, 160, 160, 160],
    'OTTime': [40, 40, 40, 40]
}, index=factories)

# Warehouse parameters
df_warehouses = pd.DataFrame({
    'OC': [5000, 4500, 6000, 4800, 5200],
    'Cap': [150, 120, 160, 110, 140]
}, index=warehouses)

# Production parameters
simple_prod_data = [
    ['F1', 'P1', 2.0, 10.0, 15.0],
    ['F1', 'P2', 3.0, 12.0, 18.0],
    ['F1', 'P3', 1.5, 8.0, 12.0],

    ['F2', 'P1', 2.5, 11.0, 16.0],
    ['F2', 'P2', 2.8, 11.0, 17.0],
    ['F2', 'P3', 1.8, 9.0, 13.0],

    ['F3', 'P1', 2.0, 10.0, 15.0],
    ['F3', 'P2', 3.2, 13.0, 19.0],
    ['F3', 'P3', 1.5, 8.0, 12.0],

    ['F4', 'P1', 2.2, 10.5, 15.5],
    ['F4', 'P2', 3.0, 12.0, 18.0],
    ['F4', 'P3', 1.6, 8.5, 12.5]
]

df_production = pd.DataFrame(
    simple_prod_data,
    columns=['Factory', 'Product', 't_ik', 'RC_ik', 'OC_ik']
)
df_production.set_index(['Factory', 'Product'], inplace=True)

# Customer demand
simple_demand_data = {
    'P1': [22, 25, 30, 21, 28, 34],
    'P2': [31, 20, 24, 29, 23, 27],
    'P3': [25, 32, 21, 26, 30, 22]
}

df_demand = pd.DataFrame(simple_demand_data, index=customers)

# Penalty parameters
P1 = 10000
P2 = 50
P3 = 10000

# Factory-to-warehouse transportation costs
sc_rate_card = {
    'F1': [4.0, 6.0, 5.0, 7.0, 3.0],
    'F2': [5.0, 4.0, 6.0, 5.0, 4.0],
    'F3': [6.0, 5.0, 4.0, 6.0, 5.0],
    'F4': [3.0, 7.0, 5.0, 4.0, 6.0]
}

sc_dict = {}
for f in factories:
    for w_index, w in enumerate(warehouses):
        for p in products:
            sc_dict[(f, w, p)] = sc_rate_card[f][w_index]

# Warehouse-to-customer transportation costs
tc_rate_card = {
    'W1': [6.0, 8.0, 7.0, 5.0, 9.0, 6.0],
    'W2': [7.0, 5.0, 6.0, 8.0, 6.0, 7.0],
    'W3': [5.0, 7.0, 8.0, 6.0, 5.0, 8.0],
    'W4': [8.0, 6.0, 5.0, 7.0, 8.0, 5.0],
    'W5': [6.0, 9.0, 6.0, 5.0, 7.0, 8.0]
}

tc_dict = {}
for w in warehouses:
    for c_index, c in enumerate(customers):
        for p in products:
            tc_dict[(w, c, p)] = tc_rate_card[w][c_index]

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