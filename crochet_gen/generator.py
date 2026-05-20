"""
High-level API for the crochet pattern generator.

Import and call `generate` with a surface function and a few parameters to get back a complete pattern + visualizations.

"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from .geometry import compute_loop_radii, total_arc_length
from .stitches import YarnProfile, radii_to_stitch_counts
from .symmetry import special_stitch_positions
from .pattern import generate_pattern, pattern_to_string
from .visualization import plot_surface_with_loops, plot_stitch_profile


@dataclass
class PatternResult:
    loop_radii: list[float]
    stitch_counts: list[int]
    special_positions: list[list[int]]
    pattern_lines: list[str]
    pattern_text: str


def generate(
    f: Callable[[float], float],
    domain: float,
    n_loops: int,
    closed: bool = False,
    name: Optional[str] = None,
    yarn: Optional[YarnProfile] = None,
    visualize: bool = False,
    save_plot: Optional[str] = None,
) -> PatternResult:
    """
    Parameters
    ----------
    f : callable
        Surface profile function z = f(r). Must be defined on [0, domain].
    domain : float
        Radial domain limit (e.g. 1.0 for a unit hemisphere).
    n_loops : int
        Number of crochet loops (more loops = larger, more detailed project).
    closed : bool
        If True, mirror the first half to create a closed shape (e.g. a sphere).
    name : str, optional
        Pattern name, shown in the header.
    yarn : YarnProfile, optional
        Physical yarn measurements. Defaults to a standard medium-weight yarn
        with a 5mm hook (stitch height 0.572cm, stitch length 0.636cm).
    visualize : bool
        If True, display matplotlib plots of the surface and stitch profile.
    save_plot : str, optional
        Path prefix for saving plots (e.g. "outputs/sphere" saves
        "outputs/sphere_surface.png" and "outputs/sphere_profile.png").

    Returns
    -------
    PatternResult
        All computed data and the written pattern.

    Raises
    ------
    ValueError
        If the domain/n_loops combination is geometrically infeasible.
    """
    if yarn is None:
        yarn = YarnProfile()

    radii = compute_loop_radii(f, n_loops, domain)
    counts = radii_to_stitch_counts(radii, f, domain, yarn, n_loops)
    positions = special_stitch_positions(counts)
    pattern_lines = generate_pattern(counts, positions, closed=closed, name=name)
    pattern_text = pattern_to_string(pattern_lines)

    if visualize or save_plot:
        surface_path = f"{save_plot}_surface.png" if save_plot else None
        profile_path = f"{save_plot}_profile.png" if save_plot else None

        plot_surface_with_loops(
            f, domain, radii, counts,
            title=name or "Crochet Surface",
            save_path=surface_path,
        )
        plot_stitch_profile(
            counts,
            title=f"Stitch Profile — {name or 'Pattern'}",
            save_path=profile_path,
        )

        if visualize:
            import matplotlib.pyplot as plt
            plt.show()

    return PatternResult(
        loop_radii=radii,
        stitch_counts=counts,
        special_positions=positions,
        pattern_lines=pattern_lines,
        pattern_text=pattern_text,
    )
