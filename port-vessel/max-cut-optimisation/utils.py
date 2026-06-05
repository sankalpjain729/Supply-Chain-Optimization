import os
import math
import random
import numpy as np

"""
GSET dataset parser and utilities.

Reads GSET graph files and provides SA classes and evaluation functions.
"""

# ---------------------------------------------------------------------------
# Parser functions
# ---------------------------------------------------------------------------

def parse_gset_from_file(filepath):
    """
    Read a GSET file and return n and edges.

    Returns:
        n     = number of vertices
        edges = list of (i, j, weight) tuples (0-indexed)
    """
    edges = []
    n = 0

    with open(filepath, "r") as f:
        first_line = f.readline().split()
        n = int(first_line[0])

        for line in f:
            parts = line.split()
            if len(parts) < 3:
                continue
            i = int(parts[0]) - 1
            j = int(parts[1]) - 1
            w = int(parts[2])
            edges.append((i, j, w))

    return n, edges


def build_adjacency(n, edges):
    """Build adjacency list: adj[i] = [(neighbor, weight), ...]"""
    adj = [[] for _ in range(n)]
    for i, j, w in edges:
        adj[i].append((j, w))
        adj[j].append((i, w))
    return adj


def load_graph(filepath):
    """Parse a GSET file and build adjacency list."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None, None, None
    n, edges = parse_gset_from_file(filepath)
    if n is None:
        return None, None, None
    adj = build_adjacency(n, edges)
    return n, edges, adj


# ---------------------------------------------------------------------------
# SA Classes
# ---------------------------------------------------------------------------

class SAParams:
    def __init__(self, T_init=0.0, alpha=0.999995, max_iter=2_000_000, seed=None):
        self.T_init = T_init
        self.alpha = alpha
        self.max_iter = max_iter
        self.seed = seed


class SAResult:
    def __init__(self, best_x, best_cut, final_cut, elapsed, history):
        self.best_x = best_x
        self.best_cut = best_cut
        self.final_cut = final_cut
        self.elapsed = elapsed
        self.history = history


# ---------------------------------------------------------------------------
# Core evaluation functions
# ---------------------------------------------------------------------------

def compute_cut_value(x, edges):
    """Full O(|E|) evaluation of cut value."""
    total = 0
    for i, j, w in edges:
        if x[i] != x[j]:
            total += w
    return total


def compute_delta(x, node, adj):
    """
    Compute change in cut value if we flip node.

    Same group neighbor    → delta += w  (flipping will separate = GAIN)
    Different group neighbor → delta -= w  (flipping will join = LOSE)
    """
    delta = 0
    for neighbor, w in adj[node]:
        if x[node] == x[neighbor]:
            delta += w
        else:
            delta -= w
    return delta


# ---------------------------------------------------------------------------
# Temperature calibration
# ---------------------------------------------------------------------------

def calibrate_temperature(n, adj, edges, target_accept=0.8, n_samples=2000):
    """
    Do 2000 test flips, measure how bad typical bad moves are,
    then pick T so that 80% of bad moves would be accepted.
    """
    x = np.random.randint(0, 2, size=n)
    bad_deltas = []

    for _ in range(n_samples):
        node = random.randint(0, n - 1)
        delta = compute_delta(x, node, adj)
        if delta < 0:
            bad_deltas.append(-delta)
        x[node] = 1 - x[node]

    if not bad_deltas:
        return 1.0

    avg_bad = np.mean(bad_deltas)
    T = -avg_bad / math.log(target_accept)
    return max(T, 0.01)