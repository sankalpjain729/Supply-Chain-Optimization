````markdown
# Multi-Echelon Supply Chain Optimization Model

A comprehensive optimization model for multi-echelon supply chain networks using Pyomo and HiGHS solver. This model optimizes production, warehousing, and distribution decisions across factories, warehouses, and customers.
## 📋 Project Overview

This project implements a **three-level supply chain network optimization**:
- **Level 1**: Factories (Production)
- **Level 2**: Warehouses (Distribution/Storage)
- **Level 3**: Customers (End Demand)

### Problem Statement
Minimize the total operating cost of a supply chain network subject to:
- Factory production capacity (regular time and overtime)
- Warehouse storage capacity and activation costs
- Customer demand fulfillment
- Material flow conservation
- Logistics accuracy constraints

## 🗂️ Project Structure

```
multi-echelon-optimization-model/
├── 01_dependencies.py           # Install required packages
├── 02_data_definition.py        # Define sets, parameters, and data
├── 03_model_initialization.py   # Initialize Pyomo model with sets, params, variables
├── 04_objective_function.py     # Define minimization objective
├── 05_constraints.py            # Add all operational constraints
├── 06_solver.py                 # Configure and run HiGHS solver
├── 07_results_analysis.py       # Analyze and display results
├── 08_visualization.py          # Create network visualization
├── 09_main_runner.py            # Main execution orchestrator
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip package manager
- HiGHS solver

### Installation & Execution

```bash
# Clone or navigate to the project directory
cd multi-echelon-optimization-model

# Run the main orchestrator (installs dependencies, solves, analyzes, visualizes)
python 09_main_runner.py
```

Or run individual modules:
```bash
# Install dependencies
python 01_dependencies.py

# Load and verify data
python 02_data_definition.py

# Initialize model
python 03_model_initialization.py

# Solve the model
python 06_solver.py

# Analyze results
python 07_results_analysis.py

# Visualize network
python 08_visualization.py
```

## 📊 Model Components

### Sets (Decision Dimensions)
| Set | Description | Elements |
|-----|-------------|----------|
| `F` | Factories | F1, F2, F3, F4 |
| `W` | Warehouses | W1, W2, W3, W4, W5 |
| `C` | Customers | C1, C2, C3, C4, C5, C6 |
| `P` | Products | P1, P2, P3 |

### Decision Variables

| Variable | Domain | Description |
|----------|--------|-------------|
| `R[i,k]` | Non-negative | Regular-time production of product k at factory i |
| `O[i,k]` | Non-negative | Overtime production of product k at factory i |
| `F_flow[i,j,k]` | Non-negative | Flow of product k from factory i to warehouse j |
| `X[j,c,k]` | Non-negative | Delivery of product k from warehouse j to customer c |
| `Y[j]` | Binary {0,1} | Warehouse j activation (1=open, 0=closed) |

### Slack Variables (Constraint Relaxation)

| Variable | Description | Purpose |
|----------|-------------|---------|
| `s_demand` | Unmet customer demand | Allows feasibility with penalty | 
| `s_cap[j]` | Warehouse j over-capacity | Allows feasibility with penalty |

### Objective Function

```
Minimize: Z = 
    ∑ OC[j]·Y[j]                                    # Fixed warehouse costs
  + ∑ SC[i,j,k]·F_flow[i,j,k]                     # Factory → warehouse transport cost
  + ∑ TC[j,c,k]·X[j,c,k]                          # Warehouse → customer transport cost
  + ∑ RC[i,k]·R[i,k]                              # Regular production cost
  + ∑ OC_p[i,k]·O[i,k]                            # Overtime production cost
  + P1·s_demand                                   # Unmet demand penalty
  + P2·∑ s_cap[j]                                 # Capacity violation penalty
  + ε1·warehouse_penalty                          # Tie-breaking term
  + ε2·flow_penalty                               # Flow regularization term
```

### Constraints

| ID | Constraint | Mathematical Form |
|----|-----------|-------------------|
| **C1** | Global demand satisfaction | ∑∑∑ X[j,c,k] + s_demand ≥ 0.8·D_total |
| **C2** | Customer-wise demand cap | ∑_{j ∈ W} X[j,c,k] ≤ D[c,k]    ∀ c ∈ C, k ∈ P |
| **C3** | Warehouse flow balance | ∑_{i ∈ F} F_flow[i,j,k] = ∑_{c ∈ C} X[j,c,k] ∀j,k |
| **C4** | Warehouse Capacity (soft) | ∑_{i ∈ F} ∑_{k ∈ P} F_flow[i,j,k] - s_cap[j] ≤ Cap[j] · Y[j]    ∀ j ∈ W |
| **C5** | Factory Production Balance (strict) | ∑_{j ∈ W} F_flow[i,j,k] = R[i,k] + O[i,k]    ∀ i ∈ F, k ∈ P |
| **C6** | Regular Time Capacity | ∑_{k ∈ P} t[i,k] · R[i,k] ≤ RegTime[i]    ∀ i ∈ F |
| **C7** | Overtime Capacity | ∑_{k ∈ P} t[i,k] · O[i,k] ≤ OTTime[i]    ∀ i ∈ F |

## 📈 Data Parameters

All input data is defined in `data_definition.py`. The tables below mirror the model inputs so you can read the problem without opening the code.

### `df_factories` — Factory time capacity (hours/week)

| Factory | RegTime | OTTime |
|---------|---------|--------|
| F1 | 160 | 40 |
| F2 | 160 | 40 |
| F3 | 160 | 40 |
| F4 | 160 | 40 |

### `df_warehouses` — Warehouse fixed cost and capacity

| Warehouse | OC ($) | Cap (units) |
|-----------|--------|-------------|
| W1 | 5,000 | 150 |
| W2 | 4,500 | 120 |
| W3 | 6,000 | 160 |
| W4 | 4,800 | 110 |
| W5 | 5,200 | 140 |

### `df_production` — Production time and unit costs

| Factory | Product | t_ik (hrs/unit) | RC_ik ($/unit) | OC_ik ($/unit OT) |
|---------|---------|-----------------|----------------|-------------------|
| F1 | P1 | 2.0 | 10.0 | 15.0 |
| F1 | P2 | 3.0 | 12.0 | 18.0 |
| F1 | P3 | 1.5 | 8.0 | 12.0 |
| F2 | P1 | 2.5 | 11.0 | 16.0 |
| F2 | P2 | 2.8 | 11.0 | 17.0 |
| F2 | P3 | 1.8 | 9.0 | 13.0 |
| F3 | P1 | 2.0 | 10.0 | 15.0 |
| F3 | P2 | 3.2 | 13.0 | 19.0 |
| F3 | P3 | 1.5 | 8.0 | 12.0 |
| F4 | P1 | 2.2 | 10.5 | 15.5 |
| F4 | P2 | 3.0 | 12.0 | 18.0 |
| F4 | P3 | 1.6 | 8.5 | 12.5 |

### `df_demand` — Customer demand by product (units)

| Customer | P1 | P2 | P3 |
|----------|----|----|-----|
| C1 | 22 | 31 | 25 |
| C2 | 25 | 20 | 32 |
| C3 | 30 | 24 | 21 |
| C4 | 21 | 29 | 26 |
| C5 | 28 | 23 | 30 |
| C6 | 34 | 27 | 22 |
| **Total** | **160** | **154** | **156** |

- **Total demand:** 470 units (6 customers × 3 products)
- **Coverage target (C1):** deliver at least **80%** → 376 units

### Factory → warehouse shipping (`sc_rate_card`, $/unit)

Same cost for all products on a given lane; full tensor is `(factory, warehouse, product)`.

| Factory | W1 | W2 | W3 | W4 | W5 |
|---------|----|----|----|----|-----|
| F1 | 4.0 | 6.0 | 5.0 | 7.0 | 3.0 |
| F2 | 5.0 | 4.0 | 6.0 | 5.0 | 4.0 |
| F3 | 6.0 | 5.0 | 4.0 | 6.0 | 5.0 |
| F4 | 3.0 | 7.0 | 5.0 | 4.0 | 6.0 |

### Warehouse → customer shipping (`tc_rate_card`, $/unit)

| Warehouse | C1 | C2 | C3 | C4 | C5 | C6 |
|-----------|----|----|----|----|----|-----|
| W1 | 6.0 | 8.0 | 7.0 | 5.0 | 9.0 | 6.0 |
| W2 | 7.0 | 5.0 | 6.0 | 8.0 | 6.0 | 7.0 |
| W3 | 5.0 | 7.0 | 8.0 | 6.0 | 5.0 | 8.0 |
| W4 | 8.0 | 6.0 | 5.0 | 7.0 | 8.0 | 5.0 |
| W5 | 6.0 | 9.0 | 6.0 | 5.0 | 7.0 | 8.0 |

### Penalty parameters

| Parameter | Value | Meaning |
|-----------|-------|---------|
| P1 | $10,000 | Per unit of unmet demand (`s_demand`) |
| P2 | $50 | Per unit of warehouse over-capacity (`s_cap`) |
| P3 | $10,000 | Reserved (legacy) |

## 📊 Sample Output

```
============================================================
SOLUTION RESULTS
============================================================

Solver Status           : ok
Termination Condition   : optimal
Opened Warehouses       : ['W1', 'W2', 'W4']
Total Network Cost      : $21,746.16
Demand Fulfillment      : 376.0 / 376.0 units (100.00%)

============================================================
FACTORY PRODUCTION PLAN
============================================================
F1 produces 72.3 units of P1 (Regular Time)
F1 produces 4.7 units of P1 (Overtime)
F1 produces 10.2 units of P2 (Overtime)
F1 produces 10.2 units of P3 (Regular Time)
F2 produces 57.1 units of P2 (Regular Time)
F2 produces 7.6 units of P2 (Overtime)
F3 produces 33.5 units of P1 (Regular Time)
F3 produces 4.5 units of P1 (Overtime)
F3 produces 62.0 units of P3 (Regular Time)
F4 produces 11.8 units of P1 (Regular Time)
F4 produces 18.2 units of P1 (Overtime)
F4 produces 83.8 units of P3 (Regular Time)

============================================================
FACTORY TO WAREHOUSE SHIPMENTS
============================================================
Ship 77.0 units of P1 from F1 → W1
Ship 10.2 units of P2 from F1 → W1
Ship 10.2 units of P3 from F1 → W1
Ship 20.0 units of P2 from F2 → W2
Ship 44.8 units of P2 from F2 → W4
Ship 38.0 units of P1 from F3 → W2
Ship 62.0 units of P3 from F3 → W2
Ship 48.5 units of P3 from F4 → W1
Ship 30.0 units of P1 from F4 → W4
Ship 35.2 units of P3 from F4 → W4

============================================================
WAREHOUSE TO CUSTOMER DELIVERIES
============================================================
Deliver 22.0 units of P1 from W1 → C1
Deliver 25.0 units of P3 from W1 → C1
Deliver 21.0 units of P1 from W1 → C4
Deliver 10.2 units of P2 from W1 → C4
Deliver 26.0 units of P3 from W1 → C4
Deliver 34.0 units of P1 from W1 → C6
Deliver 7.8 units of P3 from W1 → C6
Deliver 25.0 units of P1 from W2 → C2
Deliver 20.0 units of P2 from W2 → C2
Deliver 32.0 units of P3 from W2 → C2
Deliver 13.0 units of P1 from W2 → C5
Deliver 30.0 units of P3 from W2 → C5
Deliver 30.0 units of P1 from W4 → C3
Deliver 17.8 units of P2 from W4 → C3
Deliver 21.0 units of P3 from W4 → C3
Deliver 27.0 units of P2 from W4 → C6
Deliver 14.2 units of P3 from W4 → C6

============================================================
PENALTY & SLACK ANALYSIS
============================================================

Unmet Demand            : 0.0 units
Warehouse Over-capacity : 0.0 units

============================================================
SOLVING OPTIMIZATION MODEL...
============================================================
``` 

### Greedy Heuristic

### Starts with all warehouses closed and no production/transport decisions made
### Targets only **80% of total demand** instead of full satisfaction for feasibility
### Repeatedly searches all factory–warehouse–customer combinations

### Filters out infeasible choices:
### warehouse capacity exceeded
### factory time (regular + overtime) unavailable
### no remaining demand

### For each feasible option:
### computes production cost (regular or overtime)
### adds transport cost (factory → warehouse → customer)
### adds penalty if a warehouse is being opened for the first time

### Selects the option with **minimum total cost**

### Decides shipment quantity based on:
### remaining demand
### warehouse capacity
### factory time limits

### Executes the decision and updates:
### demand remaining
### warehouse capacity used
### factory time usage
### total cost

### Repeats until:
### 80% demand is met, or
### no valid move exists

## 🔍 Heuristic Solution

### Running Greedy Heuristic
```bash
python heuristic.py
```
### Heuristic Summary
```text
# Demand fulfilled       : 376.00 / 376.00
# Warehouses used        : ['W1', 'W3', 'W5']
# Fixed cost             : $16,200.00
# Variable cost          : $7,619.29
# Total heuristic cost   : $23,819.29
```

## 🔍 Sensitivity Analysis

Tests network resilience across three demand scenarios (85%, 100%, and 125% of baseline demand).

### Running Sensitivity Analysis
```bash
python sensitivity_analysis.py
```

### Sample Output
```
--- STARTING MILP SENSITIVITY RUNS ---

============================================================
  SCENARIO: Low Demand (85%)
============================================================
  Demand Multiplier     : 85%
  Total Demand          : 399.5 units
  Delivered / Target    : 319.6 / 319.6 units
  Fill Rate             : 80.0%
  Target Achievement    : 100.0%
  Opened Hubs (2)     : W1, W3
  True Network Cost     : $17,050.78
  Penalty Cost          : $480.00
  Capacity Violations   : 9.6 units

============================================================
  SCENARIO: Baseline Demand (100%)
============================================================
  Demand Multiplier     : 100%
  Total Demand          : 470.0 units
  Delivered / Target    : 376.0 / 376.0 units
  Fill Rate             : 80.0%
  Target Achievement    : 100.0%
  Opened Hubs (3)     : W1, W2, W4
  True Network Cost     : $21,746.16
  Penalty Cost          : $0.00
  Capacity Violations   : 0.0 units

============================================================
  SCENARIO: High Stress Demand (125%)
============================================================
  Demand Multiplier     : 125%
  Total Demand          : 587.5 units
  Delivered / Target    : 399.3 / 470.0 units
  Fill Rate             : 68.0%
  Target Achievement    : 85.0%
  Opened Hubs (3)     : W1, W2, W5
  True Network Cost     : $22,719.19
  Penalty Cost          : $706,603.17
  Capacity Violations   : 0.0 units

============================================================
             SUPPLY CHAIN RESILIENCY REPORT
============================================================
                            Status  Target 80% Vol  Actual Delivered  Hub Count  Opened Hubs  True Network Cost  Capacity Violations
Low Demand (85%)           Optimal          319.6             319.6          2  [W1, W3]        $17,050.78                  9.6
Baseline Demand (100%)     Optimal          376.0             376.0          3  [W1, W2, W4]    $21,746.16                  0.0
High Stress Demand (125%)  Optimal          470.0             399.3          3  [W1, W2, W5]    $22,719.19                  0.0
```

## 🎨 Visualization

The model generates a 3-layer network graph showing:
- **Left Layer**: Factories (production sources)
- **Middle Layer**: Active warehouses (distribution hubs)
- **Right Layer**: Customers (demand points)
- **Edges**: Product flows with quantities

## ⚙️ Configuration & Parameters

### Penalties
- **P1** (Unmet Demand): $10,000 per unit
- **P2** (Logistics Mismatch): $50 per unit
- **P3** (Over-Capacity): $10,000 per unit

### Solver
- **Solver**: HiGHS (High-Performance Solver)
- **Problem Type**: Mixed-Integer Linear Program (MILP)
- **Optimization Direction**: Minimize

## 🔧 Dependencies

```
pyomo>=6.0          # Optimization modeling
pandas>=1.0         # Data manipulation
numpy>=1.19         # Numerical computing
networkx>=2.5       # Graph visualization
matplotlib>=3.3     # Plotting
highspy>=0.1.0      # High-Performance Solver
```

Install all dependencies:
```bash
python 01_dependencies.py
```

## 📝 Modification Guide

### Change Production Capacity
Edit `02_data_definition.py`:
```python
df_factories = pd.DataFrame({
    'RegTime': [200, 200, 200, 200],  # Increase to 200 hours
    'OTTime': [50, 50, 50, 50]         # Increase to 50 hours
}, index=factories)
```

### Add New Warehouse
Edit `02_data_definition.py`:
```python
warehouses = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6']  # Add W6
```

### Adjust Demand Coverage Target
Edit `05_constraints.py`:
```python
rule=lambda m: sum(...) >= 0.9 * D_total  # Increase from 80% to 90%
```

### Modify Penalty Values
Edit `02_data_definition.py`:
```python
P1 = 15000  # Increase unmet demand penalty
P2 = 100    # Increase logistics mismatch penalty
P3 = 15000  # Increase over-capacity penalty
```

## 🐛 Troubleshooting

### Issue: "HiGHS not found"
**Solution**: Install HiGHS
```bash
# Ubuntu/Debian
sudo apt-get install highs-utils

# macOS
brew install highs

# Windows: Download from https://highs.dev/
```

### Issue: "Module not found"
**Solution**: Ensure you're running from the project directory and all dependencies are installed
```bash
cd multi-echelon-optimization-model
python 01_dependencies.py
```

### Issue: "Infeasible solution"
**Solution**: Check constraints are not too restrictive
- Lower demand coverage target (reduce 0.8 in C1)
- Increase factory capacities
- Reduce warehouse costs for more flexibility

## 📚 Theory & References

This model implements concepts from:
- **Supply Chain Network Design**: Multi-echelon inventory and distribution
- **Mixed-Integer Linear Programming**: Optimization with binary decisions
- **Operations Research**: Transportation and warehouse location problems

## 👨‍💼 Author & License

Created for supply chain optimization analysis and educational purposes.

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review constraint definitions in `05_constraints.py`
3. Verify data in `02_data_definition.py`

---

**Last Updated**: May 29, 2026
**Model Version**: 1.0
````
