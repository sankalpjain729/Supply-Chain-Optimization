"""
08_VISUALIZATION.PY
====================
Creates a network graph visualization of the optimized supply chain.

Visualization Features:
- Three-layer network: Factories → Warehouses → Customers
- Shows only active warehouses
- Edge labels display product quantities flowing through each route
- Uses multipartite layout for clear layer separation
"""

import networkx as nx
import matplotlib.pyplot as plt
import pyomo.environ as pyo
from solver import model

# =====================================================================
# NETWORK GRAPH VISUALIZATION
# =====================================================================

def create_supply_chain_visualization():
    """Create and display the supply chain network graph"""
    
    # 1. Initialize the directed graph
    G = nx.DiGraph()

    # 2. Add Nodes with layout layers (0: Left, 1: Middle, 2: Right)
    for i in model.F:
        G.add_node(i, layer=0)

    for j in model.W:
        if pyo.value(model.Y[j]) > 0.5: # Only add OPEN warehouses
            G.add_node(j, layer=1)

    for c in model.C:
        G.add_node(c, layer=2)

    # 3. Add Edges (Factory -> Warehouse)
    for i in model.F:
        for j in model.W:
            if pyo.value(model.Y[j]) > 0.5:
                # Group all products flowing on this route into one label
                flows = []
                for k in model.P:
                    val = pyo.value(model.F_flow[i,j,k])
                    if val > 0.1:
                        flows.append(f"{val:.0f} {k}")

                if flows: # If there is any flow, create the edge
                    G.add_edge(i, j, label="\n".join(flows))

    # 4. Add Edges (Warehouse -> Customer)
    for j in model.W:
        if pyo.value(model.Y[j]) > 0.5:
            for c in model.C:
                flows = []
                for k in model.P:
                    val = pyo.value(model.X[j,c,k])
                    if val > 0.1:
                        flows.append(f"{val:.0f} {k}")

                if flows:
                    G.add_edge(j, c, label="\n".join(flows))

    # 5. Plotting the Graph
    plt.figure(figsize=(16, 10))

    # Use multipartite layout to separate the 3 layers automatically
    pos = nx.multipartite_layout(G, subset_key="layer")

    # Draw Nodes
    nx.draw_networkx_nodes(G, pos, node_size=2500, node_color='#89CFF0', edgecolors='black')

    # Draw Node Labels (F1, W1, C1, etc.)
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')

    # Draw Edges (Arrows)
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20, width=1.5)

    # Draw Edge Labels (Quantities and Products)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9,
                                 bbox=dict(alpha=0.8, color='white', edgecolor='none'))

    # Final touches
    plt.title("Optimized Supply Chain Flow\n(Factories → Active Warehouses → Customers)", 
              fontsize=16, fontweight='bold')
    plt.axis("off")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GENERATING SUPPLY CHAIN VISUALIZATION...")
    print("=" * 60)
    create_supply_chain_visualization()
    print("Visualization complete!")
