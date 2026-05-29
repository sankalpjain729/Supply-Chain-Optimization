````markdown
# Multi-Echelon Supply Chain Optimization Model

A comprehensive optimization model for multi-echelon supply chain networks using Pyomo and GLPK solver. This model optimizes production, warehousing, and distribution decisions across factories, warehouses, and customers.

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
├── 06_solver.py                 # Configure and run GLPK solver
├── 07_results_analysis.py       # Analyze and display results
├── 08_visualization.py          # Create network visualization
├── 09_main_runner.py            # Main execution orchestrator
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip package manager

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
| `s_under[i,k]` | Under-shipment from factory i | Captures logistics discrepancy |
| `s_over[i,k]` | Over-shipment from factory i | Captures logistics discrepancy |
| `s_cap[j]` | Warehouse j over-capacity | Allows feasibility with penalty |

### Objective Function

```
Minimize: Z = 
    ∑ OC[j]·Y[j]                                    # Fixed warehouse costs
  + ∑ SC[i,j,k]·F_flow[i,j,k]                     # Inbound shipping costs
  + ∑ TC[j,c,k]·X[j,c,k]                          # Outbound transport costs
  + ∑ RC[i,k]·R[i,k]                              # Regular production costs
  + ∑ OC_p[i,k]·O[i,k]                            # Overtime production costs
  + P1·s_demand                                    # Unmet demand penalty (10,000)
  + P2·∑(s_under[i,k] + s_over[i,k])             # Logistics mismatch penalty (50)
  + P3·∑s_cap[j]                                  # Over-capacity penalty (10,000)
```

### Constraints

| ID | Constraint | Mathematical Form |
|----|-----------|-------------------|
| **C1** | Demand Coverage | ∑∑∑ X[j,c,k] + s_demand ≥ 0.8·D_total |
| **C2** | Max Demand Ceiling | ∑ X[j,c,k] ≤ D[c,k] ∀c,k |
| **C3** | Flow Balance | ∑ F_flow[i,j,k] = ∑ X[j,c,k] ∀j,k |
| **C4** | Warehouse Capacity | ∑∑ F_flow[i,j,k] - s_cap[j] ≤ Cap[j]·Y[j] ∀j |
| **C5** | Production Balance | ∑ F_flow[i,j,k] + s_under - s_over = R + O ∀i,k |
| **C6** | Regular Time Limit | ∑ t[i,k]·R[i,k] ≤ RegTime[i] ∀i |
| **C7** | Overtime Limit | ∑ t[i,k]·O[i,k] ≤ OTTime[i] ∀i |

## 📈 Data Parameters

### Factory Data
- Regular Time: 160 hours/week per factory
- Overtime: 40 hours/week per factory

### Warehouse Data
| Warehouse | Operating Cost | Capacity |
|-----------|----------------|----------|
| W1 | $5,000 | 150 units |
| W2 | $4,500 | 120 units |
| W3 | $6,000 | 160 units |
| W4 | $4,800 | 110 units |
| W5 | $5,200 | 140 units |

### Production Time & Cost
- Production times: 1.5-3.2 hours per unit
- Regular costs: $8-13 per unit
- Overtime costs: $12-19 per unit

### Demand
- Total demand: ~1,539 units across 6 customers and 3 products
- Coverage target: ≥80% of total demand

## 📊 Sample Output

```
====================================================================
SOLUTION RESULTS
====================================================================
Solver Status           : ok
Termination Condition   : optimal
Opened Warehouses       : ['W1', 'W3']
Total Network Cost      : $15,234.50

====================================================================
FACTORY PRODUCTION PLAN
====================================================================
F1 produces 45.0 units of P1 (Regular Time)
F1 produces 12.0 units of P2 (Overtime)
...

====================================================================
FACTORY TO WAREHOUSE SHIPMENTS
====================================================================
Ship 45.0 units of P1 from F1 → W1
Ship 12.0 units of P2 from F1 → W3
...

====================================================================
WAREHOUSE TO CUSTOMER DELIVERIES
====================================================================
Deliver 22.0 units of P1 from W1 → C1
Deliver 8.0 units of P2 from W3 → C2
...

====================================================================
PENALTY & SLACK ANALYSIS
====================================================================
Unmet Demand            : 0.0 units
Logistics Under-shipment: 0.0 units
Logistics Over-shipment : 0.0 units
Warehouse Over-capacity : 0.0 units
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
- **Solver**: GLPK (GNU Linear Programming Kit)
- **Problem Type**: Mixed-Integer Linear Program (MILP)
- **Optimization Direction**: Minimize

## 🔧 Dependencies

```
pyomo>=6.0          # Optimization modeling
pandas>=1.0         # Data manipulation
numpy>=1.19         # Numerical computing
networkx>=2.5       # Graph visualization
matplotlib>=3.3     # Plotting
glpk>=4.65          # Linear programming solver
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

### Issue: "GLPK not found"
**Solution**: Install GLPK
```bash
# Ubuntu/Debian
sudo apt-get install glpk-utils

# macOS
brew install glpk

# Windows: Download from http://www.gnu.org/software/glpk/
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
