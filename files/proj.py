#!/usr/bin/env python3
"""
proj.py -- Symbolic Explainable AI programming project (2026/27)

CSPLib prob018: Water Bucket Problem
--------------------------------------------------------------------
CSPLib already publishes MiniZinc models for this problem
(water_buckets1.mzn, water_buckets_regular.mzn), which are fixed to the
classic 3-bucket puzzle. This project's extension generalises the problem
to an arbitrary number of buckets N >= 2, with arbitrary capacities,
initial amounts and (possibly partial) goal amounts. water_bucket.mzn
encodes this generalised version; this script builds a problem instance,
invokes the MiniZinc/Gecode solver on it (via MiniZinc Python), and
prints the parsed solution to stdout, per the assignment's pipeline:

    instance --> proj.py builds CSP model --> MiniZinc solver --> proj.py
    parses solver output --> solution on stdout

Usage
-----
    # Inline instance:
    python proj.py --capacities 8 5 3 --initial 8 0 0 --goal 4 4 -1

    # From a JSON instance file:
    python proj.py --file instance.json

Where instance.json looks like:
    {
        "capacities": [8, 5, 3],
        "initial":    [8, 0, 0],
        "goal":       [4, 4, -1],
        "max_steps":  20
    }

Requirements
------------
    - MiniZinc >= 2.10.1 (https://www.minizinc.org/), with the Gecode
      solver available on PATH.
    - MiniZinc Python bindings: pip install minizinc
"""

import argparse
import json
import sys
from pathlib import Path

from minizinc import Instance, Model, Solver

MODEL_PATH = Path(__file__).resolve().parent / "water_bucket.mzn"
DEFAULT_MAX_STEPS = 20


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Solve the generalised N-bucket water pouring problem as a CSP."
    )
    parser.add_argument(
        "--file", type=str,
        help="JSON file describing the instance (capacities/initial/goal/max_steps).",
    )
    parser.add_argument("--capacities", type=int, nargs="+", help="Bucket capacities.")
    parser.add_argument("--initial", type=int, nargs="+", help="Initial amount per bucket.")
    parser.add_argument(
        "--goal", type=int, nargs="+",
        help="Goal amount per bucket (use -1 for 'any amount').",
    )
    parser.add_argument(
        "--max-steps", type=int, default=DEFAULT_MAX_STEPS,
        help=f"Search horizon / max number of pours to consider (default {DEFAULT_MAX_STEPS}).",
    )
    parser.add_argument(
        "--solver", type=str, default="gecode",
        help="MiniZinc solver id to use (default: gecode).",
    )
    return parser.parse_args(argv)


def load_instance(args):
    """Read the problem instance either from a JSON file or from CLI flags."""
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            data = json.load(f)
        capacities = data["capacities"]
        initial = data["initial"]
        goal = data["goal"]
        max_steps = data.get("max_steps", args.max_steps)
    else:
        if not (args.capacities and args.initial and args.goal):
            sys.exit(
                "error: provide either --file instance.json, "
                "or all three of --capacities --initial --goal"
            )
        capacities, initial, goal = args.capacities, args.initial, args.goal
        max_steps = args.max_steps

    n = len(capacities)
    if len(initial) != n or len(goal) != n:
        sys.exit(
            f"error: capacities, initial and goal must all have the same "
            f"length (got {len(capacities)}, {len(initial)}, {len(goal)})"
        )
    if n < 2:
        sys.exit("error: at least 2 buckets are required")
    for i in range(n):
        if capacities[i] <= 0:
            sys.exit(f"error: bucket {i + 1} capacity must be positive")
        if not (0 <= initial[i] <= capacities[i]):
            sys.exit(
                f"error: bucket {i + 1} initial amount {initial[i]} "
                f"is invalid for capacity {capacities[i]}"
            )
        if goal[i] != -1 and not (0 <= goal[i] <= capacities[i]):
            sys.exit(
                f"error: bucket {i + 1} goal amount {goal[i]} "
                f"is invalid for capacity {capacities[i]}"
            )

    return capacities, initial, goal, max_steps


def build_and_solve(capacities, initial, goal, max_steps, solver_id):
    """Build the MiniZinc instance and invoke the solver (Fig. 1 pipeline)."""
    model = Model(str(MODEL_PATH))
    solver = Solver.lookup(solver_id)
    inst = Instance(solver, model)

    n = len(capacities)
    inst["n_buckets"] = n
    inst["cap"] = capacities
    inst["init"] = initial
    inst["goal"] = goal
    inst["max_steps"] = max_steps

    return inst.solve(), n


def format_solution(result, capacities, initial, goal, n, max_steps):
    """Parse the solver's result object into the final human-readable solution."""
    if result.solution is None:
        return (
            "No solution found within the given step horizon "
            f"(max_steps={max_steps}). Try increasing --max-steps.\n"
        )

    num_steps = result["num_steps"]
    amount = result["amount"]      # amount[bucket][step], 1-indexed buckets, 0-indexed steps
    source = result["source"]      # source[step], 0-indexed steps
    target = result["target"]

    goal_display = ["any" if g == -1 else g for g in goal]

    lines = [
        f"Solution found in {num_steps} step(s)",
        f"Buckets ({n}): capacities = {capacities}",
        f"Initial: {initial}",
        f"Goal:    {goal_display}",
        "",
        "Step-by-step solution:",
        f"Step 0: {[amount[b][0] for b in range(n)]} (initial)",
    ]
    for step in range(1, num_steps + 1):
        src, tgt = source[step - 1], target[step - 1]
        state = [amount[b][step] for b in range(n)]
        lines.append(f"Step {step}: {state} (pour bucket {src} -> bucket {tgt})")

    return "\n".join(lines) + "\n"


def main(argv=None):
    args = parse_args(argv)
    capacities, initial, goal, max_steps = load_instance(args)
    result, n = build_and_solve(capacities, initial, goal, max_steps, args.solver)
    print(format_solution(result, capacities, initial, goal, n, max_steps))


if __name__ == "__main__":
    main()
