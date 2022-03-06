import itertools
import math
from typing import List, Optional, Iterator, Union, Set

from ..core import Context, Constraint, Sequence, FiniteSequence

@Constraint
def constraint_range(sequence: FiniteSequence, min: int, max: int) -> bool:
    if sequence.to_pitch_set() == {}:
        return False
    pitches = sorted(sequence.pitches)
    return pitches[0] >= min and pitches[-1] <= max

@Constraint
def constraint_in_set(sequence: FiniteSequence, _set = range(0,128)) -> bool:
    if sequence.to_pitch_set() == {}:
        return True
    return sequence.to_pitch_set().issubset(_set)

@Constraint
def constraint_no_repeated_adjacent_notes(sequence: FiniteSequence) -> bool:
    if len(sequence.events) > 2:
        return True
    it1,it2 = itertools.tee(sequence.events)
    next(it2, None)
    for left, right in zip(it1,it2):
        if right.pitches == left.pitches:
            return False
    return True

@Constraint
def constraint_limit_shared_pitches(sequence: FiniteSequence, max_shared: int=1) -> bool:
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
def constraint_enforce_shared_pitches(sequence: FiniteSequence, min_shared: int=1) -> bool:
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
def constraint_no_leaps_more_than(sequence: FiniteSequence, max_int: int) -> bool:
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
def constraint_notes_are(sequence: FiniteSequence, beat_offset: int, pitches: List[int]) -> bool:
    """Tells us if the context note on the given beat_offset
    has the same pitches as the given list of pitches
    """
    if beat_offset > sequence.duration:
        return True
    offset_event = sequence.event_at(beat_offset)
    return sorted(offset_event.pitches) == sorted(pitches)

@Constraint
def constraint_no_voice_crossing(sequence: FiniteSequence, upper_voice: FiniteSequence) -> bool:
    """Tells us if the top pitch of the context is lower than
    the top pitch of voice1 for the same time offset.
    """
    cur_time = 0
    for lower_event in sequence.events:
        cur_time = cur_time + lower_event.duration
        upper_event = upper_voice.event_at(cur_time)
        if lower_event.pitches[-1] > upper_event.pitches[-1]:
            return False
    return True

@Constraint
def constraint_restrict_to_intervals(
    sequence: FiniteSequence,
    allow_intervals: Set[int],
    upper_voice: FiniteSequence) -> bool:
    """Restrict the intervals between concurrent notes in
    seq and upper_voice to those in the set of allow_intervals.
    Where allow_intervals are intervals in the range 0...11
    (Handles compund intervals, so a 10th is considered as a 3rd)
    """
    cur_time = 0
    for lower_event in sequence.events:
        cur_time = cur_time + lower_event.duration
        upper_event = upper_voice.event_at(cur_time)
        interval = abs(upper_event.pitches[-1] - lower_event.pitches[-1]) % 12
        if abs(upper_event.pitches[-1] - lower_event.pitches[-1]) not in allow_intervals:
            return False
    return True

@Constraint
def constraint_no_consecutives(
    sequence: FiniteSequence,
    deny_intervals: Set[int],
    upper_voice: FiniteSequence) -> bool:
    """Prevent the intervals in deny_intervals
    from occuring between consecutive notes
    """
    cur_time = 0
    it1,it2 = itertools.tee(sequence.events)
    next(it2, None)
    for lwr_left, lwr_right in zip(it1,it2):
        left_time = cur_time + lwr_left.duration
        right_time = cur_time + lwr_left.duration + lwr_right.duration
        cur_time = left_time
        upr_left = upper_voice.event_at(left_time)
        upr_right = upper_voice.event_at(right_time)
        int_left = abs(upr_left.pitches[-1] - lwr_left.pitches[-1])
        int_right = abs(upr_right.pitches[-1] - lwr_right.pitches[-1])
        if int_left == int_right:
            if int_left in deny_intervals:
                return False
    return True
