"""Library functions for performing transformations on an existing Sequence.
All transformers act upon a given source Sequence to derrive a new List or
Iterator of Event objects.
"""
import itertools
import math
import random
from typing import List, Optional, Iterator, Union, Callable, Set, Any

import more_itertools

from ..core import Event, Sequence, Transformer, Context, Constraint
from ..resources import NOTE_MIN, NOTE_MAX

@Transformer
def loop(seq: Sequence,
    n_times: Optional[int]=None) -> Iterator[Event]:
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
def slice_looper(seq: Sequence,
    n_events: int,
    n_repeats: int = 1) -> Iterator[Event]:
    buffer = []
    for event in seq.events:
        if len(buffer) <= n_events:
            buffer.append(event)
        else:
            for _i in range(n_repeats):
                for event in buffer:
                    yield event
            buffer = []
    for event in buffer:
        yield event

@Transformer
def feedback(seq: Sequence,
    n_events: int) -> Iterator[Event]:
    buffer = []
    for event in seq.events:
        buffer.insert(0, event)
        if len(buffer) < n_events:
            yield event
            continue
        event2 = buffer.pop()
        event.pitches = {* event.pitches + event2.pitches}
        event.pitches = sorted(list(event.pitches))
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
    rotated = list(itertools.islice(seq.events, 0, n_pitches))
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
            if event is None:
                continue
            pitches = pitches + list(
                filter(lambda p: p is not None, event.pitches))
        yield Event(
            sorted(pitches),
            duration) # type: ignore

@Transformer
def linear_interpolate(seq: Sequence,
    steps=0,
    constrain_to_scale: Optional[List[int]] = None) -> Iterator[Event]:
    """Return a new sequence with extra events added to fill in the melodic
    gaps between sucessive events in the source seq.
    Pitches are choosen from the chromatic set, unless constrain_to_scale
    is offered.
    """
    for left, right in more_itertools.windowed(seq.events, 2, fillvalue=None):
        if right is None:
            yield left
        pitch_vector = right.pitches[-1] - left.pitches[-1]
        if pitch_vector == 0:
            yield left
        pitch_increment = int(pitch_vector/steps)
        if pitch_increment == 0:
            yield left
        duration_increment = left.duration/steps
        for _i in range(steps):
            new_pitch = left.pitches[-1] + pitch_increment
            if constrain_to_scale is not None:
                new_pitch = min(constrain_to_scale, key=lambda x:abs(x-new_pitch))
            yield Event([new_pitch], duration_increment)
            pitch_increment = pitch_increment + pitch_increment

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
        for right in seq.events[-1]:
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
    iter_pulses = itertools.cycle(iter(pulse_sequence.events))
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
    iter_pitches = itertools.cycle(iter(pitch_sequence.events))
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
def fit_to_range(seq: Sequence,
    min_pitch=NOTE_MIN,
    max_pitch=NOTE_MAX) -> Iterator[Event]:
    """Given a series of events, use octave displacement
    to adjust the pitches within the range(min_pitch, max_pitch).
    Raise an exception if max_pitch - min_pitch < 12
    """
    if max_pitch < min_pitch:
        raise Exception("max_pitch cannot be less than min_pitch")
    if max_pitch - min_pitch < 12:
        raise Exception("fit_to_range range must be >= 12")
    for event in seq.events:
        pitches = []
        for pitch in event.pitches:
            while pitch > max_pitch:
                pitch = pitch - 12
            while pitch < min_pitch:
                pitch = pitch + 12
            pitches.append(pitch)
        pitches = sorted(pitches)
        yield Event(pitches, event.duration)

@Transformer
def correct_voicings(seq: Sequence,
    prevent_intervals: List[int] = [1,2,6]) -> Iterator[Event]:
    for event in seq.events:
        pitches = sorted(event.pitches)
        for i in range(len(pitches)-1):
            lower = pitches[i]
            upper = pitches[i+1]
            if upper-lower in prevent_intervals:
                pitches[i+1] = upper - 12
        pitches = sorted(pitches)
        yield Event(pitches, event.duration)

@Transformer
def concertize(seq: Sequence,
        scale: List[int],
        voicing: List[int] = [0],
        direction="up") -> Iterator[Event]:
    """Given a sequence of single pitch events,
    build a chord "up" (or "down") using the series of intervals
    in voicing and the given scale context
    """
    for event in seq.events:
        if len(event.pitches) == 0:
            yield event
            continue
        new_pitches = []
        base_index = scale.index(event.pitches[-1])
        if direction == "up":
            new_pitches = event.pitches +\
                [scale[base_index + i] for i in voicing]
        if direction == "down":
            new_pitches = event.pitches +\
                [scale[base_index - i] for i in voicing]
        event.pitches = sorted(event.pitches)
        yield Event(new_pitches, event.duration)

@Transformer
def batch(seq: Sequence,
    transformations: List[Transformer]) -> Iterator[Event]:
    """Apply multiple transformations a sequence, such as
    batch(seq, [a,b,c]) == a(b(c(seq)))
    """
    for transformer in transformations:
        seq = Sequence(transformer(seq))
    return seq.events

@Transformer
def random_transformation(seq: Sequence,
    transformations: List[Transformer]) -> Iterator[Event]:
    choice = random.choice(transformations)
    seq = Sequence(choice(seq))
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
    a,b = itertools.tee(seq.events)
    transformed = transformer(Sequence(events=b))
    i = 0.0
    previous: Optional[Event] = None
    for event in a:
        if previous is not None:
            i = i + previous.duration
        context = Context(
            event = a,
            sequence = seq,
            beat_offset = i,
            previous = previous
        )
        if condition(context):
            previous = next(transformed)
            yield previous
        else:
            previous = event
            next(transformed)
            yield event

@Transformer
def arpeggiate(seq: Sequence,
    individual_note_len=None) -> Iterator[Event]:
    """Transform a sequence of chords into a series of arpeggios.
    individual_note_len is the length of each note in the 
    arpeggio. If not given, it is the length of the source chord
    divided by the number of notes in the chord.
    """
    for event in seq.events:
        n_pitches = len(event.pitches)
        if individual_note_len is None:
            individual_note_len = event.duration / n_pitches
        for note in event.pitches:
            yield Event(pitches=[note], duration=individual_note_len)

@Transformer
def displacement(seq: Sequence,
    interval: int=0) -> Iterator[Event]:
    yield Event([], duration=interval)
    for event in seq.events:
        yield event

@Transformer
def monody(seq: Sequence) -> Iterator[Event]:
    for event in seq.events:
        if len(event.pitches) == 0:
            yield event
            continue
        yield Event([event.pitches[-1]], event.duration)

@Transformer
def modal_quantize(seq: Sequence,
    scale: Set[int]) -> Iterator[Event]:
    """Provide modal rhythmic quantization - pitches in
    seq are aligned to the nearest neigbour in the
    given scale.
    """
    scale = {*scale}
    for event in seq.events:
        new_pitches = []
        for pitch in event.pitches:
            if pitch in scale:
                new_pitches.append(pitch)
                continue
            unused = scale.difference({*new_pitches})
            nearest = min(unused, key=lambda x:abs(x-pitch))
            new_pitches.append(nearest)
        yield Event(pitches=new_pitches, duration=event.duration)

@Transformer
def rhythmic_quantize(seq: Sequence,
    resolution: float = 1.0) -> Iterator[Event]:
    """Provide basic rhythmic quantization - events in
    seq are aligned to the nearest whole multiple of resolution
    """
    resolution = float(resolution)
    for event in seq.events:
        if event.duration <= resolution:
            yield Event(event.pitches, resolution)
            continue
        mod = event.duration % resolution
        if mod <= (resolution / 2.0):
            div = int(event.duration / resolution)
            yield Event(event.pitches, div * resolution)
            continue
        yield Event(event.pitches, event.duration + resolution-mod)

@Transformer
def filter_events(seq: Sequence,
    condition: Callable[[Event], bool],
    replace_w_rest = False) -> Iterator[Event]:
    """Filter events by a given condition.
    If condition returns true in response to a
    given event, the event is ommitted from the
    sequence. Use replace_w_rest to control
    whether to preserve the original rhythmic
    intentions of the line.
    """
    for event in seq.events:
        if condition(event):
            if replace_w_rest:
                yield Event([], event.duration)
            continue
        yield event

@Transformer
def random_mutation(seq: Sequence,
    key_function: Callable[[Event, Any], Event],
    choices = List[Any],
    threshold: float = 0.5) -> Iterator[Event]:
    """Weighed mutation of a given event parameter in a seq.
    Where key_function is a user-defined function that accepts
    an event and a randomly chosen value from choices,
    and returns the modified event.
    threshold is a float (0.0-1.0) that determines if the mutation should
    take place. if 0.0, it will always be applied.
    """
    for event in seq.events:
        should_mutate = random.choice(range(0, 10)) / 10
        if should_mutate < threshold:
            yield event
            continue
        choice = random.choice(choices)
        event = key_function(event, choice)
        yield event
