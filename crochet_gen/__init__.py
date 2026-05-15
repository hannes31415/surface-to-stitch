"""
crochet_gen
-----------
A mathematically rigorous crochet pattern generator for rotationally
symmetric 3D surfaces.

Given any surface z = f(r) with rotational symmetry about the z-axis,
this package computes a complete crochet pattern that:

  - Places loops at arc-length-equal intervals along the surface profile.
  - Determines the integer stitch count per loop from the loop circumference.
  - Optimally positions increase/decrease stitches to maximise rotational
    symmetry using number-theoretic angular offsets (π / lcm(j, k)).

Quick start
-----------
>>> from crochet_gen import generate
>>> import numpy as np
>>>
>>> result = generate(
...     f=lambda r: 1 - np.sqrt(1 - r**2),
...     domain=1.0,
...     n_loops=10,
...     closed=True,
...     name="Sphere",
... )
>>> print(result.pattern_text)
"""

from .generator import generate, PatternResult
from .stitches import YarnProfile

__all__ = ["generate", "PatternResult", "YarnProfile"]
__version__ = "1.0.0"
