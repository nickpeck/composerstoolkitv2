import itertools
from typing import List,Set
import random

from ..core import Constraint, FiniteSequence

@Constraint
def probability_gate(
    sequence: FiniteSequence,
    constraint:Constraint,
    probability: float=1.0):
    """Meta-constraint - can add a bit
    more variety to the outcome, by randomly
    ignoring a failed rule by a certain
    probability factor.
    if the outcome of testing a
    sequence by constraint returns False,
    randomly flip the outcome, allowing the
    'mistake' to pass. The likelyhood of
    this happening is weighted in favour
    of probability, on a scale 0..1
    (where 1 indicates it is always flipped)
    """
    if probability > 1 or probability < 0:
        raise Exception("probability must be in the range 0..1")
    result = constraint(sequence)
    if result:
        return True
    choices = [True, False]
    weights = [probability, 1-probability]
    choice = random.choices(choices, weights)[0]
    return choice

@Constraint
def constraint_range(sequence: FiniteSequence,
    minimum: int,
    maximum: int) -> bool:

    if sequence.to_pitch_set() == {}:
        return False
    pitches = sorted(sequence.pitches)
    return pitches[0] >= minimum and pitches[-1] <= maximum

@Constraint
def constraint_in_set(sequence: FiniteSequence,
    _set = range(0,128),
    lookback_n_beats=None) -> bool:
    if sequence.to_pitch_set() == {}:
        return True
    if lookback_n_beats is None:
        return sequence.to_pitch_set().issubset(_set)
    return sequence.time_slice(
        sequence.duration - lookback_n_beats,
        sequence.duration
    ).to_pitch_set().issubset(_set)

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
        if len(intersection) <= min_shared:
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
        if interval not in allow_intervals:
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

@Constraint
def constraint_use_chords(
    sequence: FiniteSequence,
    chords: List[Set],
    voices: List[FiniteSequence]) -> bool:

    cur_time = 0
    it1,it2 = itertools.tee(sequence.events)
    next(it2, None)
    for left, right in zip(it1,it2):
        cur_time = cur_time + left.duration
        pcs = {*[pitch % 12 for pitch in left.pitches]}
        for voice in voices:
            evt = voice.event_at(cur_time)
            pcs = pcs.union({*[pitch % 12 for pitch in evt.pitches]})
        found_match= False
        for _set in chords:

            if pcs.difference(_set) == set():
                found_match = True
                break
        if not found_match:

            return False
    return True
