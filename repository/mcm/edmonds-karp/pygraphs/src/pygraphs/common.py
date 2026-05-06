from .libpygraphs import Graph, Digraph
from typing import TypeVar, Sequence, Generator, Tuple, Union, Dict


T = TypeVar('T')  # generic type

def arbitrary(seq: Sequence[T]) -> T:
    for x in seq:
        return x

Node = str  # label type

def graph_edges(g: Union[Graph, Digraph]) \
        -> Generator[Tuple[Node, Node], None, None]:
    for u in g.nodes():
        for v in g.neighbours(u):
            yield (u, v)
