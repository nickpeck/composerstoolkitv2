from typing import List

from prefixspan import PrefixSpan

from ..core import Graph, FiniteSequence

def frequent_intervallic(
    sequences: List[FiniteSequence],
    depth=4):

    dataset = []
    for seq in sequences:
        pitches = seq.pitches
        intervals = []
        for i in range(len(pitches) -1):
            left = pitches[i]
            right = pitches[i+1]
            intervals.append(right-left)
        dataset.append(intervals)
    ps = PrefixSpan(dataset)
    return ps.topk(depth)

def frequent_rhythms(
    sequences: List[FiniteSequence],
    depth=4):

    dataset = []
    for seq in sequences:
        dataset.append(seq.durations)
    ps = PrefixSpan(dataset)
    return ps.topk(depth)

def frequent_vectors(
    sequences: List[FiniteSequence],
    depth=4):

    dataset = []
    for seq in sequences:
        dataset.append(seq.to_vectors())
    ps = PrefixSpan(dataset)
    return ps.topk(depth)
