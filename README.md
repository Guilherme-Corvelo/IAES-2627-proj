# IAES-2627-proj
IAES 26/27 project - Water Bucket Problem Solver

## Overview
This project contains solutions to the water bucket pouring problem using both:
1. **BFS (Breadth-First Search)** - Python implementation
2. **MiniZinc Constraint Programming** - Declarative constraint solver

## Files

### Python Solution
- `water_bucket_solver.py` - General BFS solver for any 3-bucket configuration

### MiniZinc Solution
- `water_bucket.mzn` - MiniZinc model for the water bucket problem
- `water_bucket_8_5_3.dzn` - Classic 8-5-3 problem data (goal: 4L in first two buckets)
- `water_bucket_10_7_4.dzn` - Custom problem: 10L, 7L, 4L buckets (goal: 5L in first)
- `water_bucket_9_6_4.dzn` - Custom problem: 9L, 6L, 4L buckets (goal: 3L in second)

## Usage

### Python BFS Solver
```bash
python water_bucket_solver.py
```

The script runs three demonstrations:
1. Classic 8-5-3 problem
2. Custom 10-7-4 problem
3. Analysis of reachable states for 9-6-4 problem

### MiniZinc Solver

Install MiniZinc from: https://www.minizinc.org/

Then run any of the problems:
```bash
# Classic 8-5-3 problem
minizinc water_bucket.mzn water_bucket_8_5_3.dzn

# Custom 10-7-4 problem
minizinc water_bucket.mzn water_bucket_10_7_4.dzn

# Custom 9-6-4 problem
minizinc water_bucket.mzn water_bucket_9_6_4.dzn
```

## Problem Definition

Given three buckets with different capacities, we want to find the minimum sequence of pours to reach a goal state.

**Parameters:**
- `cap_a, cap_b, cap_c` - Bucket capacities
- `init_a, init_b, init_c` - Initial water amounts
- `goal_a, goal_b, goal_c` - Goal amounts (use -1 for "any value")

**Actions:**
At each step, we can pour from one bucket to another until:
- The source bucket is empty, OR
- The target bucket is full

**Objective:**
Minimize the number of steps to reach the goal state.

## Example: Classic 8-5-3 Problem

**Problem:**
- Buckets: 8L, 5L, 3L
- Initial: (8, 0, 0) - 8L in first bucket
- Goal: (4, 4, ?) - 4L in each of first two buckets

**Solution Steps:**
1. (8, 0, 0) → Pour A→B → (3, 5, 0)
2. (3, 5, 0) → Pour B→C → (3, 2, 3)
3. (3, 2, 3) → Pour C→A → (6, 2, 0)
4. (6, 2, 0) → Pour B→C → (6, 0, 2)
5. (6, 0, 2) → Pour A→B → (1, 5, 2)
6. (1, 5, 2) → Pour B→C → (1, 4, 3)
7. (1, 4, 3) → Pour C→A → (4, 4, 0) ✓

## Comparison: BFS vs MiniZinc

| Aspect | BFS Python | MiniZinc |
|--------|-----------|----------|
| **Approach** | Explicit graph search | Constraint satisfaction |
| **Setup** | Simple, direct coding | Declarative model |
| **Flexibility** | Easy to modify logic | Flexible goal specifications |
| **Speed** | Fast for small problems | Optimized by solver |
| **Scalability** | Limited by search space | Better for complex constraints |

## How to Extend

To solve a different water bucket problem:

1. **With Python:**
   ```python
   config = BucketConfig(
       capacities=(A_cap, B_cap, C_cap),
       initial_state=(A_init, B_init, C_init),
       goal=(A_goal, B_goal, C_goal)  # Use -1 for "any"
   )
   solver = WaterBucketSolver(config)
   result = solver.solve()
   solver.print_solution(result)
   ```

2. **With MiniZinc:**
   Create a new `.dzn` file with your parameters and run:
   ```bash
   minizinc water_bucket.mzn your_problem.dzn
   ```

## Author
Created as part of the IAES 26/27 course project.
