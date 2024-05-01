"""Library functions for performing transformations on an existing Sequence.
All transformers act upon a given source Sequence to derrive a new List or
Iterator of Event objects.
"""
import itertools
import logging
import math
import random
import time
from typing import List, Optional, Iterator, Union, Callable, Set, Any, Dict

import more_itertools

from ..core import Event, Sequence, Transformer, Context, Constraint, FiniteSequence
from ..resources import NOTE_MIN, NOTE_MAX, pitchset

@Transformer
def rest(seq: Sequence):
    """Remove any pitches but retain the durations,
    creating a series of rest events.
    """
    for event in seq.events:
        yield event.extend(pitches=[])

@Transformer
def loop(seq: Sequence,
    n_times: Optional[int]=None) -> Iterator[Event]:
    """Loop a sequence.
    If n_times is None, loop repeatedly.
    """
    if n_times is None:
        for item in itertools.cycle(seq.events):
            yield item
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
    """Loop up to n_events of a given sequence"""
    buffer = []
    for event in seq.events:
        if len(buffer) < n_events:
            buffer.append(event)
        else:
            for _i in range(n_repeats):
                for evt in buffer:
                    yield evt
            buffer = [event]
    for event in buffer:
        yield event


@Transformer
def loop_capture(seq: Sequence, toggle=lambda: True, debug=False):
    """
    Capture midi events and play them back in a loop.
    toggle is a function that changes state in and out of capture mode (which could be based on a MIDI
    controller status, or a pre-determined algorithm).
    Whilst toggle returns True, capture events into a buffer
    when the toggle state changes to False, loop playback through the buffer until
    toggle status flips back to True again, at which point the capture process repeats.
    """
    itterable = seq.events
    while True:
        if not toggle():
            yield next(itterable)
            continue
        if debug:
            logging.getLogger().debug("loop_capture starting event capture")
        buffer = FiniteSequence()
        holding = {}
        def handle_realtime_event(event):
            if event.meta["realtime"] == "note_on":
                for pitch in event.pitches:
                    new_event = event.extend(pitches=[pitch])
                    del new_event.meta["realtime"]
                    holding[pitch] = (event, time.time())
            elif event.meta["realtime"] == "note_off":
                for pitch in event.pitches:
                    stored_event, start_time = holding.get(pitch, (None, None))
                    if stored_event is not None:
                        bpm = seq.meta.get("bpm", 60)
                        stored_event.duration = (time.time() - start_time) * (bpm / 60)
                        buffer.events.append(stored_event)
                        del holding[pitch]

        for event in itterable:
            if toggle():
                if "realtime" in event.meta:
                    handle_realtime_event(event)
                yield(event) # pass-through events during capture
            else:
                # exit capture state
                break
        if debug:
            logging.getLogger().debug("loop_capture starting buffer loop playback")
        buffer = buffer.to_sequence().transform(loop())
        while not toggle():
            for event in buffer.events:
                yield event
                if toggle():
                    break
        if debug:
            logging.getLogger().debug("loop_capture playback ending")


@Transformer
def feedback(seq: Sequence,
    n_events: int) -> Iterator[Event]:
    """
    Modify a stream of events by persisting pitches for up to n_events forwards
    """
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
        yield evt.extend(
                pitches=[p + interval for p in evt.pitches],
                duration=evt.duration)

@Transformer
def transpose_diatonic(seq: Sequence,
        steps: int,
        scale: list,
        pass_on_error = True) -> Iterator[Event]:
    """Transpose all pitches by a number of steps
    within the given scale.
    Where scale is the complete range of pitch numbers
    occupied by that scale across the whole MIDI pitch
    range (0...127)

    if pass_on_error is set to False, an exception will
    be raised if a pitch is not found in the source
    scale. Otherwise the pitch is emitted, unaltered.
    """
    if isinstance(scale, set):
        scale = list(scale)
    for evt in seq.events:
        pitches = evt.pitches
        new_event = evt.extend(pitches=[])
        for pitch in pitches:
            try:
                cur_index = scale.index(pitch)
            except ValueError as verr:
                if not pass_on_error:
                    raise verr
                new_event.pitches.append(pitch)
                continue
            new_index = cur_index + steps
            # try:
            new_pitch = scale[new_index]
            # except IndexError:
                # continue
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
            yield evt.extend(pitches=[axis_pitch-delta])
        elif delta > 0: # note is above axis
            yield evt.extend(pitches=[axis_pitch-delta])
        else: #its the axis, so stays the same
            yield evt.extend(pitches=[evt.pitches[0]])

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
        meta = {}
        for event in group:
            if event is None:
                continue
            pitches = pitches + list(
                filter(lambda p: p is not None, event.pitches))
            meta.update(event.meta)
        yield Event(
            sorted(pitches),
            duration,
            meta) # type: ignore

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
            return
        pitch_vector = right.pitches[-1] - left.pitches[-1]
        if pitch_vector == 0:
            yield left
            continue
        pitch_increment = int(pitch_vector/steps)
        # if pitch_increment == 0:
            # yield left
            # continue
        yield left
        duration_increment = left.duration/steps
        for _i in range(steps-1):
            new_pitch = left.pitches[-1] + pitch_increment
            if constrain_to_scale is not None:
                new_pitch = min(constrain_to_scale, key=lambda x:abs(x-new_pitch))
            yield Event([new_pitch], duration_increment, left.meta)
            pitch_increment = pitch_increment + pitch_increment
    yield right

@Transformer
def motivic_interpolation(seq: Sequence,
    motive: FiniteSequence) -> Iterator[Event]:
    """Map fixed sequence motive to every note of motive
    """
    if not isinstance(motive, FiniteSequence):
        raise Exception("Motive should be a FiniteSequence")
    is_first = True
    if motive.events[0].pitches == []:
        raise Exception("The motive must start with a pitch event")
    for base_evt in seq.events:
        if base_evt.pitches == []:
            yield base_evt
            continue
        if is_first:
            pitch_delta = base_evt.pitches[-1] - motive.events[0].pitches[-1]
            is_first = False
        else:
            pitch_delta = base_evt.pitches[-1] - motive.events[0].pitches[-1]
        duration = base_evt.duration
        for motive_evt in motive.events:
            relative_dur = motive_evt.duration/motive.duration
            dur = duration * relative_dur
            if motive_evt.pitches == []:
                yield base_evt.extend(pitches=[], duration=dur)
                continue
            new_pitches = [p + pitch_delta for p in motive_evt.pitches]
            yield base_evt.extend(pitches=new_pitches, duration=dur)

@Transformer
def explode_intervals(seq: Sequence,
    n_events: int,
    factor: Union[int, float],
    mode: str="exponential") -> List[Event]:
    """Progressively expand the intervals between
    each event in the source Sequence by a given factor.
    mode is either 'exponential' or 'linear'
    """
    sliced = list(itertools.islice(seq.events, 0, n_events))
    if len(sliced) == 1:
        return iter((sliced[0],))

    def _vectors(sliced):
        vectors = []
        left = sliced[0]
        for right in sliced[1:]:
            # if any event is a chord, then select the uppermost voice
            vectors.append(right.pitches[0]-left.pitches[0])
            left = right
        return vectors

    if mode == "exponential":
        interval_vectors = [(factor * v)for v in _vectors(sliced)]
    elif mode == "linear":
        interval_vectors = [(factor + v) for v in _vectors(sliced)]
    else:
        raise Exception("unrecognised mode "+ mode)

    # first item in the seq stays as-is
    i_events = iter(sliced)
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
    for e in seq.events:
        if "realtime" in e.meta:
            yield e
            continue
        yield e.extend(duration=multiplier*e.duration)

@Transformer
def rhythmic_diminution(seq: Sequence, factor: Union[int, float]) -> Iterator[Event]:
    """Return a new stream of events in which all the durations of
    the source sequence have been reduced by a given factor.
    """
    for e in seq.events:
        if "realtime" in e.meta:
            yield e
            continue
        yield e.extend(duration=e.duration/factor)

@Transformer
def map_to_pulses(seq: Sequence, pulse_sequence: Sequence) -> Iterator[Event]:
    """Return a new stream of events which has the durations of
    pitch_sequence mapped to the events of seq.
    """
    iter_pulses = itertools.cycle(iter(pulse_sequence.events))
    for event in seq.events:
        try:
            next_pulse = next(iter_pulses)
            yield event.extend(duration=next_pulse.duration)
        except StopIteration:
            yield event.extend(duration=0)

@Transformer
def map_to_pitches(seq: Sequence, pitch_sequence: Sequence) -> Iterator[Event]:
    """Return a new stream of events which has the pitches of
    pitch_sequence mapped to the events of seq.
    """
    iter_pitches = itertools.cycle(iter(pitch_sequence.events))
    for event in seq.events:
        try:
            next_pitch = next(iter_pitches)
            yield event.extend(pitches=[next_pitch.pitches[0]])
        except StopIteration:
            yield event.extend(pitches=[])


@Transformer
def map_to_intervals(seq: Sequence,
        starting_pitch: int,
        intervals:List[int],
        random_order=True,
        min=NOTE_MIN,
        max=NOTE_MAX) -> Iterator[Event]:
    """Return a new stream of events which yields a melodic
    pitch_sequence mapped to the events of seq using the given intervals,
    either in order, or randdm order.
    """
    pitch = starting_pitch
    def it():
        l = len(intervals)
        while True:
            r1 = random.choice(range(0, l))
            r2 = random.choice(range(r1, l))
            list = intervals[r1:r2]
            for r in list:
                yield r
    iter_intervals = it()
    for event in seq.events:
        next_int = next(iter_intervals)
        _pitch = pitch + next_int
        if _pitch >= min and _pitch <= max:
            pitch = _pitch
            yield event.extend(pitches=[pitch])

@Transformer
def tie_repeated(seq: Sequence) -> Iterator[Event]:
    """Tie events notes with repeated pitches
    """
    grouped = itertools.groupby(seq.events, key=lambda e: e.pitches)
    for pitches, group in grouped:
        yield Event(pitches=pitches, duration=sum([e.duration for e in group]))

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
        yield event.extend(pitches=pitches)

@Transformer
def concertize(seq: Sequence,
        scale: List[int],
        voicing: List[int] = [0],
        direction="up") -> Iterator[Event]:
    """Given a sequence of single pitch events,
    build a chord "up" (or "down") using the series of intervals
    in voicing and the given scale context
    """
    if not isinstance(scale, list):
        scale = list(scale)
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
        yield event.extend(pitches=new_pitches)

@Transformer
def batch(seq: Sequence,
    transformations: List[Transformer]) -> Iterator[Event]:
    """
    Apply multiple transformations a sequence, such as
    batch(seq, [a,b,c]) == a(b(c(seq)))
    """
    for transformer in transformations:
        seq = seq.extend(events=transformer(seq))
    return seq.events

@Transformer
def random_transformation(seq: Sequence,
    transformations: List[Transformer]) -> Iterator[Event]:
    """
    Select a transformation at random from transformations and
    return a new sequence with this transformation applied
    """
    choice = random.choice(transformations)
    seq = seq.extend(events=choice(seq))
    return seq.events

@Transformer
def gated(seq: Sequence,
    transformer: Transformer,
    condition: Callable[[Context], bool],
    get_context = lambda: Context.get_context()) -> Iterator[Event]:
    """
    Return a new stream of events such as that:
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
        context = get_context()
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
    """
    Transform a sequence of chords into a series of arpeggios.
    individual_note_len is the length of each note in the 
    arpeggio. If not given, it is the length of the source chord
    divided by the number of notes in the chord.
    """
    for event in seq.events:
        n_pitches = len(event.pitches)
        if individual_note_len is None:
            individual_note_len = event.duration / n_pitches
        for note in event.pitches:
            yield event.extend(pitches=[note], duration=individual_note_len)

@Transformer
def displacement(seq: Sequence,
    interval: int=0) -> Iterator[Event]:
    """
    Displace a seires of events by a duration of 'interval'
    """
    yield Event([], duration=interval)
    for event in seq.events:
        yield event

@Transformer
def monody(seq: Sequence) -> Iterator[Event]:
    """
    Transforms a sequence of events by filtering all but the uppermost pitch
    """
    for event in seq.events:
        if len(event.pitches) == 0:
            yield event
            continue
        yield event.extend(pitches=[event.pitches[-1]])

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
        yield event.extend(pitches=new_pitches)

@Transformer
def rhythmic_quantize(seq: Sequence,
    resolution: float = 1.0) -> Iterator[Event]:
    """Provide basic rhythmic quantization - events in
    seq are aligned to the nearest whole multiple of resolution
    """
    resolution = float(resolution)
    for event in seq.events:
        if event.duration <= resolution:
            yield event.extend(duration=resolution)
            continue
        mod = event.duration % resolution
        if mod <= (resolution / 2.0):
            div = int(event.duration / resolution)
            yield event.extend(duration=div * resolution)
            continue
        # yield Event(event.pitches, event.duration + resolution-mod)

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
                yield event.extend(pitches=[])
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

@Transformer
def shape_sine(seq: Sequence,
    get_context = lambda: Context.get_context(),
    period_beats = 100, min=60, max=90, phase=0):
    """Only allows events to pass such as that the
    shape of the resulting line obeys a sine shape.
    """
    last_pitch = None
    for event in seq.events:
        if not last_pitch:
            last_pitch = event.pitches[0]
            continue
        cur_pitch = event.pitches[0]
        if cur_pitch > max or cur_pitch < min:
            continue
        context = get_context()
        beats = context.beat_offset
        beat = context.beat_offset % period_beats
        degrees = (beat/period_beats * 360) - phase % 360
        radians = math.radians(degrees)
        sine_value = math.sin(radians)
        weights = [sine_value, random.randrange(-10,10,1)/10, -sine_value]
        active = random.choices([1, 0, -1], weights)[0]
        if active == 1:
            if cur_pitch > last_pitch:
                last_pitch = cur_pitch
                yield event
        elif active == -1:
            if cur_pitch < last_pitch:
                last_pitch = cur_pitch
                yield event
        else:
            yield event

@Transformer
def enforce_shared_pitch_class_set(seq: Sequence,
    pitch_class_set: Set[int],
    get_context = lambda: Context.get_context()):
    """Only allow events to pass where the
    aggregate of all pitches in the context is a subset
    of the given pitch class (or vice versa).
    """
    pitch_class_set = pitchset.to_prime_form(pitch_class_set)
    for event in seq.events:
        pitches = event.pitches
        sequencer = get_context().sequencer
        aggregate = set([p % 12 for p in pitches]).union(set([p % 12 for p, _c in sequencer.active_pitches]))
        aggregate = pitchset.to_prime_form(aggregate)
        if aggregate.issubset(pitch_class_set):
            yield event

@Transformer
def rhythmic_time_points(seq: Sequence,
               time_points: Dict[str, float],
               meter_duration_beats: int):
    """
    appromixation of Babbitt's time-point technique.
    time_points, a dictionary of pitch class -> meter offset
    meter_duration_beats: length of the meter (typically 12)
    """
    is_first = True
    for left, right in more_itertools.windowed(seq.events, 2, fillvalue=None):
        left_pitch = left.pitches[0]
        left_tp = time_points[left_pitch % 12]
        right_pitch = right.pitches[0]
        right_tp = time_points[right_pitch % 12]
        if is_first and left_tp != 0:
            is_first = False
            yield Event(duration=left_tp)
        duration = right_tp - left_tp
        if right_tp < left_tp:
            duration = right_tp + meter_duration_beats - left_tp
        yield Event(pitches=[left_pitch], duration=duration)

@Transformer
def tintinnabulation(seq: Sequence, t_voice_pcs: Set[int], position: str="below"):
    """
    Adds a 2nd pitch to each event in a 'tintinnabulation' style.
    t_voice_pcs is a list or set of pitch classes for the tintinnabulation tones.
    position is 'below' or 'above', or for alternating motion use: 'belowabove' or 'abovebelow'
    """
    if len(t_voice_pcs) == 0:
        return seq
    t_voice_pcs = sorted(t_voice_pcs)
    if position not in ["below", "above", "belowabove", "abovebelow"]:
        raise Exception(f"Unrecognised tintinnabulation mode {position}")
    is_alternate = True if position in ["belowabove", "abovebelow"] else False
    if position == "belowabove":
        position = "below"
    if position == "abovebelow":
        position = "above"
    for event in seq.events:
        if len(event.pitches) == 0:
            yield event
            continue
        m_voice = event.pitches[0]
        m_voice_pc = m_voice % 12
        t_voice = m_voice

        if position == "below":
            if m_voice_pc < t_voice_pcs[0]:
                m_voice_pc = m_voice_pc + 12
            try:
                t_voice_pc = list(filter(lambda t: t < m_voice_pc, t_voice_pcs))[-1]
                t_voice = m_voice - (m_voice_pc - t_voice_pc)
            except IndexError:
                t_voice_pc = t_voice_pcs[-1]
                t_voice = m_voice - (12 - t_voice_pc)
        if position == "above":
            if m_voice_pc > t_voice_pcs[-1]:
                m_voice_pc = m_voice_pc - 12
            try:
                t_voice_pc = list(filter(lambda t: t > m_voice_pc, t_voice_pcs))[0]
                t_voice = m_voice + (t_voice_pc - m_voice_pc)
            except IndexError:
                t_voice_pc = t_voice_pcs[0]
                t_voice = m_voice + (12 - m_voice_pc)
        yield Event(pitches=[m_voice, t_voice], duration=event.duration)
        if is_alternate:
            position = "below" if position == "above" else "above"

@Transformer
def split_voices(seq: Sequence, *parts: Sequence, mode="ommit"):
    """
    Split each 'chordal' event in seq into multiple sequences, creating a polyphony.
    mode is one of:
    - 'ommit' (default), if no pitches, or not enough pitches for each part, emit a 'rest' event into each lower part
    - 'doublelead' - fill all voices by doubling the lead note to compensate
    TODO add more ie doublelead
    """
    n_voices = len(parts)
    if mode not in ["ommit", "doublelead"]:
        raise Exception(f"unrecognised mode for split_voices {mode}")
    for event in seq.events:
        if mode == "ommit":
            for i,part in enumerate(parts):
                try:
                    pitch = event.pitches[i]
                    part.events = itertools.chain.from_iterable([part.events, [event.extend([pitch], event.duration)]])
                except IndexError:
                    part.events = itertools.chain.from_iterable([part.events, [event.extend(pitches=[])]])
        if mode == "doublelead":
            makeup_parts = n_voices - len(event.pitches)
            for i,part in enumerate(parts):
                if len(event.pitches) == 0:
                    pitches = []
                elif i-1 < makeup_parts:
                    pitches = [event.pitches[0]]
                else:
                    pitches = [event.pitches[i-makeup_parts]]
                part.events = itertools.chain.from_iterable([part.events, [event.extend(pitches, event.duration)]])

