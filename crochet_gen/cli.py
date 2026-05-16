"""
cli.py
------
Command-line interface for the crochet pattern generator.

Usage
-----
    python -m crochet_gen.cli --help
    python -m crochet_gen.cli sphere --n-loops 10 --closed
    python -m crochet_gen.cli cos --domain 9 --n-loops 15
    python -m crochet_gen.cli custom "np.sin(r) + r*0.1" --domain 6 --n-loops 12 --name "Wave"

Built-in presets: sphere, paraboloid, cos, cone
"""

from __future__ import annotations

import argparse
import sys
import numpy as np

from . import generate
from .stitches import YarnProfile

PRESETS: dict[str, tuple] = {
    "sphere": (
        lambda r: 1 - np.sqrt(max(1 - r**2, 0)),
        1.0,
        "Sphere (hemisphere profile: z = 1 - sqrt(1 - r²))",
    ),
    "paraboloid": (
        lambda r: r**2,
        1.0,
        "Paraboloid (z = r²)",
    ),
    "cos": (
        lambda r: np.cos(r),
        9.0,
        "Cosine surface (z = cos(r), captures 3 oscillations)",
    ),
    "cone": (
        lambda r: r,
        1.0,
        "Cone (z = r)",
    ),
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="crochet-gen",
        description="Generate crochet patterns for rotationally symmetric 3D surfaces.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "surface",
        help=(
            "Built-in preset name (sphere / paraboloid / cos / cone) "
            "OR a Python expression in r (e.g. 'np.sin(r) + r*0.1'). "
            "numpy is available as np."
        ),
    )
    parser.add_argument(
        "--domain", "-d",
        type=float,
        default=None,
        help="Radial domain limit. Defaults to preset value or 1.0 for custom.",
    )
    parser.add_argument(
        "--n-loops", "-n",
        type=int,
        default=10,
        dest="n_loops",
        help="Number of crochet loops (default: 10).",
    )
    parser.add_argument(
        "--closed", "-c",
        action="store_true",
        help="Mirror the pattern to close the shape (e.g. full sphere).",
    )
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Pattern name shown in the output header.",
    )
    parser.add_argument(
        "--stitch-height",
        type=float,
        default=0.572,
        dest="stitch_height",
        help="Stitch height in cm (default: 0.572).",
    )
    parser.add_argument(
        "--stitch-length",
        type=float,
        default=0.636,
        dest="stitch_length",
        help="Stitch length in cm (default: 0.636).",
    )
    parser.add_argument(
        "--visualize", "-v",
        action="store_true",
        help="Show matplotlib visualizations.",
    )
    parser.add_argument(
        "--save-plot",
        type=str,
        default=None,
        dest="save_plot",
        help="Path prefix for saving plots (e.g. 'outputs/sphere').",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Save pattern text to this file (prints to stdout if not set).",
    )

    return parser.parse_args(argv)


def resolve_surface(name: str, domain_override: float | None):
    """Return (f, domain, display_name) for a preset or expression."""
    if name in PRESETS:
        f, default_domain, desc = PRESETS[name]
        domain = domain_override if domain_override is not None else default_domain
        return f, domain, name.capitalize()

    try:
        f = eval(f"lambda r: {name}", {"np": np, "__builtins__": {}})
        _ = f(0.5)
    except Exception as e:
        print(f"Error: could not parse surface expression '{name}': {e}", file=sys.stderr)
        sys.exit(1)

    domain = domain_override if domain_override is not None else 1.0
    return f, domain, name


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    f, domain, display_name = resolve_surface(args.surface, args.domain)
    name = args.name or display_name

    yarn = YarnProfile(
        stitch_height_cm=args.stitch_height,
        stitch_length_cm=args.stitch_length,
    )

    print(f"  Generating pattern for: {name}")
    print(f"  Domain: [0, {domain}]   |   Loops: {args.n_loops}   |   Closed: {args.closed}")
    print()

    result = generate(
        f=f,
        domain=domain,
        n_loops=args.n_loops,
        closed=args.closed,
        name=name,
        yarn=yarn,
        visualize=args.visualize,
        save_plot=args.save_plot,
    )

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(result.pattern_text + "\n")
        print(f"Pattern saved to {args.output}")
    else:
        print(result.pattern_text)


if __name__ == "__main__":
    main()
