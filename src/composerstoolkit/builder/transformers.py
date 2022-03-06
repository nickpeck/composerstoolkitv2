import itertools
import math
from typing import List, Optional, Iterator, Union

from ..core import Event, Sequence, Transformer

@Transformer
def loop(seq: Sequence, n_times: Optional[int]=None) -> Iterator[Event]:
    """Loop a sequence.
    If n_times is None, loop repeatedly.
    """
    if n_times is None:
        while True:
            for event in seq.events:
                yield event
    if n_times < 0:
        raise ValueError("n_times cannot be less than 0")
    for i in range(n_times):
        for event in seq.events:
                yield event

@Transformer
def transpose(seq: Sequence, interval: int) -> Iterator[Event]:
    """Transpose all pitches in the 
    given sequence by a constant interval.
    """
    for evt in seq.events:
        yield Event(
                pitches=[p + interval for p in evt.pitches],
                duration=evt.duration)

@Transformer
def retrograde(seq: Sequence) -> List[Event]:
    events = list(seq.events)[:]
    events.reverse()
    return events

@Transformer
def invert(seq: Sequence, axis_pitch=None) -> Iterator[Event]:
    if axis_pitch is None:
        evt = next(seq.events)
        axis_pitch = evt.pitches[0]
        yield evt
    for evt in seq.events:
        delta = evt.pitches[0]-axis_pitch
        if delta < 0: # note is below axis
            yield Event([axis_pitch-delta], evt.duration)
        elif delta > 0: # note is above axis
            yield Event([axis_pitch-delta], evt.duration)
        else: #its the axis, so stays the same
            yield Event([evt.pitches[0]], evt.duration)

@Transformer
def rotate(seq: Sequence, no_times=1) -> List[Event]:
    if seq.events == []:
        return []
    rotated = list(seq.events)[:]
    for i in range(no_times):
        rotated = rotated[1:] + [rotated[0]]
    return rotated

@Transformer
def aggregate_into_chords(seq: Sequence,
    n_voices: int=4,
    duration: int=1) -> Iterator[Event]:

    for pitches in itertools.islice(seq.events, n_voices):
        yield Event(list(pitches), duration) # type: ignore

# @Transformer
# def linear_interpolate(seq, resolution=1):
    # events = seq.events[:]
    # if len(events) is 1:
        # return events
        
    # def _vectors(seq):
        # vectors = []
        # x = seq.events[0]
        # for y in seq.events[1:]:
            # vectors.append(y.pitch-x.pitch)
            # x = y
        # return vectors
        
    ## first item in the seq stays as-is
    # i_events = iter(seq.events)
    # i_vectors = iter(_vectors(seq))
    # result = [next(i_events)]
    
    # pitch = result[0].pitch
    # duration = result[0].duration
    # while True:
        # try:
            # next_event = next(i_events)
            # next_vector = next(i_vectors)
            # pitch_increment = next_vector/resolution
            # dur_increment = duration/resolution
            # for x in range(resolution):
                # result.append(Event(
                    # math.ceil((x * pitch_increment) + pitch),
                    # dur_increment
                # ))
            # pitch = next_event.pitch
            # duration = next_event.duration
        # except StopIteration:
            # break
    # return result

@Transformer
def explode_intervals(seq: Sequence,
    factor: Union[int, float],
    mode: str="exponential") -> List[Event]:

    events = list(seq.events)[:]
    if len(events) is 1:
        return events

    def _vectors(seq):
        vectors = []
        x = seq.events[0]
        for y in seq.events[1:]:
            # if any event is a chord, then select the uppermost voice
            vectors.append(y.pitches[0]-x.pitches[0])
            x = y
        return vectors

    if mode == "exponential":
        interval_vectors = [(factor * v)for v in _vectors(seq)]
    elif mode == "linear":
        interval_vectors = [(factor + v) for v in _vectors(seq)]
    else:
        raise Exception("unrecognised mode "+ mode)

    # first item in the seq stays as-is
    i_events = iter(seq.events)
    i_vectors = iter(interval_vectors)
    result = [next(i_events)]
    # apply the interval_vectors to distort the remaining items
    pitch = result[0].pitches[0] # once again, assuming the top voice of any chord
    while True:
        try:
            next_event = next(i_events)
            next_vector = next(i_vectors)
            pitch = math.ceil(next_vector + pitch)
            result.append(Event([pitch], next_event.duration))
        except StopIteration:
            break
    return result

@Transformer
def rhythmic_augmentation(seq: Sequence, multiplier: int) -> Iterator[Event]:
    return (Event(e.pitches, multiplier*e.duration) for e in seq.events)

@Transformer
def rhythmic_diminution(seq: Sequence, factor: Union[int, float]) -> Iterator[Event]:
    return (Event(e.pitches, math.floor(e.duration/factor)) for e in seq.events)

@Transformer
def map_to_pulses(seq: Sequence, pulse_sequence: Sequence) -> Iterator[Event]:
    iter_pulses = iter(pulse_sequence.events)
    for e in seq.events:
        try:
            next_pulse = next(iter_pulses)
            yield Event(e.pitches, next_pulse.duration)
        except StopIteration:
            return

@Transformer
def map_to_pitches(seq: Sequence, pitch_sequence: Sequence) -> Iterator[Event]:
    iter_pitches = iter(pitch_sequence.events)
    for e in seq.events:
        try:
            next_pitch = next(iter_pitches)
            yield Event([next_pitch.pitches[0]], e.duration)
        except StopIteration:
            yield Event([], e.duration)

