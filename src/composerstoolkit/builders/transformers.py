"""Library functions for performing transformations on an existing Sequence.
All transformers act upon a given source Sequence to derrive a new List or
Iterator of Event objects.
"""
import itertools
import math
from typing import List, Optional, Iterator, Union, Callable

import more_itertools

from ..core import Event, Sequence, Transformer, Context

@Transformer
def loop(seq: Sequence, n_times: Optional[int]=None) -> Iterator[Event]:
    """Loop a sequence.
    If n_times is None, loop repeatedly.
    """
    if n_times is None:
        for item in itertools.cycle(seq.events):
            yield item
        return
    if n_times < 0:
        raise ValueError("n_times cannot be less than 0")
    saved = []
    for element in seq.events:
        yield element
        saved.append(element)
    for _i in range(n_times):
        for element in saved:
            yield element

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
def transpose_diatonic(seq: Sequence,
        steps: int,
        scale: list,
        pass_on_error = False) -> Iterator[Event]:
    """Transpose all pitches by a number of steps
    within the given scale.
    Where scale is the complete range of pitch numbers
    occupied by that scale across the whole MIDI pitch
    range (0...127)

    if pass_on_error is set to True, an exception will
    be raised if a pitch is not found in the source
    scale. Otherwise the pitch is emitted, unaltered.
    """
    if isinstance(scale, set):
        scale = list(scale)
    for evt in seq.events:
        pitches = evt.pitches
        new_event = Event([], evt.duration)
        for pitch in pitches:
            try:
                cur_index = scale.index(pitch)
            except ValueError as verr:
                if pass_on_error:
                    raise verr
                new_event.pitches.append(pitch)
                continue
            new_index = cur_index + steps
            try:
                new_pitch = scale[new_index]
            except IndexError:
                continue
            new_event.pitches.append(new_pitch)
        new_event.pitches = sorted(new_event.pitches)
        yield new_event

@Transformer
def retrograde(seq: Sequence, n_pitches: int) -> Iterator[Event]:
    """Cut a section up to n_pitches from the start of the
    sequence and return the pitches in reverse order
    """
    _slice = list(itertools.islice(seq.events, 0, n_pitches))
    _slice.reverse()
    return _slice

@Transformer
def invert(seq: Sequence, axis_pitch=None) -> Iterator[Event]:
    """Invert the pitches about a given axis (mirror it
    upside down). If axis_pitch is not given, invert about
    the first pitch in the sequence.
    """
    if axis_pitch is None:
        try:
            evt = next(seq.events)
        except StopIteration:
            return
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
def rotate(seq: Sequence, n_pitches: int, no_times=1) -> Iterator[Event]:
    """Cut a section up to n_pitches from the start of the
    sequence and return the events with their order of pitches
    rotated up to no_times
    """
    rotated = list(itertools.islice(seq, 0, n_pitches))
    for _i in range(no_times):
        rotated = rotated[1:] + [rotated[0]]
    return rotated

@Transformer
def aggregate(seq: Sequence,
    n_voices: int=4,
    duration: int=1) -> Iterator[Event]:
    """Return a new stream of events in which each slice of
    pitches (up to n_voices) has been aggregated into a chordal
    structure.
    """
    for group in more_itertools.grouper(seq.events, n_voices):
        pitches = []
        for event in group:
            pitches = pitches + list(
                filter(lambda p: p is not None, event.pitches))
        yield Event(
            sorted(pitches),
            duration) # type: ignore

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
    """Progressively expand the intervals between
    each event in the source Sequence by a given factor.
    mode is either 'exponential' or 'linear'
    """
    events = list(seq.events)[:]
    if len(events) == 1:
        return events

    def _vectors(seq):
        vectors = []
        left = seq.events[0]
        for right in seq.events[1:]:
            # if any event is a chord, then select the uppermost voice
            vectors.append(right.pitches[0]-left.pitches[0])
            left = right
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
    """Return a new stream of events in which all the durations of
    the source sequence have been expanded by a given factor.
    """
    return (Event(e.pitches, multiplier*e.duration) for e in seq.events)

@Transformer
def rhythmic_diminution(seq: Sequence, factor: Union[int, float]) -> Iterator[Event]:
    """Return a new stream of events in which all the durations of
    the source sequence have been reduced by a given factor.
    """
    return (Event(e.pitches, math.floor(e.duration/factor)) for e in seq.events)

@Transformer
def map_to_pulses(seq: Sequence, pulse_sequence: Sequence) -> Iterator[Event]:
    """Return a new stream of events which has the durations of
    pitch_sequence mapped to the events of seq.
    """
    iter_pulses = iter(pulse_sequence.events)
    for event in seq.events:
        try:
            next_pulse = next(iter_pulses)
            yield Event(event.pitches, next_pulse.duration)
        except StopIteration:
            return

@Transformer
def map_to_pitches(seq: Sequence, pitch_sequence: Sequence) -> Iterator[Event]:
    """Return a new stream of events which has the pitches of
    pitch_sequence mapped to the events of seq.
    """
    iter_pitches = iter(pitch_sequence.events)
    for event in seq.events:
        try:
            next_pitch = next(iter_pitches)
            yield Event([next_pitch.pitches[0]], event.duration)
        except StopIteration:
            yield Event([], event.duration)

@Transformer
def tie_repeated(seq: Sequence) -> Iterator[Event]:
    """Tie events notes with repeated pitches
    """
    grouped = itertools.groupby(seq.events, key=lambda e: e.pitches)
    for pitches, group in grouped:
        yield Event(pitches, sum([e.duration for e in group]))

@Transformer
def batch(seq: Sequence,
    transformations: List[Transformer]) -> Iterator[Event]:
    """Apply multiple transformations a sequence, such as
    batch(seq, [a,b,c]) == a(b(c(seq)))
    """
    for transformer in transformations:
        seq = Sequence(transformer(seq))
    print(seq)
    return seq.events

@Transformer
def gated(seq: Sequence,
    transformer: Transformer,
    condition: Callable[[Context], bool]) -> Iterator[Event]:
    """Return a new stream of events such as that:
    whenever condition evaluates to true, we return the next
    item in the transformed sequence.
    Otherwise, return the next item in the source sequence
    """
    transformed = transformer(seq)
    i = 0
    previous: Optional[Event] = None
    for event in seq.events:
        i = i + 1
        context = Context(
            event = event,
            sequence = seq,
            beat_offset = i,
            previous = previous
        )
        if condition(context):
            try:
                previous = next(transformed)
                yield previous
            except StopIteration:
                return
        else:
            previous = event
            yield previous
