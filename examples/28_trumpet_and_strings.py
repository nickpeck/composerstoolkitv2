import math
import random
import logging

from composerstoolkit import *

intervals1 = range(-11,11)

NEXUS_SET = {0,2,5}
    
harmony_gate = enforce_shared_pitch_class_set(
            pitch_class_set=NEXUS_SET,
            get_context = lambda: Context.get_context())

trumpet = Sequence.from_generator(random_slice(
    Sequence.from_generator(collision_pattern(3,5))
)).transform(
    map_to_intervals(intervals=intervals1, starting_pitch=65, random_order=True, min=60, max=90)
).transform(
    harmony_gate
).transform(
    shape_sine(period_beats=20,
    get_context = lambda: Context.get_context())
).transform(
    tie_repeated()
).transform(
    linear_interpolate(steps=4)
)

cello = Sequence.from_generator(random_slice(
    Sequence.from_generator(collision_pattern(1,4))
)).transform(
    map_to_intervals(intervals=intervals1, starting_pitch=40, random_order=True, min=30, max=65)
).transform(
    harmony_gate
).transform(
    shape_sine(period_beats=20,
    get_context = lambda: Context.get_context())
)

strings = Sequence.from_generator(
    chord_cycle(
        scale=scales.chromatic,
        start=Event(pitches=[60,64,66,67], duration=16),
        cycle_of=-4,
        max_len=16)).transform(loop())

mysequencer = Context.get_context().new_sequencer(bpm=220, playback_rate=1, debug=True)\
    .add_sequence(trumpet, track_no=2)\
    .add_sequence(cello, track_no=14)\
    .add_sequence(strings, track_no=3)

mysequencer.playback()