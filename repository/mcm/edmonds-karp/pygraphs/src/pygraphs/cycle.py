# Copyright (c) 2019 Gabriel B. Sant'Anna <baiocchi.gabriel@gmail.com>
# @License Apache <https://gitlab.com/baioc/pygraphs>

from .libpygraphs import Digraph, Graph
from .common import Node, graph_edges, arbitrary
from typing import Union, Optional, Sequence, Tuple, List, Set, Dict, FrozenSet
from math import inf
from itertools import combinations


def eulerian_cycle(graph: Union[Graph, Digraph], start: Optional[Node] = None) \
        -> Optional[Sequence[Node]]:
    """Finds an eulerian cycle on a graph using Hierholzer's algorithm.
    Returns a list representing the node trail or None when no such cycle
    is found. O(E)"""

    traversed: Set[Tuple[Node, Node]] = set()

    def Hierholzer(initial: Node) -> List[Node]:
        cycle = [initial]

        u = initial
        while True:
            e = None
            for v in graph.neighbours(u):
                if (u, v) not in traversed:
                    e = (u, v)
                    break
            else:  # no break: every edge (u,v) has already been traversed
                return None

            (u, v) = e
            cycle.append(v)

            traversed.add(e)
            if not graph.directed():
                traversed.add((v, u))

            u = v
            if u == initial:
                break

        for v in cycle:
            for w in graph.neighbours(v):
                if (v, w) not in traversed:
                    subcycle = Hierholzer(v)
                    if subcycle is None:
                        return subcycle
                    else:
                        # splice internal subcycle into full cycle
                        pos = cycle.index(subcycle[0])
                        cycle =  cycle[:pos] + subcycle + cycle[pos+1:]

        return cycle

    start = arbitrary(graph.nodes()) if start is None else start
    cycle = Hierholzer(start)

    if cycle is None:
        return cycle

    for (u, v) in graph_edges(graph):
        if (u, v) not in traversed:
            return None

    return cycle


def hamiltonian_circuit(graph: Union[Graph, Digraph], start: Node) \
        -> Optional[Tuple[Sequence[Node], float]]:
    """Finds a graph's minimal hamiltonian circuit through Held-Karp.
    Returns a tuple containing the optimal tour and its cost or None if there's
    no such cycle. O(2^V * V^2)"""

    # Visits, FinalDestination, Cost = FrozenSet[Node], Node, float
    cost: Dict[Tuple[FrozenSet[Node], Node], float] = {}
    dests = frozenset({v for v in graph.nodes() if v != start})

    for place in dests:
        cost[(frozenset({place}), place)] = graph.weight(start, place)

    for size in range(2, graph.node_number()):
        for itinerary in combinations(dests, size):
            route = frozenset(itinerary)
            for final in route:
                sub = route - {final}
                opt = inf  # optimal solution for problem subset
                for mid in sub:
                    opt = min(opt, cost[(sub, mid)] + graph.weight(mid, final))
                cost[(route, final)] = opt

    minimum = inf
    for end in dests:
        minimum = min(minimum, cost[(dests, end)] + graph.weight(end, start))

    # check if no circuit was found
    if minimum == inf:
        return None

    # backtrack to find full path
    circuit = minimum
    path: List[Node] = [start]

    for _ in range(graph.node_number() - 1):
        for (route, final), opt in cost.items():
            if (circuit - graph.weight(final, path[-1]) == opt):
                path.append(final)
                circuit = opt
                break

    path.append(start)
    path.reverse()

    return (path, minimum)


def _test_cycle():
    V: Set[Node] = {'a', 'b', 'c', 'd', 'e'}
    E: Set[Tuple[Node, Node, float]] = {('b', 'a', 2.5), # ('a', 'c', 3),
                                        ('c', 'd', 2.5), # ('d', 'b', 1),
                                        ('a', 'e', 4), ('e', 'c', 2),
                                        ('e', 'b', 1.5), ('d', 'e', 2)}
    G: Union[Graph, Digraph] = Graph(len(V))
    for (u, v, w) in E:
        G.link(u, v, w)

    C = eulerian_cycle(G, 'a')
    print(C)
