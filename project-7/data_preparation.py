"""Data Preparation Module for MDVRPTW.

Handles raw data loading, distance/duration matrix generation, and dataset configuration.
Provides the DataPreparation class to prepare data for model building.
"""

import math
from typing import Dict, List, Tuple, Any
import random


class DataPreparation:
    """Prepare raw data for MDVRPTW solver.
    
    Attributes:
        n_mothers (int): Number of mother centers (depots)
        n_daughters (int): Number of daughter centers (customers)
        n_vehicles_per_depot (int): Vehicles available at each depot
        vehicle_capacity (int): Capacity of each vehicle
        distance_matrix (Dict): Precomputed distance matrix
        duration_matrix (Dict): Precomputed travel duration matrix
    """
    
    def __init__(self, n_mothers: int = 11, n_daughters: int = 191,
                 n_vehicles: int = 10, vehicle_capacity: int = None):
        """Initialize data preparation with problem dimensions.
        
        Args:
            n_mothers: Number of depots (M)
            n_daughters: Number of customers (D)
            n_vehicles: Vehicles per depot (K_m)
            vehicle_capacity: Capacity per vehicle (Q)
        """
        self.n_mothers = n_mothers
        self.n_daughters = n_daughters
        self.n_vehicles_per_depot = n_vehicles
        self.vehicle_capacity = vehicle_capacity or 100
        
        self.distance_matrix = {}
        self.duration_matrix = {}
        self.customer_data = []
        self.depot_data = []
        
    def generate_synthetic_data(self, seed: int = 42) -> Dict[str, Any]:
        """Generate synthetic dataset for MDVRPTW.
        
        Args:
            seed: Random seed for reproducibility
            
        Returns:
            Dictionary containing depots, customers, and all parameters
        """
        random.seed(seed)
        
        # Generate depot locations
        self.depot_data = self._generate_depots()
        
        # Generate customer locations and demands
        self.customer_data = self._generate_customers()
        
        # Generate distance and duration matrices
        self._compute_matrices()
        
        # Generate time window constraints
        time_windows = self._generate_time_windows()
        
        return {
            "depots": self.depot_data,
            "customers": self.customer_data,
            "time_windows": time_windows,
            "distance_matrix": self.distance_matrix,
            "duration_matrix": self.duration_matrix,
            "parameters": {
                "n_mothers": self.n_mothers,
                "n_daughters": self.n_daughters,
                "n_vehicles": self.n_vehicles_per_depot,
                "vehicle_capacity": self.vehicle_capacity,
                "time_start": 360,  # 6:00 AM in minutes
                "time_deadline": 600,  # 10:00 AM in minutes
            }
        }
    
    def _generate_depots(self) -> List[Dict[str, Any]]:
        """Generate synthetic depot (mother center) locations.
        
        Returns:
            List of depot information dictionaries
        """
        depots = []
        for i in range(self.n_mothers):
            # Distribute depots across a 100x100 grid
            x = (i % 3) * 30 + random.randint(-5, 5)
            y = (i // 3) * 30 + random.randint(-5, 5)
            depots.append({
                "id": i,
                "x": x,
                "y": y,
                "location_id": f"M{i}",  # Mother center ID
            })
        return depots
    
    def _generate_customers(self) -> List[Dict[str, Any]]:
        """Generate synthetic customer (daughter center) data.
        
        Returns:
            List of customer information dictionaries
        """
        customers = []
        for i in range(self.n_daughters):
            x = random.uniform(0, 100)
            y = random.uniform(0, 100)
            demand = random.randint(1, 50)  # q_j: Customer demand
            service_time = random.randint(5, 20)  # t_ij: Service time (minutes)
            
            customers.append({
                "id": i,
                "x": x,
                "y": y,
                "demand": demand,
                "service_time": service_time,
                "location_id": f"D{i}",  # Daughter center ID
            })
        return customers
    
    def _compute_matrices(self):
        """Compute Euclidean distance and duration matrices.
        
        Populates:
            - distance_matrix: Dict[(i,j)] = Euclidean distance
            - duration_matrix: Dict[(i,j)] = Travel time in minutes
        """
        # All nodes: depots (0 to n_mothers-1) + customers (n_mothers to n_mothers+n_daughters-1)
        all_nodes = self.depot_data + self.customer_data
        n_nodes = len(all_nodes)
        
        for i in range(n_nodes):
            for j in range(n_nodes):
                if i != j:
                    x1, y1 = all_nodes[i]["x"], all_nodes[i]["y"]
                    x2, y2 = all_nodes[j]["x"], all_nodes[j]["y"]
                    
                    # Euclidean distance
                    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                    self.distance_matrix[(i, j)] = dist
                    
                    # Travel time: distance / speed (assuming speed = 1 km/min for simplicity)
                    # Add service time if destination is a customer
                    duration = dist
                    if j >= self.n_mothers:  # j is a customer
                        duration += all_nodes[j]["service_time"]
                    
                    self.duration_matrix[(i, j)] = duration
                else:
                    self.distance_matrix[(i, i)] = 0
                    self.duration_matrix[(i, i)] = 0
    
    def _generate_time_windows(self) -> Dict[int, Tuple[int, int]]:
        """Generate time window constraints for each customer.
        
        Returns:
            Dictionary mapping customer indices to (earliest, latest) arrival times
        """
        time_windows = {}
        time_start = 360  # 6:00 AM
        time_deadline = 600  # 10:00 AM
        
        for customer in self.customer_data:
            idx = customer["id"] + self.n_mothers  # Adjust for depot offset
            # Random time window within the working hours
            earliest = random.randint(time_start, time_deadline - 30)
            latest = earliest + random.randint(30, 120)  # 30-120 minute window
            time_windows[idx] = (earliest, min(latest, time_deadline))
        
        return time_windows
    
    def load_real_data(self, data_path: str) -> Dict[str, Any]:
        """Load real MDVRPTW data from file (placeholder for future implementation).
        
        Args:
            data_path: Path to data file
            
        Returns:
            Dictionary with loaded data
            
        Raises:
            NotImplementedError: Currently uses synthetic data only
        """
        raise NotImplementedError("Real data loading to be implemented")
    
    def get_node_count(self) -> Tuple[int, int]:
        """Get total node count.
        
        Returns:
            Tuple of (n_depots, n_customers)
        """
        return self.n_mothers, self.n_daughters
    
    def get_matrix_stats(self) -> Dict[str, float]:
        """Get statistics about distance and duration matrices.
        
        Returns:
            Dictionary with min, max, mean values
        """
        distances = list(self.distance_matrix.values())
        durations = list(self.duration_matrix.values())
        
        return {
            "distance_min": min(distances) if distances else 0,
            "distance_max": max(distances) if distances else 0,
            "distance_mean": sum(distances) / len(distances) if distances else 0,
            "duration_min": min(durations) if durations else 0,
            "duration_max": max(durations) if durations else 0,
            "duration_mean": sum(durations) / len(durations) if durations else 0,
        }
