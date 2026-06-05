"""Multi-Depot Vehicle Routing Problem with Time Windows (MDVRPTW) Solver.

This package provides a complete solution for the MDVRPTW using MIP formulation,
scalability optimization techniques, and heuristic approaches.

Modules:
    - data_preparation: Raw data loading and matrix generation
    - model_builder: MIP formulation and constraint setup
    - solver: Optimization and solver management
    - utils: Utility functions for visualization and analysis
    - main: Orchestration and entry point
"""

__version__ = "1.0.0"
__author__ = "Supply Chain Optimization Team"

from .data_preparation import DataPreparation
from .model_builder import MDVRPTWModelBuilder
from .solver import MDVRPTWSolver

__all__ = ["DataPreparation", "MDVRPTWModelBuilder", "MDVRPTWSolver"]
