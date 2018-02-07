def simple_merge(min_func, *lists):
    """Do the merge part of merge sort, only with multiple input lists.
    
    This version is super side-effectful and consumes inputs lists.
    
    :param key_func: A function to extract a comparable value from list elements
    :type key_func: A -> Comparable
    :param lists: A list of iterables to merge from
    :type lists: [Iterable A]
    :rtype: Yields A
    """
    # Coerce from tuple for mutability
    lists = list(lists)
    while lists:
        best_idx, best_score = 0, min_func(lists[0][0])
        for i, l in enumerate(lists):
            x = l[0]
            score = min_func(x)
            if score < best_score:
                best_idx, best_score = i, score

        best_choice = lists[best_idx].pop(0)
        # Remove selected list if now empty
        if len(lists[best_idx]) == 0:
            lists.pop(best_idx)

        yield best_choice


def multimerge(key_func, *lists):
    """Do the merge part of merge sort, only with multiple inputs.

    :param key_func: A function to extract a comparable value from list elements
    :type key_func: A -> Comparable
    :param lists: A list of iterables to merge from
    :type lists: [Iterable A]
    :rtype: Yields A
    """
    iterators = [iter(l) for l in lists]
    pairs = [(next(i), i) for i in iterators]
    fm = keyed_min(key_func)

    while pairs:
        choice, pairs = take_min(fm, pairs)
        yield choice

def keyed_min(key_func):
    """Factory for functions evaluating min of f(x) across lists of x:xs pairs.

    In other words, give this a key function similar to sorted(xs, key=f).
    This key function will then choose the best head element available
    from a list of cons lists (i.e. (x, xs) format).

    :param f: Key function for determining minimum
    :type f: A -> Comparable
    :rtype: [(A,Iterator A)] -> (Int, A)
    """
    def fm(pairs):
        best_idx, best_score = 0, key_func(pairs[0][0])

        for i, (x, _xs) in enumerate(pairs):
            score = key_func(x)
            if score < best_score:
                best_idx, best_score = i, score

        return best_idx, pairs[best_idx][0]
    return fm

def take_min(min_func, pairs):
    """Find the best head element among many cons lists and pop it.

    This function has the side-effect of advancing a single iterator
    in pairs and possibly removing the pair containing that iterator.

    Returns the popped element and the update list of cons lists.

    :param min_func: Function for selecting the best head element and its index.
    :type min_func: [(A, Iterator A)] -> (Int, A)
    :param pairs: A list of cons lists.
    :rtype: (A, [(A, Iterator A)])
    """
    best_idx, best_choice = min_func(pairs)

    try:
        _x, xs = pairs[best_idx]
        pairs[best_idx] = (next(xs), xs)
    except IndexError:
        # Programmer error; fail hard and fail early
        raise IndexError('list index out of range - attempt to access nonexistent pair')
    except StopIteration:
        # Iterator empty at index of best choice. Remove the corresponding pair.
        pairs.pop(best_idx)

    return best_choice, pairs

if __name__ == '__main__':
    # Simple tests
    l1 = [1, 4, 4, 5]
    l2 = [2, 3, 5, 8]
    l3 = [-10, -1, 2, 3]
    id_func = lambda x: x
    id_min = keyed_min(id_func)

    iterables = [iter(l1), iter(l2), iter(l3)]
    pairs = [(next(i), i) for i in iterables]
    choice, pairs = take_min(id_min, pairs)
    assert choice == -10
    assert list(pairs[0][1]) == [4, 4, 5]
    assert list(pairs[1][1]) == [3, 5, 8]
    assert list(pairs[2][1]) == [2, 3]

    assert list(multimerge(id_func, l1, l2, l3)) == [-10, -1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 8]
    assert list(simple_merge(id_func, l1, l2, l3)) == [-10, -1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 8]

