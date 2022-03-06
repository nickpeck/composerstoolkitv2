from typing import List, Iterator

from ..core import Event

def cantus(pitches: Iterator[int]) -> Iterator[Event]:
    """Return a series of pitched events of duration 0, derrived
    from the given iterator.
    """
    return (Event(pitches=[p]) for p in pitches)

def pulses(pulses: List[int]) -> Iterator[Event]:
    """Return a series of durations events without pitch, derrived
    from the given iterator.
    """
    return (Event(duration=d) for d in pulses)

def collision_pattern(x: int, y: int) -> Iterator[Event]:
    """given clocks in the ratio x:y ,
    generate the sequence of attack points
    that results from the collision of their pulses.
    For example, given clocks 200 & 300, the resulting
    sequence of (pitch,duration) events would be:
    [200, 100, 100, 200]
    [(None, 200),(None, 100),(None, 100),(None, 200)]
    """
    if x == y:
        yield Event(duration=x)
        return
    n_ticks = x * y
    pulse_pattern = [0 for i in range(0, n_ticks)]
    for i in range(0, n_ticks):
        if i % x == 0 or i % y == 0:
            pulse_pattern[i] = 1

    cur_duration = None

    for i in range(n_ticks -1):
        current = pulse_pattern[i]

        if current is 1:
            if cur_duration is not None:
                yield Event(duration=cur_duration)
            cur_duration = 1
        elif current is 0:
            if cur_duration is None:
                cur_duration = 1
            else:
                cur_duration = cur_duration + 1
    if cur_duration is None:
        cur_duration = 0
    yield Event(duration=cur_duration + 1)
