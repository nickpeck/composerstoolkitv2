from typing import Tuple, Set

from ..core import Graph, FiniteSequence

def pitch_range(seq: FiniteSequence) -> Tuple[int, int]:
    pitches = seq.pitches
    pitches = sorted(pitches)
    return (pitches[0]. pitches[1])

def total_duration(seq: FiniteSequence) -> int:
    return sum(seq.durations)

def duration_classes(seq: FiniteSequence) -> Set[int]:
    return set(seq.durations)
