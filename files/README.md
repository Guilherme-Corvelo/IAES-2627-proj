# IAES 26/27 Project - CSPLib prob018: Water Bucket Problem

## Problem and extension

Base problem: [CSPLib prob018](https://www.csplib.org/Problems/prob018/), the
classic 8-5-3 water pouring puzzle. CSPLib already lists MiniZinc models for
this exact problem (`water_buckets1.mzn`, `water_buckets_regular.mzn`), so
per the assignment rules this project implements a non-trivial generalisation:
we do not stop at a simple shortest-path/state-transition solution.

The actual final objective of this project is a scheduling/planning variant:
find a sequence of water-transfer operations (`FILL`, `EMPTY`, `POUR`) that
reaches the target bucket amounts while minimizing the overall makespan and the
number of operations. In other words, the task is not merely to decide whether
or how the goal can be reached, but to do so in the most efficient scheduled
way.

The model is therefore generalised from a fixed 3-bucket puzzle to an arbitrary
number of buckets (`n_buckets >= 2`), with arbitrary capacities, initial
amounts, and (possibly partial) goal amounts. Pours are still "from one bucket
into another until the source is empty or the target is full", exactly as in
the original problem, but the encoding now models the explicit time-expanded
schedule rather than only raw state transitions.

## Files

- `proj.py` - the required entry point. Reads a problem instance (CLI flags
  or a JSON file), builds a MiniZinc instance from `water_bucket.mzn`,
  invokes the Gecode solver via MiniZinc Python, parses the result, and prints
  the solution to stdout.
- `proj_scheduling.py` - the final scheduling-oriented entry point. It models
  the problem as a compact planning problem with explicit operations and
  minimizes makespan.
- `water_bucket.mzn` - the generalised N-bucket MiniZinc model for the
  state-transition formulation.
- `water_bucket_scheduling.mzn` - the final scheduling/planning model used for
  the assignment objective: minimize time and operation count while reaching
  the desired bucket configuration.
- `instances/` - example instance files:
  - `classic_8_5_3.json` - the classic 8-5-3 problem used as a scheduling
    benchmark (optimal schedule length is the relevant objective).
  - `four_bucket_extension.json` - a genuine 4-bucket instance that needs all
    4 buckets to reach the goal in the minimum scheduled time, demonstrating
    the extension.
- `water_bucket_solver.py` - an independent BFS reference implementation,
  kept only to cross-check the MiniZinc solver's results and to validate the
  scheduling interpretation against a brute-force model (not part of the
  official final objective pipeline; see report for how it was used).
- `requirements.txt` - Python dependency (`minizinc` package).

## Requirements

- MiniZinc >= 2.10.1 (https://www.minizinc.org/) with the Gecode solver on
  PATH.
- `pip install -r requirements.txt`

## Usage

```bash
# Inline instance (classic problem)
python proj.py --capacities 8 5 3 --initial 8 0 0 --goal 4 4 -1

# From a JSON instance file
python proj.py --file instances/classic_8_5_3.json

# The 4-bucket extension example
python proj.py --file instances/four_bucket_extension.json

# Optional flags
python proj.py --file instances/classic_8_5_3.json --max-steps 30 --solver gecode
```

`goal` values use `-1` to mean "any amount is fine for this bucket".

## Verifying against the BFS reference

```bash
python water_bucket_solver.py
```

This independently re-solves the classic and custom cases with plain BFS, and
is useful as a sanity check that the scheduling solution and the brute-force
state-space search agree on the relevant goal reachability and optimality
criteria.
