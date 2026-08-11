##Stable Marriages
A python script that implements the [Gale-Shapley](https://en.wikipedia.org/wiki/Stable_marriage_problem) Algorithm in order to find a stable matching for any given input. According to the given arguments while running the script, it finds the matching for "men" or "women".
Input files should be given in JSON type with the following format:
```
{
  "men_rankings": {
    "abe": ["cat", "bea", "ada"],
    "bob": ["ada", "cat", "bea"],
    "cal": ["ada", "bea", "cat"]
  },

  "women_rankings": {
    "ada": ["abe", "cal", "bob"],
    "bea": ["bob", "abe", "cal"],
    "cat": ["cal", "abe", "bob"]
  }
}
```
Output is given in JSON type files with the following format:
```
{"abe": "cat", "bob": "bea", "cal": "ada"}
```

##Gale-Shapley Algorithm
```
function stableMatching {
    Initialize all m ∈ M and w ∈ W to free
    while ∃ free man m who still has a woman w to propose to {
       w = highest ranked woman to whom m has not yet proposed
       if w is free
         (m, w) become engaged
       else some pair (m', w) already exists
         if w prefers m to m'
           (m, w) become engaged
           m' becomes free
         else
           (m', w) remain engaged
    }
}
```