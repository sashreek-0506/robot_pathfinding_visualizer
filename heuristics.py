"""Heuristic functions used by informed search (A*).

Kept separate from the algorithm implementation so new heuristics can
be added, swapped, or benchmarked without touching search logic.
"""
import math


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def chebyshev(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
