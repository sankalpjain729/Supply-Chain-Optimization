import networkx as nx
import matplotlib.pyplot as plt
import pyomo.environ as pyo
from solver import model


def create_supply_chain_visualization():

    G = nx.DiGraph()

    factories = list(model.F)
    warehouses = list(model.W)
    customers = list(model.C)

    # -------------------------
    # FIXED POSITIONS (NO RANDOMNESS)
    # -------------------------
    pos = {}

    # factories on left
    for i, f in enumerate(factories):
        G.add_node(f)
        pos[f] = (0, -i)

    # warehouses in middle
    for i, w in enumerate(warehouses):
        if pyo.value(model.Y[w]) > 0.5:
            G.add_node(w)
            pos[w] = (1, -i)

    # customers on right
    for i, c in enumerate(customers):
        G.add_node(c)
        pos[c] = (2, -i)

    # -------------------------
    # EDGES: Factory → Warehouse
    # -------------------------
    for f in factories:
        for w in warehouses:
            if pyo.value(model.Y[w]) > 0.5:

                flows = []
                for k in model.P:
                    val = pyo.value(model.F_flow[f, w, k])
                    if val > 0.1:
                        flows.append(f"{val:.0f} {k}")

                if flows:
                    G.add_edge(f, w, label="\n".join(flows))

    # -------------------------
    # EDGES: Warehouse → Customer
    # -------------------------
    for w in warehouses:
        if pyo.value(model.Y[w]) > 0.5:

            for c in customers:
                flows = []
                for k in model.P:
                    val = pyo.value(model.X[w, c, k])
                    if val > 0.1:
                        flows.append(f"{val:.0f} {k}")

                if flows:
                    G.add_edge(w, c, label="\n".join(flows))

    # -------------------------
    # DRAW GRAPH
    # -------------------------
    plt.figure(figsize=(12, 7))

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_size=2000,
        node_color="lightblue",
        arrows=True,
        font_size=10
    )

    edge_labels = nx.get_edge_attributes(G, "label")

    nx.draw_networkx_edge_labels(
        G,
        pos,
        edge_labels=edge_labels,
        font_size=8
    )

    plt.title("Supply Chain Flow (Simple View)")
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    create_supply_chain_visualization()