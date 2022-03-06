"""Library functions for generating an initial series of Event Objects.
All generators return a list or Iterator of Event objects
"""
import itertools
import more_itertools
from typing import Iterator, Optional, Set, List
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

def axis_melody(axis_pitch: int,
    scale: List[int],
    steps: int=0,
    direction="contract") -> Iterator[Event]:
    """Return a sequence of single pitch events, where each event
    alternates +/- n steps about axis, within the given scale context.
    If direction is "contract", adjust interval so as to move
    towards the axis, otherwise, if "expand"
    move outwards until interval is reached.
    """
    if axis_pitch not in scale:
        raise Exception("pitch {} is not in the given scale".format(axis_pitch))
    if direction not in ["expand", "contract"]:
        raise Exception("direction should be 'expand' or 'contract'")

    axis_index = scale.index(axis_pitch)
    def should_continue(steps, max):
        if direction == "contract":
            return steps >= 0
        if direction == "expand":
            return steps <= max

    max = steps
    while should_continue(steps, max):
        upper = scale[axis_index + steps]
        yield Event(pitches=[upper])
        lower = scale[axis_index - steps]
        yield Event(pitches=[lower])
        if direction == "contract":
            steps = steps -1
        if should_continue(steps, max):
            if direction == "expand":
                steps = steps +1

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
            return random.choice(range(1, len(src_events)))
        return slice_size
    def _get_slice(src_events, max_len):
        cummulative_len = 0
        while True:
            start = random.choice(range(len(src_events) -2))
            size = _get_slice_size()
            sliced = src_events[start: start+size]
            cummulative_len = cummulative_len \
                + sum([event.duration for event in sliced])
            if max_len is not None:
                if cummulative_len >= max_len:
                    return
            for event in sliced:
                yield event
    return _get_slice(src_events, max_length)

def chord_cycle(scale: Set[int],
    start: Event,
    cycle_of=-4,
    voice_lead=True,
    max_length: Optional[int]=None) -> Iterator[Event]:
    """
    Useful for creating simple progressions (cycle of fifths).
    Scale can be diatonic, or chromatic.
    Given a chord event ('start') that is part of scale,
    transpose the chord about the given scalic distance (cycle_of)
    up to a duration of max_length beats.
    Each chord takes the duration of event start.
    If voice_lead is true, use octave displacement to preserve the best
    voice-leading between each chord motion.
    Raise an exception if the starting chord contains pitches outside the
    given scale.
    """
    scale = list(scale)
    sorted(scale)
    yield start
    i = start.duration
    if {*start.pitches}.difference({*scale}) != set():
        raise Exception("Starting chord is not part of the given scale")
    while True:
        if max_length is not None and i > max_length:
            return
        next_pitches = []
        for pitch in start.pitches:
            current_scale_index = scale.index(pitch)
            next_pitches.append(scale[current_scale_index + cycle_of])
        if voice_lead:
            # To enforce good voice-leading, sort the pitches by their pitch class
            left = [(i, pitch, pitch % 12) for i,pitch in enumerate(start.pitches)]
            left = sorted(left, key = lambda x: x[2])
            right = [(i, pitch, pitch % 12) for i,pitch in enumerate(next_pitches)]
            right = sorted(right, key = lambda x: x[2])
            next_pitches = []
            for l,r in zip(left, right):
                # common tones, leave as-is
                if abs(l[1] - r[1]) <= 6:
                    next_pitches.append(r[1])
                    continue
                # voice has moved, adjust octave to allow
                # for smoothest motion
                octave = int(l[1] / 12)
                next_pitches.append((octave * 12) + r[2])
        next_pitches = sorted(next_pitches)
        start = Event(pitches=next_pitches, duration=start.duration)
        yield start
        i = i + start.duration

def chords_from_scale(pitch_classes: Iterator[int],
    spacing=2,
    n_voices=4,
    allow_inversions=True) -> Iterator[Event]:
    """Useful for returning all chords within a scale represented
    by iterable pitch_classes.
    Where spacing is the number of scale steps between
    voices (eg, 2 for tertiary, 3 for quartal).
    Return a sequence of events, one for each chord, of duration 0
    """
    for index, root in enumerate(pitch_classes):
        seq = itertools.cycle(pitch_classes)
        pitches = list(more_itertools.islice_extended(
            seq,
            index, # start
            (n_voices*spacing) + index, # stop
            spacing)) # step

        chord = []
        for pitch in pitches:
            if chord == []:
                chord.append(pitch)
                continue
            if pitch < chord[-1] and not allow_inversions:
                while pitch < chord[-1]:
                    pitch = pitch + 12
                chord.append(pitch)
                continue
            chord.append(pitch)
        yield Event(pitches=chord)

def voice_lead(event: Event,
    scales: Iterator[Set[int]],
    chord_lexicon: List[Event]) -> Iterator[Event]:
    """
    Given starting chord 'start', and list of
    sets representing different modal colours,
    create a progression of chords, using
    transpositions of the voicings in chord_lexicon,
    that moves through the list of scales using
    lowest cost voice leading.

    All events take the duration and number of voices
    of the starting event.
    """
    yield event
    previous_chord = event
    for scale in scales:
        scale = {*scale}

        candidate_chords = []
        for chord in chord_lexicon:
            diff = {*chord.pitches}.difference({*scale})
            if diff == set():
                candidate_chords.append(chord)

        previous_pcs =\
            [(pitch, int(pitch/12), pitch % 12) for pitch in event.pitches]
        weighted_chords = []
        for chord in candidate_chords:
            cost = 0
            for pitch in chord.pitches:
                nearest = min(previous_chord.pitches, key=lambda x:abs(x-pitch))
                cost = cost + abs(nearest-pitch)
            weighted_chords.append((cost, chord))
        weighted_chords = sorted(weighted_chords, key=lambda c: c[0])
        next_chord = weighted_chords[0][1]
        previous_chord = Event(next_chord.pitches, event.duration)
        yield previous_chord
