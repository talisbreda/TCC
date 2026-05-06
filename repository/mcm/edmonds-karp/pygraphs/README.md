# pygraphs on wheels

A package for the study of graph discrete data structures and algorithms.


## Usage

### Installation

Note: at this point, distributed packages are compatible with Linux only and require a recent version of libstdc++.

1. Install via [pip](https://test.pypi.org/project/pygraphs/):</br>
    ```pip install -i https://test.pypi.org/simple/ pygraphs --user```

2. Import the package:</br>
    ```import pygraphs as pyg```

### Features

- Efficient data structures written in modern C++ are available.
  - Directed and undirected Graphs.
  - Priority Queue using binary heap.
- Classic algorithms are implemented in Python with type annotations.
  - Breadth-First and Depth-First iteration with generators.
  - Finding Eulerian cycles through Hierholzer's algorithm.
  - Computing the minimum Hamiltonian circuit using Held-Karp's method.
  - Shortest paths with Bellman-Ford, Dijkstra and Floyd-Warshall algorithms.
  - Minimum spanning trees through Prim.
  - Topological sorting and finding strongly connected components using variants of DFS.
  - Computing maximum network flow with an Edmonds-Karp implementation of the Ford-Fulkerson Algorithm.
  - Maximum cardinality matching of bipartite graphs via Hopcroft-Karp-Karzanov.


## Build process

Source code is made available in [GitLab](https://gitlab.com/baioc/pygraphs), together with simple makefiles.

Data structures and some key operations are implemented in C++17 (compiled with gcc 9.1.0) and wrapped into Python 3.6+ with [Swig](http://www.swig.org/) (version 4.0.0).
