# Copyright (c) 2019 Gabriel B. Sant'Anna <baiocchi.gabriel@gmail.com>
# @License Apache <https://gitlab.com/baioc/pygraphs>

from .libpygraphs import Graph, Digraph
from .common import Node, graph_edges
from math import inf
from typing import Dict, Tuple, Set, Generator, Sequence
from collections import deque


def max_flow(graph: Digraph, source: Node, sink: Node) \
        -> Dict[Tuple[Node, Node], float]:
    """Find the maximum flow through a digraph by Edmonds-Karp FFA. O(V * E^3)
    Returns a dictionary maping edges to their maximum flow in the network."""

    flow = {pipe: 0 for pipe in graph_edges(graph)}

    def residue(u: Node, v: Node) -> float:
        return graph.weight(u, v) - flow[(u, v)]

    while True:
        pred: Dict[Node, Node] = {}

        queue = deque()
        queue.append(source)
        while queue:
            u = queue.popleft()
            for v in graph.neighbours(u):
                if v not in pred and v != source and residue(u, v) > 0:
                    pred[v] = u
                    queue.append(v)

        if sink not in pred:
            break

        capacity = inf
        v = sink
        while v in pred:
            u = pred[v]
            capacity = min(capacity, residue(u, v))
            v = u

        for uv in flow.keys():
            flow[uv] += capacity

    return flow


def max_matching(graph: Graph, partu: Set[Node], partv: Set[Node]) \
        -> Set[Tuple[Node, Node]]:
    """Produces the maximum cardinality matching between two given partitions
    of an undirected bipartite graph via Hopcroft-Karp. O(sqrt(V) * E)
    Returns the set of edges that make up the maximum matching in the graph."""

    dist: Dict[Node, float] = {}
    mate: Dict[Node, Node] = {}

    def bfs_augment() -> bool:
        queue = deque()
        for u in partu:
            if mate[u] is None:
                dist[u] = 0
                queue.append(u)
            else:
                dist[u] = inf

        dist[None] = inf
        while queue:
            u = queue.popleft()
            if dist[u] < dist[None]:
                for v in graph.neighbours(u):
                    w = mate[v]
                    if dist[w] == inf:
                       dist[w] = dist[u] + 1
                       queue.append(w)

        return dist[None] != inf

    def dfs_match(u: Node) -> bool:
        if u is None:
            return True

        for v in graph.neighbours(u):
            w = mate[v]
            if dist[w] == dist[u] + 1:
                if dfs_match(w):
                    mate[v] = u
                    mate[u] = v
                    return True
        else: # no break
            dist[u] = inf
            return False

    for u in partu:
        dist[u] = inf
        mate[u] = None
    for v in partv:
        dist[v] = inf
        mate[v] = None

    while bfs_augment():
        for u in partu:
            if mate[u] is None:
                dfs_match(u)

    # convert dict to set representation
    matching: Set[Tuple[Node, Node]] = set()
    for u, v in mate.items():
        if v is None:
            continue
        else:
            assert(mate[u] == v and mate[v] == u)
            matching.add((u, v))
            mate[u] = None
            mate[v] = None

    return matching


# @TODO: vertex coloring <-? Lawler's method


def _test_flow():
    V: Set[Node] = {'S', 'A', 'B', 'C', 'D', 'T'}
    A: Set[Tuple[Node, Node, float]] = {('S', 'A', 5), ('S', 'B', 5),
                                        ('A', 'B', 10), ('A', 'C', 5),
                                        ('C', 'T', 5),
                                        ('B', 'D', 5), ('D', 'T', 5)}

    G: Digraph = Digraph(len(V))
    for (u, v, w) in A:
        G.link(u, v, w)

    F = max_flow(G, 'S', 'T')
    for pipe, flow in F.items():
        print(pipe, flow)


def _test_match():
    X: Set[Node] = {'a', 'b', 'c'}
    Y: Set[Node] = {'d', 'e', 'f'}
    V: Set[Node] = X.union(Y)
    E: Set[Tuple[Node, Node]] = {('a', 'd'), ('a', 'e'),
                                 ('b', 'f'), ('c', 'd')}

    G: Graph = Graph(len(V))
    for (u, v) in E:
        G.link(u, v)

    M = max_matching(G, X, Y)
    for m in M:
        print(m)
