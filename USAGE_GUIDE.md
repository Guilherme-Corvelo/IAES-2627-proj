# Water Bucket Problem Solver - Usage Guide

## Quick Start

### Option 1: Python BFS Solver (Simplest)

```bash
python water_bucket_solver.py
```

This will run three demonstrations and show all solutions step-by-step.

### Option 2: MiniZinc Constraint Solver (Professional)

**Prerequisites:** Install MiniZinc from https://www.minizinc.org/

```bash
# Classic 8-5-3 problem
minizinc water_bucket.mzn water_bucket_8_5_3.dzn

# Custom 10-7-4 problem
minizinc water_bucket.mzn water_bucket_10_7_4.dzn

# Custom 9-6-4 problem
minizinc water_bucket.mzn water_bucket_9_6_4.dzn
```

---

## Creating a New Problem

### Method 1: With Python

Edit `water_bucket_solver.py` and add:

```python
from water_bucket_solver import BucketConfig, WaterBucketSolver

# Define your problem
config = BucketConfig(
    capacities=(12, 8, 5),        # Three bucket sizes
    initial_state=(12, 0, 0),     # Starting configuration
    goal=(6, 6, -1),              # Goal (-1 means "any value")
    allow_partial_goal=True
)

# Solve
solver = WaterBucketSolver(config)
result = solver.solve()
solver.print_solution(result)

# Analyze all reachable states
reachable = solver.get_all_reachable_states()
print(f"Total reachable states: {len(reachable)}")
```

### Method 2: With MiniZinc

Create a new file `water_bucket_YOUR_PROBLEM.dzn`:

```minizinc
% Your Problem Description
% Goal: [describe what you want to achieve]

cap_a = 12;
cap_b = 8;
cap_c = 5;

init_a = 12;
init_b = 0;
init_c = 0;

goal_a = 6;
goal_b = 6;
goal_c = -1;  % -1 means "any value"
```

Then run:

```bash
minizinc water_bucket.mzn water_bucket_YOUR_PROBLEM.dzn
```

---

## Understanding the Goal Specification

In data files (`.dzn`), you can specify goals with special meanings:

| Goal Value | Meaning |
|-----------|----------|
| `0` to `cap` | Exact amount in that bucket |
| `-1` | Any amount (don't care) |

**Example:**
```minizinc
goal_a = 4;   % Exactly 4L in bucket A
goal_b = 4;   % Exactly 4L in bucket B
goal_c = -1;  % Any amount in bucket C (we don't care)
```

---

## Understanding the Output

### Python Output

```
============================================================
Solution found in 7 steps
============================================================
Capacities: (8, 5, 3)
Initial:    (8, 0, 0)
Goal:       (4, 4, -1)
Solution:   (4, 4, 0)

Path:
  Step 0: (8, 0, 0)
  Step 1: (3, 5, 0)
  Step 2: (3, 2, 3)
  ...
  Step 7: (4, 4, 0)
============================================================
```

### MiniZinc Output

```
Solution found in 7 steps
Capacities: A=8L, B=5L, C=3L
Initial: A=8L, B=0L, C=0L
Goal: A=4L, B=4L, C=anyL

Step-by-step solution:
Step 0: A=8L, B=0L, C=0L (initial)
Step 1: A=3L, B=5L, C=0L (pour A -> B)
Step 2: A=3L, B=2L, C=3L (pour B -> C)
...
Step 7: A=4L, B=4L, C=0L (pour C -> A)
```

---

## Troubleshooting

### Python: "ModuleNotFoundError"
Make sure you're running from the correct directory:
```bash
cd /path/to/IAES-2627-proj
python water_bucket_solver.py
```

### MiniZinc: "command not found"
Install MiniZinc from https://www.minizinc.org/ and add it to your PATH.

### MiniZinc: "No solution found"
The goal state might be unreachable with the given capacities and initial state. Try:
1. Changing the goal
2. Using `-1` for buckets you don't care about
3. Checking the constraints are valid

---

## Performance Comparison

### BFS (Python)
- ✅ Simple to understand and modify
- ✅ Fast for small problems (< 10 steps)
- ❌ Slower for complex problems
- ❌ Limited to 3 buckets in current implementation

### MiniZinc (Constraint Programming)
- ✅ Automatically optimized by solver
- ✅ Declarative (specify problem, not algorithm)
- ✅ More scalable
- ❌ Requires MiniZinc installation
- ❌ Slightly longer to understand

**Recommendation:** Use MiniZinc for professional/academic work, Python for learning.

---

## Files Summary

| File | Purpose |
|------|----------|
| `water_bucket.mzn` | MiniZinc model (constraint definition) |
| `water_bucket_*.dzn` | Data files for specific problems |
| `water_bucket_solver.py` | Python BFS implementation |
| `README.md` | Project overview |
| `USAGE_GUIDE.md` | This file |
| `SOLUTION_8_5_3.txt` | Pre-computed solution for classic problem |

---

## Need Help?

Check these resources:
- MiniZinc: https://www.minizinc.org/doc-latest/en/
- Problem explanation: See `SOLUTION_8_5_3.txt`
- Code comments in `water_bucket_solver.py`
