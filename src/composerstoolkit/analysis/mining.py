from collections import Counter
import itertools
from typing import List, Any, Tuple

# from prefixspan import PrefixSpan

from ..core import Graph, FiniteSequence

def common_subsequences(
    dataset: List[Any],
    min_match_len = 3,
    max_match_len = 10) -> List[Tuple[int, List[Any]]]:
    """Catalog common sequential patterns 
    (ie, occuring twice or more) that are of length
    min_match_len to max_match_len that occur within
    list dataset.
    Return a list of (count, subsequence)
    """

    results = []

    def _count_occurrences(sublist, parent):
        return sum(parent[i:i+len(sublist)]==\
            sublist for i in range(len(parent)))

    for i1 in range(len(dataset) - max_match_len):
        previous = None
        for i2 in range(min_match_len, max_match_len):
            head = dataset[i1:i1 + i2]
            tail = dataset[i1 + i2:]
            count = _count_occurrences(head, tail)
            if count == 0:
                if previous is not None:
                    head = previous
                    results.append(head)
                    previous = None
                break
            previous = head
        results.append(head)
    results = [list(j) for i, j in itertools.groupby(results)]
    results = [(len(seq), seq[0]) for seq in results]
    results = sorted(results,
        key=lambda m: m[0], reverse=True)
    return results

# def hidden_sequence(
    # dataset: List[Any],
    # depth=4):

    # dataset = []
    # for seq in sequences:
        # dataset.append(seq.to_vectors())
    # ps = PrefixSpan(dataset)
    # return ps.topk(depth)
