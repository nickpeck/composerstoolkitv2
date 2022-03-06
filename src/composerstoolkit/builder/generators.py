from typing import List

from ..core import Event

def cantus(list_pitches: List[int] = []) -> List[Event]:
    return [Event(pitches=[p]) for p in list_pitches]

def cantus_from_pulses(list_pulses: List[int] = []) -> List[Event]:
    return [Event(duration=d) for d in list_pulses]

def steady_pulse(ticks : int=0, n_pulses: int=1) -> List[Event]:
    return [Event(duration=ticks) for i in range(n_pulses)]

def collision_pattern(x: int, y: int) -> List[Event]:
    """given clocks in the ratio x:y , 
    generate the sequence of attack points 
    that results from the colision of their pulses.
    For example, given clocks 200 & 300, the resulting 
    sequence of (pitch,duration) events would be:
    
    [(None, 200),(None, 100),(None, 100),(None, 200)]
    """
    if x == y:
        return [Event(duration=x)]
    n_ticks = x * y
    pulse_pattern = [0 for i in range(0, n_ticks)]
    for i in range(0, n_ticks):
        if i % x == 0 or i % y == 0:
            pulse_pattern[i] = 1

    durations = []
    cur_duration = None

    for i in range(n_ticks -1):
        current = pulse_pattern[i]

        if current is 1:
            if cur_duration is not None:
                durations.append(cur_duration)
            cur_duration = 1
        elif current is 0:
            if cur_duration is None:
                cur_duration = 1
            else:
                cur_duration = cur_duration + 1
    if cur_duration is None:
        cur_duration = 0
    durations.append(cur_duration + 1)

    return [Event(duration=d) for d in durations]
