"""
model.py — Problem Representation for MILP Solver

A MILP has three main parts:
    1. Variables   — decision variables (continuous, integer, or binary)
    2. Objective   — linear function to minimize/maximize
    3. Constraints — linear constraints the solution must satisfy

Standard form:
    Minimize    c^T x
    Subject to: A_ub @ x <= b_ub
                A_eq @ x == b_eq
                lower <= x <= upper
                some x ∈ {0, 1, Z}
"""

import numpy as np


class Variable:
    """
    One decision variable in the model.

    Parameters:
        name     : string label (e.g., "x1", "y")
        var_type : "continuous", "integer", or "binary"
        lower    : lower bound (default 0)
        upper    : upper bound (default None = no upper bound)
    """
    def __init__(self, name, var_type="continuous", lower=0, upper=None):
        self.name = name
        self.var_type = var_type
        self.lower = lower
        self.upper = upper
        self.index = None

        if var_type == "binary":
            self.lower = 0
            self.upper = 1


class Constraint:
    """
    One linear constraint: sum of (coefficient * variable) sense rhs

    Example: 2*x1 + 3*x2 <= 10
        coefficients = {"x1": 2, "x2": 3}
        sense        = "<="
        rhs          = 10

    Parameters:
        coefficients : dict  {variable_name: coefficient_value}
        sense        : "<=" or ">=" or "=="
        rhs          : right-hand side number
        name         : optional label for this constraint
    """
    def __init__(self, coefficients, sense, rhs, name=""):
        self.coefficients = coefficients
        self.sense = sense
        self.rhs = rhs
        self.name = name


class Model:
    """
    Container for a full MILP problem.

    Usage:
        m = Model("my problem")
        m.add_variable("x1", var_type="integer", lower=0, upper=10)
        m.add_variable("x2", var_type="continuous", lower=0)
        m.set_objective({"x1": 3, "x2": 2}, sense="minimize")
        m.add_constraint({"x1": 1, "x2": 1}, "<=", 10, name="capacity")
    """

    def __init__(self, name="MILP"):
        self.name = name
        self.variables = {}
        self.var_order = []
        self.constraints = []
        self.objective = {}
        self.sense = "minimize"

    def add_variable(self, name, var_type="continuous", lower=0, upper=None):
        """
        Add a decision variable to the model.
        
        Returns the Variable object.
        """
        var = Variable(name, var_type, lower, upper)
        var.index = len(self.var_order)
        self.variables[name] = var
        self.var_order.append(name)
        return var

    def set_objective(self, coefficients, sense="minimize"):
        """
        Set the objective function.

        Args:
            coefficients : dict {variable_name: coefficient}
            sense : "minimize" or "maximize"
        """
        self.objective = coefficients
        self.sense = sense

    def add_constraint(self, coefficients, sense, rhs, name=""):
        """
        Add a linear constraint.

        Args:
            coefficients : dict {variable_name: coefficient}
            sense        : "<=", ">=", or "=="
            rhs          : right-hand side value
            name         : optional label
        """
        con = Constraint(coefficients, sense, rhs, name)
        self.constraints.append(con)
        return con

    def to_standard_form(self):
        """
        Convert the model into numpy arrays for scipy.optimize.linprog.

        Returns:
            dict with keys c, A_ub, b_ub, A_eq, b_eq, bounds, int_vars
        """
        n = len(self.var_order)

        # Objective vector c
        c = np.zeros(n)
        for var_name, coeff in self.objective.items():
            idx = self.variables[var_name].index
            c[idx] = coeff

        # scipy only minimizes; for maximize, negate c
        if self.sense == "maximize":
            c = -c

        # Split constraints into <= and ==
        ub_rows = []
        ub_rhs = []
        eq_rows = []
        eq_rhs = []

        for con in self.constraints:
            row = np.zeros(n)
            for var_name, coeff in con.coefficients.items():
                idx = self.variables[var_name].index
                row[idx] = coeff

            if con.sense == "<=":
                ub_rows.append(row)
                ub_rhs.append(con.rhs)
            elif con.sense == ">=":
                # flip: a >= b  becomes  -a <= -b
                ub_rows.append(-row)
                ub_rhs.append(-con.rhs)
            elif con.sense == "==":
                eq_rows.append(row)
                eq_rhs.append(con.rhs)

        A_ub = np.array(ub_rows) if ub_rows else None
        b_ub = np.array(ub_rhs) if ub_rhs else None
        A_eq = np.array(eq_rows) if eq_rows else None
        b_eq = np.array(eq_rhs) if eq_rhs else None

        # Variable bounds
        bounds = []
        for name in self.var_order:
            var = self.variables[name]
            bounds.append((var.lower, var.upper))

        # Integer variable indices
        int_vars = []
        for name in self.var_order:
            var = self.variables[name]
            if var.var_type in ("integer", "binary"):
                int_vars.append(var.index)

        return {
            "c": c,
            "A_ub": A_ub,
            "b_ub": b_ub,
            "A_eq": A_eq,
            "b_eq": b_eq,
            "bounds": bounds,
            "int_vars": int_vars,
        }

    def print_model(self):
        """Print the full model in readable form."""
        print(f"Model: {self.name}")
        print(f"Sense: {self.sense}")
        print()

        # Objective
        terms = []
        for name in self.var_order:
            coeff = self.objective.get(name, 0)
            if coeff == 0:
                continue
            if coeff == 1:
                terms.append(name)
            elif coeff == -1:
                terms.append(f"-{name}")
            else:
                terms.append(f"{coeff}*{name}")
        obj_str = " + ".join(terms).replace("+ -", "- ")
        print(f"Objective: {self.sense}  {obj_str}")
        print()

        # Constraints
        print("Constraints:")
        for i, con in enumerate(self.constraints):
            label = con.name if con.name else f"C{i+1}"
            terms = []
            for name in self.var_order:
                coeff = con.coefficients.get(name, 0)
                if coeff == 0:
                    continue
                if coeff == 1:
                    terms.append(name)
                elif coeff == -1:
                    terms.append(f"-{name}")
                else:
                    terms.append(f"{coeff}*{name}")
            lhs_str = " + ".join(terms).replace("+ -", "- ")
            print(f"  {label}: {lhs_str} {con.sense} {con.rhs}")
        print()

        # Variables
        print("Variables:")
        for name in self.var_order:
            var = self.variables[name]
            bound_str = f"[{var.lower}, {var.upper}]"
            print(f"  {name}: {var.var_type}, bounds={bound_str}")
        print()

        # Summary
        n_int = sum(1 for name in self.var_order
                    if self.variables[name].var_type in ("integer", "binary"))
        n_cont = len(self.var_order) - n_int
        print(f"Total variables: {len(self.var_order)} "
              f"({n_cont} continuous, {n_int} integer/binary)")
        print(f"Total constraints: {len(self.constraints)}")
