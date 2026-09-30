% Parallel water-bucket scheduling model.
% Each active operation transfers one unit per time tick.

int: n_buckets;
array[1..n_buckets] of int: cap;
array[1..n_buckets] of int: init;
array[1..n_buckets] of int: goal;
int: max_steps;

int: max_parallel = n_buckets;
array[1..n_buckets, 0..max_steps] of var 0..max(cap): amount;
array[0..max_steps-1, 1..max_parallel] of var 0..3: op;
array[0..max_steps-1, 1..max_parallel] of var 1..n_buckets: source;
array[0..max_steps-1, 1..max_parallel] of var 1..n_buckets: target;
var 0..max_steps: makespan;
var 0..max_steps * max_parallel: operation_count;

constraint forall(b in 1..n_buckets)(amount[b, 0] = init[b]);
constraint forall(b in 1..n_buckets, t in 0..max_steps)(amount[b, t] <= cap[b]);
constraint forall(b in 1..n_buckets)(goal[b] = -1 \/ amount[b, makespan] = goal[b]);

constraint operation_count = sum(t in 0..max_steps-1, k in 1..max_parallel)(
  if op[t, k] > 0 then 1 else 0 endif
);
constraint forall(t in 0..max_steps-1)(
  t < makespan -> exists(k in 1..max_parallel)(op[t, k] > 0)
);
constraint forall(t in 0..max_steps-1, k in 1..max_parallel)(
  t >= makespan -> op[t, k] = 0
);
constraint forall(t in 0..max_steps-1, k in 1..max_parallel)(
  op[t, k] = 0 -> source[t, k] = 1 /\ target[t, k] = 1
);
constraint forall(t in 0..max_steps-1, k in 1..max_parallel)(
  (op[t, k] = 1 \/ op[t, k] = 2) -> source[t, k] = target[t, k]
);
constraint forall(t in 0..max_steps-1, k in 1..max_parallel)(
  op[t, k] = 3 -> source[t, k] != target[t, k]
);

constraint forall(t in 0..max_steps-1)(
  sum(k in 1..max_parallel)(if op[t, k] = 1 then 1 else 0 endif) <= 1 /\
  sum(k in 1..max_parallel)(if op[t, k] = 2 then 1 else 0 endif) <= 1 /\
  sum(k in 1..max_parallel)(if op[t, k] = 3 then 1 else 0 endif) <= 1
);

constraint forall(t in 0..max_steps-1, k1, k2 in 1..max_parallel where k1 < k2)(
  forall(b in 1..n_buckets)(
    not (op[t, k1] > 0 /\ (source[t, k1] = b \/ target[t, k1] = b) /\
         op[t, k2] > 0 /\ (source[t, k2] = b \/ target[t, k2] = b))
  )
);

constraint forall(t in 0..max_steps-1, k in 1..max_parallel)(
  op[t, k] = 1 -> amount[target[t, k], t] < cap[target[t, k]]
);
constraint forall(t in 0..max_steps-1, k in 1..max_parallel)(
  op[t, k] = 2 -> amount[source[t, k], t] > 0
);
constraint forall(t in 0..max_steps-1, k in 1..max_parallel)(
  op[t, k] = 3 -> amount[source[t, k], t] > 0 /\ amount[target[t, k], t] < cap[target[t, k]]
);

constraint forall(t in 0..max_steps-1, b in 1..n_buckets)(
  amount[b, t + 1] = amount[b, t]
    + sum(k in 1..max_parallel)(if op[t, k] = 1 /\ target[t, k] = b then 1 else 0 endif)
    - sum(k in 1..max_parallel)(if op[t, k] = 2 /\ source[t, k] = b then 1 else 0 endif)
    + sum(k in 1..max_parallel)(if op[t, k] = 3 /\ target[t, k] = b then 1 else 0 endif)
    - sum(k in 1..max_parallel)(if op[t, k] = 3 /\ source[t, k] = b then 1 else 0 endif)
);

solve :: int_search(array1d(op) ++ array1d(source) ++ array1d(target), first_fail, indomain_min)
  minimize makespan;
