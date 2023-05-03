"""Using the sine_shape gate to compose a real time line with shaping
"""

import math
import random

from composerstoolkit import *

# maj 2nds, 4ths,5ths and aug5th
intervals1 = [2,5,67,11,-2,-5,-6,-7,-11]
# min 2nds, maj/min 3rds
intervals2 = [1,3,4,8,9,11,-1,-3,-4,-8,-9,-11]

NEXUS_SET = {0,4,6,7}
    
harmony_gate = enforce_shared_pitch_class_set(
            pitch_class_set=NEXUS_SET,
            get_context = lambda: Context.get_context())

flute = Sequence.from_generator(random_slice(
    Sequence.from_generator(collision_pattern(3,5))
)).transform(
    map_to_intervals(intervals=intervals1, starting_pitch=65, random_order=True, min=60, max=90)
).transform(
    shape_sine(period_beats=20,
    get_context = lambda: Context.get_context())
)


oboe = Sequence.from_generator(random_slice(
    Sequence.from_generator(collision_pattern(3,5))
)).transform(
    map_to_intervals(intervals=intervals2, starting_pitch=65, random_order=True, min=60, max=90)
).transform(
    harmony_gate
).transform(
    shape_sine(period_beats=40,
    get_context = lambda: Context.get_context())
)


mysequencer = Context.get_context().new_sequencer(bpm=120, playback_rate=1, debug=True)\
    .add_sequence(flute, channel_no=1)\
    .add_sequence(oboe, channel_no=2)

mysequencer.playback()