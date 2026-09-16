% Water Bucket Problem - MiniZinc Model
% Solves the general 3-bucket water pouring problem
% Finds the sequence of pours to reach a goal state

include "globals.mzn";

% Problem parameters (to be set by user)
int: cap_a;           % Capacity of bucket A
int: cap_b;           % Capacity of bucket B
int: cap_c;           % Capacity of bucket C

int: init_a;          % Initial amount in bucket A
int: init_b;          % Initial amount in bucket B
int: init_c;          % Initial amount in bucket C

int: goal_a;          % Goal amount in bucket A (-1 means any)
int: goal_b;          % Goal amount in bucket B (-1 means any)
int: goal_c;          % Goal amount in bucket C (-1 means any)

int: max_steps = 20;  % Maximum number of steps to search

% Decision variables
% State at each step: amount of water in each bucket
array[0..max_steps] of var 0..cap_a: amount_a;
array[0..max_steps] of var 0..cap_b: amount_b;
array[0..max_steps] of var 0..cap_c: amount_c;

% Action at each step: which bucket pours into which
% 0 = no action, 1 = A->B, 2 = A->C, 3 = B->A, 4 = B->C, 5 = C->A, 6 = C->B
array[0..max_steps-1] of var 0..6: action;

% Number of steps actually taken (to minimize)
var 0..max_steps: num_steps;

% Constraints

% Initial state
constraint amount_a[0] = init_a;
constraint amount_b[0] = init_b;
constraint amount_c[0] = init_c;

% Goal state (at step num_steps)
constraint (goal_a = -1) \/ (amount_a[num_steps] = goal_a);
constraint (goal_b = -1) \/ (amount_b[num_steps] = goal_b);
constraint (goal_c = -1) \/ (amount_c[num_steps] = goal_c);

% State transitions based on actions
forall(step in 0..max_steps-1) (
  if step < num_steps then
    % Action must be taken
    action[step] > 0 /\
    
    % A -> B: pour from A to B
    (action[step] = 1 -> (
      let {
        int: pour_amount = min(amount_a[step], cap_b - amount_b[step])
      } in (
        amount_a[step+1] = amount_a[step] - pour_amount /\
        amount_b[step+1] = amount_b[step] + pour_amount /\
        amount_c[step+1] = amount_c[step]
      )
    )) /\
    
    % A -> C: pour from A to C
    (action[step] = 2 -> (
      let {
        int: pour_amount = min(amount_a[step], cap_c - amount_c[step])
      } in (
        amount_a[step+1] = amount_a[step] - pour_amount /\
        amount_b[step+1] = amount_b[step] /\
        amount_c[step+1] = amount_c[step] + pour_amount
      )
    )) /\
    
    % B -> A: pour from B to A
    (action[step] = 3 -> (
      let {
        int: pour_amount = min(amount_b[step], cap_a - amount_a[step])
      } in (
        amount_a[step+1] = amount_a[step] + pour_amount /\
        amount_b[step+1] = amount_b[step] - pour_amount /\
        amount_c[step+1] = amount_c[step]
      )
    )) /\
    
    % B -> C: pour from B to C
    (action[step] = 4 -> (
      let {
        int: pour_amount = min(amount_b[step], cap_c - amount_c[step])
      } in (
        amount_a[step+1] = amount_a[step] /\
        amount_b[step+1] = amount_b[step] - pour_amount /\
        amount_c[step+1] = amount_c[step] + pour_amount
      )
    )) /\
    
    % C -> A: pour from C to A
    (action[step] = 5 -> (
      let {
        int: pour_amount = min(amount_c[step], cap_a - amount_a[step])
      } in (
        amount_a[step+1] = amount_a[step] + pour_amount /\
        amount_b[step+1] = amount_b[step] /\
        amount_c[step+1] = amount_c[step] - pour_amount
      )
    )) /\
    
    % C -> B: pour from C to B
    (action[step] = 6 -> (
      let {
        int: pour_amount = min(amount_c[step], cap_b - amount_b[step])
      } in (
        amount_a[step+1] = amount_a[step] /\
        amount_b[step+1] = amount_b[step] + pour_amount /\
        amount_c[step+1] = amount_c[step] - pour_amount
      )
    ))
  else
    % No action after goal is reached
    action[step] = 0 /\
    amount_a[step+1] = amount_a[step] /\
    amount_b[step+1] = amount_b[step] /\
    amount_c[step+1] = amount_c[step]
  endif
);

% Minimize the number of steps
solve minimize num_steps;

% Output
output [
  "Solution found in ", show(num_steps), " steps\n",
  "Capacities: A=", show(cap_a), "L, B=", show(cap_b), "L, C=", show(cap_c), "L\n",
  "Initial: A=", show(init_a), "L, B=", show(init_b), "L, C=", show(init_c), "L\n",
  "Goal: A=", if goal_a = -1 then "any" else show(goal_a) endif, "L, B=",
    if goal_b = -1 then "any" else show(goal_b) endif, "L, C=",
    if goal_c = -1 then "any" else show(goal_c) endif, "L\n",
  "\nStep-by-step solution:\n"
] ++
[
  if step = 0 then
    "Step 0: A=" ++ show(amount_a[0]) ++ "L, B=" ++ show(amount_b[0]) ++ "L, C=" ++ show(amount_c[0]) ++ "L (initial)\n"
  else if step <= num_steps then
    let {
      string: action_str = 
        if action[step-1] = 1 then "A -> B"
        elseif action[step-1] = 2 then "A -> C"
        elseif action[step-1] = 3 then "B -> A"
        elseif action[step-1] = 4 then "B -> C"
        elseif action[step-1] = 5 then "C -> A"
        elseif action[step-1] = 6 then "C -> B"
        else "none"
        endif
    } in
    "Step " ++ show(step) ++ ": A=" ++ show(amount_a[step]) ++ "L, B=" ++ show(amount_b[step]) ++ "L, C=" ++ show(amount_c[step]) ++ "L (pour " ++ action_str ++ ")\n"
  else "" endif endif
  | step in 0..max_steps
]
