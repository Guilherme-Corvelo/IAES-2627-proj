% ============================================================
% CSPLib prob018 - Water Bucket Problem
% Extension: Scheduling/Planning perspective
% ============================================================
% This model extends the base water bucket problem by treating
% each time step as an explicit operation: FILL, EMPTY, or POUR.
% This allows optimization of makespan and number of operations
% as a scheduling/planning problem.
%
% Operations:
%   - FILL(b):   fill bucket b to capacity
%   - EMPTY(b):  empty bucket b
%   - POUR(i,j): pour from bucket i into bucket j
% ============================================================

int: n_buckets;                                  % number of buckets (>= 2)
array[1..n_buckets] of int: cap;                 % bucket capacities
array[1..n_buckets] of int: init;                % initial amounts
array[1..n_buckets] of int: goal;                % goal amounts, -1 = "any"
int: max_steps;                                  % search horizon

% Operation types: 1=FILL, 2=EMPTY, 3=POUR
% amount[b, s] = liters in bucket b after step s (s = 0 is initial state)
array[1..n_buckets, 0..max_steps] of var 0..max(cap): amount;

% operation at step s
array[0..max_steps-1] of var 1..3: op;

% source and target buckets for each step
array[0..max_steps-1] of var 1..n_buckets: source;
array[0..max_steps-1] of var 1..n_buckets: target;

% makespan: the actual number of meaningful steps (not padding)
var 0..max_steps: makespan;

% ---- domain / capacity bounds ----
constraint forall(b in 1..n_buckets)(amount[b, 0] = init[b]);
constraint forall(b in 1..n_buckets, s in 0..max_steps)(amount[b, s] <= cap[b]);

% ---- goal condition ----
constraint forall(b in 1..n_buckets)(
  goal[b] = -1 \/ amount[b, makespan] = goal[b]
);

% ---- symmetry breaking ----
% Once the goal is reached, freeze remaining steps to FILL bucket 1
constraint forall(s in 0..max_steps-1)(
  s >= makespan -> (
    op[s] = 1 /\ source[s] = 1 /\ target[s] = 1
  )
);

% ---- state transition for every step ----
constraint forall(s in 0..max_steps-1)(
  if s < makespan then
    % Meaningful step: one of the three operations must execute
    (
      % FILL: fill target bucket to capacity
      op[s] = 1 ->
        source[s] = target[s] /\
        amount[target[s], s+1] = cap[target[s]] /\
        forall(b in 1..n_buckets where b != target[s])(
          amount[b, s+1] = amount[b, s]
        )
    )
    \/ 
    (
      % EMPTY: empty source bucket
      op[s] = 2 ->
        source[s] = target[s] /\
        amount[source[s], s+1] = 0 /\
        forall(b in 1..n_buckets where b != source[s])(
          amount[b, s+1] = amount[b, s]
        )
    )
    \/
    (
      % POUR: pour from source to target
      op[s] = 3 ->
        source[s] != target[s] /\
        let {
          var 0..max(cap): pour = min(amount[source[s], s], cap[target[s]] - amount[target[s], s])
        } in (
          forall(b in 1..n_buckets)(
            amount[b, s+1] =
              amount[b, s]
              + (if b = target[s] then pour else 0 endif)
              - (if b = source[s] then pour else 0 endif)
          )
        )
    )
  else
    % Padding step (after goal reached): FILL op, no state change
    op[s] = 1 /\ source[s] = 1 /\ target[s] = 1 /\
    forall(b in 1..n_buckets)(amount[b, s+1] = amount[b, s])
  endif
);

% Branch on operation decisions first, then source/target
solve :: int_search(op ++ source ++ target ++ [makespan], first_fail, indomain_min)
      minimize makespan;

% ---- human-readable output ----
output
  let { int: ms = fix(makespan) } in
  ["Solution found in \(ms) operation(s)\n",
   "Buckets (\(n_buckets)): capacities = \(cap)\n",
   "Initial: \(init)\n",
   "Goal:    \(goal)  (-1 = any)\n\n",
   "Step-by-step solution:\n",
   "Step 0: \([amount[b,0] | b in 1..n_buckets]) (initial)\n"]
  ++
  [ "Step \(s): \([amount[b,s] | b in 1..n_buckets]) (op=\(op[s-1]), src=\(source[s-1]), tgt=\(target[s-1]))\n"
  | s in 1..ms ];
