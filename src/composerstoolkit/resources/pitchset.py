"""
Some helpers for dealing with pitch class sets
Based upon discussion here https://www.thecodingforums.com/threads/algorithm-for-generating-pitch-class-sets-in-prime-form.742728/
with ammendments for considering inversions as well as improved width calculation.
"""
from functools import reduce
from typing import Set, List, Union

def to_interval_vectors(pcs: Union[Set[int],List[int]]) -> List[int]:
    pcs = list(pcs)
    if len(pcs) == 0:
        return []
    return [pcs[i + 1] - pcs[i] for i in range(len(pcs) - 1)] + [12 + min(pcs) - pcs[-1]]
    
def get_compact_form(rotations: List[List[int]]) -> List[int]:
    rotations = sorted(rotations, key=lambda r: reduce((lambda x, y: x * y), r))
    return rotations[0]
    
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
    intervals_i0 = intervals_p0
    intervals_i0.reverse()
    intervals_i0 = intervals_i0[1:] + intervals_i0[:1]
    all_rotations = get_rotations(intervals_i0) + get_rotations(intervals_p0)
    prime_intervals = get_compact_form(all_rotations)
    result = [sum(prime_intervals[:i]) for i in range(len(prime_intervals))]
    return set(result)
