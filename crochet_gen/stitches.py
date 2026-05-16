"""
Converts geometric loop radii into discrete stitch counts.

Each loop is a circle of radius R_n (scaled to real yarn dimensions).
The circumference gives the loop length, which is then divided by the
stitch length and floored to get an integer stitch count.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .geometry import total_arc_length, compute_loop_radii
from typing import Callable


@dataclass
class YarnProfile:
    """
    Physical measurements of a yarn + hook combination.

    Measure a small swatch to determine these values.

    Attributes
    ----------
    stitch_height_cm : float
        Height of a single crochet stitch in centimetres.
    stitch_length_cm : float
        Width (horizontal length) of a single crochet stitch in centimetres.
    """
    stitch_height_cm: float = 0.572
    stitch_length_cm: float = 0.636

    def scaling_factor(self, total_arc: float, n_loops: int) -> float:
        """
        Ratio between the real project height and the unit arc length.

        The real project has height = stitch_height * n_loops.
        The unit arc length is the arc over the mathematical domain.
        Their ratio scales unit radii to real-world centimetres.

        Parameters
        ----------
        total_arc : float
            Arc length of the profile curve over its domain.
        n_loops : int
            Number of loops in the pattern.

        Returns
        -------
        float
            Scale factor c such that R_real = c * R_unit.
        """
        return (self.stitch_height_cm * n_loops) / total_arc


def radii_to_stitch_counts(
    radii: list[float],
    f: Callable[[float], float],
    domain: float,
    yarn: YarnProfile,
    n_loops: int,
) -> list[int]:
    """
    Convert loop radii to integer stitch counts by computing the scaling factor from unit radius to real centimetres, scaling each radius, computing loop circumference = 2π * R_scaled, and then divide by stitch length and floor.

    Parameters
    ----------
    radii : list[float]
        Radial positions of each loop (unit scale).
    f : callable
        Surface profile function (needed for arc length).
    domain : float
        Radial domain limit.
    yarn : YarnProfile
        Physical yarn measurements.
    n_loops : int
        Total number of loops.

    Returns
    -------
    list[int]
        Integer stitch count for each loop.
    """
    arc = total_arc_length(f, domain)
    c = yarn.scaling_factor(arc, n_loops)

    counts = []
    for r in radii:
        circumference = 2 * math.pi * r * c
        counts.append(int(math.floor(circumference / yarn.stitch_length_cm)))

    return counts
