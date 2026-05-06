#include <catch2/catch.hpp>

#include "graph.hpp"
using structures::Graph;

#include <vector>
#include <cmath> // HUGE_VALF


TEST_CASE("Graph directivity is a given at compile-time", "[Graph][template]")
{
	SECTION("Graphs are undirected by default") {
		Graph<char,float> g;
		REQUIRE(g.directed() == false);
		g.link('a', 'b');
		g.link('b', 'c');
		g.link('a', 'c');
		REQUIRE(g.degree_out('c') == g.degree('c'));
		REQUIRE(g.degree_out('c') == g.degree_in('c'));
	}
	SECTION("but can also be made directed") {
		Graph<char,double,true> g;
		REQUIRE(g.directed() == true);
		g.link('a', 'b');
		g.link('b', 'c');
		g.link('a', 'c');
		REQUIRE(g.degree('b') == 2);
		REQUIRE(g.degree_in('b') == 1);
		REQUIRE(g.degree_out('b') == 1);
	}
}


TEMPLATE_TEST_CASE_SIG(
	"Graphs are templated for any Hashable Label type", "[Graph][template]",
	((typename L, bool D), L, D),
	(std::string,false), (int,false), (char,false), (double,false),
	(std::string,true),  (int,true),  (char,true),  (double,true)
) {
	SECTION("Weights are normally floating point numbers") {
		Graph<L,float,D> g;
		REQUIRE(g.node_number() == 0);
	}
	SECTION("or any other IEEE754/iec_559 FP formats") {
		Graph<L,long double,D> g;
		REQUIRE(g.node_number() == 0);
	}
}


TEMPLATE_TEST_CASE(
	"individual nodes can be inserted and erased from Graphs", "[Graph]",
	(Graph<char,float,false>), (Graph<char,float,true>)
) {
	TestType g(3);
	REQUIRE(g.node_number() == 0);

	REQUIRE(g.contains('a') == false);
	g.insert('a');
	REQUIRE(g.contains('a') == true);
	REQUIRE(g.node_number() == 1);

	REQUIRE(g.contains('b') == false);
	g.insert('b');
	REQUIRE(g.contains('b') == true);
	REQUIRE(g.node_number() == 2);

	SECTION("each successful insertion returns true") {
		REQUIRE(g.insert('c') == true);
		REQUIRE(g.contains('c') == true);
		REQUIRE(g.node_number() == 3);
	}

	SECTION("a node with the same label can't be inserted again") {
		REQUIRE(g.insert('a') == false);
		REQUIRE(g.node_number() == 2);
	}

	SECTION("erasing a node returns the number of edges removed as a consequence") {
		REQUIRE(g.insert('c') == true);
		REQUIRE(g.node_number() == 3);

		g.link('b', 'c');
		g.link('b', 'a');
		REQUIRE(g.erase('b') == 2);
		REQUIRE(g.contains('b') == false);
		REQUIRE(g.node_number() == 2);

		REQUIRE(g.erase('a') == 0);
		REQUIRE(g.contains('a') == false);
		REQUIRE(g.node_number() == 1);

		REQUIRE(g.erase('c') == 0);
		REQUIRE(g.contains('c') == false);
		REQUIRE(g.node_number() == 0);
	}

	SECTION("trying to erase a node not in the graph yields a negative value") {
		REQUIRE(g.contains('c') == false);
		REQUIRE(g.erase('c') < 0);
		REQUIRE(g.node_number() == 2);
	}
}


TEST_CASE("any pair of different nodes can be linked and unlinked in a Graph", "[Graph]")
{
	Graph<char,float> g(5);
	REQUIRE(g.edge_number() == 0);

	g.link('a', 'b', 1.0);
	REQUIRE(g.contains('a', 'b') == true);
	REQUIRE(g.weight('a', 'b') == 1.0);
	REQUIRE(g.edge_number() == 1);

	g.link('b', 'c', 2.0);
	REQUIRE(g.contains('b', 'c') == true);
	REQUIRE(g.weight('b', 'c') == 2.0);
	REQUIRE(g.edge_number() == 2);

	SECTION("weights are optional and if ommited default to 1") {
		g.link('d', 'e');
		REQUIRE(g.weight('d', 'e') == 1.0);

		SECTION("reflexive edges are ignored") {
			REQUIRE(g.link('a', 'a', 25) == 0);
			REQUIRE(g.contains('a', 'a') == false);
		}
	}

	SECTION("vertices can be explicitly inserted before connecting them") {
		g.insert('d');
		g.insert('e');
		REQUIRE(g.edge_number() == 2);
		g.link('d', 'e');
		g.link('c', 'd');
		g.link('d', 'b');
		REQUIRE(g.edge_number() == 5);
	}

	SECTION("linking non-existing labels implicitly adds them as nodes, returning the number of created vertices") {
		REQUIRE(g.node_number() == 3);
		REQUIRE(g.link('d', 'e') == 2);
		REQUIRE(g.link('c', 'd') == 0);
		REQUIRE(g.link('d', 'b') == 0);
		REQUIRE(g.link('e', 'f') == 1);
		REQUIRE(g.node_number() == 6);
		REQUIRE(g.edge_number() == 6);
	}

	SECTION("unlink returns the number of deleted connections") {
		REQUIRE(g.unlink('x', 'y') == 0);
		SECTION("that means 1 on directed arcs") {
			Graph<char,float,true> h(2);
			h.link('a', 'b');
			h.link('b', 'a');
			REQUIRE(h.unlink('a', 'b') == 1);
		}
		SECTION("and 2 on undirected edges") {
			REQUIRE(g.unlink('a', 'b') == 2);
		}
	}

	SECTION("re-linking an edge can be used to update its weight") {
		REQUIRE(g.contains('a', 'b') == true);
		REQUIRE(g.weight('a', 'b') == 1.0);
		g.link('a', 'b', 5);
		REQUIRE(g.weight('a', 'b') == 5.0);
	}
}


TEMPLATE_TEST_CASE(
	"a Graph returns iterables to its nodes and to neighbours of each node", "[Graph]",
	(Graph<int,float,false>), (Graph<int,float,true>)
) {
	const int n = 10;
	TestType g(n);

	for (int i = 1; i < n; ++i)
		g.link(i, i+1);

	REQUIRE(g.node_number() == n);

	int sum = 0;
	for (const auto &u: g.nodes()) {
		sum += u.first;
		for (const auto &v: g.neighbours(u.first))
			REQUIRE(std::abs(v.first - u.first) == 1);
	}

	REQUIRE(sum == (1 + n) * n / 2);
}


TEMPLATE_TEST_CASE(
	"weighting unexisting and reflexive edges depend on Graph directivity",
	"[Graph][template]", (Graph<char,float,false>), (Graph<char,float,true>)
) {
	TestType g(3);
	g.link('a', 'b');
	g.link('c', 'a');

	SECTION("unconnected edges on undirected graphs have infinite weight and zero flow for directed arcs") {
		if (!g.directed())
			REQUIRE(g.weight('b', 'c') == HUGE_VALF);
		else if (g.directed())
			REQUIRE(g.weight('b', 'c') == 0);
	}

	SECTION("reflexive edges on undirected graphs have zero weight and infinite flow for directed arcs") {
		if (!g.directed())
			REQUIRE(g.weight('x', 'x') == 0);
		else if (g.directed())
			REQUIRE(g.weight('x', 'x') == HUGE_VALF);
	}
}
