"""
Some helpers for dealing with pitch class sets
Based upon discussion here https://www.thecodingforums.com/threads/algorithm-for-generating-pitch-class-sets-in-prime-form.742728/
with ammendments for considering inversions as well as improved width calculation.
"""
from functools import reduce
from itertools import groupby
from typing import Set, List, Union

def to_interval_vectors(pcs: Union[Set[int],List[int]]) -> List[int]:
    pcs = list(pcs)
    if len(pcs) == 0:
        return []
    return [pcs[i + 1] - pcs[i] for i in range(len(pcs) - 1)] + [12 + min(pcs) - pcs[-1]]
    
def get_compact_form(rotations: List[List[int]]) -> List[int]:
    # find the rotations with the smallest left-right width
    # there will probably be a tie, so group these.
    def width(r):
        return sum(r[:-1])
    sorted_by_width = sorted(rotations, key=width)
    grouped_by_width = [list(it) for k, it in groupby(sorted_by_width, width)] 
    narrowest = grouped_by_width[0]
    if len(narrowest) == 1:
        return narrowest[0]
    # if there is a tie, select the form that has the smallest intervals to the left
    left_compact_form = sorted(narrowest, key=lambda r: reduce((lambda x, y: pow(x+1,y-1)), r), reverse=True)
    return left_compact_form[0]

    
def get_rotations(intervals: List[int]) -> List[List[int]]:
    pcs = list(intervals)
    return [intervals[i:] + intervals[:i] for i in range(len(intervals))]
  
def to_prime_form(s: Union[Set[int],List[int]]) -> Set[int]:
    s = set([i % 12 for i in s])
    if s == set():
        return s
    if len(s) == 1:
        return set([0])
    pcs = sorted(list(set(s)))
    intervals_p0 = to_interval_vectors(pcs)
    intervals_i0 = intervals_p0[:]
    intervals_i0.reverse()
    intervals_i0 = intervals_i0[1:] + intervals_i0[:1]
    all_rotations = get_rotations(intervals_i0) + get_rotations(intervals_p0)
    prime_intervals = get_compact_form(all_rotations)
    result = [sum(prime_intervals[:i]) for i in range(len(prime_intervals))]
    return set(result)
    
def get_compliment(pcs, base_set=set(range(0,11))):
    return base_set - pcs
    
def complete_set(pitches: Set, target_pcs=set(range(0,11))):
    """Return combinations of pitch classes, that when added to 
    'pitches' will form a set that matches target_pcs
    """
    visited = []
    if pitches.issubset(target_pcs):
        visited.append(target_pcs - pitches)
        yield visited[0]
    pitches_base_12 = set([p % 12 for p in pitches])
    target_pcs = to_prime_form(target_pcs)
    pitches_pf = to_prime_form(pitches)
    compliment = get_compliment(pitches_pf, target_pcs)
    for i in range(0,12):
        transposed_compliment = set([(p + i) % 12 for p in compliment])
        aggregate = to_prime_form(pitches_base_12.union(transposed_compliment))
        if aggregate == target_pcs and transposed_compliment not in visited:
            visited.append(transposed_compliment)
            yield transposed_compliment
