"""
Water Bucket Problem Solver
Solves the general 3-bucket water pouring problem using BFS.

Given 3 buckets with capacities (A, B, C) and initial amounts,
find the minimum number of steps to reach a target state.

Example: Classic 8-5-3 problem
- Buckets: 8L, 5L, 3L
- Initial: (8, 0, 0)
- Goal: Reach any state with 4L in any bucket(s)
"""

from collections import deque
from typing import Tuple, List, Optional, Set, Dict
from dataclasses import dataclass


@dataclass
class BucketConfig:
    """Configuration for the water bucket problem."""
    capacities: Tuple[int, int, int]  # (A_capacity, B_capacity, C_capacity)
    initial_state: Tuple[int, int, int]  # (A_amount, B_amount, C_amount)
    goal: Tuple[int, int, int]  # Target state or partial target
    allow_partial_goal: bool = True  # If True, goal can be partial (use -1 for "any value")


class WaterBucketSolver:
    """Solver for the 3-bucket water pouring problem."""

    def __init__(self, config: BucketConfig):
        """
        Initialize the solver.
        
        Args:
            config: BucketConfig with capacities, initial state, and goal
        """
        self.capacities = config.capacities
        self.initial_state = config.initial_state
        self.goal = config.goal
        self.allow_partial_goal = config.allow_partial_goal
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate the configuration."""
        # Check that initial amounts don't exceed capacities
        for i in range(3):
            if self.initial_state[i] > self.capacities[i]:
                raise ValueError(
                    f"Bucket {i}: initial amount {self.initial_state[i]} "
                    f"exceeds capacity {self.capacities[i]}"
                )
            if self.initial_state[i] < 0 or self.capacities[i] < 0:
                raise ValueError("Amounts and capacities must be non-negative")

    def _is_goal(self, state: Tuple[int, int, int]) -> bool:
        """
        Check if a state matches the goal.
        
        If allow_partial_goal is True, -1 in goal means "any value".
        """
        for i in range(3):
            if self.goal[i] != -1 and state[i] != self.goal[i]:
                return False
        return True

    def _pour(
        self, state: Tuple[int, int, int], source: int, target: int
    ) -> Tuple[int, int, int]:
        """
        Pour from source bucket to target bucket.
        
        Pour until source is empty or target is full.
        
        Args:
            state: Current state (a, b, c)
            source: Index of source bucket (0, 1, or 2)
            target: Index of target bucket (0, 1, or 2)
            
        Returns:
            New state after pouring
        """
        if source == target:
            return state

        new_state = list(state)
        # Amount to pour: min of (source content, space in target)
        amount = min(new_state[source], self.capacities[target] - new_state[target])
        new_state[source] -= amount
        new_state[target] += amount

        return tuple(new_state)

    def _get_neighbors(self, state: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        """Get all valid next states from current state."""
        neighbors = []
        # Pour from each bucket to every other bucket
        for source in range(3):
            for target in range(3):
                if source != target:
                    new_state = self._pour(state, source, target)
                    if new_state != state:  # Only add if state changed
                        neighbors.append(new_state)
        return neighbors

    def solve(self) -> Optional[Dict]:
        """
        Solve using BFS to find shortest path to goal.
        
        Returns:
            Dict with 'path', 'steps', 'solution' if found, else None
        """
        if self._is_goal(self.initial_state):
            return {
                "path": [self.initial_state],
                "steps": 0,
                "solution": self.initial_state,
            }

        queue: deque = deque([(self.initial_state, [self.initial_state])])
        visited: Set[Tuple[int, int, int]] = {self.initial_state}

        while queue:
            current_state, path = queue.popleft()

            for neighbor in self._get_neighbors(current_state):
                if neighbor not in visited:
                    visited.add(neighbor)

                    if self._is_goal(neighbor):
                        path.append(neighbor)
                        return {
                            "path": path,
                            "steps": len(path) - 1,
                            "solution": neighbor,
                        }

                    queue.append((neighbor, path + [neighbor]))

        return None

    def get_all_reachable_states(self) -> Set[Tuple[int, int, int]]:
        """
        Get all states reachable from initial state.
        
        Useful for analysis and finding valid goals.
        """
        visited: Set[Tuple[int, int, int]] = {self.initial_state}
        queue: deque = deque([self.initial_state])

        while queue:
            current_state = queue.popleft()
            for neighbor in self._get_neighbors(current_state):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return visited

    def print_solution(self, result: Optional[Dict]) -> None:
        """Pretty print the solution."""
        if result is None:
            print("No solution found!")
            return

        print(f"\n{'='*60}")
        print(f"Solution found in {result['steps']} steps")
        print(f"{'='*60}")
        print(f"Capacities: {self.capacities}")
        print(f"Initial:    {self.initial_state}")
        print(f"Goal:       {self.goal}")
        print(f"Solution:   {result['solution']}")
        print(f"\nPath:")

        for i, state in enumerate(result["path"]):
            print(f"  Step {i}: {state}")

        print(f"{'='*60}\n")


def demo_classic_problem():
    """Demo: Classic 8-5-3 water bucket problem."""
    print("\n" + "="*60)
    print("CLASSIC PROBLEM: 8-5-3 Bucket")
    print("="*60)

    config = BucketConfig(
        capacities=(8, 5, 3),
        initial_state=(8, 0, 0),
        goal=(4, 4, -1),  # Goal: 4 liters in first two buckets
        allow_partial_goal=True,
    )

    solver = WaterBucketSolver(config)
    result = solver.solve()
    solver.print_solution(result)


def demo_custom_problem():
    """Demo: Custom problem with different bucket sizes."""
    print("\n" + "="*60)
    print("CUSTOM PROBLEM: 10-7-4 Bucket")
    print("="*60)

    config = BucketConfig(
        capacities=(10, 7, 4),
        initial_state=(10, 0, 0),
        goal=(5, 5, 0),  # Goal: 5 liters in first two buckets
        allow_partial_goal=True,
    )

    solver = WaterBucketSolver(config)
    result = solver.solve()
    solver.print_solution(result)

    print("All reachable states:")
    reachable = solver.get_all_reachable_states()
    print(f"Total: {len(reachable)} states")
    for state in sorted(reachable):
        print(f"  {state}")


def demo_analysis():
    """Demo: Analyze different goals for a custom problem."""
    print("\n" + "="*60)
    print("ANALYSIS: What goals can we reach?")
    print("="*60)

    config = BucketConfig(
        capacities=(9, 6, 4),
        initial_state=(9, 0, 0),
        goal=(-1, -1, -1),  # Placeholder, will be changed
        allow_partial_goal=True,
    )

    solver = WaterBucketSolver(config)
    reachable = solver.get_all_reachable_states()

    print(f"\nWith buckets {config.capacities}:")
    print(f"Starting from {config.initial_state}")
    print(f"\nReachable states: {len(reachable)}")

    # Group by amount in first bucket
    by_first = {}
    for state in reachable:
        amt = state[0]
        if amt not in by_first:
            by_first[amt] = []
        by_first[amt].append(state)

    print("\nGrouped by amount in first bucket:")
    for amt in sorted(by_first.keys()):
        print(f"  {amt}L: {len(by_first[amt])} state(s)")


if __name__ == "__main__":
    demo_classic_problem()
    demo_custom_problem()
    demo_analysis()
