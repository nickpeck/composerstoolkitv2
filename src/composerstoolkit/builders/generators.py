"""Library functions for generating an initial series of Event Objects.
All generators return a list or Iterator of Event objects
"""
from typing import Iterator, Optional
import random

from ..core import Event, Sequence

def cantus(pitches: Iterator[int]) -> Iterator[Event]:
    """Return a series of pitched events of duration 0, derrived
    from the given iterator.
    """
    return (Event(pitches=[p]) for p in pitches)

def pulses(pulse_values: Iterator[int]) -> Iterator[Event]:
    """Return a series of durations events without pitch, derrived
    from the given iterator.
    """
    return (Event(duration=d) for d in pulse_values)

def collision_pattern(clock1: int, clock2: int) -> Iterator[Event]:
    """given clocks in the ratio x:y ,
    generate the sequence of attack points
    that results from the collision of their pulses.
    For example, given clocks 200 & 300, the resulting
    sequence of (pitch,duration) events would be:
    [200, 100, 100, 200]
    [(None, 200),(None, 100),(None, 100),(None, 200)]
    """
    if clock1 == clock2:
        yield Event(duration=clock1)
        return
    n_ticks = clock1 * clock2
    pulse_pattern = [0 for i in range(0, n_ticks)]
    for i in range(0, n_ticks):
        if i % clock1 == 0 or i % clock2 == 0:
            pulse_pattern[i] = 1

    cur_duration = None

    for i in range(n_ticks -1):
        current = pulse_pattern[i]

        if current == 1:
            if cur_duration is not None:
                yield Event(duration=cur_duration)
            cur_duration = 1
        elif current == 0:
            if cur_duration is None:
                cur_duration = 1
            else:
                cur_duration = cur_duration + 1
    if cur_duration is None:
        cur_duration = 0
    yield Event(duration=cur_duration + 1)

def random_choice(choices: Iterator[Event],
    max_length: Optional[int]=None) -> Iterator[Event]:
    """Return a series of randomly chosen Events from
    the list of choices up to max_len.
    If max_len is None, the sequence is infinate.
    """
    def _chooser(choices, max_len):
        if max_len is None:
            while True:
                yield random.choice(choices)
        cummulative_len = 0
        while True:
            next_choice = random.choice(choices)
            cummulative_len = cummulative_len + next_choice.duration
            if cummulative_len >= max_len:
                return
            yield next_choice
    return _chooser(choices, max_length)

def random_slice(base_seq: Sequence,
    slice_size: Optional[int]=None,
    max_length: Optional[int]=None) -> Iterator[Event]:
    """Return a series Events by slicing random
    portions of base_seq up to size max_length
    If slice_size is None, a slice of randomly chosen
    length will be used each time.
    If max_len is None, the sequence is infinate.
    """
    src_events = list(base_seq.events)[:]
    def _get_slice_size() -> int:
        if slice_size is None:
            return random.choice(range(len(src_events)))
        return slice_size
    def _get_slice(src_events, max_len):
        cummulative_len = 0
        while True:
            start = random.choice(range(len(src_events))-1)
            size = _get_slice_size()
            sliced = src_events[start: start+size]
            cummulative_len = cummulative_len \
                + [event.duration for event in sliced]
            if cummulative_len >= max_len:
                return
            yield sliced
    return _get_slice(src_events, max_length)
