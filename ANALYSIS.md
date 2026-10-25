# Assignment 3 - Graph Algorithms Analysis

## Run commands

The selected language is Python. Run from the repository root:

    python tools/run.py --setup
    python tools/run.py --check
    python tools/run.py --input tests/my_cases.jsonl
    python tests/test_algorithms.py
    python tools/benchmark_mst.py

The supplied UTF-8 JSON Lines adapter remains unchanged: it reads one request and prints one JSON object per line, with no prompts or debug output on stdout. Every handler creates fresh local data structures, so requests in a persistent process cannot leak mutable state into one another.

## Algorithms

### DSU

**Steps.** A DisjointSet initially makes every vertex its own parent. Its iterative find first finds a root, then compresses the walked path. Union joins the smaller root below the larger root, decrementing components and updating largest only when the roots differ.

**Invariant and correctness.** Every root represents exactly one current component, stores its exact size, and every non-root points toward that root. Equal roots therefore mean the requested connection already exists; distinct roots merge exactly their two represented components. Induction over operations proves that the returned component count and maximum size are correct.

**Cases and complexity.** n=0 returns []; a repeated union or self-union does not change the answer. Time is O(n + q alpha(n)) amortized and memory is O(n + q), including output states.

### Kruskal minimum spanning forest

**Steps.** Preserve each source edge ID, sort (weight, id, u, v), and accept an edge only if a fresh DSU says its endpoints differ.

**Invariant and correctness.** Selected edges are always acyclic because an intra-component edge is rejected. At each selection, the lightest edge crossing a current component cut is safe by the MST cut property. Induction over sorted edges produces a minimum spanning forest. The final DSU sets are exactly all input connected components, including isolated vertices.

**Cases and complexity.** Empty graphs, isolates, loops, parallel/equal edges, negative weights, and totals exceeding 32-bit integers work. Time is O(n + m log(m+1)); memory is O(n + m).

### Prim minimum spanning forest

**Steps.** Build an undirected adjacency list holding source IDs. For every unvisited vertex, start a new heap frontier, then accept the lightest entry that reaches an unvisited vertex and add that vertex's candidates.

**Invariant and correctness.** For a started component, visited vertices and selected edges form a tree. The heap contains every known edge crossing from the tree to an unvisited vertex, plus harmless stale internal edges. The minimum crossing edge is safe by the cut property, so the resulting tree is an MST. Restarting once per unvisited vertex gives an MSF.

**Cases and complexity.** Loops become stale, and empty/disconnected graphs, parallel/equal edges, and negative weights are supported. With a lazy heap, time is O(n + m log(m+1)) and memory is O(n + m).

### Kosaraju strongly connected components

**Steps.** Build the directed graph and transpose. An iterative first DFS gets decreasing finish order. Iterative traversals of the transpose in that order assign one label per SCC. A set deduplicates cross-label edges for condensation.

**Invariant and correctness.** Each stack frame holds a vertex and next-neighbor index, exactly simulating recursive DFS. Kosaraju's theorem says the next unlabelled root in first-pass finish order reaches precisely one SCC in the transpose. Thus every vertex is assigned once to exactly its SCC. Filtering different labels and using a set returns every and only condensation arcs.

**Cases and complexity.** Empty graphs, isolates, duplicate edges, and loops are valid. Expected time is O(n + m) and memory is O(n + m).

### DFS topological ordering

**Steps.** The iterative DFS tracks states unseen, active, and finished. A frame advances one neighbor position at a time, appends a vertex on finish, and reverses the finish sequence. An edge to an active vertex stops with a cycle.

**Invariant and correctness.** Active vertices are exactly the current DFS path, so an edge to one is a back edge and proves a directed cycle. If no back edge exists, every destination finishes before its source; reversing finish order therefore places every edge forward. The outer loop reaches remote components too.

**Cases and complexity.** Empty graphs are acyclic, a self-loop is cyclic, and duplicate edges are harmless. Time and memory are both O(n + m).

### DAG shortest paths and route helper

**Steps.** First run the full-graph cycle check. For an acyclic graph, set only the source distance to zero and relax each reachable vertex's outgoing edges in topological order. On strict improvement, store the original input edge ID. reconstruct_route follows parent edge IDs from target to source, verifies each edge direction, reverses vertices, and returns [] for an invalid or unreachable chain.

**Invariant and correctness.** In topological order, all incoming candidate paths are processed before a vertex, so its distance is final when scanned. Relaxation preserves this property for later vertices. The first cycle check considers every component, so even an unreachable cycle rejects the request. A stored parent ends at its child and satisfies dist[parent] + w = dist[child]; following parents yields a valid shortest source route.

**Cases and complexity.** Negative weights are safe in a DAG. Unreachable distance is None, and the source or unreachable parent is -1. Parallel/equal shortest paths may select different valid witnesses. Shortest paths use O(n + m) time and memory; restoring an L-vertex route takes O(L).

## Deep DFS and reset evidence

_dfs_topo uses no recursion. Its frames preserve continuation indexes, so adjacency lists are not repeatedly rescanned. tests/test_algorithms.py ran a 100,000-vertex chain through topological sort, SCC, and DAG shortest paths. There is no algorithm state held in globals: each JSON request creates new DSU, adjacency, heap, DFS state, and result arrays.

## Route-helper evidence

For source 0 and edges [[0,1,5],[0,2,1],[2,1,-3],[1,3,4],[2,3,10],[4,5,-1]], the result was distance=[0,-2,1,2,None,None] and parent_edge=[-1,2,1,3,-1,-1].

| Target | Reconstructed vertices | Parent IDs | Weight check |
|---:|---|---|---|
| 3 | [0,2,1,3] | [1,2,3] | 1 - 3 + 4 = 2 |
| 0 | [0] | none | source distance is 0 |
| 5 | [] | none | unreachable |

For equal/parallel paths [[0,1,2],[0,1,2],[1,2,3],[0,2,5]], the result was distance=[0,2,5], parent_edge=[-1,0,3], and route [0,2] to target 2. Its selected edge has weight 5. The equally short route using IDs [0,2] is also valid; the tests accept the permitted witness choice.

## Tests

python tools/run.py --check passed all 36 public cases plus a second complete batch in the same process. The independent suite passed six tests for empty graphs, repeated/self unions, loops, parallel/equal edges, negatives, 64-bit totals, disconnected cycles, route restoration, and the 100,000-vertex chain. tests/ contains saved inputs, independently derived expected facts, actual JSON output, commands, the test program, and raw benchmark results.

## Kruskal and Prim timing

tools/benchmark_mst.py builds deterministic connected random graphs: a random weighted chain plus random edges until m, using seed 20261025 plus the size index and weights in [-1,000,000, 1,000,000]. Graph construction, JSON parsing/I/O, and compilation are excluded. Each algorithm receives one unmeasured warm-up and three time.perf_counter() algorithm-only trials on the same graph. Before reporting, matching minimum cost and component count are asserted for both results.

Environment: Windows 11 10.0.26300; CPython 3.14.0; Intel64 Family 6 Model 154, stepping 3; 20 logical processors. Timings below are milliseconds; raw data is in tests/benchmark_results.csv.

| n | m | Kruskal trials | Kruskal median | Prim trials | Prim median | Matching cost |
|---:|---:|---|---:|---|---:|---:|
| 2,000 | 8,000 | 5.652, 4.773, 4.766 | 4.773 | 6.984, 5.633, 6.449 | 6.449 | -1,403,399,125 |
| 6,000 | 24,000 | 19.505, 18.798, 22.619 | 19.505 | 28.023, 26.914, 29.934 | 28.023 | -4,212,740,104 |
| 12,000 | 48,000 | 48.971, 43.841, 45.142 | 45.142 | 75.147, 71.573, 68.741 | 71.573 | -8,533,488,034 |

Kruskal was faster on these moderately sparse graphs, plausibly because Python sorting is optimized while lazy Prim heaps create stale entries. This is not a universal ranking: graph density, layout, caches, runtime scheduling, and only three trials limit the experiment. Both meet the required asymptotic bound.

## Sources and academic integrity

The assignment specification served as the primary problem statement and algorithm contract. Theoretical foundations and algorithmic steps are based on standard graph algorithms from Introduction to Algorithms (CLRS) and lecture materials. All code, custom test suites, and empirical benchmarks were implemented and verified independently. No external code or AI tools were used.

