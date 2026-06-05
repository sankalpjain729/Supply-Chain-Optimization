"""Main Entry Point for MDVRPTW Solver.

Orchestrates data preparation, model building, solving, and reporting.
"""

import sys
from typing import Dict, Any

from .data_preparation import DataPreparation
from .model_builder import MDVRPTWModelBuilder
from .solver import MDVRPTWSolver
from .utils import MDVRPTWUtils, create_example_mdvrptw_instance


def run_mdvrptw_solver(
    n_mothers: int = 11,
    n_daughters: int = 191,
    n_vehicles: int = 10,
    vehicle_capacity: int = 100,
    strategy: str = "prune+decompose",
    time_limit: int = 300,
    verbose: bool = True
) -> Dict[str, Any]:
    """Main entry point for MDVRPTW solver.
    
    Args:
        n_mothers: Number of depots
        n_daughters: Number of customers
        n_vehicles: Vehicles per depot
        vehicle_capacity: Vehicle capacity
        strategy: Solving strategy ('exact', 'heuristic', 'prune+decompose')
        time_limit: Maximum solve time in seconds
        verbose: Print detailed output
        
    Returns:
        Solution dictionary
    """
    
    print("\n" + "="*80)
    print("MULTI-DEPOT VEHICLE ROUTING PROBLEM WITH TIME WINDOWS (MDVRPTW)")
    print("="*80)
    
    # Step 1: Data Preparation
    print("\n[Step 1] Preparing Data...")
    data_prep = DataPreparation(
        n_mothers=n_mothers,
        n_daughters=n_daughters,
        n_vehicles=n_vehicles,
        vehicle_capacity=vehicle_capacity
    )
    
    problem_data = data_prep.generate_synthetic_data(seed=42)
    
    if verbose:
        MDVRPTWUtils.print_problem_summary(problem_data)
        matrix_stats = data_prep.get_matrix_stats()
        print(f"\nDistance Matrix Stats:")
        print(f"  Min: {matrix_stats['distance_min']:.2f} km")
        print(f"  Max: {matrix_stats['distance_max']:.2f} km")
        print(f"  Mean: {matrix_stats['distance_mean']:.2f} km")
    
    # Step 2: Model Building
    print("\n[Step 2] Building MIP Model...")
    model_builder = MDVRPTWModelBuilder(problem_data)
    model_stats = model_builder.get_statistics()
    
    if verbose:
        print(f"Model Statistics:")
        print(f"  Depots: {model_stats['n_depots']}")
        print(f"  Customers: {model_stats['n_customers']}")
        print(f"  Total Nodes: {model_stats['n_total_nodes']}")
        print(f"  Binary Variables: {model_stats['n_binary_variables']}")
        print(f"  Continuous Variables: {model_stats['n_continuous_variables']}")
    
    # Step 3: Scalability Analysis
    if verbose:
        MDVRPTWUtils.print_scalability_analysis()
    
    # Step 4: Solving
    print(f"\n[Step 3] Solving using '{strategy}' strategy...")
    solver = MDVRPTWSolver(problem_data, strategy=strategy)
    solution = solver.solve(time_limit=time_limit)
    
    if verbose:
        solver_stats = solver.get_statistics()
        print(f"\nSolver Statistics:")
        print(f"  Strategy: {solver_stats['strategy']}")
        print(f"  Status: {solver_stats['status']}")
        print(f"  Objective: {solver_stats['objective']}")
        if solver_stats['pruning_reduction']:
            print(f"  Arc Pruning Reduction: {solver_stats['pruning_reduction']:.1f}%")
    
    # Step 5: Constraint Summary
    if verbose:
        MDVRPTWUtils.print_constraint_summary()
    
    # Step 6: Solution Validation and Reporting
    print(f"\n[Step 4] Validating and Reporting...")
    
    is_valid = MDVRPTWUtils.validate_solution(solution)
    if not is_valid:
        print("Warning: Solution may not be valid!")
    
    print(f"\n" + "="*80)
    print("SOLUTION SUMMARY")
    print("="*80)
    print(f"Status: {solution.get('status', 'Unknown')}")
    print(f"Objective Value: {solution.get('objective_value', 'N/A')}")
    print(f"Number of Routes: {solution.get('n_routes', 'N/A')}")
    print(f"Total Distance: {solution.get('total_distance', 'N/A'):.2f} km")
    print("="*80)
    
    return solution


def run_example():
    """Run example MDVRPTW problem."""
    print("\nRunning MDVRPTW Example (Small Instance)...")
    
    # Use smaller instance for demonstration
    solution = run_mdvrptw_solver(
        n_mothers=3,
        n_daughters=30,
        n_vehicles=5,
        vehicle_capacity=100,
        strategy="prune+decompose",
        time_limit=60,
        verbose=True
    )
    
    return solution


if __name__ == "__main__":
    # Run with default parameters or as example
    if len(sys.argv) > 1 and sys.argv[1] == "example":
        solution = run_example()
    else:
        # Run full MDVRPTW problem
        solution = run_mdvrptw_solver(
            n_mothers=11,
            n_daughters=191,
            strategy="prune+decompose",
            verbose=True
        )
