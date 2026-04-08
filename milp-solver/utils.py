"""
utils.py — Utility Functions

Distance metrics, solution validation helpers, and general utilities.
"""

import math
import numpy as np


def tsplib_geo_distance(a, b):
    """
    TSPLIB Geographic distance calculation.
    
    Latitude/longitude coordinates with TSPLIB formula.
    """
    def to_radians(x):
        deg = int(x)
        minutes = x - deg
        return math.pi * (deg + 5.0 * minutes / 3.0) / 180.0

    lat1 = to_radians(a[0])
    lon1 = to_radians(a[1])
    lat2 = to_radians(b[0])
    lon2 = to_radians(b[1])

    q1 = math.cos(lon1 - lon2)
    q2 = math.cos(lat1 - lat2)
    q3 = math.cos(lat1 + lat2)

    arg = 0.5 * ((1.0 + q2) * q1 - (1.0 - q2) * q3)
    arg = max(-1.0, min(1.0, arg))

    return int(6378.388 * math.acos(arg) + 1.0)


def euclidean_rounded_distance_matrix(coords):
    """Compute Euclidean distance matrix with rounding."""
    coords = np.asarray(coords, dtype=float)
    n = len(coords)
    dist = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            if i != j:
                d = np.linalg.norm(coords[i] - coords[j])
                dist[i, j] = int(round(d))
    return dist


def geo_distance_matrix(coords):
    """Compute geographic distance matrix."""
    n = len(coords)
    dist = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            if i != j:
                dist[i, j] = tsplib_geo_distance(coords[i], coords[j])
    return dist


def compute_distance_matrix(coords, metric="euclidean"):
    """
    Compute distance matrix using specified metric.
    
    Args:
        coords : array of coordinates
        metric : "euclidean" or "geo"
    
    Returns:
        n x n distance matrix
    """
    if metric == "geo":
        return geo_distance_matrix(coords)
    return euclidean_rounded_distance_matrix(coords)


def compute_gap_pct(sense, your_obj, baseline_obj):
    """
    Compute optimality gap as percentage.
    
    For minimization: gap = (yours - baseline) / baseline * 100
    For maximization: gap = (baseline - yours) / baseline * 100
    """
    if your_obj is None or baseline_obj is None:
        return None
    if abs(baseline_obj) < 1e-12:
        return None

    if sense == "maximize":
        return ((baseline_obj - your_obj) / abs(baseline_obj)) * 100.0
    return ((your_obj - baseline_obj) / abs(baseline_obj)) * 100.0
