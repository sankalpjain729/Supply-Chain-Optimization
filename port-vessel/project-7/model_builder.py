"""Model Builder Module for MDVRPTW.

Constructs the Mixed-Integer Programming (MIP) formulation of the MDVRPTW problem
using Pyomo, including all decision variables, constraints, and the objective function.
"""

from typing import Dict, Any, Tuple
import pyomo.environ as pyo


class MDVRPTWModelBuilder:
    """Build the MIP formulation for MDVRPTW.
    
    Attributes:
        model (pyomo.ConcreteModel): Pyomo optimization model
        data (Dict): Problem data from DataPreparation
        M (int): Number of depots
        D (int): Number of customers
        K_m (int): Vehicles per depot
        Q (int): Vehicle capacity
    """
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize model builder with problem data.
        
        Args:
            data: Dictionary from DataPreparation.generate_synthetic_data()
        """
        self.data = data
        self.model = pyo.ConcreteModel()
        
        # Extract parameters
        self.M = data["parameters"]["n_mothers"]  # Number of depots
        self.D = data["parameters"]["n_daughters"]  # Number of customers
        self.K_m = data["parameters"]["n_vehicles"]  # Vehicles per depot
        self.Q = data["parameters"]["vehicle_capacity"]  # Vehicle capacity
        
        # Node indices
        self.N = self.M + self.D  # Total nodes
        self.depots = list(range(self.M))
        self.customers = list(range(self.M, self.N))
        
        self._build_model()
    
    def _build_model(self):
        """Build complete MIP model with sets, parameters, variables, and constraints."""
        self._define_sets()
        self._define_parameters()
        self._define_variables()
        self._define_objective()
        self._define_constraints()
    
    def _define_sets(self):
        """Define model sets: nodes, depots, customers, vehicles, arcs."""
        self.model.N = pyo.Set(initialize=list(range(self.N)))  # All nodes
        self.model.M_set = pyo.Set(initialize=self.depots)  # Depots
        self.model.D_set = pyo.Set(initialize=self.customers)  # Customers
        
        # Set of vehicles for each depot
        self.model.K_m = pyo.Set(initialize=[i for i in range(self.K_m)])  # Vehicles per depot
        
        # Set of all (depot, vehicle) pairs
        self.model.MK = pyo.Set(
            initialize=[(m, k) for m in self.depots for k in range(self.K_m)]
        )
    
    def _define_parameters(self):
        """Define problem parameters: distances, costs, time windows, demands."""
        distance_matrix = self.data["distance_matrix"]
        duration_matrix = self.data["duration_matrix"]
        
        # Distance parameter d[i,j,km]
        def init_distance(m, k, i, j):
            return distance_matrix.get((i, j), 0)
        
        self.model.d_ijk = pyo.Param(
            self.model.M_set, self.model.K_m, self.model.N, self.model.N,
            initialize=init_distance, mutable=True
        )
        
        # Duration parameter t[i,j,km]
        def init_duration(m, k, i, j):
            return duration_matrix.get((i, j), 0)
        
        self.model.t_ij = pyo.Param(
            self.model.M_set, self.model.K_m, self.model.N, self.model.N,
            initialize=init_duration, mutable=True
        )
        
        # Demand q_j
        def init_demand(j):
            if j in self.customers:
                customer_idx = j - self.M
                return self.data["customers"][customer_idx]["demand"]
            return 0
        
        self.model.q_j = pyo.Param(self.model.N, initialize=init_demand)
        
        # Time windows (a_j, b_j)
        time_windows = self.data["time_windows"]
        def init_tw_start(j):
            return time_windows.get(j, (360, 600))[0]
        
        def init_tw_end(j):
            return time_windows.get(j, (360, 600))[1]
        
        self.model.a_j = pyo.Param(self.model.N, initialize=init_tw_start, mutable=True)
        self.model.b_j = pyo.Param(self.model.N, initialize=init_tw_end, mutable=True)
        
        # Cost parameters
        self.model.F = pyo.Param(initialize=1000)  # Fixed cost per vehicle
        self.model.c_d = pyo.Param(initialize=10)  # Cost per km
        self.model.c_t = pyo.Param(initialize=0.833)  # Cost per minute
        self.model.P = pyo.Param(initialize=100000)  # Penalty for skipping
        self.model.M_big = pyo.Param(initialize=10000)  # Big-M constant
    
    def _define_variables(self):
        """Define decision variables: arc flows, arrival times, slack variables."""
        # x[i,j,km]: Binary - vehicle k from depot m travels from i to j
        self.model.x_ijk = pyo.Var(
            self.model.M_set, self.model.K_m, self.model.N, self.model.N,
            domain=pyo.Binary
        )
        
        # y[km]: Binary - vehicle k at depot m is activated
        self.model.y_km = pyo.Var(
            self.model.M_set, self.model.K_m,
            domain=pyo.Binary
        )
        
        # t_i[km,i]: Continuous - arrival time at node i for vehicle k from depot m
        self.model.t_i = pyo.Var(
            self.model.M_set, self.model.K_m, self.model.N,
            domain=pyo.NonNegativeReals
        )
        
        # late[i]: Continuous - lateness slack at customer i
        self.model.late_i = pyo.Var(
            self.model.N,
            domain=pyo.NonNegativeReals
        )
        
        # overload[km]: Continuous - overload slack for vehicle k from depot m
        self.model.overload_km = pyo.Var(
            self.model.M_set, self.model.K_m,
            domain=pyo.NonNegativeReals
        )
        
        # s[j]: Binary - customer j is skipped
        self.model.s_j = pyo.Var(
            self.model.D_set,
            domain=pyo.Binary
        )
    
    def _define_objective(self):
        """Define objective function: minimize total cost."""
        # C1: Fixed cost for activated vehicles
        fixed_cost = pyo.summation(self.model.F, self.model.y_km)
        
        # C2: Distance cost
        distance_cost = pyo.summation(
            self.model.c_d * self.model.d_ijk,
            self.model.x_ijk
        )
        
        # C3: Time cost
        time_cost = pyo.summation(
            self.model.c_t * self.model.t_ij,
            self.model.x_ijk
        )
        
        # C4: Penalty for lateness
        lateness_penalty = pyo.summation(
            self.model.P,
            self.model.late_i
        )
        
        # C5: Penalty for skipped customers
        skip_penalty = pyo.summation(
            self.model.P,
            self.model.s_j
        )
        
        self.model.obj = pyo.Objective(
            expr=fixed_cost + distance_cost + time_cost + lateness_penalty + skip_penalty,
            sense=pyo.minimize
        )
    
    def _define_constraints(self):
        """Define all model constraints."""
        # C1: Visit each customer once or skip
        def constraint_visit_or_skip(m, j):
            return (pyo.summation(self.model.x_ijk, self.model.M_set, 
                                 self.model.K_m, self.model.N, j) + 
                   self.model.s_j[j] == 1)
        
        self.model.c_visit_or_skip = pyo.Constraint(
            self.model.D_set, rule=constraint_visit_or_skip
        )
        
        # C2: Flow conservation at each customer
        def constraint_flow_conservation(m, k, j):
            return (pyo.summation(self.model.x_ijk, self.model.N, j) ==
                   pyo.summation(self.model.x_ijk, j, self.model.N))
        
        self.model.c_flow = pyo.Constraint(
            self.model.M_set, self.model.K_m, self.model.D_set,
            rule=constraint_flow_conservation
        )
        
        # C3: Vehicle capacity constraint
        def constraint_capacity(m, k):
            demand_expr = pyo.summation(
                self.model.q_j * self.model.x_ijk,
                self.model.N, self.model.D_set
            )
            return demand_expr <= self.model.Q + self.model.overload_km[m, k]
        
        self.model.c_capacity = pyo.Constraint(
            self.model.M_set, self.model.K_m,
            rule=constraint_capacity
        )
        
        # C4: Time window constraints
        def constraint_time_window_lower(m, k, j):
            return self.model.t_i[m, k, j] >= self.model.a_j[j]
        
        def constraint_time_window_upper(m, k, j):
            return self.model.t_i[m, k, j] <= self.model.b_j[j] + self.model.late_i[j]
        
        self.model.c_time_lower = pyo.Constraint(
            self.model.M_set, self.model.K_m, self.model.N,
            rule=constraint_time_window_lower
        )
        
        self.model.c_time_upper = pyo.Constraint(
            self.model.M_set, self.model.K_m, self.model.N,
            rule=constraint_time_window_upper
        )
        
        # C5: Time continuity constraint (subtour elimination)
        def constraint_time_continuity(m, k, i, j):
            if i != j:
                return (self.model.t_i[m, k, i] + self.model.t_ij[m, k, i, j] <=
                       self.model.t_i[m, k, j] +
                       self.model.M_big * (1 - self.model.x_ijk[m, k, i, j]))
            return pyo.Constraint.Skip
        
        self.model.c_time_continuity = pyo.Constraint(
            self.model.M_set, self.model.K_m, self.model.N, self.model.N,
            rule=constraint_time_continuity
        )
    
    def get_model(self) -> pyo.ConcreteModel:
        """Return the Pyomo model.
        
        Returns:
            Configured Pyomo ConcreteModel
        """
        return self.model
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get model statistics.
        
        Returns:
            Dictionary with model dimensions and variable counts
        """
        return {
            "n_depots": self.M,
            "n_customers": self.D,
            "n_total_nodes": self.N,
            "n_vehicles_per_depot": self.K_m,
            "vehicle_capacity": self.Q,
            "n_binary_variables": self.M * self.K_m + self.D,  # Approximate
            "n_continuous_variables": self.N + self.D,  # Approximate
        }
