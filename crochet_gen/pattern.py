"""
Converts numeric stitch data into a human-usable crochet pattern.

Each loop is expressed as a sequence of instructions like:
    sc3, inc, sc5, inc, sc4
where:
  - sc<n>  = n consecutive single crochet stitches
  - inc    = increase (2 stitches in 1)
  - dec    = decrease (2 stitches into 1)

For a closed shape (like a sphere), the second half mirrors the first:
the loops are reversed and increases become decreases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LoopInstruction:
    """
    Represents the crochet instructions for a single loop.

    Attributes
    ----------
    loop_number : int
        1-indexed loop number in the pattern.
    stitch_count : int
        Total number of stitches in this loop.
    steps : list[str]
        Ordered list of crochet instructions (e.g. ["sc3", "inc", "sc5"]).
    """
    loop_number: int
    stitch_count: int
    steps: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return f"Loop {self.loop_number}: " + ", ".join(self.steps)


def build_loop_instructions(
    loop_number: int,
    stitch_count: int,
    prev_stitch_count: int,
    special_positions: list[int],
) -> LoopInstruction:
    """
    Build the instruction sequence for a single loop.

    Walks through stitch indices 0..stitch_count-1. At a special position,
    emits an inc or dec. Between specials, groups consecutive plain stitches
    into a single sc<n> instruction.

    Parameters
    ----------
    loop_number : int
        1-indexed loop number.
    stitch_count : int
        Total stitches in this loop.
    prev_stitch_count : int
        Stitches in the previous loop (to determine inc vs dec).
    special_positions : list[int]
        Sorted stitch indices where inc/dec occurs.

    Returns
    -------
    LoopInstruction
        Complete instruction object for this loop.
    """
    if stitch_count > prev_stitch_count:
        special = "inc"
    elif stitch_count < prev_stitch_count:
        special = "dec"
    else:
        special = None  # no special stitches needed

    pos_set = set(special_positions)
    steps: list[str] = []
    i = 0

    while i < stitch_count:
        if special and i in pos_set:
            steps.append(special)
            i += 1
        else:
            # Collect a run of plain single crochets
            run = 0
            while i < stitch_count and not (special and i in pos_set):
                run += 1
                i += 1
            steps.append(f"sc{run}")

    return LoopInstruction(loop_number, stitch_count, steps)


def generate_pattern(
    stitch_counts: list[int],
    special_positions: list[list[int]],
    closed: bool = False,
    name: Optional[str] = None,
) -> list[str]:
    """
    Generate the full written crochet pattern.

    Parameters
    ----------
    stitch_counts : list[int]
        Stitch count per loop (for the first half, if closed).
    special_positions : list[list[int]]
        Special stitch indices per loop.
    closed : bool
        If True, mirror the pattern to close the shape (e.g. a sphere).
        The second half reverses the loops and swaps inc <-> dec.
    name : str, optional
        Display name for the pattern header.

    Returns
    -------
    list[str]
        Lines of the written pattern, ready to print or save.
    """
    lines = []

    if name:
        lines.append(f"Pattern: {name}")
        lines.append("=" * (len(name) + 9))

    lines.append("Chain On")

    # --- First half ---
    prev = 0
    for i, count in enumerate(stitch_counts):
        instr = build_loop_instructions(
            loop_number=i + 1,
            stitch_count=count,
            prev_stitch_count=prev,
            special_positions=special_positions[i],
        )
        lines.append(str(instr))
        prev = count

    # --- Mirror for closed shapes ---
    if closed:
        n = len(stitch_counts)
        # The equator loop (last in first half) is not repeated
        for j, i in enumerate(range(n - 2, -1, -1)):
            mirror_count = stitch_counts[i]
            mirror_prev = stitch_counts[i + 1]  # decreasing now
            loop_num = n + j + 1

            # Flip inc <-> dec by swapping count/prev
            instr = build_loop_instructions(
                loop_number=loop_num,
                stitch_count=mirror_count,
                prev_stitch_count=mirror_prev,
                special_positions=special_positions[i],
            )
            lines.append(str(instr))

    lines.append("Chain Off")
    return lines


def pattern_to_string(lines: list[str]) -> str:
    """Join pattern lines into a single printable string."""
    return "\n".join(lines)
