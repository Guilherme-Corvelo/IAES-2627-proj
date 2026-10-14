# Water Bucket Problem

This project solves water bucket puzzles with MiniZinc and Python. An instance
defines the bucket capacities, starting amounts and goal amounts. Use `-1` in
the goal to leave a bucket unconstrained.

A pour transfers as much water as it can: it stops when the source is empty or
the destination is full. In the scheduling model, FILL fills a bucket to
capacity and EMPTY drains it completely. These are whole actions, not
one-litre steps.

## Programs

- `files/proj.py` solves a sequence of pours with `files/water_bucket.mzn`.
- `files/proj_scheduling.py` schedules FILL, EMPTY and POUR operations with
  `files/water_bucket_scheduling.mzn`.
- `files/visualize_schedule.py` animates solutions from
  `proj_scheduling.py`.
- `files/instances/` contains the classic 8-5-3 puzzle and a four-bucket
  example.

## Run

Install MiniZinc with Gecode, then install the Python binding:

```bash
python3 -m pip install -r files/requirements.txt
```

From the repository root:

```bash
python3 files/proj.py --file files/instances/classic_8_5_3.json
python3 files/proj_scheduling.py --file files/instances/classic_8_5_3.json
python3 files/visualize_schedule.py --file files/instances/classic_8_5_3.json
python3 -m unittest discover -s files/tests -v
```

For the classic puzzle, the first pour is `[8, 0, 0] -> [3, 5, 0]`: the
5-litre bucket fills, leaving 3 litres in the first bucket. The goal
`[4, 4, -1]` is reached in seven pours:

```text
[8, 0, 0] -> [3, 5, 0] -> [3, 2, 3] -> [6, 2, 0] ->
[6, 0, 2] -> [1, 5, 2] -> [1, 4, 3] -> [4, 4, 0]
```

The visualizer opens a local browser page. Use its Stop server button or press
Ctrl+C in the terminal when finished.
