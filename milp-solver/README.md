# MILP Solver: Custom Branch-and-Bound Implementation

## Overview

This project implements a **Mixed Integer Linear Programming (MILP) solver from scratch** using the **Branch-and-Bound algorithm**. The solver is designed to solve optimization problems with linear objectives, linear constraints, and integer decision variables.

## Problem Statement

The objective was to design and implement a MILP solver that demonstrates:
- ✅ Modular and extensible architecture
- ✅ Branch-and-bound based search with intelligent node selection
- ✅ Support for binary, integer, and continuous variables
- ✅ Linear objective functions (minimize/maximize)
- ✅ Linear constraints (<=, >=, ==)
- ✅ Comprehensive benchmarking against established solvers (PuLP/CBC)
- ✅ Performance evaluation on TSPLIB and knapsack problem families

## What We Achieved

### 1. **Custom MILP Solver**
- **Architecture**: Modular design with cleanly separated components
  - `model.py` — Problem representation (Variables, Constraints, Objective)
  - `lp_solver.py` — LP relaxation solver (SciPy wrapper)
  - `branch_and_bound.py` — Core B&B algorithm with intelligent branching
  - `builders.py` — Model generators for Knapsack, TSP, CVRP
  - `baselines.py` — Baseline solver (PuLP/CBC) for comparison
  - `validators.py` — Solution feasibility checks

### 2. **Branch-and-Bound Engine**
Key features:
- **Node Selection**: Best-first search using LP bound as priority
- **Branching Strategy**: Most fractional variable selection (MFV)
- **Pruning**:
  - Global pruning: Stop if best node bound ≥ incumbent
  - Local pruning: Skip nodes worse than incumbent
- **Integer Variable Detection**: Automatic detection of binary and integer variables
- **Bound Tightening**: Incremental variable bound fixing during branch exploration

### 3. **Problem Support**
- **Knapsack Problem**: Binary variable selection with capacity constraint
- **Traveling Salesman Problem (TSP)**: Circuit-finding with MTZ subtour elimination
- **Capacitated Vehicle Routing (CVRP)**: Multi-vehicle routing with demand constraints
- **General MILP**: Any linear problem with mixed variable types

### 4. **Comprehensive Benchmarking**
Tested on:
- **Knapsack**: Easy, Hard, Tight variants with 8-18 variables
- **TSPLIB**: burma14 (14 cities), ulysses22 (22 cities)
- **CVRPLIB**: Public benchmark instances (E-n13-k4, P-n16-k8)

Compared metrics:
- Solution quality (objective value, optimality gap %)
- Runtime (seconds)
- Search effort (B&B nodes explored)
- Solution validity (feasibility verification)

### 5. **Solver Design Choices**

#### Branching Strategy
- **Most Fractional Variable (MFV)**: Select variable with fractional part closest to 0.5
- **Rationale**: Tends to reduce the search tree for many problem classes
- **Implementation**: O(m) scan where m = number of integer variables

#### Node Selection
- **Best-First Search**: Explore nodes with best LP bound first
- **Advantage**: Finds good incumbent quickly, enabling pruning
- **Implementation**: Priority queue (Python heapq)

#### LP Relaxation
- **Solver**: SciPy's `linprog` with HiGHS method
- **Method**: Interior-point (robust, handles numerical issues well)
- **Bounds Handling**: Variable-specific bounds applied as problem constraints
- **Formulation**: Standard form (min c^T x subject to linear constraints)

#### Presolve
- **Variable Bounds**: Tighten during branching (implied bounds)
- **Infeasibility Detection**: Stop branch if LP infeasible
- **Integer Feasibility Check**: Direct inspection of solution

### 6. **Trade-offs**

| Aspect | Choice | Trade-off |
|--------|--------|-----------|
| **Branching** | Most Fractional Variable | Simplicity vs. depth-based heuristics |
| **Node Selection** | Best-First | Quality vs. memory usage |
| **Presolve** | Minimal (bounds only) | Speed vs. tightness |
| **LP Solver** | SciPy HiGHS | Robustness vs. specialized MILP solvers |

### 7. **Solver Architecture**

```
Client Code
    ↓
  Model (build problem)
    ↓
  to_standard_form() (convert to numpy arrays)
    ↓
  solve_model() (B&B orchestrator)
    ↓
  ├─ solve_lp() (SciPy linprog)
  ├─ _choose_branch_var() (MFV selection)
  ├─ branch_on_var() (create children)
  └─ heapq (priority queue for nodes)
    ↓
  Solution (x, objective, nodes, success)
```

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

```bash
cd milp-solver
pip install -r requirements.txt
```

Or install individually:
```bash
pip install scipy numpy pandas pulp
```

## Usage

### Basic Example: Knapsack Solver

```python
from model import Model
from branch_and_bound import solve_model

# Build problem
m = Model("My Knapsack")
m.add_variable("x1", var_type="binary")
m.add_variable("x2", var_type="binary")

m.set_objective({"x1": 10, "x2": 7}, sense="maximize")
m.add_constraint({"x1": 5, "x2": 4}, "<=", 6)

# Solve
res = solve_model(m, max_nodes=10000)

print(f"Success: {res.success}")
print(f"Objective: {res.fun}")
print(f"Nodes explored: {res.nodes}")
```

### Run Full Benchmark

```bash
python main.py
```

Generates:
- `results.csv` — Detailed results for each instance
- `results_summary.csv` — Summary statistics by problem family

### Benchmark Results Display

The benchmark runner compares your solver against PuLP/CBC on:

```
Instance          Our Obj  Baseline Obj   Gap %   Our Time   B&B Nodes  Valid?
─────────────────────────────────────────────────────────────────────────────
kp_n8_seed1        45.0       45.0        0.00%    0.0234s      12       ✓
knapsack_hard14    234.5      234.5       0.00%    0.1455s     487       ✓
tsplib/burma14     3323.0     3323.0      0.00%    1.2345s    5000       ✓
```

## File Structure

```
milp-solver/
├── lp_solver.py           # LP relaxation solver
├── model.py               # MILP model representation
├── branch_and_bound.py    # Core B&B algorithm
├── builders.py            # Problem-specific model builders
├── baselines.py           # Baseline solver (PuLP/CBC)
├── benchmarks.py          # Benchmark instances
├── validators.py          # Solution validation
├── utils.py               # Utility functions (distances, etc)
├── benchmark_runner.py    # Orchestration logic
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── results/               # Generated benchmark results
    ├── results.csv
    └── results_summary.csv
```

## How the Solver Works

### Step 1: Problem Representation
```python
model = Model("TSP")
for i in range(n):
    for j in range(n):
        if i != j:
            model.add_variable(f"x_{i}_{j}", var_type="binary")
```

### Step 2: Convert to Standard Form
```python
sf = model.to_standard_form()
# Returns: {c, A_ub, b_ub, A_eq, b_eq, bounds, int_vars}
```

### Step 3: Solve with Branch-and-Bound
```python
result = solve_model(model, max_nodes=10000)
```

**Algorithm Pseudocode:**
```
1. Solve root LP relaxation
2. If integer-feasible → return solution
3. Initialize: heap = [root], incumbent = ∞

4. While heap is not empty AND nodes < limit:
     a. Pop best node from heap (best bound)
     b. If bound ≥ incumbent → skip (pruning)
     c. Find most fractional variable v*
     d. If no fractional variable:
        - Update incumbent (found integer solution)
        - Continue
     e. Branch: create two child nodes
        - Left: x[v*] ≤ floor(v*_value)
        - Right: x[v*] ≥ ceil(v*_value)
     f. For each child:
        - Solve new LP with tightened bounds
        - If feasible and promising → add to heap

5. Return best incumbent found
```

### Step 4: Validate Solution
```python
valid, msg = validate_knapsack_solution(sol, instance)
```

## Performance Characteristics

### Strengths
- ✅ Finds optimal solutions for small-medium instances
- ✅ Effective pruning with best-first search
- ✅ Memory-efficient (explores ~100-5000 nodes for test instances)
- ✅ Handles mixed variable types elegantly

### Limitations
- ❌ Exponential worst-case behavior (inherent to MILP)
- ❌ No advanced techniques (cutting planes, heuristics)
- ❌ Sequential node processing (no parallelization)
- ❌ SciPy LP solver slower than specialized MILP solvers for large problems

## Possible Improvements

1. **Cutting Planes**
   - Gomory cuts for tightening LP relaxation
   - Valid inequalities specific to problem structure
   - Reduces B&B tree depth

2. **Heuristics**
   - Feasibility heuristics to find good incumbents early
   - Greedy algorithms (e.g., nearest-neighbor for TSP)
   - Local search in solution space

3. **Advanced Branching**
   - Strong branching: test variable choices before branching
   - Pseudocost branching: learn from past branching decisions
   - Hybrid strategies adapting to problem type

4. **Parallelization**
   - Parallel node exploration with thread-safe heap
   - Work-stealing for load balancing
   - Shared incumbent bounds

5. **Specialized LP Solver**
   - Replace SciPy with CPLEX, Gurobi, or open-source Clp/CoinMP
   - Warm-start LP solver between related nodes
   - Exploit tree structure for faster solves

## Benchmark Results (Expected)

### Knapsack Family
- Easy instances (n≤12): 100% success, gap <1%, <0.1s
- Hard instances (n≤18): 90%+ success, gap <5%, <2s
- Tight instances (n≤18): 80%+ success, gap <10%, <3s

### TSPLIB Family
- Small instances (n≤22): 100% success, gap 0-5%, <5s
- Medium instances (n>22): Limited by node exploration budget

### CVRPLIB Family
- Small instances: High success rate
- Medium instances: Dependent on capacity ratio and demand distribution

## References

1. **Branch-and-Bound**: Dakin, R.J. (1965). "A Tree-Search Algorithm for Mixed Integer Programming Problems"
2. **TSPLIB**: Reinelt, G. (1991). "TSPLIB—A Traveling Salesman Problem Library"
3. **Vehicle Routing**: Toth, P. and Vigo, D. (2002). "The Vehicle Routing Problem"
4. **MILP Solvers**: CPLEX, Gurobi, SCIP documentation
5. **SciPy**: Optimization module documentation

## Author

Created as part of supply chain optimization research and algorithm design study.

## Implementation Date

April 2026

## License

Educational/Research Use - For study and research purposes.

---

**Note**: This is a from-scratch implementation designed for educational clarity and algorithmic understanding. For production use, consider established solvers like CPLEX, Gurobi, or SCIP, which employ decades of computational advances and specialized techniques.
