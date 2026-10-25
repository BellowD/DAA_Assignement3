"""Reproducible algorithm-only benchmark for Prim and Kruskal."""

import pathlib
import random
import statistics
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "Python"))
import algorithms  # noqa: E402


SEED = 20261025
SIZES = ((2_000, 8_000), (6_000, 24_000), (12_000, 48_000))
TRIALS = 3


def make_graph(n, m, seed):
    rng = random.Random(seed)
    edges = [[vertex, vertex + 1, rng.randint(-1_000_000, 1_000_000)]
             for vertex in range(n - 1)]
    while len(edges) < m:
        left = rng.randrange(n)
        right = rng.randrange(n)
        edges.append([left, right, rng.randint(-1_000_000, 1_000_000)])
    return {"n": n, "edges": edges}


def measure(function, request):
    values = []
    for _ in range(TRIALS):
        start = time.perf_counter()
        answer = function(request)
        values.append((time.perf_counter() - start) * 1_000)
    return values, answer


def main():
    print("seed,n,m,algorithm,trial_ms,median_ms,cost,components")
    for index, (n, m) in enumerate(SIZES):
        request = make_graph(n, m, SEED + index)
        # One unmeasured warm-up per algorithm; graph construction is excluded.
        algorithms.kruskal(request)
        algorithms.prim(request)
        k_values, kruskal = measure(algorithms.kruskal, request)
        p_values, prim = measure(algorithms.prim, request)
        if (kruskal["cost"], kruskal["components"]) != (prim["cost"], prim["components"]):
            raise AssertionError("MST implementations disagree")
        for name, values, result in (("kruskal", k_values, kruskal), ("prim", p_values, prim)):
            median = statistics.median(values)
            for value in values:
                print(f"{SEED + index},{n},{m},{name},{value:.3f},{median:.3f},{result['cost']},{result['components']}")


if __name__ == "__main__":
    main()
