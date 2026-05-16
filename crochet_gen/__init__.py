"""
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
