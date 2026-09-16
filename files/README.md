# IAES 26/27 Project - CSPLib prob018: Water Bucket Problem

## Problem and extension

Base problem: [CSPLib prob018](https://www.csplib.org/Problems/prob018/), the
classic 8-5-3 water pouring puzzle. CSPLib already lists MiniZinc models for
this exact problem (`water_buckets1.mzn`, `water_buckets_regular.mzn`), so
per the assignment rules this project implements a **non-trivial
extension**: the model is generalised from a fixed 3-bucket puzzle to an
**arbitrary number of buckets** (`n_buckets >= 2`), with arbitrary
capacities, initial amounts, and (possibly partial) goal amounts. Pours are
still "from one bucket into another until the source is empty or the target
is full", exactly as in the original problem, but the encoding no longer
hardcodes 3 buckets or 6 pour directions — it works for any N.

## Files

- `proj.py` - the required entry point. Reads a problem instance (CLI flags
  or a JSON file), builds a MiniZinc instance from `water_bucket.mzn`,
  invokes the Gecode solver via MiniZinc Python, parses the result, and
  prints the solution to stdout.
- `water_bucket.mzn` - the generalised N-bucket MiniZinc model.
- `instances/` - example instance files:
  - `classic_8_5_3.json` - the classic 8-5-3 problem (optimal: 7 steps).
  - `four_bucket_extension.json` - a genuine 4-bucket instance that needs
    all 4 buckets to reach the goal in the minimum number of steps,
    demonstrating the extension.
- `water_bucket_solver.py` - an independent BFS reference implementation,
  kept only to cross-check the MiniZinc solver's results (not part of the
  official CSP pipeline; see report for how it was used).
- `requirements.txt` - Python dependency (`minizinc` package).

## Requirements

- MiniZinc >= 2.10.1 (https://www.minizinc.org/) with the Gecode solver
  on PATH.
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

This independently re-solves the classic and custom cases with plain BFS,
useful as a sanity check that the CSP model's optimal step counts agree
with brute-force search (both find 7 steps for the classic 8-5-3 case).
