# Copyright (c) 2019 Gabriel B. Sant'Anna <baiocchi.gabriel@gmail.com>
# @License Apache <https://gitlab.com/baioc/pygraphs>

from .libpygraphs import Graph, Digraph
from .common import Node
from typing import Union, Generator, Tuple, Set, List
from collections import deque


def breadth_first(graph: Union[Graph, Digraph], root: Node) \
        -> Generator[Tuple[Node, int, Node], None, None]:
    """Traverse a graph's nodes breadth-first starting from given vertex.
    Yields a tuple containing each visited node (except starting one), together
    with the depth level it was found and its search tree antecessor. O(V+E)"""

    visited: Set[Node] = {root}
    queue = deque()
    queue.append((root, 0))

    while queue:
        (u, depth) = queue.popleft()
        for v in graph.neighbours(u):
            if v not in visited:
                yield (v, depth + 1, u)
                visited.add(v)
                queue.append((v, depth + 1))


def depth_first(graph: Union[Graph, Digraph], root: Node) \
        -> Generator[Tuple[Node, int, Node], None, None]:
    """Traverse a graph's nodes depth-first starting from given vertex.
    Yields a tuple containing each visited node (except starting one), together
    with the depth level it was found and its search tree antecessor. O(V+E)"""

    visited: Set[Node] = {root}
    stack: List[Tuple[Node, int, Node]] = []
    for v in graph.neighbours(root):
        visited.add(v)
        stack.append((v, 1, root))

    while stack:
        (u, depth, antecessor) = stack.pop()
        yield (u, depth, antecessor)
        for v in graph.neighbours(u):
            if v not in visited:
                visited.add(v)
                stack.append((v, depth + 1, u))


def _test_search():
    V: Set[Node] = {'1', '2', '3', '4', '5', '6', '7', '8'}
    E: Set[Tuple[Node, Node]] = {('8', '3'), ('8', '4'),
                                 ('8', '5'), ('1', '8'),
                                 ('3', '1'), ('3', '2'),
                                 ('4', '6'), ('5', '7')}

    G: Union[Graph, Digraph] = Digraph(len(V))
    for (u, v) in E:
        G.link(u, v)

    for (node, depth, antecessor) in depth_first(G, '8'):
        print(node, depth, antecessor)
