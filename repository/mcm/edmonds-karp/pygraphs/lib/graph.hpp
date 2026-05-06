/*
 * Copyright (c) 2019 Gabriel B. Sant'Anna <baiocchi.gabriel@gmail.com>
 * @License Apache <https://gitlab.com/baioc/pygraphs>
 */

#ifndef STRUCTURES_GRAPH_HPP
#define STRUCTURES_GRAPH_HPP

#include <unordered_map>
#include <utility> // move, pair
#include <limits> // infinity
#include <cassert>


namespace structures {

using std::unordered_map;

template <typename Label, typename Weight, bool direct=false>
	// requires Hashable<Label>,
	//          LessThanComparable<Weight>,
	//          std::numeric_limits<Weight>::has_infinity(),
	//          Assignable<Weight,1>, Assignable<Weight,0>
class Graph {
 public:
	Graph() = default;
	explicit Graph(int);

	constexpr bool directed() const;

	int node_number() const;
	int edge_number() const;

	bool insert(Label);
	int erase(const Label&);

	int link(const Label&, const Label&, Weight=1);
	int unlink(const Label&, const Label&);

	bool contains(const Label&) const;
	int degree(const Label&) const;
	int degree_out(const Label&) const;
	int degree_in(const Label&) const;

	bool contains(const Label&, const Label&) const;
	Weight weight(const Label&, const Label&) const;

	// returning vectors or using output iterators would be cleaner; the
	// intention is that these methods return some iterable in constant time
	const unordered_map<Label,unordered_map<Label,Weight>>& nodes() const;
	const unordered_map<Label,Weight>& neighbours(const Label&) const;

 private:
	unordered_map<Label,unordered_map<Label,Weight>> adjacencies_;
	int edges_{0};
};


template <typename L, typename W, bool d>
Graph<L,W,d>::Graph(int node_capacity)
{
	assert(node_capacity > 0);
	adjacencies_.reserve(node_capacity);
}

template <typename L, typename W, bool dir>
constexpr bool Graph<L,W,dir>::directed() const
{
	return dir;
}

template <typename L, typename W, bool d>
inline int Graph<L,W,d>::node_number() const
{
	return adjacencies_.size();
}

template <typename L, typename W, bool d>
inline int Graph<L,W,d>::edge_number() const
{
	return edges_;
}

template <typename L, typename W, bool d>
inline bool Graph<L,W,d>::insert(L node)
{
	unordered_map<L,W> empty = {};
	const auto ret = adjacencies_.emplace(std::move(node), std::move(empty));
	return ret.second; // map's signaling of whether emplace occurred
}

template <typename L, typename W, bool dir>
int Graph<L,W,dir>::erase(const L& node)
{
	if (!contains(node))
		return -1;

	int erased = adjacencies_[node].size();
	adjacencies_.erase(node);

	for (auto& assoc: adjacencies_) {
		if constexpr (dir)
			erased += assoc.second.erase(node);
		else
			assoc.second.erase(node);
	}

	return erased; // number of erased edges
}

template <typename L, typename W, bool dir>
int Graph<L,W,dir>::link(const L& node_from, const L& node_to, W weight)
{
	if (node_from == node_to)
		return 0; // ignore reflexive edges

	// inserts any unregistered nodes before linking
	const int inserted = insert(node_from) + insert(node_to);

	// either making a new link
	if (!contains(node_from, node_to))
		++edges_;

	// or just updating its weight
	adjacencies_[node_from][node_to] = std::move(weight);
	if constexpr (!dir)
		adjacencies_[node_to][node_from] = std::move(weight);

	return inserted; // number of implicitly created nodes
}

template <typename L, typename W, bool dir>
int Graph<L,W,dir>::unlink(const L& node_from, const L& node_to)
{
	int disconnected = 0;

	if (contains(node_from) && contains(node_to)) {
		disconnected += adjacencies_[node_from].erase(node_to);

		if (disconnected)
			--edges_;

		if constexpr (!dir)
			disconnected += adjacencies_[node_to].erase(node_from);
	}

	return disconnected; // number of removed links
}

template <typename L, typename W, bool d>
inline bool Graph<L,W,d>::contains(const L& node) const
{
	return adjacencies_.find(node) != adjacencies_.end();
}

template <typename L, typename W, bool dir>
inline int Graph<L,W,dir>::degree(const L& node) const
{
	if constexpr (!dir)
		return degree_out(node);
	else
		return contains(node) ? degree_out(node) + degree_in(node) : -1;
}

template <typename L, typename W, bool d>
inline int Graph<L,W,d>::degree_out(const L& node) const
{
	return contains(node) ? adjacencies_.at(node).size() : -1;
}

template <typename L, typename W, bool dir>
int Graph<L,W,dir>::degree_in(const L& node) const
{
	if constexpr (!dir) {
		return degree_out(node);

	} else {
		if (!contains(node))
			return -1;

		int sum = 0;
		for (const auto& assoc: adjacencies_)
			sum += assoc.second.count(node);

		return sum;
	}
}

template <typename L, typename W, bool d>
inline bool Graph<L,W,d>::contains(const L& node_from, const L& node_to) const
{
	if (contains(node_from)) {
		auto adj = adjacencies_.at(node_from);
		return adj.find(node_to) != adj.end();
	}
	return false;
}

template <typename L, typename Weight, bool dir>
Weight Graph<L,Weight,dir>::weight(const L& node_from, const L& node_to) const
{
	if (node_from == node_to) {
		if constexpr (!dir)
			return 0;
		else // if constexpr (dir)
			return std::numeric_limits<Weight>::infinity();

	} else if (contains(node_from)) {
		const auto& adj = adjacencies_.at(node_from);
		const auto& pos = adj.find(node_to);
		if (pos != adj.end())
			return pos->second;
	}

	if constexpr (!dir)
		return std::numeric_limits<Weight>::infinity();
	else // if constexpr (dir)
		return 0;
}

template <typename L, typename W, bool d>
const unordered_map<L,unordered_map<L,W>>& Graph<L,W,d>::nodes() const
{
	return adjacencies_;
}

template <typename L, typename W, bool d>
const unordered_map<L,W>& Graph<L,W,d>::neighbours(const L& node) const
{
	unordered_map<L,W> empty{};
	return contains(node) ? adjacencies_.at(node) : empty;
}

} // namespace structures

#endif // STRUCTURES_GRAPH_HPP
