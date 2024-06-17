"""
Some helpers for dealing with pitch class sets
Based upon discussion here https://www.thecodingforums.com/threads/algorithm-for-generating-pitch-class-sets-in-prime-form.742728/
with ammendments for considering inversions as well as improved width calculation.
"""
import csv
import itertools
from dataclasses import dataclass
from functools import reduce
from itertools import groupby
import os
from typing import Set, List, Union

import more_itertools

from ..core.sequence import Event

def to_interval_vectors(pcs: Union[Set[int],List[int]]) -> List[int]:
    """Get the Forte interval vectors (ie count of each interval class)
    across the whole set. Returns a list of length 6
    """
    pcs = list(pcs)
    vectors = [0,0,0,0,0,0]
    if len(pcs) == 0:
        return vectors
    for i1 in range(len(pcs)):
        for i2 in range(len(pcs)):
            if i2 <= i1:
                continue
            interval = abs(pcs[i2] - pcs[i1])
            if interval > 6:
                interval = abs(interval - 12)
            vectors[interval-1] = vectors[interval-1] + 1
    return vectors

def get_linear_vector(pcs: Union[Set[int],List[int]]) -> List[int]:
    """
    Get the interval vector reading from L to R across the ordered pcs
    """
    pcs = list(pcs)
    if len(pcs) == 0:
        return vectors
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
    candidates = narrowest
    set_len = len(rotations[0])
    for i in range(1, set_len):
        # look at the leftmost items in each candidate - which has the smallest sum (interval distance)
        # on each iteration, reduce the size of the list head under examination until a winner emerges
        candidates = [(sum(c[:-i]), c) for c in candidates]
        candidates = sorted(candidates, key=lambda c: c[0], reverse=False)
        if len(candidates) == 1:
            return candidates[0][1]
        # highest ranking candidates proceed to next round.
        candidates = itertools.groupby(candidates, lambda c: c[0])
        k, g = next(candidates)
        candidates = [c for _, c in list(g)]
    return candidates[0]


    
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
    intervals_p0 = get_linear_vector(pcs)
    intervals_i0 = intervals_p0[:]
    intervals_i0.reverse()
    intervals_i0 = intervals_i0[1:] + intervals_i0[:1]
    all_rotations = get_rotations(intervals_i0) + get_rotations(intervals_p0)
    prime_intervals = get_compact_form(all_rotations)
    result = [sum(prime_intervals[:i]) for i in range(len(prime_intervals))]
    return set(result)
    
def get_compliment(pcs, base_set=set(range(0,11))):
    return base_set - pcs

def get_intervallic_compliments(pcs):
    """
    Yield all sets that have interval vectors that are the compliment of the
    vector of pcs in its prime form.
    """
    all_sets = ForteSet.as_dict()
    prime_a = tuple(to_prime_form(set(pcs)))
    try:
        vector_a = all_sets[prime_a].vector
    except KeyError:
        raise Exception(f"Invalid set {pcs}")
    has_intervals_a = list(filter(lambda i: vector_a[i-1] > 0, range(0,6)))
    solutions = []
    for _,sets in all_sets.items():
        if not isinstance(sets, list):
            sets = [sets]
        for s in sets:
            vector_b = s.vector
            has_intervals_b = list(filter(lambda i: vector_b[i-1] > 0, range(0,6)))
            if set(has_intervals_a).intersection(set(has_intervals_b)) == set() and s not in solutions:
                solutions.append(s)
                yield s

    
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

@dataclass
class ForteSet:
    name: str
    prime: tuple
    vector: tuple
    cardinality: int
    """convenience class for looking up Forte sets"""
    __data__ = None
    def __init__(self, name, prime, vector):
        self.name = name
        self.prime = prime
        self.vector = vector
        self.cardinality = len(prime)

    def as_event(self, transposition=0):
        pitches = [p + transposition for p in self.prime]
        return Event(pitches=pitches)

    def __eq__(self, other):
        if isinstance(other, ForteSet):
            return self.prime == other.prime
        return False


    @staticmethod
    def as_dict():
        """
        Return the list of forte sets, indexed as a multi-key dictionary to enable lookup by
        name, prime or interval vector.
        (Interval vector may point to one or more set instances).
        """
        if ForteSet.__data__ is None:
            ForteSet.__data__ = {}
            path = os.path.dirname(__file__)
            with open(os.path.join(path, "forte_sets.csv")) as csvfile:
                reader = csv.reader(csvfile, delimiter=",", quotechar='"')
                for name, prime, vector in reader:
                    prime = tuple(int(i) for i in prime.split(","))
                    vector = tuple(int(i) for i in vector.split(","))
                    f_set = ForteSet(name, prime, vector)
                    ForteSet.__data__[name] = f_set
                    ForteSet.__data__[prime] = f_set
                    # a few vectors are shared, so this is a list
                    if vector not in ForteSet.__data__:
                        ForteSet.__data__[vector] = [f_set]
                    else:
                        ForteSet.__data__[vector].append(f_set)
        return ForteSet.__data__
