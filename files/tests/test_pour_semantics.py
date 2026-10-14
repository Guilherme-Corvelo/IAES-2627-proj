import sys
import unittest
from pathlib import Path


FILES_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FILES_DIR))

import proj
import proj_scheduling


class CompletePourSemanticsTests(unittest.TestCase):
    capacities = [8, 5, 3]

    def check_one_operation(self, solver, initial, goal, expected, expected_op=None):
        result, bucket_count = solver(
            self.capacities, initial, goal, max_steps=1, solver_id="gecode"
        )
        self.assertIsNotNone(result.solution)
        amounts = result["amount"]
        self.assertEqual(
            [amounts[bucket][1] for bucket in range(bucket_count)],
            expected,
        )
        if expected_op is not None:
            self.assertIn(expected_op, [int(op) for op in result["op"][0]])

    def test_pour_fills_destination_completely(self):
        for solver in (proj.build_and_solve, proj_scheduling.build_and_solve):
            with self.subTest(solver=solver.__module__):
                self.check_one_operation(
                    solver, [8, 0, 0], [3, 5, 0], [3, 5, 0],
                    expected_op=3 if solver is proj_scheduling.build_and_solve else None,
                )

    def test_pour_empties_source_if_it_runs_out_first(self):
        for solver in (proj.build_and_solve, proj_scheduling.build_and_solve):
            with self.subTest(solver=solver.__module__):
                self.check_one_operation(
                    solver, [2, 0, 0], [0, 2, 0], [0, 2, 0],
                    expected_op=3 if solver is proj_scheduling.build_and_solve else None,
                )

    def test_fill_fills_bucket_completely(self):
        self.check_one_operation(
            proj_scheduling.build_and_solve,
            [8, 0, 0],
            [8, 5, 0],
            [8, 5, 0],
            expected_op=1,
        )

    def test_empty_drains_bucket_completely(self):
        self.check_one_operation(
            proj_scheduling.build_and_solve,
            [2, 5, 0],
            [0, 5, 0],
            [0, 5, 0],
            expected_op=2,
        )


if __name__ == "__main__":
    unittest.main()
