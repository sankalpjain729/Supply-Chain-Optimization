import math
import random
import numpy as np
import time

from utils import SAParams, SAResult, compute_cut_value, compute_delta, calibrate_temperature

"""
Simulated Annealing algorithms for Max-Cut.
"""

# ---------------------------------------------------------------------------
# Simulated Annealing
# ---------------------------------------------------------------------------

def simulated_annealing(n, edges, adj, params=None):
    """
    Single-run Simulated Annealing for Max-Cut.

    Returns: SAResult
    """
    if params is None:
        params = SAParams()

    if params.seed is not None:
        random.seed(params.seed)
        np.random.seed(params.seed)

    x = np.random.randint(0, 2, size=n)
    current_cut = compute_cut_value(x, edges)

    best_cut = current_cut
    best_x = x.copy()

    T = params.T_init
    if T <= 0:
        T = calibrate_temperature(n, adj, edges)

    alpha = params.alpha
    max_iter = params.max_iter

    history = []
    log_interval = max(max_iter // 200, 1)
    print_interval = max(max_iter // 10, 1)
    start = time.time()

    for it in range(max_iter):
        node = random.randint(0, n - 1)
        delta = compute_delta(x, node, adj)

        if delta >= 0:
            accept = True
        else:
            accept = random.random() < math.exp(delta / T)

        if accept:
            x[node] = 1 - x[node]
            current_cut += delta

            if current_cut > best_cut:
                best_cut = current_cut
                best_x = x.copy()

        T *= alpha

        if it % log_interval == 0:
            history.append((it, current_cut, best_cut, T))

        if it % print_interval == 0:
            print(f"    iteration {it}/{max_iter}, best_cut={best_cut}, T={T:.3f}")

    elapsed = time.time() - start
    final_cut = current_cut
    print(f"    done: best_cut={best_cut}, time={elapsed:.2f}s")

    return SAResult(best_x, best_cut, final_cut, elapsed, history)


# ---------------------------------------------------------------------------
# Multi-start wrapper
# ---------------------------------------------------------------------------

def multi_start_sa(n, edges, adj, n_starts=5, params=None):
    """Run SA multiple times and return the best result."""
    if params is None:
        params = SAParams()

    overall_best = None

    for run in range(n_starts):
        run_params = SAParams(
            T_init=params.T_init,
            alpha=params.alpha,
            max_iter=params.max_iter,
            seed=(params.seed + run) if params.seed is not None else None,
        )
        print(f"\n  Run {run+1}/{n_starts}:")
        result = simulated_annealing(n, edges, adj, run_params)

        if overall_best is None or result.best_cut > overall_best.best_cut:
            overall_best = result

    print(f"\n  Best across {n_starts} starts: {overall_best.best_cut}")

    return overall_best