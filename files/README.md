# Water Bucket Problem

The models solve water bucket puzzles with two or more buckets. An instance
specifies capacities, initial amounts and goal amounts. A goal value of `-1`
means that any final amount is acceptable.

Each action follows the usual bucket rules:

- **POUR** transfers water until the source is empty or the destination is
  full.
- **FILL** fills the selected bucket.
- **EMPTY** empties the selected bucket.

The sequential model supports pours. The scheduling model also supports
filling and emptying, and minimizes the number of time units. In one time unit,
it can run independent actions on buckets that do not overlap.

## Files

- `proj.py` and `water_bucket.mzn` implement the sequential-pour solver.
- `proj_scheduling.py` and `water_bucket_scheduling.mzn` implement the
  scheduling solver.
- `visualize_schedule.py` displays schedules from `proj_scheduling.py`.
- `instances/classic_8_5_3.json` is the classic puzzle.
- `instances/four_bucket_ext.json` is the four-bucket example.
- `tests/test_pour_semantics.py` checks fill, empty and pour behavior.

## Requirements and commands

Install MiniZinc with Gecode and the Python binding:

```bash
python3 -m pip install -r files/requirements.txt
```

Run these from the repository root:

```bash
python3 files/proj.py --file files/instances/classic_8_5_3.json
python3 files/proj_scheduling.py --file files/instances/classic_8_5_3.json
python3 files/visualize_schedule.py --file files/instances/classic_8_5_3.json
python3 -m unittest discover -s files/tests -v
```

For the classic 8-5-3 puzzle, the first pour takes `[8, 0, 0]` to
`[3, 5, 0]`. The full solution for goal `[4, 4, -1]` takes seven pours:

```text
[8, 0, 0] -> [3, 5, 0] -> [3, 2, 3] -> [6, 2, 0] ->
[6, 0, 2] -> [1, 5, 2] -> [1, 4, 3] -> [4, 4, 0]
```
