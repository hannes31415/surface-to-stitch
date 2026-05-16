"""
Reproduce a sphere design with N=10 loops and a unit hemisphere profile.
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crochet_gen import generate

def sphere_profile(r: float) -> float:
    """Bottom hemisphere of a unit sphere, translated to start at the origin."""
    return 1.0 - np.sqrt(max(1.0 - r**2, 0.0))

result = generate(
    f=sphere_profile,
    domain=1.0,
    n_loops=10,
    closed=True,
    name="Sphere (N=10)",
    visualize=False,
    save_plot="outputs/sphere",
)

print(result.pattern_text)
print()
print(f"Loop radii:    {[round(r, 3) for r in result.loop_radii]}")
print(f"Stitch counts: {result.stitch_counts}")
