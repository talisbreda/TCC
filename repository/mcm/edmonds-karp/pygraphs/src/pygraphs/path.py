# Copyright (c) 2019 Gabriel B. Sant'Anna <baiocchi.gabriel@gmail.com>
# @License Apache <https://gitlab.com/baioc/pygraphs>

from .libpygraphs import Graph, Digraph, PriorityQueue
from .common import Node, graph_edges
from typing import Union, Dict, Tuple, Sequence, Optional, Set
from math import inf
from pprint import pprint


def shortest_routes(graph: Union[Graph, Digraph], start: Node) \
        -> Dict[Node, Tuple[Sequence[Node], float]]:
    """
    Compute shortest routes from a single vertex to all others in a graph
    using the Bellman-Ford algorithm.
    Returns a dictionary containing nodes as keys that map to tuples with the
    shortest path found to them and the path's cost. Disconnected vertices are
    mapped to (None, inf).
    Raises a ValueError exception in case a negative cycle is found. O(V*E)
    """

    # initialize
    distances: Dict[Node, float] = {}
    antecessors: Dict[Node, Optional[Node]] = {}
    for v in graph.nodes():
        distances[v] = inf if v != start else 0
        antecessors[v] = None

    for _ in range(1, graph.node_number()):
        done = True
        for (u, v) in graph_edges(graph):
            # relax
            Duv = distances[u] + graph.weight(u, v)
            if Duv < distances[v]:
                distances[v] = Duv
                antecessors[v] = u
                done = False
        if done:
            break

    # report negative cycle
    for (u, v) in graph_edges(graph):
        if distances[u] + graph.weight(u, v) < distances[v]:
            raise ValueError("Negative cycle found near ({}, {})".format(u,v))

    return _pathmap(distances, antecessors)


def shortest_paths(graph: Union[Graph, Digraph], source: Node) \
        -> Dict[Node, Tuple[Sequence[Node], float]]:
    """
    Use Dijkstra's Shortest Path First algorithm to find the shortest paths
    between a given origin and all other nodes in a graph.
    Does not guarantee a shortest path when presented with negative weights.
    Returns a dictionary containing nodes as keys that map to tuples with the
    shortest path found to them and the path's cost. Disconnected vertices are
    mapped to (None, inf). O((V+E)*lg(V))
    """

    # initialize
    distances: Dict[Node, float] = {}
    antecessors: Dict[Node, Optional[Node]] = {}
    unclosed = PriorityQueue(graph.node_number())
    for v in graph.nodes():
        d = inf if v != source else 0
        distances[v] = d
        antecessors[v] = None
        unclosed.enqueue(v, d)

    while not unclosed.empty():
        u = unclosed.dequeue()
        for v in graph.neighbours(u):
            if unclosed.contains(v):
                # relax
                Duv = distances[u] + graph.weight(u, v)
                if Duv < distances[v]:
                    antecessors[v] = u
                    distances[v] = Duv
                    unclosed.update(v, Duv)

    return _pathmap(distances, antecessors)


def shortest_network(graph: Union[Graph, Digraph]) \
        -> Dict[Node, Dict[Node, float]]:
    """Find shortest paths for all vertex pairs in a graph via Floyd-Warshall.
    Returns a bidimensional dictionary D that uses node labels as indexes such
    that D[u][v] is the shortest circuit cost going from u to v. O(V^3)"""

    vertices = graph.nodes()
    dist = {u: {v: graph.weight(u, v) for v in vertices} for u in vertices}

    # for every vertex, check if it is a shortcut between two pairs
    for interm in vertices:
        for source in vertices:
            for destination in vertices:
                shc = dist[source][interm] + dist[interm][destination]
                dist[source][destination] = min(dist[source][destination], shc)

    return dist


def _pathmap(distances: Dict[Node, float],
             antecessors: Dict[Node, Optional[Node]]) \
        -> Dict[Node, Tuple[Sequence[Node], float]]:
    paths: Dict[Node, Tuple[Sequence[Node], float]] = {}

    for (dest, dist) in distances.items():
        if dist < inf:
            path: List[Node] = []

            last = dest
            while not last is None:
                path.append(last)
                last = antecessors[last]

            path.reverse()
            paths[dest] = (path, dist)

        else:
            paths[dest] = (None, inf)

    return paths


def _test_path():
    V: Set[Node] = {'A', 'B', 'C', 'S'}
    E: Set[Tuple[Node, Node, float]] = {('S', 'A', 5), ('S', 'B', 3),
                                        ('B', 'A', 1),
                                        ('A', 'C', 6), ('B', 'C', 4)}
    G: Union[Graph, Digraph] = Graph(len(V))
    for (u, v, w) in E:
        G.link(u, v, w)

    N = shortest_paths(G, 'S')
    pprint(N)
