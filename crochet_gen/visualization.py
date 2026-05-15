"""
visualization.py
----------------
Produces visual outputs for the crochet pattern generator:

  1. A 3D surface plot of the profile function z = f(r), revolved
     around the z-axis, with loop positions marked.
  2. A top-down 2D loop diagram showing stitch counts and special
     stitch positions per loop.

Uses only matplotlib (no extra dependencies).
"""

from __future__ import annotations

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from typing import Callable, Optional


def _revolve_surface(
    f: Callable[[float], float],
    domain: float,
    n_r: int = 60,
    n_theta: int = 80,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return X, Y, Z arrays for the revolved surface z = f(r)."""
    r_vals = np.linspace(0, domain, n_r)
    theta_vals = np.linspace(0, 2 * math.pi, n_theta)
    R, Theta = np.meshgrid(r_vals, theta_vals)
    X = R * np.cos(Theta)
    Y = R * np.sin(Theta)
    Z = np.vectorize(f)(R)
    return X, Y, Z


def plot_surface_with_loops(
    f: Callable[[float], float],
    domain: float,
    loop_radii: list[float],
    stitch_counts: list[int],
    title: str = "Crochet Surface",
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Plot the 3D surface with horizontal loop rings and stitch count labels.

    Parameters
    ----------
    f : callable
        Surface profile function z = f(r).
    domain : float
        Radial domain limit.
    loop_radii : list[float]
        Radius of each loop (unit scale).
    stitch_counts : list[int]
        Number of stitches per loop.
    title : str
        Plot title.
    save_path : str, optional
        If given, save the figure to this path.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig = plt.figure(figsize=(14, 6), facecolor="#0f0f0f")
    gs = GridSpec(1, 2, figure=fig, wspace=0.05)

    # --- 3D surface ---
    ax3d = fig.add_subplot(gs[0], projection="3d")
    ax3d.set_facecolor("#0f0f0f")

    X, Y, Z = _revolve_surface(f, domain)
    ax3d.plot_surface(
        X, Y, Z,
        alpha=0.25,
        color="#7ec8e3",
        linewidth=0,
        antialiased=True,
    )

    # Draw loop rings
    theta = np.linspace(0, 2 * math.pi, 200)
    cmap = plt.cm.plasma
    n = len(loop_radii)
    for i, (r, sc) in enumerate(zip(loop_radii, stitch_counts)):
        z_val = f(r)
        color = cmap(i / max(n - 1, 1))
        ax3d.plot(
            r * np.cos(theta),
            r * np.sin(theta),
            z_val,
            color=color,
            linewidth=1.8,
            alpha=0.9,
        )

    ax3d.set_xlabel("x", color="#888", labelpad=4)
    ax3d.set_ylabel("y", color="#888", labelpad=4)
    ax3d.set_zlabel("z", color="#888", labelpad=4)
    ax3d.tick_params(colors="#555")
    ax3d.xaxis.pane.fill = False
    ax3d.yaxis.pane.fill = False
    ax3d.zaxis.pane.fill = False
    for pane in [ax3d.xaxis.pane, ax3d.yaxis.pane, ax3d.zaxis.pane]:
        pane.set_edgecolor("#222")
    ax3d.set_title(title, color="white", fontsize=13, pad=12, fontfamily="monospace")

    # --- 2D loop diagram (top-down, r vs stitch count) ---
    ax2d = fig.add_subplot(gs[1])
    ax2d.set_facecolor("#0f0f0f")

    for i, (r, sc) in enumerate(zip(loop_radii, stitch_counts)):
        color = cmap(i / max(n - 1, 1))
        circle = plt.Circle((0, 0), r, color=color, fill=False, linewidth=1.5, alpha=0.8)
        ax2d.add_patch(circle)
        # Label stitch count at the rightmost point
        ax2d.text(
            r + domain * 0.02, 0,
            str(sc),
            color=color,
            fontsize=7,
            va="center",
            fontfamily="monospace",
        )

    ax2d.set_xlim(-domain * 1.25, domain * 1.5)
    ax2d.set_ylim(-domain * 1.25, domain * 1.25)
    ax2d.set_aspect("equal")
    ax2d.set_title("Loop Radii (top view) + Stitch Counts",
                   color="white", fontsize=11, pad=12, fontfamily="monospace")
    ax2d.tick_params(colors="#555")
    for spine in ax2d.spines.values():
        spine.set_edgecolor("#333")

    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=1, vmax=n))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax2d, shrink=0.6, pad=0.02)
    cbar.set_label("Loop number", color="#aaa", fontsize=9)
    cbar.ax.yaxis.set_tick_params(color="#555")
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color="#aaa")

    fig.subplots_adjust(left=0.05, right=0.92, top=0.92, bottom=0.05)

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="#0f0f0f")

    return fig


def plot_stitch_profile(
    stitch_counts: list[int],
    title: str = "Stitch Count Per Loop",
    save_path: Optional[str] = None,
) -> plt.Figure:
    """
    Bar chart of stitch counts per loop.

    Useful for a quick sanity check: the profile should match the
    shape of the surface cross-section.

    Parameters
    ----------
    stitch_counts : list[int]
        Stitch count per loop.
    title : str
        Plot title.
    save_path : str, optional
        Save path.

    Returns
    -------
    matplotlib.figure.Figure
    """
    fig, ax = plt.subplots(figsize=(9, 4), facecolor="#0f0f0f")
    ax.set_facecolor("#0f0f0f")

    n = len(stitch_counts)
    colors = plt.cm.plasma(np.linspace(0, 1, n))
    ax.bar(range(1, n + 1), stitch_counts, color=colors, width=0.75, alpha=0.9)
    ax.set_xlabel("Loop number", color="#aaa", fontsize=10)
    ax.set_ylabel("Stitch count", color="#aaa", fontsize=10)
    ax.set_title(title, color="white", fontsize=12, fontfamily="monospace")
    ax.tick_params(colors="#666")
    for spine in ax.spines.values():
        spine.set_edgecolor("#333")

    # Annotate bars
    for i, v in enumerate(stitch_counts):
        ax.text(i + 1, v + 0.3, str(v), ha="center", va="bottom",
                color="#ccc", fontsize=8, fontfamily="monospace")

    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight", facecolor="#0f0f0f")

    return fig
