import itertools
import math
from typing import List, Optional, Iterator, Union

from ..core import Context, Constraint, Sequence, FixedSequence

@Constraint
def constraint_in_set(sequence: FixedSequence, _set = range(0,128)) -> bool:
    if sequence.to_pitch_set() == {}:
        return False
    return sequence.to_pitch_set().issubset(_set)

@Constraint
def constraint_no_repeated_adjacent_notes(sequence: FixedSequence) -> bool:
    if len(sequence.events) > 2:
        return True
    it1,it2 = itertools.tee(sequence.events)
    next(it2, None)
    for left, right in zip(it1,it2):
        if right.pitches == left.pitches:
            return False
    return True

@Constraint
def constraint_limit_shared_pitches(sequence: FixedSequence, max_shared: int=1) -> bool:
    if len(sequence.events) > 2:
        return True
    it1,it2 = itertools.tee(sequence.events)
    next(it2, None)
    for left, right in zip(it1,it2):
        intersection = set(right.pitches).intersection(set(left.pitches))
        if len(intersection) > max_shared:
            return False
    return True

@Constraint
def constraint_enforce_shared_pitches(sequence: FixedSequence, min_shared: int=1) -> bool:
    if len(sequence.events) > 2:
        return True
    it1,it2 = itertools.tee(sequence.events)
    next(it2, None)
    for left, right in zip(it1,it2):
        intersection = set(right.pitches).intersection(set(left.pitches))
        if len(intersection) <= max_shared:
            return False
    return True

@Constraint
def constraint_no_leaps_more_than(sequence: FixedSequence, max_int: int) -> bool:
    if len(sequence.events) < 2:
        return True
    it1,it2 = itertools.tee(sequence.events)
    next(it2, None)
    for left, right in zip(it1,it2):
        if left.pitches == [] or right.pitches == []:
            continue
        delta = right.pitches[-1] - left.pitches[-1]
        if abs(delta) > max_int:
            return False
    return True

@Constraint
def constraint_notes_are(sequence: FixedSequence, beat_offset: int, pitches: List[int]) -> bool:
    """Tells us if the context note on the given beat_offset
    has the same pitches as the given list of pitches
    """
    if beat_offset > sequence.duration:
        return True
    offset_event = sequence.event_at(beat_offset)
    return sorted(offset_event.pitches) == sorted(pitches)

@Constraint
def constraint_no_voice_crossing(sequence: FixedSequence, upper_voice: Sequence) -> bool:
    """Tells us if the top pitch of the context is lower than
    the top pitch of voice1 for the same time offset.
    """
    for i in range(len(sequence.events)):
        try:
            upper_event = upper_voice.events[i]
        except IndexError:
            return True
        lower_event = sequence.events[i]
        if lower_event.pitches[-1] > upper_event.pitches[-1]:
            return False
    return True
