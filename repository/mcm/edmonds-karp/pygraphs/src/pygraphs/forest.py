# Copyright (c) 2019 Gabriel B. Sant'Anna <baiocchi.gabriel@gmail.com>
# @License Apache <https://gitlab.com/baioc/pygraphs>

from .libpygraphs import Digraph, Graph, PriorityQueue
from .common import Node, arbitrary
from typing import Set, Tuple, Dict, Optional, Sequence, Union, Iterable, List
from math import inf
from collections import deque


# @TODO: min_forest with Kruskall <- data structure for Disjoint Sets
def min_tree(graph: Graph, root: Node = None) -> Set[Tuple[Node, Node, float]]:
    """Find the minimum spanning tree of an undirected graph through Prim.
    Returns a set containing every edge in the MSP.  O((V+E)*lg(V))"""

    root = arbitrary(graph.nodes()) if root is None else root
    ancestors: Dict[Node, Optional[Node]] = {}
    queue = PriorityQueue()
    for v in graph.nodes():
        ancestors[v] = None
        queue.enqueue(v, inf if v != root else 0)

    while not queue.empty():
        u = queue.dequeue()
        for v in graph.neighbours(u):
            w = graph.weight(u, v)
            if queue.contains(v) and w < queue.priority(v):
                ancestors[v] = u
                queue.update(v, w)

    forest: Set[Tuple[Node, Node, float]] = set()
    for (v, u) in ancestors.items():
        if u is not None:
            forest.add((u, v, graph.weight(u, v)))

    return forest


def toposort(graph: Digraph) -> Sequence[Node]:
    """Topologically sort a directed graph's vertices using Tarjan's DFS.
    Returns a sequence containing the result of the partial ordering. O(V+E)"""

    visited: Set[Node] = set()
    order = deque()

    def dfs_ord(u: Node):
        if u not in visited:
            visited.add(u)

            for v in graph.neighbours(u):
                dfs_ord(v)

            order.appendleft(u)

    for u in graph.nodes():
        dfs_ord(u)

    return order


def components(graph: Union[Digraph, Graph]) -> Iterable[Set[Node]]:
    """Find a graph's strongly connected components via Kosaraju's algorithm.
    Returns an iterable containing each partition. O(V+E)"""

    visited: Set[Node] = set()
    stack: List[Node] = []
    connections: Dict[Node, Set[Node]] = {v: set() for v in graph.nodes()}
    components: Dict[Node, Set[Node]] = {}

    def dfs_visit(u: Node):
        if u not in visited:
            visited.add(u)

            for v in graph.neighbours(u):
                connections[v].add(u)
                dfs_visit(v)

            stack.append(u)

    def component_assign(u: Node, root: Node):
        if u in connections.keys():
            if root not in components:
                components[root] = set()

            components[root].add(u)

            in_neighbours = connections[u]
            connections.pop(u)

            for v in in_neighbours:
                component_assign(v, root)

    for u in graph.nodes():
        dfs_visit(u)

    while stack:
        u = stack.pop()
        component_assign(u, u)

    return components.values()


def _test_forest():
    V: Set[Node] = {'a', 'b', 'c', 'd', 'e'}
    E: Set[Tuple[Node, Node, float]] = {('a', 'b', 3), ('c', 'a', 2),
                                        ('c', 'd', 1), ('c', 'e', 3),
                                        ('d', 'e', 2), ('b', 'd', 4)}
    G: Graph = Graph(len(V))
    for (u, v, w) in E:
        G.link(u, v, w)

    A = min_tree(G, 'a')
    print(A)


def _test_sort():
    V: Set[Node] = {'5', '7', '3', '11', '8', '2', '9', '10'}
    E: Set[Tuple[Node, Node]] = {('5','11'), ('7','11'), ('7','8'), ('3','8'),
                                 ('3','10'), ('11','2'), ('11','9'), ('8','9'),
                                 ('11','10')}
    G: Digraph = Digraph(len(V))
    for (u, v) in E:
        G.link(u, v)

    tord = toposort(G)
    print(tord)


def _test_connect():
    V: Set[Node] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'}
    E: Set[Tuple[Node, Node]] = {('a','b'), ('b','e'), ('e','a'),
                                 ('f','g'), ('g','f'),
                                 ('c','d'), ('d','c'), ('d','h'), ('h','d'),
                                 ('b','c'),
                                 ('b','f'), ('e','f'),
                                 ('c','g'), ('h','g')}
    G: Digraph = Digraph(len(V))
    for (u, v) in E:
        G.link(u, v)

    print(components(G))
