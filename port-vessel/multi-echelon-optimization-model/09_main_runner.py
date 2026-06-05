from data_definition import data_package
from model_initialization import model
from objective_function import model as obj_model
from constraints import model as constraint_model
from solver import solve_model
import results_analysis
from visualization import create_supply_chain_visualization


def main():
    results = solve_model()
    create_supply_chain_visualization()

    return results


if __name__ == "__main__":
    main()