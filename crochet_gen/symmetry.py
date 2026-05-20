"""
Compute angular offsets for increase/decrease stitches.

Special stitches should be evenly spaced within a loop and offset from
those in the previous loop to avoid alignment.

For loops with j and k special stitches, the optimal offset is
φ = π / lcm(j, k)
derived from the spacing between distinct stitch-alignment events.
"""

from __future__ import annotations

import math
import numpy as np


def special_stitch_counts(stitch_counts: list[int]) -> list[tuple[int, int]]:
    """
    For each loop, compute (j, k): the number of special stitches in the
    previous loop (j) and the current loop (k).

    j is the absolute change from loop n-2 to loop n-1.
    k is the absolute change from loop n-1 to loop n.

    Parameters
    ----------
    stitch_counts : list[int]
        Integer stitch count per loop.

    Returns
    -------
    list[tuple[int, int]]
        (j, k) pairs for each loop.
    """
    n = len(stitch_counts)
    jk = [(0, 0)]
    jk.append((0, stitch_counts[0]))

    for i in range(n - 2):
        j = abs(stitch_counts[i] - stitch_counts[i + 1])
        k = abs(stitch_counts[i + 1] - stitch_counts[i + 2])
        jk.append((j, k))

    return jk


def optimal_offset(j: int, k: int) -> float:
    """
    Compute the optimal angular offset φ = π / lcm(j, k).

    Returns 0 if either j or k is zero (no special stitches, no offset needed).

    Parameters
    ----------
    j : int
        Special stitch count in the previous loop.
    k : int
        Special stitch count in the current loop.

    Returns
    -------
    float
        Optimal offset in radians.
    """
    if j == 0 or k == 0:
        return 0.0
    return math.pi / math.lcm(j, k)


def compute_offsets(
    stitch_counts: list[int],
) -> tuple[list[float], list[float], list[float]]:
    """
    Compute raw, cumulative, and reduced angular offsets for all loops.

    The cumulative offset accumulates across loops so that each new loop's
    special stitches start as far as possible from the previous layer's.
    The reduced offset maps the cumulative value into [0, β) using modular
    arithmetic, giving the minimum starting offset within one period.

    Parameters
    ----------
    stitch_counts : list[int]
        Integer stitch count per loop.

    Returns
    -------
    tuple of three lists
        (phi_raw, phi_cumulative, phi_reduced), each of length n_loops.
    """
    jk = special_stitch_counts(stitch_counts)
    n = len(stitch_counts)

    beta = []
    for i in range(n):
        k = jk[i][1]
        beta.append((2 * math.pi / k) if k != 0 else 0.0)

    phi_raw = [optimal_offset(j, k) for j, k in jk]

    # cumulative offsets
    phi_cumulative = []
    running = 0.0
    for phi in phi_raw:
        running += phi
        phi_cumulative.append(running)

    # reduced: map into [0, β) so the first special stitch is as early as possible
    phi_reduced = []
    for i in range(n):
        if beta[i] != 0:
            phi_reduced.append(phi_cumulative[i] % beta[i])
        else:
            phi_reduced.append(0.0)

    return phi_raw, phi_cumulative, phi_reduced


def special_stitch_positions(
    stitch_counts: list[int],
) -> list[list[int]]:
    """
    Map angular offsets to discrete stitch-index positions within each loop.

    Starting from φ_reduced, we step in increments of β around the loop,
    then convert each angle to a stitch index by:
        index = round(angle / 2π * total_stitches)

    Parameters
    ----------
    stitch_counts : list[int]
        Integer stitch count per loop.

    Returns
    -------
    list[list[int]]
        For each loop, a sorted list of stitch indices where
        the increase/decrease stitch occurs.
    """
    jk = special_stitch_counts(stitch_counts)
    _, _, phi_reduced = compute_offsets(stitch_counts)
    n = len(stitch_counts)

    beta = []
    for i in range(n):
        k = jk[i][1]
        beta.append((2 * math.pi / k) if k != 0 else 0.0)

    positions = []
    for i in range(n):
        if beta[i] == 0 or jk[i][1] == 0:
            positions.append([])
            continue

        angles = []
        angle = phi_reduced[i]
        while angle <= 2 * math.pi + 1e-9:
            angles.append(angle)
            angle += beta[i]

        # convert angles to stitch indices
        total = stitch_counts[i]
        indices = sorted(set(
            round(a / (2 * math.pi) * total) % total
            for a in angles
        ))
        positions.append(indices)

    return positions
