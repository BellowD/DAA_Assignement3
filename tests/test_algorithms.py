"""Independent tests for Assignment 3; uses only the Python standard library."""

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "Python"))
import algorithms  # noqa: E402


class AlgorithmTests(unittest.TestCase):
    def assert_forest(self, request, answer, expected_cost, expected_components):
        self.assertEqual(answer["cost"], expected_cost)
        self.assertEqual(answer["components"], expected_components)
        self.assertEqual(len(answer["edge_ids"]), request["n"] - expected_components)
        self.assertEqual(len(set(answer["edge_ids"])), len(answer["edge_ids"]))
        parent = list(range(request["n"]))
        def find(v):
            while parent[v] != v:
                parent[v] = parent[parent[v]]
                v = parent[v]
            return v
        cost = 0
        for edge_id in answer["edge_ids"]:
            left, right, weight = request["edges"][edge_id]
            a, b = find(left), find(right)
            self.assertNotEqual(a, b)
            parent[b] = a
            cost += weight
        self.assertEqual(cost, expected_cost)

    def test_dsu_empty_repeat_and_large_component(self):
        self.assertEqual(algorithms.dsu({"n": 0, "operations": []}), {"states": []})
        answer = algorithms.dsu({"n": 4, "operations": [[0, 1], [0, 1], [2, 2], [1, 2]]})
        self.assertEqual(answer["states"], [[3, 2], [3, 2], [3, 2], [2, 3]])

    def test_mst_negative_parallel_loops_and_64_bit_sum(self):
        request = {"n": 5, "edges": [[0, 1, 4], [1, 2, -2], [0, 2, 1],
                                        [3, 3, -9], [2, 3, 7], [3, 4, 0], [0, 1, 1]]}
        self.assert_forest(request, algorithms.kruskal(request), 6, 1)
        self.assert_forest(request, algorithms.prim(request), 6, 1)
        heavy = {"n": 3, "edges": [[0, 1, 2_000_000_000], [1, 2, 2_000_000_000]]}
        self.assertEqual(algorithms.kruskal(heavy)["cost"], 4_000_000_000)
        self.assertEqual(algorithms.prim(heavy)["cost"], 4_000_000_000)

    def test_scc_partition_and_condensation(self):
        request = {"n": 6, "edges": [[0, 1], [1, 0], [1, 2], [2, 3], [3, 2],
                                        [3, 4], [4, 5], [4, 5], [5, 5]]}
        answer = algorithms.scc(request)
        labels = answer["component"]
        self.assertEqual(labels[0], labels[1])
        self.assertEqual(labels[2], labels[3])
        self.assertEqual(len({labels[0], labels[2], labels[4], labels[5]}), 4)
        self.assertEqual({tuple(pair) for pair in answer["condensation"]},
                         {(labels[1], labels[2]), (labels[3], labels[4]), (labels[4], labels[5])})

    def test_topo_and_all_component_cycle_detection(self):
        dag = {"n": 5, "edges": [[0, 2], [1, 2], [2, 3], [1, 4], [1, 4]]}
        order = algorithms.topo(dag)
        self.assertTrue(order["acyclic"])
        position = {vertex: index for index, vertex in enumerate(order["order"])}
        self.assertEqual(set(position), set(range(5)))
        self.assertTrue(all(position[a] < position[b] for a, b in dag["edges"]))
        self.assertEqual(algorithms.topo({"n": 5, "edges": [[0, 1], [3, 4], [4, 3]]}),
                         {"acyclic": False, "order": []})

    def test_dag_paths_cycles_and_route_helper(self):
        request = {"n": 6, "source": 0,
                   "edges": [[0, 1, 5], [0, 2, 1], [2, 1, -3], [1, 3, 4],
                             [2, 3, 10], [4, 5, -1]]}
        answer = algorithms.dag(request)
        self.assertEqual(answer["distance"], [0, -2, 1, 2, None, None])
        self.assertEqual(algorithms.reconstruct_route(answer["parent_edge"], request["edges"], 0, 3),
                         [0, 2, 1, 3])
        self.assertEqual(algorithms.reconstruct_route(answer["parent_edge"], request["edges"], 0, 0), [0])
        self.assertEqual(algorithms.reconstruct_route(answer["parent_edge"], request["edges"], 0, 5), [])
        equal = {"n": 3, "source": 0,
                 "edges": [[0, 1, 2], [0, 1, 2], [1, 2, 3], [0, 2, 5]]}
        equal_answer = algorithms.dag(equal)
        self.assertEqual(equal_answer["distance"], [0, 2, 5])
        self.assertEqual(algorithms.reconstruct_route(equal_answer["parent_edge"], equal["edges"], 0, 2),
                         [0, 2])
        self.assertEqual(equal_answer["parent_edge"][2], 3)
        cycle = {"n": 5, "source": 0, "edges": [[0, 1, 1], [3, 4, 1], [4, 3, -2]]}
        self.assertEqual(algorithms.dag(cycle), {"acyclic": False, "distance": [], "parent_edge": []})

    def test_100k_deep_chain_without_recursion(self):
        n = 100_000
        directed = [[i, i + 1] for i in range(n - 1)]
        weighted = [[i, i + 1, 1] for i in range(n - 1)]
        dsu_result = algorithms.dsu({"n": n, "operations": directed})
        self.assertEqual(dsu_result["states"][-1], [1, n])
        self.assertEqual(algorithms.kruskal({"n": n, "edges": weighted})["cost"], n - 1)
        self.assertEqual(algorithms.prim({"n": n, "edges": weighted})["cost"], n - 1)
        self.assertTrue(algorithms.topo({"n": n, "edges": directed})["acyclic"])
        self.assertEqual(len(set(algorithms.scc({"n": n, "edges": directed})["component"])), n)
        result = algorithms.dag({"n": n, "source": 0, "edges": weighted})
        self.assertEqual(result["distance"][-1], n - 1)
        self.assertEqual(result["parent_edge"][-1], n - 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
