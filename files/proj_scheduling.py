#!/usr/bin/env python3
"""
proj_scheduling.py -- Scheduling extension for the water bucket problem

Uses water_bucket_scheduling.mzn to model the problem as a sequence of
explicit operations (FILL, EMPTY, POUR) rather than just state transitions.
This enables optimization of makespan and number of operations.

Usage
-----
    # Inline instance:
    python proj_scheduling.py --capacities 8 5 3 --initial 8 0 0 --goal 4 4 -1

    # From a JSON instance file:
    python proj_scheduling.py --file instances/classic_8_5_3.json

    # With objective specification:
    python proj_scheduling.py --file instances/classic_8_5_3.json --objective makespan

Where objective can be: makespan (default), operations, or lexicographic

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
from enum import Enum

from minizinc import Instance, Model, Solver, Status

MODEL_PATH = Path(__file__).resolve().parent / "water_bucket_scheduling.mzn"
DEFAULT_MAX_STEPS = 20


class OpType(Enum):
    """Operation types in the scheduling model."""
    FILL = 1
    EMPTY = 2
    POUR = 3


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Solve the water bucket problem using a scheduling/planning model."
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
        help=f"Search horizon / max number of operations (default {DEFAULT_MAX_STEPS}).",
    )
    parser.add_argument(
        "--objective", choices=["makespan", "operations"],
        default="makespan",
        help="Optimization objective: makespan (minimize steps, default) "
             "or operations (minimize meaningful ops).",
    )
    parser.add_argument(
        "--solver", type=str, default="gecode",
        help="MiniZinc solver id to use (default: gecode).",
    )
    return parser.parse_args(argv)


def load_instance(args):
    """Read the problem instance either from a JSON file or from CLI flags."""
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            sys.exit(f"error: instance file not found: {args.file}")
        except json.JSONDecodeError as exc:
            sys.exit(f"error: {args.file} is not valid JSON ({exc})")
        for key in ("capacities", "initial", "goal"):
            if key not in data:
                sys.exit(f"error: {args.file} is missing the '{key}' field")
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


def build_and_solve(capacities, initial, goal, max_steps, solver_id, objective):
    """Build the MiniZinc instance and invoke the solver."""
    model = Model(str(MODEL_PATH))
    solver = Solver.lookup(solver_id)
    inst = Instance(solver, model)

    n = len(capacities)
    inst["n_buckets"] = n
    inst["cap"] = capacities
    inst["init"] = initial
    inst["goal"] = goal
    inst["max_steps"] = max_steps

    return inst.solve(), n, objective


def operation_name(op_int):
    """Convert operation integer to human-readable name."""
    ops = {1: "FILL", 2: "EMPTY", 3: "POUR"}
    return ops.get(op_int, f"OP({op_int})")


def format_solution(result, capacities, initial, goal, n, max_steps, objective):
    """Parse the solver's result object into the final human-readable solution."""
    if result.solution is None:
        if result.status == Status.UNSATISFIABLE:
            return (
                "UNSATISFIABLE: the goal is unreachable within the given step "
                f"horizon (max_steps={max_steps}). Either the goal is impossible "
                "for these capacities, or the horizon is too short — try "
                "increasing --max-steps.\n"
            )
        return (
            f"No solution proved within the search limits (status: {result.status}).\n"
        )

    makespan = result["makespan"]
    amount = result["amount"]
    op = result["op"]
    source = result["source"]
    target = result["target"]

    goal_display = ["any" if g == -1 else g for g in goal]

    lines = [
        f"Solution found in {makespan} operation(s)",
        f"Buckets ({n}): capacities = {capacities}",
        f"Initial: {initial}",
        f"Goal:    {goal_display}",
        f"Objective: {objective}",
        "",
        "Step-by-step solution:",
        f"Step 0: {[amount[b][0] for b in range(n)]} (initial)",
    ]
    for step in range(1, makespan + 1):
        op_type = operation_name(op[step - 1])
        src, tgt = source[step - 1], target[step - 1]
        state = [amount[b][step] for b in range(n)]
        
        if op_type == "FILL":
            lines.append(f"Step {step}: {state} (FILL bucket {tgt})")
        elif op_type == "EMPTY":
            lines.append(f"Step {step}: {state} (EMPTY bucket {src})")
        else:  # POUR
            lines.append(f"Step {step}: {state} (POUR bucket {src} -> bucket {tgt})")

    return "\n".join(lines) + "\n"


def main(argv=None):
    args = parse_args(argv)
    capacities, initial, goal, max_steps = load_instance(args)
    result, n, objective = build_and_solve(
        capacities, initial, goal, max_steps, args.solver, args.objective
    )
    print(
        format_solution(result, capacities, initial, goal, n, max_steps, objective),
        end=""
    )


if __name__ == "__main__":
    main()
