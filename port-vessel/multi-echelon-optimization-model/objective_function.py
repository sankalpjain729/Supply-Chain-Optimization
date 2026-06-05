import pyomo.environ as pyo
from model_initialization import model
from data_definition import data_package

P1 = data_package['P1']
P2 = data_package['P2']

def objective_rule(m):

    # =========================
    # MAIN COST COMPONENT
    # =========================
    cost = (
        sum(m.OC_w[j] * m.Y[j] for j in m.W)

        + sum(
            m.SC[i, j, k] * m.F_flow[i, j, k]
            for i in m.F for j in m.W for k in m.P
        )

        + sum(
            m.TC[j, c, k] * m.X[j, c, k]
            for j in m.W for c in m.C for k in m.P
        )

        + sum(
            m.RC[i, k] * m.R[i, k]
            for i in m.F for k in m.P
        )

        + sum(
            m.OC_p[i, k] * m.O[i, k]
            for i in m.F for k in m.P
        )

        + P1 * m.s_demand
        + P2 * sum(m.s_cap[j] for j in m.W)
    )

    # =========================
    # TIE-BREAK TERMS (STRUCTURAL STABILITY)
    # =========================

    warehouse_penalty = sum(
    j_index * m.Y[j]
    for j_index, j in enumerate(m.W)
    )

    flow_penalty = sum(
        m.F_flow[i, j, k]
        for i in m.F for j in m.W for k in m.P
    )

    # =========================
    # FINAL OBJECTIVE
    # =========================
    epsilon1 = 1e-3   # warehouse preference
    epsilon2 = 1e-4   # flow simplification

    return cost + epsilon1 * warehouse_penalty + epsilon2 * flow_penalty


model.Obj = pyo.Objective(rule=objective_rule, sense=pyo.minimize)