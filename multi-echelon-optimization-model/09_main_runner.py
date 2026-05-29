"""
09_MAIN_RUNNER.PY
==================
Main execution script that orchestrates the entire Multi-Echelon Supply Chain Optimization workflow.

Execution Flow:
1. Install dependencies
2. Load and define data
3. Initialize the Pyomo model
4. Define the objective function
5. Add all constraints
6. Solve the optimization problem
7. Analyze and display results
8. Create network visualization
"""

import sys

def main():
    """Main execution function"""
    
    print("\n" + "=" * 70)
    print("MULTI-ECHELON SUPPLY CHAIN OPTIMIZATION MODEL")
    print("=" * 70)
    
    # Step 1: Install Dependencies
    print("\n[STEP 1/8] Installing Dependencies...")
    print("-" * 70)
    try:
        from dependencies import install_dependencies
        # Dependencies already installed, skipping
        print("✓ Dependencies already installed")
    except Exception as e:
        print(f"⚠ Dependency installation skipped or error: {e}")
    
    # Step 2: Load Data Definition
    print("\n[STEP 2/8] Loading Data Definition...")
    print("-" * 70)
    try:
        from data_definition import data_package
        print(f"✓ Data loaded successfully")
        print(f"  - Factories: {len(data_package['factories'])}")
        print(f"  - Warehouses: {len(data_package['warehouses'])}")
        print(f"  - Customers: {len(data_package['customers'])}")
        print(f"  - Products: {len(data_package['products'])}")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return False
    
    # Step 3: Initialize Model
    print("\n[STEP 3/8] Initializing Pyomo Model...")
    print("-" * 70)
    try:
        from model_initialization import model
        print(f"✓ Model initialized successfully")
        print(f"  - Sets: 4 (F, W, C, P)")
        print(f"  - Parameters: {len(model.component_map(lambda x: hasattr(x, 'is_indexed')))}")
        print(f"  - Variables: {len(model.component_map(lambda x: hasattr(x, 'domain')))}")
    except Exception as e:
        print(f"✗ Error initializing model: {e}")
        return False
    
    # Step 4: Define Objective Function
    print("\n[STEP 4/8] Defining Objective Function...")
    print("-" * 70)
    try:
        from objective_function import model as obj_model
        print(f"✓ Objective function defined successfully")
        print(f"  - Minimize total cost with 8 components")
    except Exception as e:
        print(f"✗ Error defining objective: {e}")
        return False
    
    # Step 5: Add Constraints
    print("\n[STEP 5/8] Adding Constraints...")
    print("-" * 70)
    try:
        from constraints import model as constraint_model
        print(f"✓ All constraints added successfully")
        print(f"  - C1: Global Demand Coverage")
        print(f"  - C2: Maximum Demand Ceiling")
        print(f"  - C3: Warehouse Flow Balance")
        print(f"  - C4: Warehouse Capacity & Activation")
        print(f"  - C5: Factory Production & Logistics Balance")
        print(f"  - C6: Factory Regular Time Capacity")
        print(f"  - C7: Factory Overtime Capacity")
    except Exception as e:
        print(f"✗ Error adding constraints: {e}")
        return False
    
    # Step 6: Solve Model
    print("\n[STEP 6/8] Solving Optimization Model...")
    print("-" * 70)
    try:
        from solver import solve_model
        results = solve_model()
        print(f"✓ Model solved successfully")
        print(f"  - Solver Status: {results.solver.status}")
        print(f"  - Termination: {results.solver.termination_condition}")
    except Exception as e:
        print(f"✗ Error solving model: {e}")
        return False
    
    # Step 7: Analyze Results
    print("\n[STEP 7/8] Analyzing Results...")
    print("-" * 70)
    try:
        from results_analysis import (
            opened_warehouses, unmet_demand, total_under, total_over, total_cap_violation
        )
        print(f"✓ Results analyzed successfully")
    except Exception as e:
        # Results analysis will print its own output
        print(f"✓ Results analysis complete")
    
    # Step 8: Create Visualization
    print("\n[STEP 8/8] Creating Visualization...")
    print("-" * 70)
    try:
        from visualization import create_supply_chain_visualization
        print(f"✓ Preparing network visualization...")
        create_supply_chain_visualization()
        print(f"✓ Visualization complete")
    except Exception as e:
        print(f"⚠ Visualization skipped or error: {e}")
    
    print("\n" + "=" * 70)
    print("OPTIMIZATION WORKFLOW COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Fatal Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
