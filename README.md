# surface-to-stitch

**A mathematically rigorous crochet pattern generator for rotationally symmetric 3D surfaces.**

Given any surface *z = f(r)* in cylindrical coordintes with rotational symmetry about the z-axis, this tool produces a complete, step-by-step crochet pattern. Modern geometric crochet designs are made with guesswork, but this method includes precise stitch counts, increase/decrease placement, and angular offsets, all derived entirely from calculus and number theory.

---

## The Problem

Crocheting a 3D shape requires decisions that people usually approximate:

1. **How many stitches per loop?** (how much to expand or contract)
2. **Where in the loop do you place the increases/decreases?** (to optimize the preservation of rotational symmetry)

This tool solves both problems analytically.

---

## The Math (in short)

### Loop positions: arc length parameterization

Crochet loops follow the *surface* of a shape, not a flat grid. So the correct question is: at what radius *R_n* does the *n*-th loop sit, such that the arc length between consecutive loops is constant?

This reduces to solving:

$$\frac{n}{N} \int_0^1 \sqrt{1 + \left(\frac{dz}{dr}\right)^2} \, dr = \int_0^{R_n} \sqrt{1 + \left(\frac{dz}{dr}\right)^2} \, dr$$

For a sphere (*z = 1 - √(1 - r²)*), this simplifies beautifully to a closed form:

$$R_n = \sin\left(\frac{\pi n}{2N}\right)$$

For arbitrary surfaces, the bisection method for integration finds *R_n* numerically.

### Optimal increase/decrease placement: number theory

When transitioning between a loop with *j* special stitches and one with *k*, the increases/decreases should be placed as far as possible from the previous layer's. The optimal angular offset is:

$$\varphi = \frac{\pi}{\text{lcm}(j,\, k)}$$

This follows from a collision argument: in one full revolution, *jk* overlaps occur, but simultaneous ones reduce this to *lcm(j,k)* distinct events. The halfway point between events maximises separation.

---

## Project Structure

```
crochet_gen/
├── geometry.py       # Arc length computation + bisection root-finding
├── stitches.py       # Radius -> integer stitch count conversion
├── symmetry.py       # Angular offset computation (lcm-based)
├── pattern.py        # Writes the human-readable crochet pattern
├── visualization.py  # 3D surface + stitch profile plots
├── generator.py      # High-level API
└── cli.py            # Command-line interface

examples/
├── sphere.py         # sphere, N=10
└── cosine.py         # cos(r) surface, N=15

```

---

## Quickstart

### Install

```bash
git clone https://github.com/your-username/crochet-gen
cd crochet-gen
pip install -r requirements.txt
```

### Python API

```python
from crochet_gen import generate
import numpy as np

result = generate(
    f=lambda r: 1 - np.sqrt(max(1 - r**2, 0)),
    domain=1.0,
    n_loops=10,
    closed=True,        # mirror to close the sphere
    name="Sphere",
    visualize=True,     # show matplotlib plots
)

print(result.pattern_text)
# Loop 1: sc5
# Loop 2: inc, sc1, inc, sc1, inc, sc2, inc, sc1, inc, sc1
# ...
```

### CLI

```bash
# Built-in presets: sphere, paraboloid, cos, cone
python -m crochet_gen.cli sphere --n-loops 10 --closed
python -m crochet_gen.cli cos --domain 9 --n-loops 15 --visualize

# Custom expression (numpy available as np)
python -m crochet_gen.cli "np.sin(r) + 0.3*r" --domain 6 --n-loops 12 --name "Sine Wave"

# Save output
python -m crochet_gen.cli sphere --closed --output sphere_pattern.txt --save-plot outputs/sphere
```

### Custom yarn measurements

By default, the tool uses measurements from a 5.0mm hook with medium-weight yarn (stitch height 0.572 cm, stitch length 0.636 cm). You can override these for your own yarn:

```python
from crochet_gen import generate, YarnProfile

my_yarn = YarnProfile(stitch_height_cm=0.45, stitch_length_cm=0.50)
result = generate(f, domain=1.0, n_loops=12, yarn=my_yarn)
```

Or via CLI:
```bash
python -m crochet_gen.cli sphere --stitch-height 0.45 --stitch-length 0.50
```

---

## Example: Sphere (N=10)

**Stitch counts:** `[5, 11, 16, 21, 25, 29, 32, 34, 35, 36]`

```
Pattern: Sphere (N=10)
======================
Chain On
Loop 1: sc5
Loop 2: inc, sc1, inc, sc1, inc, sc2, inc, sc1, inc, sc1
Loop 3: inc, sc2, inc, sc3, inc, sc2, inc, sc2, inc, sc2
Loop 4: sc2, inc, sc4, inc, sc3, inc, sc3, inc, sc3, inc, sc1
...
Loop 19: sc5
Chain Off
```

The pattern was physically crocheted to verify correctness.

---

## Limitations & Future Work

- **Rotational symmetry required.** The current approach assumes *z = f(r)*, i.e. the surface is independent of *θ*. Generalising to asymmetric surfaces would require a density-function approach to stitch placement: a significantly harder problem involving multivariable calculus that I'm currently working on.

- **Yarn stretch.** The scaling factor is measured from a flat swatch. Yarn stretch under tension could be modelled more precisely.

- **Other stitch types.** Half-double crochet, treble crochet, and bobble stitches all have different height-to-width ratios. Extending the `YarnProfile` to support multiple stitch types would expand the design space considerably.

---

## Citation

If you use this in a project, a nod would be appreciated!

```


---

## License

MIT
