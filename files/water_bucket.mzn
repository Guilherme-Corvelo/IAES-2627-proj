% ============================================================
% CSPLib prob018 - Water Bucket Problem
% Extension: generalized from a fixed 3-bucket puzzle to an
% arbitrary number of buckets (n_buckets), with arbitrary
% capacities, initial amounts and (partial) goal amounts.
% ============================================================

int: n_buckets;                                  % number of buckets (>= 2)
array[1..n_buckets] of int: cap;                 % bucket capacities
array[1..n_buckets] of int: init;                % initial amounts
array[1..n_buckets] of int: goal;                % goal amounts, -1 = "any"
int: max_steps;                                  % search horizon

% amount[b, s] = liters in bucket b after step s (s = 0 is initial state)
array[1..n_buckets, 0..max_steps] of var 0..max(cap): amount;

% at step s, pour from bucket source[s] into bucket target[s]
array[0..max_steps-1] of var 1..n_buckets: source;
array[0..max_steps-1] of var 1..n_buckets: target;

% number of pours actually used (steps beyond this are "no-ops")
var 0..max_steps: num_steps;

% ---- domain / capacity bounds ----
constraint forall(b in 1..n_buckets)(amount[b, 0] = init[b]);
constraint forall(b in 1..n_buckets, s in 0..max_steps)(amount[b, s] <= cap[b]);

% ---- goal condition ----
constraint forall(b in 1..n_buckets)(
  goal[b] = -1 \/ amount[b, num_steps] = goal[b]
);

% symmetry breaking: once the goal is reached, freeze source/target of the
% remaining (unused) steps instead of leaving them free - otherwise the
% solver wastes huge amounts of search proving optimality over millions of
% equivalent "don't care" assignments for padding steps.
constraint forall(s in 0..max_steps-1)(
  s >= num_steps -> (source[s] = 1 /\ target[s] = min(2, n_buckets))
);

% ---- state transition for every step ----
constraint forall(s in 0..max_steps-1)(
  if s < num_steps then
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
  else
    % padding steps once the goal has been reached: no-op
    forall(b in 1..n_buckets)(amount[b, s+1] = amount[b, s])
  endif
);

% branch on the (small-domain) pour choices first - amount[] and pour are
% fully determined once source/target/num_steps are fixed, so searching
% over them directly (instead of the default variable order) is what makes
% this solvable in practice rather than timing out.
solve :: int_search(source ++ target ++ [num_steps], first_fail, indomain_min)
      minimize num_steps;

% ---- human-readable output ----
% fix() turns the already-solved decision variables into plain values so
% they can be used in par (compile-time) string conditionals below.
output
  let { int: ns = fix(num_steps) } in
  ["Solution found in \(ns) step(s)\n",
   "Buckets (\(n_buckets)): capacities = \(cap)\n",
   "Initial: \(init)\n",
   "Goal:    \(goal)  (-1 = any)\n\n",
   "Step-by-step solution:\n",
   "Step 0: \([amount[b,0] | b in 1..n_buckets]) (initial)\n"]
  ++
  [ "Step \(s): \([amount[b,s] | b in 1..n_buckets]) (pour bucket \(source[s-1]) -> bucket \(target[s-1]))\n"
  | s in 1..ns ];
