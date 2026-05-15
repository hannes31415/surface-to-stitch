"""
examples/cosine.py
------------------
Generate a pattern for z = cos(r) over domain [0, 9],
reproducing the second example from the paper (N=15).
"""

import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crochet_gen import generate

result = generate(
    f=np.cos,
    domain=9.0,
    n_loops=15,
    closed=False,
    name="cos(r), N=15",
    visualize=False,
    save_plot="outputs/cosine",
)

print(result.pattern_text)
print()
print(f"Stitch counts: {result.stitch_counts}")
