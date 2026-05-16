"""
Core geometric computations for the crochet pattern generator.

Given a rotationally symmetric 3D surface z = f(r), this module computes
the arc-length-parameterized loop radii that ensure each crochet loop is
equally spaced along the surface profile curve.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import quad
from typing import Callable


def arc_length_integrand(r: float, f: Callable[[float], float], dr: float = 1e-6) -> float:
    """
    Integrand for the arc length formula: sqrt(1 + (dz/dr)^2).

    Uses central finite differences to approximate dz/dr, making this
    compatible with any callable f, not just analytically differentiable ones.

    Parameters
    ----------
    r : float
        Radial coordinate.
    f : callable
        Surface profile function z = f(r).
    dr : float
        Step size for numerical differentiation.

    Returns
    -------
    float
        Value of the arc length integrand at r.
    """
    dz_dr = (f(r + dr) - f(r - dr)) / (2 * dr)
    return np.sqrt(1.0 + dz_dr**2)


def total_arc_length(f: Callable[[float], float], domain: float, tol: float = 1e-8) -> float:
    """
    Compute the total arc length of z = f(r) from r=0 to r=domain.

    Parameters
    ----------
    f : callable
        Surface profile function.
    domain : float
        Upper limit of the radial domain.
    tol : float
        Absolute and relative tolerance for numerical integration.

    Returns
    -------
    float
        Total arc length of the profile curve.
    """
    length, _ = quad(
        arc_length_integrand, 0, domain,
        args=(f,), epsabs=tol, epsrel=tol
    )
    return length


def cumulative_arc_length(r: float, f: Callable[[float], float], tol: float = 1e-8) -> float:
    """
    Arc length from r=0 to r=r along z = f(r).

    Parameters
    ----------
    r : float
        Upper radial bound.
    f : callable
        Surface profile function.
    tol : float
        Numerical integration tolerance.

    Returns
    -------
    float
        Arc length from 0 to r.
    """
    length, _ = quad(
        arc_length_integrand, 0, r,
        args=(f,), epsabs=tol, epsrel=tol
    )
    return length


def find_loop_radius(
    target_arc: float,
    f: Callable[[float], float],
    domain: float,
    tol: float = 1e-6,
    max_iter: int = 100,
) -> float:
    """
    Find the radius R_n such that the arc length from 0 to R_n equals target_arc.

    Uses the bisection method: since arc length is monotonically increasing,
    we can binary-search for the radius that hits a given arc length target.

    Parameters
    ----------
    target_arc : float
        Desired cumulative arc length.
    f : callable
        Surface profile function.
    domain : float
        Maximum radial value (upper bound for bisection).
    tol : float
        Convergence tolerance on the radius.
    max_iter : int
        Maximum bisection iterations.

    Returns
    -------
    float
        Radius R_n at which cumulative arc length equals target_arc.

    Raises
    ------
    ValueError
        If target_arc lies outside the arc length range of [0, domain].
    """
    a, b = 0.0, domain

    if cumulative_arc_length(b, f) < target_arc:
        raise ValueError(
            f"target_arc={target_arc:.4f} exceeds total arc length over [0, {domain}]. "
            "Try increasing the domain or reducing N."
        )

    for _ in range(max_iter):
        if (b - a) / 2 < tol:
            break
        mid = (a + b) / 2.0
        if cumulative_arc_length(mid, f) < target_arc:
            a = mid
        else:
            b = mid

    return (a + b) / 2.0


def compute_loop_radii(
    f: Callable[[float], float],
    n_loops: int,
    domain: float,
) -> list[float]:
    """
    Compute the radial position of each crochet loop.

    Divides the total arc length into n_loops equal segments and finds the
    radius corresponding to each arc length milestone.

    Parameters
    ----------
    f : callable
        Surface profile function z = f(r).
    n_loops : int
        Number of crochet loops.
    domain : float
        Radial domain limit.

    Returns
    -------
    list[float]
        List of n_loops radii, one per loop.
    """
    arc = total_arc_length(f, domain)
    radii = []
    for n in range(1, n_loops + 1):
        target = (n / n_loops) * arc
        r_n = find_loop_radius(target, f, domain)
        radii.append(r_n)
    return radii
