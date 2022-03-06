from collections import Counter
import itertools
from typing import List, Any, Tuple, Set

from prefixspan import PrefixSpan

from ..core import Graph, FiniteSequence

def common_subsequences(
    dataset: List[Any],
    min_match_len = 3,
    max_match_len = 10) -> List[Tuple[int, List[Any]]]:
    """Catalog common sequential patterns 
    (ie, occuring twice or more) that are of length
    min_match_len to max_match_len that occur within
    list dataset.
    Return a list of (count, subsequence), most
    frequent first.
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

def hidden_subsequences(
    dataset: List[Any],
    depth=4):
    """
    Catalog frequent hidden sequences within
    dataset. (A wrapper around PrefixSpan).
    Return a list of (count, subsequence), longest
    matches first.
    """
    ps = PrefixSpan(dataset)
    detected = ps.topk(depth)
    detected = sorted(detected, key=lambda x: len(x[1]), reverse=True)
    return detected

def chord_analysis(seq: FiniteSequence,
    window_size=1,
    chord_lexicon=List[Set]):
    """Break the given seq down into chunks of
    window_size (expressed in beats).
    Analyse the content within to determine the
    most likely chordal background.
    In the case of abmiguity, resort to
    the best voice-leading solution.
    Return a list of transposed chord voicings.
    """
    pass