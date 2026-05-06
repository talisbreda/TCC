/*
 * Copyright (c) 2019 Gabriel B. Sant'Anna <baiocchi.gabriel@gmail.com>
 * @License Apache <https://gitlab.com/baioc/pygraphs>
 */

#ifndef STRUCTURES_PRIORITY_QUEUE_HPP
#define STRUCTURES_PRIORITY_QUEUE_HPP

#include <vector>
#include <tuple>
#include <map>
#include <functional> // less
#include <utility> // move, size_t
#include <algorithm> // swap, transform
#include <cassert>


namespace structures {

template <typename T, typename P = int, typename F = std::less<P>>
	// requires Hashable<T>, Comparable<P>, DefaultConstructible<P>
class PriorityQueue {
 public:
	PriorityQueue() = default;
	explicit PriorityQueue(int);

	bool empty() const;
	int size() const;

	const T& front() const;
	void enqueue(T, P);
	T dequeue();

	bool contains(const T&) const;
	P priority(const T&) const;
	P update(const T&, P);

	// iterable container with ordered items
	const std::map<T,int>& items() const;

 private:
	int parent(int) const;
	int children(int) const;
	void sift(int);
	void sink(int);
	static bool priorize(const std::tuple<P,std::size_t,T>&,
	                     const std::tuple<P,std::size_t,T>&);
	void exchange(int, int);

	std::vector<std::tuple<P,std::size_t,T>> heap_;
	std::map<T,int> index_map_;
	std::size_t count_{0};
};


template <typename T, typename P, typename F>
PriorityQueue<T,P,F>::PriorityQueue(int size)
{
	assert(size > 0);
	heap_.reserve(size);
}

template <typename T, typename P, typename F>
inline bool PriorityQueue<T,P,F>::empty() const
{
	return heap_.empty();
}

template <typename T, typename P, typename F>
inline int PriorityQueue<T,P,F>::size() const
{
	return static_cast<int>(heap_.size());
}

template <typename T, typename P, typename F>
inline bool PriorityQueue<T,P,F>::contains(const T& elem) const
{
	return index_map_.find(elem) != index_map_.end();
}

template <typename T, typename P, typename F>
const T& PriorityQueue<T,P,F>::front() const
{
	assert(size() > 0);
	return std::get<2>(heap_[0]);
}

template <typename T, typename P, typename F>
inline int PriorityQueue<T,P,F>::parent(int child) const
{
	return (child - 1) / 2;
}

template <typename T, typename P, typename F>
inline int PriorityQueue<T,P,F>::children(int parent) const
{
	return 2*parent + 1;
}

template <typename T, typename P, typename Comp>
inline bool PriorityQueue<T,P,Comp>::priorize(
	const std::tuple<P,std::size_t,T>& lhs,
	const std::tuple<P,std::size_t,T>& rhs
) {
	// priority weights more, break tie via FIFO order
	return Comp()(std::get<0>(lhs), std::get<0>(rhs))
	       || (std::get<0>(lhs) == std::get<0>(rhs)
		       && std::get<1>(lhs) < std::get<1>(rhs));
}

template <typename T, typename P, typename F>
void PriorityQueue<T,P,F>::exchange(int a, int b)
{
	index_map_[std::get<2>(heap_[a])] = b;
	index_map_[std::get<2>(heap_[b])] = a;
	std::swap(heap_[a], heap_[b]);
}

template <typename T, typename P, typename F>
void PriorityQueue<T,P,F>::sift(int leaf)
{
	while (leaf > 0) {
		const int root = parent(leaf);
		if (priorize(heap_[leaf], heap_[root])) {
			exchange(root, leaf);
			leaf = root;
		} else {
			break;
		}
	}
}

template <typename T, typename P, typename F>
void PriorityQueue<T,P,F>::sink(int root)
{
	while (children(root) < size()) {
		const int leaf = children(root);
		int swap = root;

		if (priorize(heap_[leaf], heap_[root]))
			swap = leaf;
		if (leaf+1 < size() && priorize(heap_[leaf+1], heap_[swap]))
			swap = leaf + 1;
		if (swap == root)
			break;

		exchange(root, swap);
		root = swap;
	}
}

template <typename T, typename P, typename F>
void PriorityQueue<T,P,F>::enqueue(T elem, P prio)
{
	if (!contains(elem)) {
		auto entry = std::make_tuple(std::move(prio), count_++, elem);
		heap_.emplace_back(std::move(entry));
		index_map_[elem] = size() - 1;
		sift(size() - 1);
	} else {
		// @NOTE: enqueuing an existing element simply updates its priority
		update(elem, prio);
	}
}

template <typename T, typename P, typename F>
T PriorityQueue<T,P,F>::dequeue()
{
	assert(size() > 0);
	const auto top = std::get<2>(heap_[0]);
	exchange(0, size() - 1);
	heap_.pop_back();
	index_map_.erase(top);
	sink(0);
	return top;
}

template <typename T, typename P, typename Comp>
P PriorityQueue<T,P,Comp>::priority(const T& elem) const
{
	assert(contains(elem));
	const auto pos = index_map_.find(elem);
	if (pos == index_map_.end())
		return P();
	else
		return std::get<0>(heap_[pos->second]);
}

template <typename T, typename P, typename Comp>
P PriorityQueue<T,P,Comp>::update(const T& elem, P prio)
{
	const auto pos = index_map_.find(elem);
	if (pos == index_map_.end())
		return prio;

	const int idx = pos->second;
	const auto entry = heap_[idx];

	const P old = std::get<0>(entry);
	heap_[idx] = std::make_tuple(std::move(prio), count_++, std::get<2>(entry));

	if (Comp()(prio, old))
		sift(idx);
	else if (prio != old)
		sink(idx);

	return old;
}

template <typename T, typename P, typename F>
const std::map<T,int>& PriorityQueue<T,P,F>::items() const
{
	return index_map_;
}

} // namespace structures

#endif // STRUCTURES_PRIORITY_QUEUE_HPP
