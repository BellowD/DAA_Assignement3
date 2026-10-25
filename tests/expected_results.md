# Independently derived expected results

`my_cases.jsonl` is deliberately a mixed batch: it checks that no request
leaks mutable state into the next one. Run it with the command in
`commands.txt`; the saved output is `actual_results.jsonl`.

| Line | Case | Expected fact used for checking |
|---:|---|---|
| 1 | DSU | States are `[[4,2],[3,2],[2,4],[2,4],[2,4]]`. |
| 2-3 | MSF | The minimum forest uses IDs `{1,4,5,6}`; cost is `6`, components is `1`, and exactly four non-loop edges are selected. Prim may choose a different equally valid witness only when weights tie. |
| 4 | SCC | Partition is `{0,1}`, `{2,3}`, `{4}`, `{5}`. Condensation has exactly `{A->B, B->C, C->D}`. Labels themselves are intentionally not prescribed. |
| 5 | Topological sort | It is acyclic; every vertex occurs once and each listed edge points forward. |
| 6 | DAG paths | Distances are `[0,-2,1,2,null,null]`. The valid route to 3 is `0,2,1,3`, using edge IDs `1,2,3`; 4 and 5 remain unreachable. |
| 7 | DAG cycle | The cycle outside source 0 still requires `acyclic=false`, `distance=[]`, `parent_edge=[]`. |

The Python test module additionally checks empty inputs, loops, duplicate and
parallel edges, negative/64-bit-scale weights, route reconstruction, a
100,000-vertex deep chain, and witnesses rather than relying only on one fixed
answer where the contract permits several correct answers.
